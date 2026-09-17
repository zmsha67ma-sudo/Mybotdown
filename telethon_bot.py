"""
بوت تحميل فيديوهات يعمل بحسابك الشخصي على تيلجرام عبر Telethon.
يدعم إرسال ملفات لغاية 2 جيجا (بدل حد الـ 50 ميجا لبوتات Bot API العادية).

طريقة الاستخدام بعد التشغيل:
- افتح محادثة "Saved Messages" (رسائلي المحفوظة) في تيلجرام.
- أرسل رابط فيديو من X أو أي موقع مدعوم.
- البوت يحمّله ويرسله لك بأعلى جودة متوفرة بالموقع ضمن حد 2 جيجا.
- لو تبي جودة محددة، أضف الرقم بعد الرابط بنفس الرسالة، مثال:
  https://x.com/xxx/status/123 720
  (الأرقام المدعومة: 240, 360, 480, 720, 1080, 1440, 2160)
  لو ما حددت رقم، يحمّل أعلى جودة موجودة تلقائيًا.

متغيرات البيئة المطلوبة:
- API_ID, API_HASH: من https://my.telegram.org
- SESSION_STRING: تحصل عليه من تشغيل generate_session.py على جهازك أولاً
- PORT: يوفره Render تلقائيًا (لخادم فحص الصحة فقط)

متغير بيئة اختياري (لتحميل فيديوهات تتطلب تسجيل دخول، مثل المحتوى
المقيد بعمر):
- COOKIES_B64: محتوى ملف cookies.txt مُرمّز بصيغة Base64 (راجع README
  لطريقة تصديره من المتصفح وترميزه)
"""

import asyncio
import base64
import json
import logging
import os
import re
import shutil
import subprocess
import tempfile
import time

from aiohttp import web
from telethon import TelegramClient, events
from telethon.sessions import StringSession
from telethon.tl.types import DocumentAttributeVideo
from telethon.errors import FloodWaitError
import yt_dlp

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

API_ID = int(os.environ.get("API_ID", "0"))
API_HASH = os.environ.get("API_HASH", "")
SESSION_STRING = os.environ.get("SESSION_STRING", "")
PORT = int(os.environ.get("PORT", "10000"))
COOKIES_B64 = os.environ.get("COOKIES_B64", "")

MAX_FILE_SIZE = 2000 * 1024 * 1024  # 2 جيجا
URL_REGEX = re.compile(r"https?://\S+")
QUALITY_REGEX = re.compile(r"\b(240|360|480|720|1080|1440|2160)\b")

# لو مزوّد كوكيز، نفك ترميزها ونكتبها بملف عشان yt-dlp يستخدمها لاحقًا
COOKIES_FILE_PATH = None
if COOKIES_B64:
    try:
        cookies_content = base64.b64decode(COOKIES_B64).decode("utf-8")
        COOKIES_FILE_PATH = os.path.join(tempfile.gettempdir(), "cookies.txt")
        with open(COOKIES_FILE_PATH, "w", encoding="utf-8") as f:
            f.write(cookies_content)
        logging.getLogger(__name__).info("تم تحميل ملف الكوكيز بنجاح")
    except Exception:
        logging.getLogger(__name__).exception("فشل فك ترميز الكوكيز - سيتم التجاهل")
        COOKIES_FILE_PATH = None

client = TelegramClient(
    StringSession(SESSION_STRING), API_ID, API_HASH,
    # نمنع Telethon من النوم تلقائيًا عند استقبال FloodWaitError (سلوكه
    # الافتراضي لو المدة أقل من 60 ثانية) - بدلها نخلي الخطأ يوصل لكودنا
    # فورًا عشان نتجاهله بأنفسنا عبر safe_edit بدون أي تأخير حقيقي.
    flood_sleep_threshold=0,
)


def get_video_metadata(filepath: str):
    """يستخرج المدة والأبعاد عبر ffprobe (مثبت مع ffmpeg)، ويولّد صورة
    مصغّرة (thumbnail) عبر ffmpeg، عشان تيلجرام يعرض الفيديو بشكل مرتب
    (مدة، أبعاد، صورة معاينة) بدل ما يعرضه كملف عادي."""
    duration = 0
    width = 0
    height = 0
    thumb_path = None

    try:
        result = subprocess.run(
            [
                "ffprobe", "-v", "error",
                "-select_streams", "v:0",
                "-show_entries", "stream=width,height",
                "-show_entries", "format=duration",
                "-of", "json",
                filepath,
            ],
            capture_output=True, text=True, timeout=30,
        )
        data = json.loads(result.stdout)
        if data.get("streams"):
            width = int(data["streams"][0].get("width") or 0)
            height = int(data["streams"][0].get("height") or 0)
        duration = int(float(data.get("format", {}).get("duration") or 0))
    except Exception:
        logger.exception("تعذر استخراج معلومات الفيديو عبر ffprobe")

    try:
        thumb_path = filepath + "_thumb.jpg"
        subprocess.run(
            [
                "ffmpeg", "-y", "-i", filepath,
                "-ss", "00:00:01", "-vframes", "1",
                "-vf", "scale=320:-1",
                thumb_path,
            ],
            capture_output=True, timeout=30,
        )
        if not os.path.exists(thumb_path):
            thumb_path = None
    except Exception:
        logger.exception("تعذر توليد صورة مصغّرة عبر ffmpeg")
        thumb_path = None

    return duration, width, height, thumb_path


def friendly_error_message(raw_error: str) -> str:
    """يحوّل رسائل خطأ yt-dlp التقنية (أكواد/نصوص إنجليزية) لرسالة
    عربية واضحة تشرح المشكلة الفعلية بدل نص غير مفهوم للمستخدم."""
    msg = raw_error.lower()

    age_signals = [
        "sign in", "age-restricted", "age restricted", "confirm your age",
        "login required", "log in", "authentication", "private video",
        "this account", "you need to log in",
    ]
    if any(sig in msg for sig in age_signals):
        return (
            "🔞 هذا المحتوى مقيّد بعمر أو يتطلب تسجيل دخول، وما أقدر أوصله "
            "بدون كوكيز حساب مسجّل دخول.\n"
            "راجع قسم إضافة الكوكيز بالـ README لتفعيل هذي الميزة."
        )

    unsupported_signals = ["unsupported url", "no extractor", "is not a valid url"]
    if any(sig in msg for sig in unsupported_signals):
        return "❌ هذا الرابط أو الموقع غير مدعوم حاليًا من أداة التحميل."

    no_video_signals = ["no video could be found", "no video formats found", "no media found"]
    if any(sig in msg for sig in no_video_signals):
        return "❌ ما لقيت أي فيديو بهذا الرابط - تأكد إنه يحتوي على فيديو فعلي."

    geo_signals = ["geo", "not available in your country", "blocked it in your country"]
    if any(sig in msg for sig in geo_signals):
        return "🌍 هذا المحتوى محجوب جغرافيًا وغير متاح من موقع السيرفر."

    unavailable_signals = ["video unavailable", "this content isn't available", "has been removed", "deleted"]
    if any(sig in msg for sig in unavailable_signals):
        return "❌ الفيديو غير متاح - إما محذوف أو خاص أو الرابط غير صحيح."

    # أي خطأ ثاني غير معروف: نعرض جزء مختصر بدل النص التقني الكامل
    return f"❌ تعذّر التحميل لسبب غير معروف. (تفاصيل مختصرة: {raw_error[:150]})"


async def safe_edit(status_msg, text: str):
    """يعدّل رسالة الحالة، ويتجاهل أخطاء FloodWaitError (تيلجرام يحد
    عدد التعديلات المسموحة بفترة قصيرة) بدل ما يفشل العملية كلها."""
    try:
        await status_msg.edit(text)
    except FloodWaitError as e:
        logger.warning(f"FloodWaitError عند تعديل الرسالة - تجاهلناها ({e.seconds}s)")
    except Exception:
        logger.exception("خطأ غير متوقع أثناء تعديل الرسالة")


@client.on(events.NewMessage(outgoing=True, chats="me"))
async def handle_message(event):
    """يستمع فقط لرسائلك أنت في محادثة Saved Messages.
    يدعم أكثر من رابط بنفس الرسالة - يعالجهم واحدًا تلو الآخر.
    يدعم تحديد جودة اختيارية (رقم بعد الرابط، مثل 720 أو 1080)."""
    text = event.raw_text or ""
    urls = URL_REGEX.findall(text)
    if not urls:
        return

    quality_match = QUALITY_REGEX.search(text)
    quality = int(quality_match.group(1)) if quality_match else None

    if len(urls) > 1:
        await event.respond(f"📋 لقيت {len(urls)} روابط، رح أعالجهم بالترتيب...")

    for url in urls:
        await process_single_url(event, url, quality)


async def process_single_url(event, url: str, quality: int | None = None):
    """يحمّل رابط واحد ويرسله، مع تحديث حي لنسبة التقدم بنفس الرسالة.
    quality: أعلى ارتفاع مسموح (مثل 720)، أو None لأعلى جودة متوفرة."""
    quality_label = f" (جودة {quality}p)" if quality else ""
    status = await event.respond(f"⏳ جاري التحميل...{quality_label} 0%\n{url}")

    tmp_dir = tempfile.mkdtemp(prefix="ytdlp_")
    output_template = os.path.join(tmp_dir, "%(title).80s.%(ext)s")

    loop = asyncio.get_event_loop()
    progress_state = {"last_percent": -100, "last_edit_time": 0.0}

    def progress_hook(d):
        """يشتغل داخل ثريد التحميل (مو asyncio) - نستخدم
        run_coroutine_threadsafe عشان نعدّل الرسالة بأمان من هناك."""
        try:
            if d.get("status") == "downloading":
                percent_str = (d.get("_percent_str") or "").strip().replace("%", "")
                percent = float(percent_str) if percent_str else None
                if percent is None:
                    return

                now = time.monotonic()
                # تحديث كل 25% تقدّم أو كل 15 ثانية كحد أدنى - متحفظين
                # جدًا لتجنب أي احتكاك مع حد تيلجرام لتعديل الرسائل
                if (percent - progress_state["last_percent"] >= 25
                        or now - progress_state["last_edit_time"] >= 15):
                    progress_state["last_percent"] = percent
                    progress_state["last_edit_time"] = now
                    new_text = f"⏳ جاري التحميل... {percent:.0f}%\n{url}"
                    asyncio.run_coroutine_threadsafe(
                        safe_edit(status, new_text), loop
                    )
            elif d.get("status") == "finished":
                asyncio.run_coroutine_threadsafe(
                    safe_edit(status, f"✅ التحميل 100% - جاري التجهيز...\n{url}"),
                    loop,
                )
        except Exception:
            logger.exception("خطأ داخل progress_hook")

    if quality:
        # نحدد سقف ارتفاع الفيديو (height) حسب الجودة المطلوبة، مع نفس
        # ترتيب الأفضلية (MP4 مباشر > أي شي مباشر > MP4 مجزأ > أي شي)
        fmt = (
            f"best[height<={quality}][protocol!*=m3u8][ext=mp4]/"
            f"best[height<={quality}][protocol!*=m3u8]/"
            f"best[height<={quality}][ext=mp4]/"
            f"best[height<={quality}]/"
            f"best[protocol!*=m3u8][ext=mp4]/best[protocol!*=m3u8]/best[ext=mp4]/best"
        )
    else:
        # بدون تحديد جودة: أعلى جودة متوفرة بالموقع مباشرة
        fmt = "best[protocol!*=m3u8][ext=mp4]/best[protocol!*=m3u8]/best[ext=mp4]/best"

    ydl_opts = {
        "outtmpl": output_template,
        "format": fmt,
        "noplaylist": True,
        "quiet": True,
        "no_warnings": True,
        "max_filesize": MAX_FILE_SIZE,
        # تحميل عدة أجزاء بالتوازي بدل التسلسل - يسرّع الفيديوهات
        # المجزأة (HLS) بشكل كبير جدًا لأنها عملية شبكة وليست معالجة.
        "concurrent_fragment_downloads": 8,
        "progress_hooks": [progress_hook],
    }

    # لو فيه كوكيز مضبوطة، نمررها لـ yt-dlp عشان يقدر يحمّل محتوى
    # يتطلب تسجيل دخول (حسابات خاصة، محتوى مقيّد بعمر، إلخ)
    if COOKIES_FILE_PATH:
        ydl_opts["cookiefile"] = COOKIES_FILE_PATH

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = await asyncio.to_thread(ydl.extract_info, url, download=True)
            filename = ydl.prepare_filename(info)
            if not os.path.exists(filename):
                base, _ = os.path.splitext(filename)
                filename = base + ".mp4"

        if not os.path.exists(filename):
            raise FileNotFoundError("تعذر إيجاد الملف بعد التحميل")

        file_size = os.path.getsize(filename)
        if file_size > MAX_FILE_SIZE:
            await safe_edit(
                status,
                f"⚠️ الملف أكبر من {MAX_FILE_SIZE // (1024*1024)} ميجا، تعذر إرساله.\n{url}"
            )
            return

        await safe_edit(status, f"📤 جاري الإرسال... 0%\n{url}")

        duration, width, height, thumb_path = get_video_metadata(filename)
        attributes = None
        if duration or width or height:
            attributes = [
                DocumentAttributeVideo(
                    duration=duration,
                    w=width or 640,
                    h=height or 360,
                    supports_streaming=True,
                )
            ]

        upload_state = {"last_percent": -100, "last_edit_time": 0.0}

        def upload_progress(current: int, total: int):
            """يشتغل داخل asyncio (Telethon يستدعيها مباشرة أثناء الرفع)،
            نجدول تعديل الرسالة بدون ما نوقف الرفع نفسه."""
            try:
                if total <= 0:
                    return
                percent = current / total * 100
                now = time.monotonic()
                if (percent - upload_state["last_percent"] >= 25
                        or now - upload_state["last_edit_time"] >= 15
                        or percent >= 100):
                    upload_state["last_percent"] = percent
                    upload_state["last_edit_time"] = now
                    asyncio.ensure_future(
                        safe_edit(status, f"📤 جاري الإرسال... {percent:.0f}%\n{url}")
                    )
            except Exception:
                logger.exception("خطأ داخل upload_progress")

        await client.send_file(
            "me",
            filename,
            caption=info.get("title", ""),
            supports_streaming=True,
            attributes=attributes,
            thumb=thumb_path,
            progress_callback=upload_progress,
        )
        try:
            await status.delete()
        except FloodWaitError:
            pass

    except yt_dlp.utils.DownloadError as e:
        await safe_edit(status, f"{friendly_error_message(str(e))}\n{url}")
    except Exception as e:
        logger.exception("خطأ غير متوقع")
        await safe_edit(status, f"❌ حدث خطأ غير متوقع: {str(e)[:150]}\n{url}")
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)


async def health_check(request):
    """صفحة بسيطة فقط عشان Render يعتبر الخدمة شغّالة"""
    return web.Response(text="Bot is running")


async def start_health_server():
    app = web.Application()
    app.router.add_get("/", health_check)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", PORT)
    await site.start()
    logger.info(f"خادم الفحص الصحي يعمل على المنفذ {PORT}")


async def main():
    if not API_ID or not API_HASH or not SESSION_STRING:
        raise SystemExit(
            "لازم تضبط متغيرات البيئة: API_ID, API_HASH, SESSION_STRING"
        )

    await start_health_server()
    await client.start()
    logger.info("البوت (Telethon) يعمل الآن... أرسل رابطًا في Saved Messages")
    await client.run_until_disconnected()


if __name__ == "__main__":
    asyncio.run(main())
