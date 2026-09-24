"""
بوت تحميل فيديوهات يعمل بحسابك الشخصي على تيلجرام عبر Telethon.
يدعم إرسال ملفات لغاية 2 جيجا (بدل حد الـ 50 ميجا لبوتات Bot API العادية).

طريقة الاستخدام بعد التشغيل:
- افتح محادثة "Saved Messages" (رسائلي المحفوظة) في تيلجرام.
- أرسل رابط فيديو من X أو أي موقع مدعوم.
- البوت يحمّله ويرسله لك بأعلى جودة متوفرة بالموقع ضمن حد 2 جيجا.
- لو تبي جودة محددة مسبقًا، أضف الرقم بعد الرابط بنفس الرسالة، مثال:
  https://x.com/xxx/status/123 720
  (الأرقام المدعومة: 240, 360, 480, 720, 1080, 1440, 2160)
  بهالحالة يبدأ التحميل فورًا بدون أي سؤال.
- لو ما حددت رقم، البوت يجيب أولاً قائمة الجودات المتوفرة فعليًا (مع حجم
  كل جودة، ومعها خيارات 🎵 MP3 و🎞️ GIF بحجمها التقديري)
  لهذا الفيديو تحديدًا (استعلام خفيف جدًا، بدون تحميل أي بايت من
  الفيديو نفسه) ويسألك تختار بالرد برقم الخيار خلال 60 ثانية. لو ما
  رديت بالوقت، يكمل تلقائيًا بأعلى جودة.
- لتحويل فيديو قصير إلى GIF، أضف كلمة gif (أو جيف) بعد الرابط، مثال:
  https://x.com/xxx/status/123 gif
  يرسله لك كـ GIF متحرك بتيليجرام (بدون صوت)، بدون سؤال جودة.
  الحد الأقصى لمدة الـ GIF: 30 ثانية (يقصّ الباقي)، وعرض أقصى 480.
- لتحويل فيديوهات جاهزة عندك إلى GIF: أرسل كلمة gif (أو جيف) لحالها
  فيدخل البوت "وضع GIF"، وبعدها أي فيديو ترسله (أو رابط) يتحول لـ GIF.
  للخروج والرجوع للوضع العادي أرسل: الغاء gif
  (الوضع ينتهي تلقائيًا بعد فترة خمول - GIF_MODE_TIMEOUT_MIN، الافتراضي 15).
  خارج هذا الوضع، الفيديو المرسل ما يتحول إلا لو كتبت gif بوصفه (caption).
- لقص جزء محدد كـ GIF: أضف المدى بعد كلمة gif، مثال: رابط gif 10-20
  (من الثانية 10 إلى 20) أو gif 1:30-1:45. تنفع كذلك بوصف الفيديو المرفوع.
  ملاحظة: يحمّل الفيديو كاملًا (بجودة منخفضة) ثم يقص المقطع.
- لتحميل الصوت فقط: أضف كلمة mp3 (أو صوت) بعد الرابط → يرسله ملف MP3.
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

متغير بيئة اختياري ثاني (للتعامل مع البوت من أرقامك الأخرى):
- GROUP_CHAT_ID: معرّف مجموعة خاصة (رقم صحيح مثل -1001234567890) تضم
  حسابك اللي شغّل عليه البوت + أرقامك الثانية. لو مضبوط، أي رابط يوصل
  بهذي المجموعة من أي رقم فيها يُعامل بنفس طريقة Saved Messages تمامًا
  (تحميل، قائمة جودة، أوامر تحكم). استخدم get_group_id.py لإيجاد
  الرقم الصحيح بعد ما تسوي المجموعة وتضيف لها الأرقام.

متغيرات بيئة اختيارية إضافية:
- ALLOWED_USER_IDS: أرقام (user id) مفصولة بفواصل، هي فقط اللي يقدر
  يشغّل البوت من المجموعة الخاصة (get_group_id.py يعرض لك أرقام الأعضاء).
  لو ما ضبطته، أي عضو بالمجموعة يقدر يشغّل البوت.
- MAX_CONCURRENT_JOBS: أقصى عدد عمليات (تحميل/تحويل) بنفس الوقت؛ الباقي
  ينتظر بالطابور (الافتراضي 2).
- MAX_FILE_MB: يفرض حد حجم الملف يدويًا. لو ما ضبطته، البوت يكتشف حسابك
  تلقائيًا: 2000 ميجا للحساب العادي و4000 ميجا لو Telegram Premium.
- GIF_MODE_TIMEOUT_MIN / GIF_MAX_SECONDS / GIF_MAX_INPUT_MB: إعدادات GIF.
"""

import asyncio
import base64
import collections
import glob
import logging
import os
import re
import shutil
import subprocess
import tempfile
import threading
import time
import urllib.parse
from datetime import datetime

try:
    import resource  # متوفر فقط على أنظمة Linux/Unix (نفس بيئة Render)
except ImportError:
    resource = None

from aiohttp import web
from telethon import TelegramClient, events
from telethon.sessions import StringSession
from telethon.tl.types import (
    DocumentAttributeAnimated,
    DocumentAttributeAudio,
    DocumentAttributeVideo,
)
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

# معرّف مجموعة خاصة اختيارية (تضم حسابك اللي شغّل عليه البوت + أرقامك
# الثانية) - لو مضبوط، البوت يتعامل مع أي رابط يوصل بهذي المجموعة من
# أي رقم فيها بنفس طريقة تعامله مع Saved Messages. يُقرأ كرقم صحيح
# (زي -1001234567890)؛ لو ما كان رقم، نتركه نص عادي (يقبل يوزرنيم
# المجموعة العام لو كانت من هذا النوع).
_group_env = os.environ.get("GROUP_CHAT_ID", "").strip()
GROUP_CHAT_ID: "int | str | None" = None
if _group_env:
    try:
        GROUP_CHAT_ID = int(_group_env)
    except ValueError:
        GROUP_CHAT_ID = _group_env

# قائمة المحادثات اللي يستمع لها البوت فعليًا بكل المعالجات أدناه:
# محادثتك مع نفسك (Saved Messages) دايمًا، + المجموعة الخاصة لو انضبطت.
ALLOWED_CHATS = ["me"] + ([GROUP_CHAT_ID] if GROUP_CHAT_ID else [])

# حد حجم الملف: يُضبط تلقائيًا وقت التشغيل حسب حسابك (2 جيجا عادي، 4 جيجا
# لو Telegram Premium) عبر apply_account_limits()، إلا لو فرضته يدويًا
# بمتغير MAX_FILE_MB.
_max_mb_env = os.environ.get("MAX_FILE_MB", "").strip()
MAX_FILE_SIZE_FORCED = False
MAX_FILE_SIZE = 2000 * 1024 * 1024  # 2 جيجا
if _max_mb_env:
    try:
        MAX_FILE_SIZE = int(_max_mb_env) * 1024 * 1024
        MAX_FILE_SIZE_FORCED = True
    except ValueError:
        logging.getLogger(__name__).warning("قيمة MAX_FILE_MB غير صالحة - تم تجاهلها")

# أقصى عدد عمليات ثقيلة (تحميل/تحويل) بنفس الوقت - الباقي ينتظر بالطابور.
# الخطة المجانية بـ Render ذاكرتها ومعالجها محدودين، فتشغيل عدة تحميلات
# مع بعض ممكن يوقف السيرفر.
try:
    MAX_CONCURRENT_JOBS = max(1, int(os.environ.get("MAX_CONCURRENT_JOBS", "2")))
except ValueError:
    MAX_CONCURRENT_JOBS = 2
job_slots = asyncio.Semaphore(MAX_CONCURRENT_JOBS)
queued_jobs = 0

# أرقام المستخدمين المسموح لهم بتشغيل البوت من المجموعة الخاصة (اختياري).
# فاضي = أي عضو بالمجموعة يقدر يشغّل البوت.
ALLOWED_USER_IDS: set = set()
for _part in os.environ.get("ALLOWED_USER_IDS", "").replace(";", ",").split(","):
    _part = _part.strip()
    if not _part:
        continue
    try:
        ALLOWED_USER_IDS.add(int(_part))
    except ValueError:
        logging.getLogger(__name__).warning(f"رقم غير صالح بـ ALLOWED_USER_IDS: {_part}")
URL_REGEX = re.compile(r"https?://\S+")
QUALITY_REGEX = re.compile(r"\b(240|360|480|720|1080|1440|2160)\b")
# كلمة gif / جيف لوحدها (نبحث عنها بالنص بعد إزالة الروابط، عشان ما
# تتطابق مع رابط فيه كلمة gif مثل .../funny.gif)
GIF_REGEX = re.compile(r"(?i)(?<![\w])(gif|جيف)(?![\w])")
# كلمة mp3 / صوت / audio → تحميل الصوت فقط
AUDIO_REGEX = re.compile(r"(?i)(?<![\w])(mp3|audio|صوت)(?![\w])")
# مدى القص: 10-20 أو 1:30-1:45 (نمنع الالتصاق بـ - أو : أو . أو حرف، عشان
# التواريخ مثل 2026-09-24 ما تنحسب كمدى قص بالغلط)
_TIME = r"\d{1,5}(?::\d{1,2}){0,2}"
CLIP_REGEX = re.compile(rf"(?<![\w:.\-]){_TIME}\s*[-–—]\s*{_TIME}(?![\w:.\-])")


class UserFacingError(Exception):
    """خطأ نعرض رسالته للمستخدم كما هي (مو خطأ برمجي غير متوقع)."""


def _to_seconds(token: str) -> int:
    total = 0
    for part in token.split(":"):
        total = total * 60 + int(part)
    return total


def parse_clip_range(text: str):
    """يبحث عن مدى قص (مثل 10-20 أو 1:30-1:45) بالنص.
    يرجّع (clip, النص بدون المدى) حيث clip:
      None      → ما فيه مدى
      "bad"     → مدى غير صالح (النهاية لازم تكون بعد البداية)
      (بداية، نهاية) بالثواني."""
    m = CLIP_REGEX.search(text)
    if not m:
        return None, text
    left, right = re.split(r"\s*[-–—]\s*", m.group(0))
    start, end = _to_seconds(left), _to_seconds(right)
    rest = text[: m.start()] + " " + text[m.end():]
    if end <= start:
        return "bad", rest
    return (start, end), rest


def resolve_gif_window(clip, total_duration):
    """يحسب (بداية، طول) المقطع اللي بنحوله GIF بالثواني، بحد أقصى
    GIF_MAX_SECONDS ومحصور داخل مدة الفيديو الفعلية لو معروفة."""
    start, end = clip if clip else (0, None)
    if total_duration and start >= total_duration:
        raise UserFacingError(
            f"بداية المقطع ({start} ثانية) بعد نهاية الفيديو "
            f"(مدته {int(total_duration)} ثانية)."
        )
    length = GIF_MAX_SECONDS if end is None else min(end - start, GIF_MAX_SECONDS)
    if total_duration:
        length = min(length, total_duration - start)
    return int(start), max(1, int(length))


def fmt_eta(seconds) -> str:
    seconds = int(seconds)
    minutes, sec = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    return f"{hours}:{minutes:02d}:{sec:02d}" if hours else f"{minutes}:{sec:02d}"


def progress_extra(speed, eta) -> str:
    """سطر السرعة والوقت المتبقي (يرجّع نص فاضي لو ما فيه بيانات)."""
    parts = []
    if speed:
        parts.append(f"🚀 {speed / (1024 * 1024):.1f} MB/s")
    if eta is not None:
        parts.append(f"⏱️ باقي {fmt_eta(eta)}")
    return ("\n" + " | ".join(parts)) if parts else ""


def apply_account_limits(me):
    """يضبط حد حجم الملف حسب حسابك: 4 جيجا لو Telegram Premium، وإلا 2
    جيجا (إلا لو فرضت MAX_FILE_MB يدويًا). يرجّع True لو الحساب Premium."""
    global MAX_FILE_SIZE
    is_premium = bool(getattr(me, "premium", False))
    if not MAX_FILE_SIZE_FORCED:
        MAX_FILE_SIZE = (4000 if is_premium else 2000) * 1024 * 1024
    return is_premium


async def acquire_job_slot(status, label: str, cancel_event) -> bool:
    """ينتظر دوره بالطابور لو فيه MAX_CONCURRENT_JOBS عمليات شغّالة.
    يرجّع True لو اضطر ينتظر. يرفع RuntimeError(CANCELLED_MARKER) لو
    أُلغيت العملية وهي بالانتظار. مهم: المستدعي مسؤول عن job_slots.release()."""
    global queued_jobs
    if not job_slots.locked():
        await job_slots.acquire()
        return False

    queued_jobs += 1
    acquire_task = asyncio.ensure_future(job_slots.acquire())
    try:
        await safe_edit(
            status,
            f"🕐 بالطابور... (فيه {queued_jobs} بالانتظار، والحد "
            f"{MAX_CONCURRENT_JOBS} عمليات بنفس الوقت)\n{label}\n\n"
            "(أرسل \"الغاء\" لإلغاء الانتظار)",
        )
        while True:
            done, _ = await asyncio.wait({acquire_task}, timeout=2)
            if done:
                return True
            if cancel_event.is_set():
                acquire_task.cancel()
                try:
                    await acquire_task
                except asyncio.CancelledError:
                    pass
                else:
                    job_slots.release()  # حصلنا المكان لحظة الإلغاء - نرجعه
                raise RuntimeError(CANCELLED_MARKER)
    except asyncio.CancelledError:
        acquire_task.cancel()
        raise
    finally:
        queued_jobs -= 1

# إعدادات تحويل GIF (تيليجرام يعرض الـ GIF كفيديو mp4 صامت قصير - أخف
# وأوضح بكثير من ملف .gif الحقيقي)
GIF_MAX_SECONDS = int(os.environ.get("GIF_MAX_SECONDS", "30"))
GIF_MAX_WIDTH = 480
GIF_MAX_HEIGHT = 480
GIF_FPS = 20
# تقدير تقريبي جدًا لمعدل بايتات الثانية بالـ GIF الناتج (≈0.5 ميجابت/ث لفيديو
# 480 بجودة CRF 26) - يُستخدم فقط لعرض "حجم تقديري" بقائمة الاختيار قبل
# التحويل. الحجم الحقيقي يظهر بوصف الملف بعد الإرسال.
GIF_EST_BYTES_PER_SEC = 60_000
# MP3 بجودة 192kbps ثابتة = 24000 بايت بالثانية
MP3_BYTES_PER_SEC = 24_000
# "وضع GIF": لما ترسل كلمة gif لحالها، يدخل البوت هذا الوضع بنفس المحادثة
# (Saved Messages أو المجموعة، كل محادثة مستقلة)، وأي فيديو أو رابط ترسله
# يتحول إلى GIF لغاية ما ترسل "الغاء gif". ينتهي تلقائيًا بعد فترة خمول
# (تتجدد مع كل استخدام) عشان ما تنسى وتتحول روابطك العادية بالغلط.
GIF_MODE_TIMEOUT_MIN = int(os.environ.get("GIF_MODE_TIMEOUT_MIN", "15"))
gif_mode_until: dict = {}  # chat_id -> وقت انتهاء الوضع (time.monotonic)


def is_gif_mode(chat_id) -> bool:
    deadline = gif_mode_until.get(chat_id)
    if deadline is None:
        return False
    if time.monotonic() >= deadline:
        gif_mode_until.pop(chat_id, None)
        return False
    return True


def touch_gif_mode(chat_id):
    """يفعّل/يجدد وضع GIF للمحادثة لمدة GIF_MODE_TIMEOUT_MIN من الآن."""
    gif_mode_until[chat_id] = time.monotonic() + GIF_MODE_TIMEOUT_MIN * 60

# أقصى حجم للفيديو المرسل عشان نحوّله (بالميجا) - نتفادى تنزيل ملفات ضخمة
GIF_MAX_INPUT_MB = int(os.environ.get("GIF_MAX_INPUT_MB", "200"))

# مواقع "مرآة" (نفس المحتوى، دومين مختلف) غير مدعومة مباشرة من yt-dlp
# فيرجع لها لآلية استخراج عامة (generic extractor) ما تقدر تكتشف
# خيارات الجودة الحقيقية (ترجع جودة واحدة فقط بدون بيانات height) -
# نبدّل الدومين للأساسي المدعوم تلقائيًا قبل أي معالجة، عشان يقدر
# yt-dlp يستخرج بيانات الجودة الصحيحة دايمًا بغض النظر عن أي دومين
# أرسل المستخدم الرابط منه.
MIRROR_DOMAIN_REWRITES = {
    "xnxx-arabic.com": "xnxx.com",
    "www.xnxx-arabic.com": "www.xnxx.com",
    "xvideos-ar.com": "xvideos.com",
    "www.xvideos-ar.com": "www.xvideos.com",
}


def is_allowed_trigger(event) -> bool:
    """يتحقق إن هذي الرسالة فعليًا مسموح تشغّل البوت منها:
    - Saved Messages: لازم تكون رسالة "صادرة" منك (out=True) - نفس
      المنطق القديم (كل رسالة ترسلها لنفسك تعتبر outgoing).
    - المجموعة الخاصة (GROUP_CHAT_ID): لازم تكون "واردة" (out=False)
      أي من رقم ثاني غيرك بالمجموعة - هذا يستثني تلقائيًا رسائل حالة/
      ردود البوت نفسه اللي يرسلها بنفس المجموعة (تطلع out=True لأنها
      من نفس حسابك اللي شغّل عليه البوت)، فما تسبب تحميل مكرر لو كانت
      تحتوي رابط بالغلط."""
    if event.is_private and event.out:
        return True
    if GROUP_CHAT_ID and event.chat_id == GROUP_CHAT_ID and not event.out:
        # لو حددت ALLOWED_USER_IDS، فقط هذي الأرقام تقدر تشغّل البوت
        if ALLOWED_USER_IDS and getattr(event, "sender_id", None) not in ALLOWED_USER_IDS:
            return False
        return True
    return False


def normalize_url(url: str) -> str:
    """يستبدل دومين الرابط بالدومين الأساسي المدعوم لو كان من إحدى
    دومينات المرايا المعروفة أعلاه، ويترجع الرابط كما هو غير ذلك."""
    try:
        parsed = urllib.parse.urlsplit(url)
        new_host = MIRROR_DOMAIN_REWRITES.get(parsed.netloc.lower())
        if not new_host:
            return url
        return urllib.parse.urlunsplit(parsed._replace(netloc=new_host))
    except Exception:
        return url

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

# كيان (entity) حسابك نفسه - نجيبه مرة وحدة بعد بدء تشغيل العميل
# ونعيد استخدامه بكل مكان يحتاج إرسال رسالة لنفسك.
SELF_ENTITY = None

# طلب اختيار الجودة المفتوح حاليًا (لو فيه واحد) - بديل عن
# client.conversation() اللي طلع إنها غير متوافقة أصلاً مع محادثة
# الحساب مع نفسه (Saved Messages): أي entity تمرره لها يتحول داخليًا
# لنوع خاص (InputPeerSelf) يفشل بخطأ TypeError جوا آلية تتبعها الداخلية،
# بغض النظر عن طريقة استخدامنا لها. الحل: نبني آلية انتظار يدوية بسيطة
# عبر asyncio.Future، ونلتقط رد المستخدم من نفس handle_message العام
# (بما إن الاستخدام شخصي وسؤال واحد بس يكون مفتوح بأي لحظة، متغير
# وحيد كافٍ بدون تعقيد إضافي).
# نفس آلية الانتظار اليدوي، بس صارت مفهرسة بمعرّف المحادثة (chat_id)
# بدل متغير عام واحد - هذا ضروري الآن بعد دعم أكثر من محادثة (Saved
# Messages + المجموعة الخاصة)، عشان سؤال جودة مفتوح بمحادثة وحدة ما
# يتعارض مع سؤال ثاني مفتوح بمحادثة ثانية بنفس الوقت.
pending_quality_futures: dict = {}
pending_quality_options: dict = {}


# معرّفات الرسائل اللي أرسلها البوت نفسه (محادثة، رقم رسالة). ضروري لأن
# أي شي يرسله البوت بـ Saved Messages يعتبر "صادر منك" (out=True) - بدونها
# كان البوت يحوّل الفيديوهات اللي هو أرسلها بنفسه لـ GIF بحلقة لا تنتهي.
bot_sent_ids = collections.deque(maxlen=500)


async def send_bot_file(chat_id, *args, **kwargs):
    """يرسل ملف عبر client.send_file ويسجّل رقم الرسالة المرسلة، عشان
    معالج الفيديوهات المرسلة (handle_uploaded_video) يتجاهلها."""
    msg = await client.send_file(chat_id, *args, **kwargs)
    first = msg[0] if isinstance(msg, (list, tuple)) else msg
    bot_sent_ids.append((chat_id, first.id))
    return msg


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


def convert_to_gif(filepath: str, start: int = 0, length: int | None = None):
    """يحوّل الفيديو إلى "GIF تيليجرام": mp4 صامت (H.264) بعرض أقصى 480
    ومدة أقصاها GIF_MAX_SECONDS، ويرجّع مسار الملف الناتج (أو None لو
    فشل التحويل). تيليجرام يعرضه كـ GIF متحرك لما نضيف له خاصية
    DocumentAttributeAnimated وقت الإرسال."""
    out_path = os.path.splitext(filepath)[0] + "_gif.mp4"
    length = min(length or GIF_MAX_SECONDS, GIF_MAX_SECONDS)
    try:
        result = subprocess.run(
            [
                "ffmpeg", "-y",
                # -ss قبل -i = قفز سريع لنقطة البداية بدون فك تشفير اللي قبلها
                "-ss", str(start or 0),
                "-i", filepath,
                "-t", str(length),
                "-an",
                "-vf", f"fps={GIF_FPS},scale='min({GIF_MAX_WIDTH},iw)':-2",
                "-c:v", "libx264", "-preset", "veryfast", "-crf", "26",
                "-pix_fmt", "yuv420p",
                "-movflags", "+faststart",
                out_path,
            ],
            capture_output=True, timeout=180,
        )
        # ملاحظة: لو نقطة البداية بعد نهاية الفيديو، ffmpeg يرجّع نجاح (0) لكن
        # ينتج ملف mp4 فاضي (بدون أي إطار) - نعتبره فشل بدل ما نرسل ملف تالف.
        if (
            result.returncode != 0
            or not os.path.exists(out_path)
            or os.path.getsize(out_path) == 0
            or b"Output file is empty" in result.stderr
        ):
            logger.error(
                "فشل تحويل GIF: " + result.stderr.decode("utf-8", "ignore")[-300:]
            )
            return None
        return out_path
    except Exception:
        logger.exception("تعذر تحويل الفيديو إلى GIF")
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


@client.on(events.NewMessage(chats=ALLOWED_CHATS, pattern=r"(?i)^(الغاء|إلغاء|cancel|stop)$"))
async def handle_cancel(event):
    """يلغي كل التحميلات الجارية حاليًا (لو فيه أكثر من رابط قيد
    المعالجة)، وكمان يلغي سؤال اختيار جودة مفتوح حاليًا لو فيه واحد.
    يشتغل بس لو الرسالة عبارة عن كلمة إلغاء فقط، عشان ما يتعارض مع
    رسائل عادية فيها كلمة "الغاء" ضمن سياق ثاني."""
    if not is_allowed_trigger(event):
        return
    future = pending_quality_futures.get(event.chat_id)
    cancelled_quality = False
    if future is not None and not future.done():
        future.set_result("cancelled")
        cancelled_quality = True

    if not active_operations:
        if not cancelled_quality:
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


@client.on(events.NewMessage(chats=ALLOWED_CHATS, pattern=r"(?i)^(تنظيف|مسح الكاش|clean|clear cache)$"))
async def handle_clean_cache(event):
    """يمسح أي ملفات تحميل مؤقتة متبقية من عمليات سابقة توقفت بشكل
    غير طبيعي (تعطل، انقطاع اتصال، إلخ)، دون التأثير على أي تحميل
    شغّال حاليًا."""
    if not is_allowed_trigger(event):
        return
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


@client.on(events.NewMessage(chats=ALLOWED_CHATS, pattern=r"(?i)^(اعادة تشغيل|إعادة تشغيل|restart)$"))
async def handle_restart(event):
    """يعيد تشغيل السيرفر بالكامل. يوقف العملية الحالية عمدًا، وبما إن
    Render يراقب الخدمة ويعيد تشغيلها تلقائيًا عند توقفها (نفس سلوكه
    مع أي تعطل)، هذا يعادل "إعادة تشغيل" حقيقية بدون حاجة للدخول للوحة
    تحكم Render يدويًا."""
    if not is_allowed_trigger(event):
        return
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


@client.on(events.NewMessage(chats=ALLOWED_CHATS, pattern=r"(?i)^تأكيد إعادة التشغيل$"))
async def handle_force_restart(event):
    """تأكيد إعادة التشغيل رغم وجود تحميلات شغّالة - تُفقد هذي
    التحميلات الجارية بدون استكمال."""
    if not is_allowed_trigger(event):
        return
    await event.respond("🔄 جاري إعادة التشغيل رغم العمليات الجارية...")
    await asyncio.sleep(1.5)
    os._exit(0)


@client.on(events.NewMessage(chats=ALLOWED_CHATS, pattern=r"(?i)^(حالة|status)$"))
async def handle_status(event):
    """يعرض حالة السيرفر الحالية: تحميلات شغّالة، مساحة القرص
    المتبقية، واستهلاك الذاكرة التقريبي - يفيد لتشخيص أي بطء غير
    طبيعي (مثلاً امتلاء القرص أو تراكم ذاكرة)."""
    if not is_allowed_trigger(event):
        return
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

    lines.append(
        f"🚦 العمليات المتزامنة: {len(active_operations)} / {MAX_CONCURRENT_JOBS}"
        + (f" ({queued_jobs} بالانتظار)" if queued_jobs else "")
    )
    lines.append(f"📏 أقصى حجم للملف: {MAX_FILE_SIZE // (1024 * 1024)} ميجا")

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


@client.on(events.NewMessage(chats=ALLOWED_CHATS, pattern=r"(?i)^(احصائيات|إحصائيات|stats)$"))
async def handle_stats(event):
    """يعرض إحصائيات الاستخدام الكلي منذ آخر إعادة تشغيل - يساعدك
    تتابع استهلاكك من حصة Render الشهرية (100 جيجا باندويدث مجانًا)."""
    if not is_allowed_trigger(event):
        return
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


@client.on(events.NewMessage(chats=ALLOWED_CHATS, pattern=r"(?i)^(مساعدة|help)$"))
async def handle_help(event):
    """يعرض قائمة كل الأوامر والكلمات المتاحة بالبوت (رسالة أولى)، ثم
    الإعدادات الحالية ومتغيرات البيئة اللي تغيّرها من Render (رسالة ثانية)."""
    if not is_allowed_trigger(event):
        return
    await event.respond(build_help_text())
    await event.respond(build_settings_text())


def build_help_text() -> str:
    return (
        "🤖 **قائمة أوامر البوت**\n\n"
        "📥 **تحميل فيديو**\n"
        "• `الرابط` → يعرض الصيغ المتوفرة مع **حجم كل صيغة** (كل جودة فيديو، "
        "أعلى جودة تلقائيًا، 🎵 صوت MP3، 🎞️ GIF) وترد برقم الخيار خلال 60 ثانية "
        "(وإلا يكمل بأعلى جودة)\n"
        "• `الرابط 720` → جودة محددة فورًا بدون سؤال "
        "(240 · 360 · 480 · 720 · 1080 · 1440 · 2160)\n"
        "• أكثر من رابط بنفس الرسالة → يعالجهم بالترتيب\n\n"
        "🏷️ **كلمات تضيفها بعد الرابط**\n"
        "• `720` (أو أي جودة) → تحميل بهذي الجودة\n"
        "• `gif` أو `جيف` → GIF متحرك\n"
        "• `mp3` أو `صوت` أو `audio` → صوت فقط بصيغة MP3\n"
        "• `10-20` أو `1:30-1:45` → قص مقطع (من ثانية إلى ثانية، مع gif فقط)\n"
        "• تركيبة مثال: `الرابط gif 360 10-20`\n\n"
        "🎞️ **وضع GIF (لعدة فيديوهات)**\n"
        "• `gif` (أو `جيف`) لحالها → يدخل الوضع: أي فيديو ترسله (رفع أو إعادة "
        "توجيه) أو رابط يتحول لـ GIF\n"
        "• `الغاء gif` → يخرج ويرجع لتحميل الروابط العادي "
        f"(وينتهي تلقائيًا بعد {GIF_MODE_TIMEOUT_MIN} دقيقة خمول)\n"
        "• فيديو مرفوع بدون الوضع: اكتب `gif` بوصفه (وتقدر تضيف مدى القص، "
        "مثل `gif 5-15`)\n"
        f"• الحد الأقصى {GIF_MAX_SECONDS} ثانية (يقصّ الباقي)، بدون صوت، "
        f"وعرض أقصى {GIF_MAX_WIDTH}\n\n"
        "**أوامر التحكم:**\n"
        "• `الغاء` - يوقف أي تحميل شغّال أو ينتظر بالطابور\n"
        "• `تنظيف` - يمسح الملفات المؤقتة المتراكمة\n"
        "• `اعادة تشغيل` - يعيد تشغيل السيرفر بالكامل\n"
        "• `حالة` - حالة السيرفر (تحميلات، طابور، قرص، ذاكرة)\n"
        "• `احصائيات` - إجمالي الاستخدام منذ آخر تشغيل\n"
        "• `مساعدة` - يعرض هذي القائمة"
    )


def build_settings_text() -> str:
    """الإعدادات الحالية (قراءة فقط) مع اسم متغير البيئة اللي يغيّرها بـ
    Render → Environment. لا تعرض أي قيمة سرية (الجلسة/الكوكيز/المفاتيح)."""
    max_mb = MAX_FILE_SIZE // (1024 * 1024)
    if MAX_FILE_SIZE_FORCED:
        size_line = f"{max_mb} ميجا (محدد يدويًا)"
    else:
        size_line = f"{max_mb} ميجا (تلقائي: 2000 عادي / 4000 Premium)"
    users_line = (
        f"{len(ALLOWED_USER_IDS)} رقم مسموح" if ALLOWED_USER_IDS else "غير محدد (أي عضو بالمجموعة)"
    )
    return (
        "⚙️ **الإعدادات الحالية** (تغيّرها من Render ← Environment)\n\n"
        "**الأداء والحدود:**\n"
        f"• `MAX_CONCURRENT_JOBS` = {MAX_CONCURRENT_JOBS} - عمليات تحميل/تحويل "
        "بنفس الوقت (الباقي بالطابور)\n"
        f"• `MAX_FILE_MB` = {size_line} - أقصى حجم للملف\n\n"
        "**GIF:**\n"
        f"• `GIF_MAX_SECONDS` = {GIF_MAX_SECONDS} - أقصى مدة للـ GIF بالثواني\n"
        f"• `GIF_MODE_TIMEOUT_MIN` = {GIF_MODE_TIMEOUT_MIN} - دقائق الخمول قبل "
        "خروج وضع GIF تلقائيًا\n"
        f"• `GIF_MAX_INPUT_MB` = {GIF_MAX_INPUT_MB} - أقصى حجم لفيديو مرفوع "
        "يتحول لـ GIF\n\n"
        "**الأمان والمجموعة:**\n"
        f"• `GROUP_CHAT_ID` = {'مضبوط ✅' if GROUP_CHAT_ID else 'غير مضبوط'} - "
        "المجموعة الخاصة لأرقامك الثانية\n"
        f"• `ALLOWED_USER_IDS` = {users_line}\n"
        f"• `COOKIES_B64` = {'مضبوط ✅' if COOKIES_FILE_PATH else 'غير مضبوط'} - "
        "كوكيز للمحتوى المقيّد بتسجيل دخول\n\n"
        "**أساسية (مطلوبة):** `API_ID` · `API_HASH` · `SESSION_STRING`\n\n"
        "(الأحجام بقائمة الاختيار: بدون ~ = حجم معلن من الموقع، ومعها ~ = تقديري)"
    )


@client.on(events.NewMessage(chats=ALLOWED_CHATS, pattern=r"(?i)^(gif|جيف)$"))
async def handle_gif_mode_on(event):
    """كلمة gif لحالها → تفعيل وضع GIF بهذي المحادثة."""
    if not is_allowed_trigger(event):
        return
    touch_gif_mode(event.chat_id)
    await event.respond(
        "🎞️ **وضع GIF مفعّل**\n"
        "أرسل الفيديو (أو رابط فيديو) وأحوّله إلى GIF.\n"
        "للخروج والرجوع لتحميل الروابط العادي: `الغاء gif`\n"
        f"(ينتهي تلقائيًا بعد {GIF_MODE_TIMEOUT_MIN} دقيقة بدون استخدام)"
    )


@client.on(events.NewMessage(chats=ALLOWED_CHATS, pattern=r"(?i)^(الغاء|إلغاء|cancel|stop)\s+(gif|جيف)$"))
async def handle_gif_mode_off(event):
    """الغاء gif → الخروج من وضع GIF والرجوع للوضع العادي."""
    if not is_allowed_trigger(event):
        return
    was_on = is_gif_mode(event.chat_id)
    gif_mode_until.pop(event.chat_id, None)
    if was_on:
        await event.respond("✅ تم الخروج من وضع GIF - رجعنا لتحميل الروابط العادي.")
    else:
        await event.respond("ℹ️ وضع GIF مو مفعّل أصلاً - أنت بالوضع العادي.")


@client.on(events.NewMessage(chats=ALLOWED_CHATS))
async def handle_uploaded_video(event):
    """يحوّل الفيديو المرسل إلى GIF ويرسله كرد على نفس الفيديو، بس لما
    يكون "وضع GIF" مفعّل بهذي المحادثة (أو لو كتبت gif بوصف الفيديو
    كتحويل لمرة وحدة). يتجاهل: الـ GIF أصلاً، الفيديوهات الدائرية،
    وأي فيديو أرسله البوت نفسه (تحميلاته)."""
    if not is_allowed_trigger(event):
        return
    msg = event.message
    doc = msg.document
    if doc is None:
        return
    mime = getattr(doc, "mime_type", "") or ""
    if not mime.startswith("video/") or msg.gif or msg.video_note:
        return

    caption = event.raw_text or ""
    caption_no_urls = URL_REGEX.sub(" ", caption)
    in_mode = is_gif_mode(event.chat_id)
    if not in_mode and not GIF_REGEX.search(caption_no_urls):
        return

    # ننتظر لحظات عشان رقم رسالة البوت نفسه (لو هو المرسل) يتسجل أول -
    # حدث الرسالة أحيانًا يوصل قبل ما ترجع send_file بنتيجتها.
    await asyncio.sleep(2.5)
    if (event.chat_id, msg.id) in bot_sent_ids:
        return
    if in_mode:
        touch_gif_mode(event.chat_id)  # نجدد مهلة الخمول مع كل استخدام

    # مدى القص من وصف الفيديو (مثل: gif 5-15)، ونشيل كلمة gif والمدى من
    # الوصف عشان الـ GIF الناتج ما يحمل وصف تقني، ويبقى فقط أي نص ثاني كتبته.
    clip, caption_rest = parse_clip_range(caption_no_urls)
    if clip == "bad":
        await event.respond(
            "⚠️ مدى القص غير صحيح - النهاية لازم تكون بعد البداية "
            "(مثال: `gif 10-20`)."
        )
        return
    caption = re.sub(r"\s+", " ", GIF_REGEX.sub(" ", caption_rest)).strip()

    if doc.size and doc.size > GIF_MAX_INPUT_MB * 1024 * 1024:
        await event.respond(
            f"⚠️ الفيديو أكبر من {GIF_MAX_INPUT_MB} ميجا، تعذر تحويله إلى GIF."
        )
        return

    vattr = next(
        (a for a in doc.attributes if isinstance(a, DocumentAttributeVideo)), None
    )
    duration = int(vattr.duration) if vattr and vattr.duration else 0
    width = int(vattr.w) if vattr and vattr.w else 0
    height = int(vattr.h) if vattr and vattr.h else 0

    status = await event.respond("🎞️ جاري تحويل الفيديو إلى GIF...\n(أرسل \"الغاء\" للإيقاف)")
    tmp_dir = tempfile.mkdtemp(prefix="ytdlp_")
    cancel_event = threading.Event()
    operation = {
        "cancel_event": cancel_event,
        "url": "فيديو مرسل ← GIF",
        "tmp_dir": tmp_dir,
    }
    active_operations.append(operation)

    def download_progress(current: int, total: int):
        if cancel_event.is_set():
            raise RuntimeError(CANCELLED_MARKER)

    slot_held = False
    try:
        waited = await acquire_job_slot(status, "فيديو مرسل ← GIF", cancel_event)
        slot_held = True
        if waited:
            await safe_edit(status, "🎞️ جاري تحويل الفيديو إلى GIF...")
        src_path = await client.download_media(
            msg, file=tmp_dir, progress_callback=download_progress
        )
        if not src_path or not os.path.exists(src_path):
            raise FileNotFoundError("تعذر تنزيل الفيديو")

        win_start, gif_length = resolve_gif_window(clip, duration)
        gif_path = await asyncio.to_thread(
            convert_to_gif, src_path, win_start, gif_length
        )
        if not gif_path:
            if clip:
                raise UserFacingError(
                    "ما قدرت أقص هذا المقطع - تأكد إن المدى داخل مدة الفيديو."
                )
            raise RuntimeError("تعذر تحويل الفيديو إلى GIF")

        # نفس حساب الأبعاد/المدة بعد التحويل (scale بالـ ffmpeg)
        duration = gif_length
        if width and width > GIF_MAX_WIDTH:
            height = int(round(height * GIF_MAX_WIDTH / width / 2) * 2) if height else 0
            width = GIF_MAX_WIDTH

        thumb_path = await asyncio.to_thread(generate_thumbnail, gif_path)
        await send_bot_file(
            event.chat_id,
            gif_path,
            caption=caption,
            reply_to=msg.id,
            supports_streaming=True,
            thumb=thumb_path,
            attributes=[
                DocumentAttributeVideo(
                    duration=duration,
                    w=width or 480,
                    h=height or 270,
                    supports_streaming=True,
                ),
                DocumentAttributeAnimated(),
            ],
        )
        stats["completed_downloads"] += 1
        stats["total_bytes_sent"] += os.path.getsize(gif_path)
        try:
            await status.delete()
        except FloodWaitError:
            pass
    except UserFacingError as e:
        stats["failed_downloads"] += 1
        await safe_edit(status, f"⚠️ {e}")
    except RuntimeError as e:
        if str(e) == CANCELLED_MARKER:
            await safe_edit(status, "🛑 تم إلغاء التحويل.")
        else:
            stats["failed_downloads"] += 1
            logger.exception("فشل تحويل فيديو مرسل إلى GIF")
            await safe_edit(status, f"❌ تعذر تحويل الفيديو إلى GIF: {str(e)[:150]}")
    except Exception as e:
        stats["failed_downloads"] += 1
        logger.exception("خطأ غير متوقع أثناء تحويل فيديو مرسل إلى GIF")
        await safe_edit(status, f"❌ حدث خطأ غير متوقع: {str(e)[:150]}")
    finally:
        if slot_held:
            job_slots.release()
        if operation in active_operations:
            active_operations.remove(operation)
        shutil.rmtree(tmp_dir, ignore_errors=True)


@client.on(events.NewMessage(chats=ALLOWED_CHATS))
async def handle_message(event):
    """يستمع لرسائلك بمحادثة Saved Messages، وكمان (لو مضبوطة)
    بالمجموعة الخاصة بأرقامك الأخرى - راجع is_allowed_trigger لشرح
    الفرق بين الحالتين (outgoing مقابل incoming).
    يدعم أكثر من رابط بنفس الرسالة - يعالجهم واحدًا تلو الآخر.
    يدعم تحديد جودة اختيارية (رقم بعد الرابط، مثل 720 أو 1080)."""
    if not is_allowed_trigger(event):
        return

    chat_id = event.chat_id
    text = (event.raw_text or "").strip()

    # لو فيه سؤال اختيار جودة مفتوح حاليًا **بنفس هذي المحادثة تحديدًا**،
    # أي رد نصي يُعتبر إجابة عليه (رقم الخيار أو إلغاء)، مو رابط جديد -
    # نتحقق قبل أي شي ثاني. (سؤال مفتوح بمحادثة ثانية ما يتأثر).
    future = pending_quality_futures.get(chat_id)
    if future is not None and not future.done():
        options = pending_quality_options.get(chat_id, {})
        if re.match(r"(?i)^(الغاء|إلغاء|cancel)$", text):
            future.set_result("cancelled")
            return
        auto_option = options.get("auto_option")
        if text.isdigit():
            idx = int(text)
            heights = options.get("heights", [])
            if idx == auto_option:
                future.set_result(None)
                return
            if idx == options.get("audio_option"):
                future.set_result("audio")
                return
            if idx == options.get("gif_option"):
                future.set_result("gif")
                return
            if 1 <= idx <= len(heights):
                future.set_result(heights[idx - 1])
                return
            max_option = options.get("max_option", auto_option)
            if max_option:
                await client.send_message(
                    chat_id, f"❌ رقم غير صالح. رد برقم من 1 إلى {max_option}."
                )
            return
        if URL_REGEX.search(text):
            # رابط جديد وسؤال الجودة لسه مفتوح - ننبّه بدل ما نتجاهله بصمت
            await client.send_message(
                chat_id,
                "⏳ فيه سؤال جودة مفتوح - جاوبه برقم الخيار أو أرسل \"الغاء\" "
                "أول، وبعدها أرسل الرابط الجديد.",
            )
            return
        # أي نص ثاني (أوامر مثل \"حالة\" أو \"gif\"، أو كلام عادي) يتعامل معه
        # معالجه الخاص - ما نعتبره جواب خاطئ على السؤال.
        return

    urls = [normalize_url(u) for u in URL_REGEX.findall(text)]
    if not urls:
        return

    # نبحث عن الجودة وكلمة gif بالنص بعد إزالة الروابط، عشان رقم أو
    # كلمة داخل الرابط نفسه (مثل /video/480/) ما تنحسب كطلب من المستخدم
    text_no_urls = URL_REGEX.sub(" ", text)
    # كلمة mp3/صوت صريحة تتغلب على وضع GIF (طلب صوت فقط لهذا الرابط)
    as_audio = bool(AUDIO_REGEX.search(text_no_urls))
    as_gif = (bool(GIF_REGEX.search(text_no_urls)) or is_gif_mode(chat_id)) and not as_audio
    if as_gif and is_gif_mode(chat_id):
        touch_gif_mode(chat_id)

    # مدى القص (10-20) يُقرأ فقط لطلبات GIF، ونشيله من النص قبل قراءة
    # الجودة عشان مدى مثل 360-370 ما ينحسب طلب جودة 360.
    clip = None
    if as_gif:
        clip, text_no_urls = parse_clip_range(text_no_urls)
        if clip == "bad":
            await event.respond(
                "⚠️ مدى القص غير صحيح - النهاية لازم تكون بعد البداية "
                "(مثال: `gif 10-20`)."
            )
            return

    quality_match = QUALITY_REGEX.search(text_no_urls)
    quality = int(quality_match.group(1)) if quality_match else None

    if len(urls) > 1:
        await event.respond(f"📋 لقيت {len(urls)} روابط، رح أعالجهم بالترتيب...")

    for url in urls:
        await process_single_url(event, url, quality, as_gif, clip, as_audio)


def build_probe_ydl_opts() -> dict:
    """نفس إعدادات yt-dlp الأساسية المستخدمة بالتحميل الفعلي (كوكيز +
    واجهات يوتيوب البديلة)، بدون أي إعداد تحميل - نستخدمها فقط
    لاستعلام الميتاداتا، عشان قائمة الجودات المعروضة تطابق تمامًا
    وش يقدر التحميل الفعلي يوصله لاحقًا."""
    opts = {
        "quiet": True,
        "no_warnings": True,
        "noplaylist": True,
        "skip_download": True,
        "extractor_args": {
            "youtube": {"player_client": ["ios", "android", "web"]},
        },
    }
    if COOKIES_FILE_PATH:
        opts["cookiefile"] = COOKIES_FILE_PATH
    return opts


def format_size(size_bytes, estimate: bool = False) -> str:
    """يحوّل عدد بايتات لنص مقروء (135MB / 1.2GB). estimate=True يضيف ~
    (حجم تقديري). لو الحجم مجهول يرجّع "غير معروف"."""
    if not size_bytes:
        return "غير معروف"
    mb = size_bytes / (1024 * 1024)
    if mb >= 1024:
        text = f"{mb / 1024:.1f}GB"
    elif mb >= 10:
        text = f"{mb:.0f}MB"
    else:
        text = f"{mb:.1f}MB"
    return ("~" if estimate else "") + text


def _format_bytes(fmt: dict, duration: int):
    """حجم صيغة وحدة: (بايتات أو None، هل هو تقديري). الأولوية للحجم
    المعلن بدقة، ثم التقريبي، ثم تقدير من معدل البت × المدة."""
    if fmt.get("filesize"):
        return int(fmt["filesize"]), False
    if fmt.get("filesize_approx"):
        return int(fmt["filesize_approx"]), True
    tbr = fmt.get("tbr")
    if tbr and duration:
        return int(tbr * 1000 / 8 * duration), True
    return None, False


def compute_quality_sizes(info: dict) -> dict:
    """يحسب حجم كل جودة (ارتفاع) كما سيحمّلها البوت فعليًا: أفضل صيغة
    فيديو بهذا الارتفاع + أفضل مسار صوت منفصل (لو الفيديو بدون صوت).
    يرجّع {الارتفاع: (بايتات أو None، هل هو تقديري)}."""
    duration = int(info.get("duration") or 0)
    formats = info.get("formats") or []
    video_fmts = [f for f in formats if f.get("height") and f.get("vcodec") != "none"]
    audio_fmts = [
        f for f in formats
        if f.get("acodec") not in (None, "none") and f.get("vcodec") in (None, "none")
    ]
    best_audio = max(
        (_format_bytes(f, duration) for f in audio_fmts),
        key=lambda x: x[0] or 0,
        default=(None, False),
    )
    sizes = {}
    for height in {f["height"] for f in video_fmts}:
        best = max(
            (f for f in video_fmts if f["height"] == height),
            key=lambda f: _format_bytes(f, duration)[0] or 0,
        )
        size, estimate = _format_bytes(best, duration)
        if size is None:
            sizes[height] = (None, False)
            continue
        if best.get("acodec") == "none":  # فيديو بدون صوت → نضيف الصوت المنفصل
            audio_size, audio_estimate = best_audio
            if audio_size:
                size += audio_size
                estimate = estimate or audio_estimate
            else:
                estimate = True
        sizes[height] = (size, estimate)
    return sizes


def probe_formats(url: str) -> dict:
    """يجيب من الموقع (بدون تحميل أي بايت من الفيديو) قائمة الجودات
    المتوفرة فعليًا + حجم كل جودة + مدة الفيديو. هذا استعلام ميتاداتا خفيف
    جدًا (yt-dlp أصلاً يسويه قبل أي تحميل عادي)، فما يأثر على السرعة."""
    with yt_dlp.YoutubeDL(build_probe_ydl_opts()) as ydl:
        info = ydl.extract_info(url, download=False)
    formats = info.get("formats") or []
    heights = sorted({f.get("height") for f in formats if f.get("height")}, reverse=True)
    return {
        "heights": heights,
        "sizes": compute_quality_sizes(info),
        "duration": int(info.get("duration") or 0),
    }


async def ask_quality_choice(url: str, probe: dict, chat_id):
    """يعرض قائمة الصيغ الحقيقية المتوفرة لهذا الفيديو تحديدًا مع حجم كل
    صيغة: كل جودة فيديو + أعلى جودة تلقائيًا + 🎵 صوت MP3 + 🎞️ GIF،
    بنفس المحادثة (chat_id) اللي جا منها الرابط، وينتظر رد المستخدم برقم
    الخيار خلال 60 ثانية.
    ملاحظة: ما نستخدم أزرار ضغط (Button.text/Inline) لأن تيليجرام
    يتجاهلها تمامًا (على مستوى السيرفر) لو أُرسلت من حساب مستخدم
    عادي - هذي الميزة محصورة بحسابات البوت الرسمية عبر @BotFather
    فقط، بغض النظر عن أي مكتبة تُستخدم (Telethon أو غيرها).
    بدل client.conversation() (غير متوافقة مع محادثة الحساب مع نفسه)،
    نرسل السؤال كرسالة عادية، ونفتح asyncio.Future يلتقط الرد من
    handle_message العام لحظة ما يوصل، بدون انتظار حجب (blocking) هنا.
    يرجّع: الارتفاع المختار (int) - أو None لو اختار \"أعلى جودة
    تلقائيًا\" أو انتهى الوقت - أو \"audio\" / \"gif\" - أو \"cancelled\" لو ألغى."""
    heights = probe["heights"]
    sizes = probe.get("sizes", {})
    duration = probe.get("duration", 0)
    auto_option = len(heights) + 1
    audio_option = auto_option + 1
    gif_option = auto_option + 2

    lines = ["🎚️ اختر الصيغة (رد برقم الخيار):\n"]
    for i, h in enumerate(heights, start=1):
        size, estimate = sizes.get(h, (None, False))
        warn = " ⚠️ أكبر من حد الإرسال" if size and size > MAX_FILE_SIZE else ""
        lines.append(f"{i}. {h}p — الحجم {format_size(size, estimate)}{warn}")
    top_size, top_estimate = sizes.get(heights[0], (None, False))
    lines.append(
        f"{auto_option}. أعلى جودة تلقائيًا (Auto) — الحجم "
        f"{format_size(top_size, top_estimate)}"
    )
    mp3_size = duration * MP3_BYTES_PER_SEC if duration else None
    lines.append(
        f"{audio_option}. 🎵 صوت فقط (MP3) — الحجم {format_size(mp3_size, True)}"
    )
    gif_seconds = min(duration or GIF_MAX_SECONDS, GIF_MAX_SECONDS)
    lines.append(
        f"{gif_option}. 🎞️ GIF (حتى {GIF_MAX_SECONDS} ثانية) — الحجم "
        f"{format_size(gif_seconds * GIF_EST_BYTES_PER_SEC, True)}"
    )
    lines.append(
        "\n(~ = حجم تقديري)\n"
        "(60 ثانية قبل ما نكمل تلقائيًا بأعلى جودة، أو أرسل \"الغاء\" للتجاهل)"
    )
    prompt = "\n".join(lines)

    await client.send_message(chat_id, prompt)

    loop = asyncio.get_event_loop()
    future = loop.create_future()
    pending_quality_futures[chat_id] = future
    pending_quality_options[chat_id] = {
        "heights": heights,
        "auto_option": auto_option,
        "audio_option": audio_option,
        "gif_option": gif_option,
        "max_option": gif_option,
    }
    try:
        return await asyncio.wait_for(future, timeout=60)
    except asyncio.TimeoutError:
        await client.send_message(
            chat_id, "⏰ انتهى الوقت، جاري المتابعة بأعلى جودة تلقائيًا."
        )
        return None
    finally:
        pending_quality_futures.pop(chat_id, None)
        pending_quality_options.pop(chat_id, None)


async def process_single_url(
    event,
    url: str,
    quality: int | None = None,
    as_gif: bool = False,
    clip=None,
    as_audio: bool = False,
):
    """يحمّل رابط واحد ويرسله، مع تحديث حي لنسبة التقدم بنفس الرسالة.
    quality: أعلى ارتفاع مسموح (مثل 720)، أو None لأعلى جودة متوفرة
    (لو None، يسأل المستخدم أولاً عن الجودات الحقيقية المتوفرة - إلا
    لو فيه جودة وحدة بس متوفرة، بهالحالة ما فيه داعي نسأل)."""
    if quality is None and not as_gif and not as_audio:
        try:
            probe = await asyncio.to_thread(probe_formats, url)
        except Exception:
            logger.exception(
                "تعذر جلب قائمة الجودات المتوفرة - سيتم المتابعة بأعلى جودة تلقائيًا"
            )
            probe = {"heights": [], "sizes": {}, "duration": 0}

        if len(probe["heights"]) > 1:
            choice = await ask_quality_choice(url, probe, event.chat_id)
            if choice == "cancelled":
                await event.respond(f"🛑 تم تجاهل هذا الرابط.\n{url}")
                return
            elif choice == "audio":
                as_audio = True  # اختار 🎵 صوت فقط من القائمة
            elif choice == "gif":
                as_gif = True  # اختار 🎞️ GIF من القائمة
            else:
                quality = choice  # None يعني أعلى جودة تلقائيًا (بدون تغيير)

    quality_label = f" (جودة {quality}p)" if quality else ""
    if as_gif:
        quality_label += " 🎞️ (سيتحول إلى GIF)"
        if clip:
            quality_label += f" ✂️ {clip[0]}-{clip[1]}"
    elif as_audio:
        quality_label += " 🎵 (صوت فقط)"
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
                    extra = progress_extra(d.get("speed"), d.get("eta"))
                    new_text = (
                        f"⏳ جاري التحميل... {percent:.0f}%{extra}\n{url}\n\n"
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

    if as_audio:
        # صوت فقط: نطلب أفضل مسار صوت (أو أفضل صيغة لو الموقع ما يفصل)
        fmt = "bestaudio/best"
    elif as_gif:
        # GIF صامت وقصير: ما نحتاج جودة عالية ولا صوت - نطلب فيديو فقط
        # بحد أقصى GIF_MAX_HEIGHT (أو الجودة اللي حددها المستخدم) لتوفير
        # الباندويدث، مع رجوع لصيغة جاهزة لو الموقع ما يفصل الصوت.
        cap = quality or GIF_MAX_HEIGHT
        fmt = f"bestvideo[height<={cap}]/best[height<={cap}]/best"
    elif quality:
        # لما تحدد جودة بنفسك (مثل 1080)، نسمح بدمج فيديو+صوت منفصلين
        # لو احتاج الأمر، عشان نضمن الوصول لأعلى جودة حقيقية متوفرة
        # تحت هذا السقف، حتى لو ما كانت بصيغة جاهزة مسبقًا.
        fmt = f"bestvideo[height<={quality}]+bestaudio/best[height<={quality}]"
    else:
        # بدون تحديد جودة: نطلب أعلى جودة موجودة بالموقع دايمًا، حتى
        # لو احتاجت دمج فيديو منفصل مع صوت منفصل (bestvideo+bestaudio) -
        # هذا ضروري لأن أعلى جودة بمواقع كثيرة (يوتيوب وغيره) تكون
        # بصيغتين منفصلتين، ومحصورين بـ"best" وحدها كان يهبط الجودة
        # لأقصى صيغة "جاهزة مسبقًا" متوفرة، مو أعلى جودة حقيقية بالموقع.
        fmt = "bestvideo+bestaudio/best"

    ydl_opts = {
        "outtmpl": output_template,
        "format": fmt,
        "merge_output_format": "mp4",
        "noplaylist": True,
        "quiet": True,
        "no_warnings": True,
        "max_filesize": MAX_FILE_SIZE,
        # تحميل عدة أجزاء بالتوازي بدل التسلسل - يسرّع الفيديوهات
        # المجزأة (HLS) بشكل كبير جدًا لأنها عملية شبكة وليست معالجة.
        "concurrent_fragment_downloads": 8,
        "progress_hooks": [progress_hook],
        # حل احتياطي معروف لمشكلة "The page needs to be reloaded" من
        # يوتيوب - نطلب البيانات عبر واجهة تطبيق أندرويد الداخلية
        # (تتجاوز غالبًا تشديدات الحماية الجديدة المطبّقة على واجهة
        # الويب العادية)، مع الرجوع لواجهة الويب لو فشلت.
        "extractor_args": {
            "youtube": {"player_client": ["ios", "android", "web"]},
        },
    }

    if as_audio:
        # تحويل الصوت المُحمّل إلى MP3 عبر ffmpeg (مثبّت بالـ Dockerfile)
        ydl_opts.pop("merge_output_format", None)
        ydl_opts["postprocessors"] = [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }
        ]

    # لو فيه كوكيز مضبوطة، نمررها لـ yt-dlp عشان يقدر يحمّل محتوى
    # يتطلب تسجيل دخول (حسابات خاصة، محتوى مقيّد بعمر، إلخ)
    if COOKIES_FILE_PATH:
        ydl_opts["cookiefile"] = COOKIES_FILE_PATH

    slot_held = False
    try:
        # طابور: لو فيه MAX_CONCURRENT_JOBS عمليات شغّالة، ننتظر دورنا
        waited = await acquire_job_slot(status, url, cancel_event)
        slot_held = True
        if waited:
            await safe_edit(
                status,
                f"⏳ جاري التحميل...{quality_label} 0%\n{url}\n\n"
                "(أرسل \"الغاء\" لإيقاف هذا التحميل)",
            )

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = await asyncio.to_thread(ydl.extract_info, url, download=True)
            filename = ydl.prepare_filename(info)
            if not os.path.exists(filename):
                base, _ = os.path.splitext(filename)
                filename = base + ".mp4"

        if as_audio:
            # بعد التحويل يصير الملف .mp3 (الأصلي يُحذف تلقائيًا)
            mp3_candidate = os.path.splitext(filename)[0] + ".mp3"
            if not os.path.exists(mp3_candidate):
                found = glob.glob(os.path.join(tmp_dir, "*.mp3"))
                if found:
                    mp3_candidate = found[0]
            filename = mp3_candidate

        # تسجيل كل الصيغ المتوفرة بالمصدر بالسجلات (Logs) - يساعدنا
        # نشخّص لو صار فرق بين "أعلى جودة معلنة" و"أعلى جودة فعليًا
        # متاحة للتحميل عبر yt-dlp" (أحيانًا تختلف حسب الموقع والكوكيز)
        try:
            available = info.get("formats") or []
            heights = sorted({f.get("height") for f in available if f.get("height")}, reverse=True)
            chosen_height = info.get("height")
            chosen_width = info.get("width")
            logger.info(
                f"[{url}] الجودات المتوفرة بالمصدر: {heights} | "
                f"المختارة فعليًا: {chosen_width}x{chosen_height}"
            )
        except Exception:
            pass

        if not os.path.exists(filename):
            raise FileNotFoundError("تعذر إيجاد الملف بعد التحميل")

        gif_length = 0
        if as_gif:
            win_start, gif_length = resolve_gif_window(
                clip, int(info.get("duration") or 0)
            )
            await safe_edit(status, f"🎞️ جاري التحويل إلى GIF...\n{url}")
            gif_path = await asyncio.to_thread(
                convert_to_gif, filename, win_start, gif_length
            )
            if not gif_path:
                if clip:
                    raise UserFacingError(
                        "ما قدرت أقص هذا المقطع - تأكد إن المدى داخل مدة الفيديو."
                    )
                raise RuntimeError("تعذر تحويل الفيديو إلى GIF")
            filename = gif_path

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
        if as_gif:
            # أبعاد ومدة الملف بعد التحويل (نفس حساب scale بالـ ffmpeg)
            duration = gif_length
            if width and width > GIF_MAX_WIDTH:
                height = int(round(height * GIF_MAX_WIDTH / width / 2) * 2) if height else 0
                width = GIF_MAX_WIDTH
        thumb_path = (
            None if as_audio else await asyncio.to_thread(generate_thumbnail, filename)
        )
        attributes = None
        if as_audio:
            attributes = [
                DocumentAttributeAudio(
                    duration=duration,
                    title=(info.get("title") or "")[:64] or None,
                    performer=(info.get("uploader") or info.get("channel") or None),
                )
            ]
        elif duration or width or height:
            attributes = [
                DocumentAttributeVideo(
                    duration=duration,
                    w=width or 640,
                    h=height or 360,
                    supports_streaming=True,
                )
            ]
        if as_gif:
            # هذي الخاصية هي اللي تخلي تيليجرام يعرضه كـ GIF متحرك
            attributes = (attributes or []) + [DocumentAttributeAnimated()]

        upload_state = {
            "last_percent": -100,
            "last_edit_time": 0.0,
            "start": time.monotonic(),
        }

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
                    elapsed = now - upload_state["start"]
                    speed = current / elapsed if elapsed > 1 else None
                    eta = (total - current) / speed if speed and not is_done else None
                    asyncio.ensure_future(
                        safe_edit(
                            status,
                            f"📤 جاري الإرسال... {percent:.0f}%"
                            f"{progress_extra(speed, eta)}\n{url}",
                        )
                    )
            except RuntimeError:
                raise
            except Exception:
                logger.exception("خطأ داخل upload_progress")

        video_title = info.get("title", "")
        resolution_note = f"📐 {width}x{height}" if (width and height) else ""
        size_note = f"📦 {format_size(file_size)}"
        if as_gif or as_audio:
            caption = f"{video_title}\n{size_note}".strip()
        else:
            caption = f"{video_title}\n{resolution_note}  {size_note}".strip()

        await send_bot_file(
            event.chat_id,
            filename,
            caption=caption,
            supports_streaming=not as_audio,
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

    except UserFacingError as e:
        stats["failed_downloads"] += 1
        await safe_edit(status, f"⚠️ {e}\n{url}")
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
        if slot_held:
            job_slots.release()
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
    global SELF_ENTITY
    SELF_ENTITY = await client.get_me()
    is_premium = apply_account_limits(SELF_ENTITY)
    logger.info(
        f"نوع الحساب: {'Premium' if is_premium else 'عادي'} | أقصى حجم للملف: "
        f"{MAX_FILE_SIZE // (1024 * 1024)} ميجا | أقصى عمليات متزامنة: "
        f"{MAX_CONCURRENT_JOBS}"
    )
    if GROUP_CHAT_ID and not ALLOWED_USER_IDS:
        logger.warning(
            "GROUP_CHAT_ID مضبوط بدون ALLOWED_USER_IDS - أي عضو بالمجموعة "
            "يقدر يشغّل البوت. يُنصح بتحديد أرقامك بـ ALLOWED_USER_IDS."
        )
    if GROUP_CHAT_ID:
        logger.info(
            f"البوت (Telethon) يعمل الآن... أرسل رابطًا في Saved Messages "
            f"أو بالمجموعة الخاصة (GROUP_CHAT_ID={GROUP_CHAT_ID})"
        )
    else:
        logger.info("البوت (Telethon) يعمل الآن... أرسل رابطًا في Saved Messages")
    await client.run_until_disconnected()


if __name__ == "__main__":
    asyncio.run(main())
