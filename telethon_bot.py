"""
بوت تحميل فيديوهات يعمل بحسابك الشخصي على تيلجرام عبر Telethon.
يدعم إرسال ملفات لغاية 2 جيجا (بدل حد الـ 50 ميجا لبوتات Bot API العادية).

طريقة الاستخدام بعد التشغيل:
- افتح محادثة "Saved Messages" (رسائلي المحفوظة) في تيلجرام.
- أرسل رابط فيديو من X أو أي موقع مدعوم.
- البوت يحمّله ويرسله لك بأعلى جودة ممكنة ضمن حد 2 جيجا.

متغيرات البيئة المطلوبة:
- API_ID, API_HASH: من https://my.telegram.org
- SESSION_STRING: تحصل عليه من تشغيل generate_session.py على جهازك أولاً
- PORT: يوفره Render تلقائيًا (لخادم فحص الصحة فقط)
"""

import asyncio
import logging
import os
import re
import shutil
import tempfile

from aiohttp import web
from telethon import TelegramClient, events
from telethon.sessions import StringSession
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

MAX_FILE_SIZE = 2000 * 1024 * 1024  # 2 جيجا
URL_REGEX = re.compile(r"https?://\S+")

client = TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH)


@client.on(events.NewMessage(outgoing=True, chats="me"))
async def handle_message(event):
    """يستمع فقط لرسائلك أنت في محادثة Saved Messages"""
    text = event.raw_text or ""
    match = URL_REGEX.search(text)
    if not match:
        return

    url = match.group(0)
    status = await event.respond("⏳ جاري التحميل...")

    tmp_dir = tempfile.mkdtemp(prefix="ytdlp_")
    output_template = os.path.join(tmp_dir, "%(title).80s.%(ext)s")

    ydl_opts = {
        "outtmpl": output_template,
        # نفضّل صيغة MP4 مباشرة (غير مجزّأة) لو متوفرة - أسرع بكثير لأنها
        # ملف واحد جاهز بدون قطع. لو غير متوفرة (أغلب فيديوهات X الطويلة)
        # نرجع لأفضل جودة حتى لو كانت مجزأة (HLS).
        "format": "best[protocol!*=m3u8][ext=mp4]/best[protocol!*=m3u8]/best[ext=mp4]/best",
        "noplaylist": True,
        "quiet": True,
        "no_warnings": True,
        "max_filesize": MAX_FILE_SIZE,
        # تحميل عدة أجزاء بالتوازي بدل التسلسل - يسرّع الفيديوهات
        # المجزأة (HLS) بشكل كبير جدًا لأنها عملية شبكة وليست معالجة.
        "concurrent_fragment_downloads": 8,
    }

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
            await status.edit(
                f"⚠️ الملف أكبر من {MAX_FILE_SIZE // (1024*1024)} ميجا، تعذر إرساله."
            )
            return

        await status.edit("📤 جاري الإرسال...")
        await client.send_file(
            "me",
            filename,
            caption=info.get("title", ""),
            supports_streaming=True,
        )
        await status.delete()

    except yt_dlp.utils.DownloadError as e:
        await status.edit(f"❌ فشل التحميل: {str(e)[:300]}")
    except Exception as e:
        logger.exception("خطأ غير متوقع")
        await status.edit(f"❌ حدث خطأ: {str(e)[:300]}")
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
