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
- لإلغاء أي تحميل جارٍ، أرسل كلمة: الغاء (أو إلغاء أو cancel)
- لمسح أي ملفات مؤقتة متراكمة من عمليات سابقة، أرسل: تنظيف (أو مسح الكاش)
- لإعادة تشغيل السيرفر بالكامل، أرسل: اعادة تشغيل (أو restart)
- لعرض حالة السيرفر (تحميلات شغّالة، ذاكرة، مساحة قرص)، أرسل: حالة (أو status)
- لعرض إحصائيات الاستخدام الكلي (حجم التحميلات منذ آخر تشغيل)، أرسل: احصائيات (أو stats)
- لعرض قائمة كل الأوامر المتاحة، أرسل: مساعدة (أو help)

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
import logging
import os
import re
import shutil
import subprocess
import tempfile
import threading
import time
from datetime import datetime

try:
    import resource  # متوفر فقط على أنظمة Linux/Unix (نفس بيئة Render)
except ImportError:
    resource = None

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

# قائمة العمليات الجارية حاليًا (تحميل/إرسال) - كل عملية عندها
# threading.Event خاص فيها، لو انضبط (set) نوقف التحميل من داخل
# progress_hook مباشرة. بما إن الاستخدام شخصي (حساب واحد بس)، قائمة
# بسيطة كافية بدون تعقيد إضافي.
active_operations = []
CANCELLED_MARKER = "USER_CANCELLED_OPERATION"

# إحصائيات بسيطة تُحفظ بالذاكرة فقط (تصفر عند أي إعادة تشغيل) - تساعدك
# تتابع استهلاكك من حصة الباندويدث الشهرية عند Render (100 جيجا مجانًا)
BOT_START_TIME = datetime.now()
stats = {"completed_downloads": 0, "total_bytes_sent": 0, "failed_downloads": 0}


def generate_thumbnail(filepath: str):
    """يولّد صورة مصغّرة (thumbnail) عبر ffmpeg فقط - أخف بكثير من قبل
    لأننا صرنا نجيب المدة والأبعاد من yt-dlp نفسه بدل استدعاء ffprobe
    كعملية منفصلة (توفير كامل لعملية subprocess زايدة).
    كمان نضع -ss قبل -i (البحث من طرف الإدخال) بدل بعده: هذا يخلي ffmpeg
    يقفز مباشرة لأقرب "keyframe" بدون فك تشفير كل الثواني اللي قبلها،
    فايدة كبيرة بالسرعة والمعالج خصوصًا بالفيديوهات الطويلة، وبدون أي
    تأثير على جودة الفيديو الأصلي (الصورة المصغّرة فقط للمعاينة)."""
    thumb_path = filepath + "_thumb.jpg"
    try:
        subprocess.run(
            [
                "ffmpeg", "-y",
                "-ss", "1",           # بحث سريع قبل فتح الملف
                "-i", filepath,
                "-frames:v", "1",
                "-vf", "scale=320:-1",
                "-q:v", "5",
                thumb_path,
            ],
            capture_output=True, timeout=15,
        )
        if not os.path.exists(thumb_path):
            return None
        return thumb_path
    except Exception:
        logger.exception("تعذر توليد صورة مصغّرة عبر ffmpeg")
        return None


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


@client.on(events.NewMessage(outgoing=True, chats="me", pattern=r"(?i)^(الغاء|إلغاء|cancel|stop)$"))
async def handle_cancel(event):
    """يلغي كل التحميلات الجارية حاليًا (لو فيه أكثر من رابط قيد
    المعالجة). يشتغل بس لو الرسالة عبارة عن كلمة إلغاء فقط، عشان ما
    يتعارض مع رسائل عادية فيها كلمة "الغاء" ضمن سياق ثاني."""
    if not active_operations:
        await event.respond("ℹ️ ما فيه أي تحميل جارٍ حاليًا لإلغائه.")
        return

    count = len(active_operations)
    for op in list(active_operations):
        op["cancel_event"].set()

    await event.respond(f"🛑 يتم إلغاء {count} عملية جارية...")


def _clear_leftover_temp_dirs(protected_dirs):
    """يمسح أي مجلدات تحميل مؤقتة (ytdlp_*) متبقية من عمليات قديمة
    (توقفت فجأة قبل ما توصل لخطوة التنظيف الطبيعية، مثل انقطاع مفاجئ
    أو تعطل السيرفر)، بدون ما يلمس أي عملية شغّالة حاليًا."""
    base = tempfile.gettempdir()
    freed_bytes = 0
    removed_count = 0
    try:
        for name in os.listdir(base):
            if not name.startswith("ytdlp_"):
                continue
            full_path = os.path.join(base, name)
            if full_path in protected_dirs:
                continue
            try:
                size = 0
                for dirpath, _, filenames in os.walk(full_path):
                    for f in filenames:
                        fp = os.path.join(dirpath, f)
                        if os.path.exists(fp):
                            size += os.path.getsize(fp)
                shutil.rmtree(full_path, ignore_errors=True)
                freed_bytes += size
                removed_count += 1
            except Exception:
                logger.exception(f"تعذر حذف المجلد المؤقت: {full_path}")
    except Exception:
        logger.exception("تعذر مسح الملفات المؤقتة")
    return removed_count, freed_bytes


@client.on(events.NewMessage(outgoing=True, chats="me", pattern=r"(?i)^(تنظيف|مسح الكاش|clean|clear cache)$"))
async def handle_clean_cache(event):
    """يمسح أي ملفات تحميل مؤقتة متبقية من عمليات سابقة توقفت بشكل
    غير طبيعي (تعطل، انقطاع اتصال، إلخ)، دون التأثير على أي تحميل
    شغّال حاليًا."""
    status = await event.respond("🧹 جاري تنظيف الملفات المؤقتة...")
    protected = {op["tmp_dir"] for op in active_operations}
    removed_count, freed_bytes = await asyncio.to_thread(
        _clear_leftover_temp_dirs, protected
    )
    freed_mb = freed_bytes / (1024 * 1024)
    if removed_count:
        await safe_edit(
            status,
            f"✅ تم حذف {removed_count} مجلد مؤقت متبقٍّ، وتحرير {freed_mb:.1f} ميجا."
        )
    else:
        await safe_edit(status, "✅ ما فيه أي ملفات مؤقتة متراكمة - كل شي نظيف.")


@client.on(events.NewMessage(outgoing=True, chats="me", pattern=r"(?i)^(اعادة تشغيل|إعادة تشغيل|restart)$"))
async def handle_restart(event):
    """يعيد تشغيل السيرفر بالكامل. يوقف العملية الحالية عمدًا، وبما إن
    Render يراقب الخدمة ويعيد تشغيلها تلقائيًا عند توقفها (نفس سلوكه
    مع أي تعطل)، هذا يعادل "إعادة تشغيل" حقيقية بدون حاجة للدخول للوحة
    تحكم Render يدويًا."""
    if active_operations:
        await event.respond(
            f"⚠️ فيه {len(active_operations)} عملية تحميل شغّالة حاليًا. "
            "أرسل \"الغاء\" أول لو تبي توقفها، أو أرسل \"تأكيد إعادة التشغيل\" "
            "للمتابعة رغم ذلك."
        )
        return

    await event.respond("🔄 جاري إعادة تشغيل السيرفر... البوت بيرجع يشتغل خلال دقيقة تقريبًا.")
    await asyncio.sleep(1.5)  # نضمن وصول الرسالة قبل إيقاف العملية
    logger.info("إعادة تشغيل مطلوبة يدويًا - إيقاف العملية الآن")
    os._exit(0)


@client.on(events.NewMessage(outgoing=True, chats="me", pattern=r"(?i)^تأكيد إعادة التشغيل$"))
async def handle_force_restart(event):
    """تأكيد إعادة التشغيل رغم وجود تحميلات شغّالة - تُفقد هذي
    التحميلات الجارية بدون استكمال."""
    await event.respond("🔄 جاري إعادة التشغيل رغم العمليات الجارية...")
    await asyncio.sleep(1.5)
    os._exit(0)


@client.on(events.NewMessage(outgoing=True, chats="me", pattern=r"(?i)^(حالة|status)$"))
async def handle_status(event):
    """يعرض حالة السيرفر الحالية: تحميلات شغّالة، مساحة القرص
    المتبقية، واستهلاك الذاكرة التقريبي - يفيد لتشخيص أي بطء غير
    طبيعي (مثلاً امتلاء القرص أو تراكم ذاكرة)."""
    lines = ["📊 **حالة السيرفر**\n"]

    if active_operations:
        lines.append(f"⏳ تحميلات شغّالة الآن: {len(active_operations)}")
        for op in active_operations:
            lines.append(f"  • {op['url'][:60]}")
    else:
        lines.append("⏳ ما فيه أي تحميل شغّال حاليًا")

    try:
        disk = shutil.disk_usage(tempfile.gettempdir())
        free_mb = disk.free / (1024 * 1024)
        total_mb = disk.total / (1024 * 1024)
        lines.append(f"\n💾 مساحة القرص المتاحة: {free_mb:.0f} / {total_mb:.0f} ميجا")
    except Exception:
        lines.append("\n💾 تعذر قراءة معلومات القرص")

    if resource:
        try:
            mem_kb = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
            lines.append(f"🧠 أعلى استهلاك ذاكرة: {mem_kb / 1024:.0f} ميجا")
        except Exception:
            pass

    uptime = datetime.now() - BOT_START_TIME
    hours = int(uptime.total_seconds() // 3600)
    minutes = int((uptime.total_seconds() % 3600) // 60)
    lines.append(f"⏱️ يعمل منذ آخر تشغيل: {hours} ساعة و{minutes} دقيقة")

    await event.respond("\n".join(lines))


@client.on(events.NewMessage(outgoing=True, chats="me", pattern=r"(?i)^(احصائيات|إحصائيات|stats)$"))
async def handle_stats(event):
    """يعرض إحصائيات الاستخدام الكلي منذ آخر إعادة تشغيل - يساعدك
    تتابع استهلاكك من حصة Render الشهرية (100 جيجا باندويدث مجانًا)."""
    sent_gb = stats["total_bytes_sent"] / (1024 ** 3)
    percent_of_limit = (sent_gb / 100) * 100  # من أصل 100 جيجا الحصة الشهرية

    text = (
        "📈 **إحصائيات الاستخدام** (منذ آخر إعادة تشغيل)\n\n"
        f"✅ تحميلات ناجحة: {stats['completed_downloads']}\n"
        f"❌ تحميلات فاشلة: {stats['failed_downloads']}\n"
        f"📦 إجمالي حجم البيانات المرسلة: {sent_gb:.2f} جيجا\n\n"
        f"⚠️ هذا يعادل تقريبًا {percent_of_limit:.1f}% من حصة الباندويدث "
        "الشهرية المجانية عند Render (100 جيجا).\n\n"
        "ملاحظة: هذي الأرقام تصفر تلقائيًا عند أي إعادة تشغيل للسيرفر "
        "(يدوي أو تلقائي من Render)، فهي تقريبية وليست دقيقة 100% لكامل الشهر."
    )
    await event.respond(text)


@client.on(events.NewMessage(outgoing=True, chats="me", pattern=r"(?i)^(مساعدة|help)$"))
async def handle_help(event):
    """يعرض قائمة كل الأوامر المتاحة بالبوت."""
    text = (
        "🤖 **قائمة أوامر البوت**\n\n"
        "📥 أرسل أي رابط فيديو → يحمّله ويرسله لك تلقائيًا\n"
        "🎚️ أضف رقم جودة بعد الرابط (مثل: 720) → يحمّل بتلك الجودة\n\n"
        "**أوامر التحكم:**\n"
        "• `الغاء` - يوقف أي تحميل شغّال حاليًا\n"
        "• `تنظيف` - يمسح الملفات المؤقتة المتراكمة\n"
        "• `اعادة تشغيل` - يعيد تشغيل السيرفر بالكامل\n"
        "• `حالة` - يعرض حالة السيرفر الحالية (تحميلات، قرص، ذاكرة)\n"
        "• `احصائيات` - يعرض إجمالي الاستخدام منذ آخر تشغيل\n"
        "• `مساعدة` - يعرض هذي القائمة"
    )
    await event.respond(text)


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
    status = await event.respond(
        f"⏳ جاري التحميل...{quality_label} 0%\n{url}\n\n"
        "(أرسل \"الغاء\" لإيقاف هذا التحميل)"
    )

    tmp_dir = tempfile.mkdtemp(prefix="ytdlp_")
    output_template = os.path.join(tmp_dir, "%(title).80s.%(ext)s")

    loop = asyncio.get_event_loop()
    progress_state = {"last_percent": -100, "last_edit_time": 0.0}
    cancel_event = threading.Event()
    operation = {"cancel_event": cancel_event, "url": url, "tmp_dir": tmp_dir}
    active_operations.append(operation)

    def progress_hook(d):
        """يشتغل داخل ثريد التحميل (مو asyncio) - نستخدم
        run_coroutine_threadsafe عشان نعدّل الرسالة بأمان من هناك."""
        try:
            # لو المستخدم طلب الإلغاء، نوقف التحميل فورًا من هنا - رفع
            # استثناء داخل progress_hook يخلي yt-dlp يوقف العملية مباشرة
            # بدل ما ينتظر اكتمال التحميل ثم نتجاهل النتيجة.
            if cancel_event.is_set():
                raise RuntimeError(CANCELLED_MARKER)

            if d.get("status") == "downloading":
                percent_str = (d.get("_percent_str") or "").strip().replace("%", "")
                percent = float(percent_str) if percent_str else None
                if percent is None:
                    return

                now = time.monotonic()
                # تحديث فقط لو مرّت 5 ثوانٍ على الأقل من آخر تحديث -
                # نعتمد على الوقت فقط (مو النسبة) عشان ما تصير دفعة
                # تحديثات متلاحقة بالفيديوهات السريعة (تصطدم بحد تيلجرام
                # وتخلي الرسائل المهمة، زي "اكتمل 100%"، تضيع بصمت).
                if now - progress_state["last_edit_time"] >= 5:
                    progress_state["last_percent"] = percent
                    progress_state["last_edit_time"] = now
                    new_text = (
                        f"⏳ جاري التحميل... {percent:.0f}%\n{url}\n\n"
                        "(أرسل \"الغاء\" لإيقاف هذا التحميل)"
                    )
                    asyncio.run_coroutine_threadsafe(
                        safe_edit(status, new_text), loop
                    )
            elif d.get("status") == "finished":
                asyncio.run_coroutine_threadsafe(
                    safe_edit(status, f"✅ التحميل 100% - جاري التجهيز...\n{url}"),
                    loop,
                )
        except RuntimeError:
            raise
        except Exception:
            logger.exception("خطأ داخل progress_hook")

    if quality:
        # لما تحدد جودة بنفسك (مثل 720)، نحترم السقف اللي طلبته بالضبط،
        # ونفضّل صيغة MP4 مباشرة (أسرع) بس فقط لو نفس الجودة المطلوبة
        # متوفرة بها - ما تحدث فرق جودة لأنك أصلاً حددت سقف معين.
        fmt = (
            f"best[height<={quality}][protocol!*=m3u8][ext=mp4]/"
            f"best[height<={quality}][protocol!*=m3u8]/"
            f"best[height<={quality}][ext=mp4]/"
            f"best[height<={quality}]"
        )
    else:
        # بدون تحديد جودة: نطلب أعلى جودة موجودة بالموقع دايمًا،
        # بغض النظر عن كونها MP4 مباشر أو مجزأة (HLS) - الأولوية
        # المطلقة للجودة، والتحميل المتوازي (concurrent_fragment_
        # downloads) أصلاً يعوّض بطء HLS المحتمل بدون التضحية بالجودة.
        fmt = "best"

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

        # المدة والأبعاد نجيبها مباشرة من بيانات yt-dlp نفسه (كان أصلاً
        # يجلبها من الموقع)، بدون أي استدعاء إضافي لـ ffprobe - توفير
        # كامل لعملية subprocess زايدة كانت تستهلك معالج بلا داعي.
        duration = int(info.get("duration") or 0)
        width = int(info.get("width") or 0)
        height = int(info.get("height") or 0)
        thumb_path = await asyncio.to_thread(generate_thumbnail, filename)
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
                if cancel_event.is_set():
                    raise RuntimeError(CANCELLED_MARKER)
                if total <= 0:
                    return
                percent = current / total * 100
                now = time.monotonic()
                # نفس منطق الوقت فقط (مو النسبة) لتفادي دفعات التحديث
                # السريعة بالملفات الصغيرة اللي ترفع خلال ثوانٍ قليلة
                is_done = percent >= 100
                if now - upload_state["last_edit_time"] >= 5 or is_done:
                    upload_state["last_percent"] = percent
                    upload_state["last_edit_time"] = now
                    asyncio.ensure_future(
                        safe_edit(status, f"📤 جاري الإرسال... {percent:.0f}%\n{url}")
                    )
            except RuntimeError:
                raise
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
        stats["completed_downloads"] += 1
        stats["total_bytes_sent"] += file_size
        try:
            await status.delete()
        except FloodWaitError:
            pass

    except RuntimeError as e:
        if str(e) == CANCELLED_MARKER:
            await safe_edit(status, f"🛑 تم إلغاء العملية بنجاح.\n{url}")
        else:
            stats["failed_downloads"] += 1
            logger.exception("خطأ غير متوقع")
            await safe_edit(status, f"❌ حدث خطأ غير متوقع: {str(e)[:150]}\n{url}")
    except yt_dlp.utils.DownloadError as e:
        if CANCELLED_MARKER in str(e):
            await safe_edit(status, f"🛑 تم إلغاء العملية بنجاح.\n{url}")
        else:
            stats["failed_downloads"] += 1
            await safe_edit(status, f"{friendly_error_message(str(e))}\n{url}")
    except Exception as e:
        stats["failed_downloads"] += 1
        logger.exception("خطأ غير متوقع")
        await safe_edit(status, f"❌ حدث خطأ غير متوقع: {str(e)[:150]}\n{url}")
    finally:
        if operation in active_operations:
            active_operations.remove(operation)
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
