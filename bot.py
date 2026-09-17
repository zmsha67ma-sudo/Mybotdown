"""
بوت تيلجرام لتحميل الفيديوهات من روابط خارجية (X/تويتر ومواقع أخرى كثيرة)
يستخدم yt-dlp للتحميل بأعلى جودة متاحة.

هذا الإصدار يعمل بوضع WEBHOOK (وليس polling) عشان يتوافق مع خطة
Render.com المجانية (Web Service)، التي لا تتطلب بطاقة بنكية.

متغيرات البيئة المطلوبة عند التشغيل على Render:
- BOT_TOKEN: توكن البوت من BotFather
- RENDER_EXTERNAL_URL: يوفرها Render تلقائيًا (رابط الخدمة العام)
- PORT: يوفرها Render تلقائيًا
"""

import logging
import os
import re
import tempfile
import shutil

from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters
import yt_dlp

# ---------------------------------------------------------------------------
# الإعدادات
# ---------------------------------------------------------------------------

BOT_TOKEN = os.environ.get("BOT_TOKEN", "ضع_التوكن_هنا")

# الحد الأقصى لحجم الملف الذي يمكن للبوت إرساله (بالبايت).
# البوت العادي (Bot API الرسمي) محدود بـ 50 ميجا للرفع من البوت للمستخدم.
# إذا شغّلت Local Bot API Server ارفع هذا الرقم إلى 2000 * 1024 * 1024 (2 جيجا).
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50 MB

URL_REGEX = re.compile(r"https?://\S+")

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# أوامر البوت
# ---------------------------------------------------------------------------

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "أهلاً 👋\n\n"
        "أرسل لي رابط فيديو من X (تويتر) أو أي موقع مدعوم، وسأحمّله لك بأعلى جودة ممكنة.\n\n"
        "ملاحظة: الحد الأقصى لحجم الملف حاليًا هو "
        f"{MAX_FILE_SIZE // (1024 * 1024)} ميجابايت بسبب قيود تيلجرام."
    )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text or ""
    match = URL_REGEX.search(text)

    if not match:
        await update.message.reply_text("أرسل رابطًا صحيحًا يبدأ بـ http:// أو https://")
        return

    url = match.group(0)
    status_msg = await update.message.reply_text("⏳ جاري التحميل...")

    tmp_dir = tempfile.mkdtemp(prefix="ytdlp_")
    output_template = os.path.join(tmp_dir, "%(title).80s.%(ext)s")

    ydl_opts = {
        "outtmpl": output_template,
        "format": "bestvideo+bestaudio/best",
        "merge_output_format": "mp4",
        "noplaylist": True,
        "quiet": True,
        "no_warnings": True,
        "max_filesize": MAX_FILE_SIZE,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            # بعد الدمج قد يتغير الامتداد إلى mp4
            if not os.path.exists(filename):
                base, _ = os.path.splitext(filename)
                filename = base + ".mp4"

        if not os.path.exists(filename):
            raise FileNotFoundError("تعذر إيجاد الملف بعد التحميل")

        file_size = os.path.getsize(filename)
        if file_size > MAX_FILE_SIZE:
            await status_msg.edit_text(
                "⚠️ الملف أكبر من الحد المسموح به حاليًا "
                f"({MAX_FILE_SIZE // (1024 * 1024)} ميجا). "
                "يحتاج هذا تشغيل Local Bot API Server لرفع الحد إلى 2 جيجا."
            )
            return

        await status_msg.edit_text("📤 جاري الإرسال...")
        with open(filename, "rb") as f:
            await update.message.reply_video(
                video=f,
                caption=info.get("title", ""),
                supports_streaming=True,
            )
        await status_msg.delete()

    except yt_dlp.utils.DownloadError as e:
        await status_msg.edit_text(f"❌ فشل التحميل: {str(e)[:300]}")
    except Exception as e:
        logger.exception("خطأ غير متوقع")
        await status_msg.edit_text(f"❌ حدث خطأ: {str(e)[:300]}")
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)


def main():
    if BOT_TOKEN == "ضع_التوكن_هنا":
        raise SystemExit(
            "الرجاء ضبط متغير البيئة BOT_TOKEN أو تعديل القيمة مباشرة في bot.py"
        )

    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # وضع Webhook (مطلوب على Render Free Web Service)
    external_url = os.environ.get("RENDER_EXTERNAL_URL")
    port = int(os.environ.get("PORT", "10000"))

    if external_url:
        # على Render: نشغّل خادم ويب يستقبل تحديثات تيلجرام مباشرة
        webhook_path = BOT_TOKEN  # نستخدم التوكن كمسار سري لمنع أي أحد غيرنا من الإرسال
        webhook_url = f"{external_url}/{webhook_path}"
        logger.info(f"تشغيل Webhook على {webhook_url}")
        app.run_webhook(
            listen="0.0.0.0",
            port=port,
            url_path=webhook_path,
            webhook_url=webhook_url,
        )
    else:
        # للتشغيل المحلي على جهازك أثناء التجربة فقط
        logger.info("تشغيل البوت بوضع polling (محلي)...")
        app.run_polling()


if __name__ == "__main__":
    main()
