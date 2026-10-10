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
  اختياري: لو ما ضبطته، أي عضو بالمجموعة الخاصة يقدر يشغّل البوت.
- MAX_CONCURRENT_JOBS: أقصى عدد عمليات (تحميل/تحويل) بنفس الوقت؛ الباقي
  ينتظر بالطابور (الافتراضي 2).
- MAX_FILE_MB: يفرض حد حجم الملف يدويًا. لو ما ضبطته، البوت يكتشف حسابك
  تلقائيًا: 2000 ميجا للحساب العادي و4000 ميجا لو Telegram Premium.
- GIF_MODE_TIMEOUT_MIN / GIF_MAX_SECONDS / GIF_MAX_INPUT_MB: إعدادات GIF.
- PREVIEW_MAX_SIDE / PREVIEW_MAX_INPUT_MB: حدود المعاينة (الباقي بالأوامر).

المعاينة (GIF يلخّص الفيديو من بدايته لنهايته بـ 4 مقاطع على الأقل):
- معاينة: قائمة الأوامر | تفعيل المعاينة / تعطيل المعاينة
- دقة المعاينة (5 مستويات) | مدة المعاينة (5-180 ثانية أو تلقائي)
- الرابط معاينة: المعاينة فقط بدون الفيديو
- الإعدادات تُحفظ بشكل دائم برسالة داخل Saved Messages (لا تحذفها).
- اختيار ذكي للمقاطع بـ FFmpeg: يتجنب اللقطات السوداء/الثابتة/المكررة
  (PREVIEW_SMART_PICK=0 يعطّله).

ترجمة كلام الفيديو للعربية (ملف SRT + فيديو بترجمة مدموجة، ملف translator.py):
- الرابط ترجمة: يحمّل الفيديو ويفرّغ كلامه ويترجمه (أي لغة ← عربي) بتوقيت مزامن.
- رد بكلمة ترجمة على أي فيديو بالمحادثة، أو أرسل فيديو ووصفه ترجمة.
- يحتاج GROQ_API_KEY (مجاني من console.groq.com). متغيرات اختيارية:
  TRANSLATE_MAX_MINUTES / TRANSLATE_MAX_INPUT_MB / TRANSLATE_BURN /
  TRANSLATE_BURN_HEIGHT / TRANSLATE_BURN_MAX_MINUTES / TRANSLATE_LLM_MODEL ...
"""

import asyncio
import base64
import collections
import glob
import json
import logging
import os
import sys
import re
import secrets
import shutil
import socket
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
from telethon.errors import FloodWaitError, MessageNotModifiedError
import yt_dlp

import translator

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


def _env_int(name: str, default: int, minimum: "int | None" = None) -> int:
    """يقرأ متغير بيئة رقمي بأمان: قيمة غير صالحة (أو أقل من الحد الأدنى)
    تُتجاهل مع تحذير بالسجلات ويُستخدم الافتراضي، بدل ما يتعطل البوت
    كله عند التشغيل بـ ValueError."""
    raw = os.environ.get(name, "").strip()
    if not raw:
        return default
    try:
        value = int(raw)
    except ValueError:
        logger.warning(f"قيمة {name} غير صالحة ({raw!r}) - استُخدم الافتراضي {default}")
        return default
    if minimum is not None and value < minimum:
        logger.warning(f"قيمة {name} أقل من الحد الأدنى {minimum} - استُخدم الافتراضي {default}")
        return default
    return value


API_ID = _env_int("API_ID", 0)
API_HASH = os.environ.get("API_HASH", "")
SESSION_STRING = os.environ.get("SESSION_STRING", "")
PORT = _env_int("PORT", 10000, 1)
COOKIES_B64 = os.environ.get("COOKIES_B64", "")

# أرقام المستخدمين (user id) المسموح لهم بتشغيل البوت من المجموعة الخاصة
# (اختياري). فاضي = أي عضو بالمجموعة يقدر يشغّل البوت (مناسب لمجموعة خاصة
# فيها أرقامك فقط).
ALLOWED_USER_IDS: set = set()
for _part in os.environ.get("ALLOWED_USER_IDS", "").replace(";", ",").split(","):
    _part = _part.strip()
    if not _part:
        continue
    try:
        ALLOWED_USER_IDS.add(int(_part))
    except ValueError:
        logging.getLogger(__name__).warning(f"رقم غير صالح بـ ALLOWED_USER_IDS: {_part}")

# معرّف مجموعة خاصة اختيارية (تضم حسابك اللي شغّل عليه البوت + أرقامك
# الثانية) - لو مضبوط، البوت يتعامل مع أي رابط يوصل بهذي المجموعة من
# أي رقم فيها بنفس طريقة Saved Messages.
# رقم صحيح فقط (مثل -1001234567890): القيم النصّية (username) لا تُدعم
# لأن مقارنتها مع event.chat_id ما تنجح أصلًا.
_group_env = os.environ.get("GROUP_CHAT_ID", "").strip()
GROUP_REQUESTED = bool(_group_env)
GROUP_CHAT_ID: "int | None" = None
if _group_env:
    try:
        GROUP_CHAT_ID = int(_group_env)
    except ValueError:
        logging.getLogger(__name__).error(
            "GROUP_CHAT_ID لازم يكون رقمًا صحيحًا (مثل -1001234567890) - "
            "تم تجاهله والمجموعة الخاصة معطّلة."
        )

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

URL_REGEX = re.compile(r"https?://\S+")
# رموز تحكم اتجاه النص (Bidi) اللي تيليجرام/لوحة المفاتيح تضيفها تلقائيًا
# غالبًا لما يختلط عربي وإنجليزي بنفس النص - غير مرئية لكنها تُنسخ فعليًا
# مع الرابط وتكسره لو انحطت بنص الرابط.
BIDI_CONTROL_CHARS = re.compile(
    "[\u200b\u200c\u200d\u200e\u200f\u061c\u202a-\u202e\u2066-\u2069]"
)
# علامات ترقيم شائعة تلتصق بنهاية الرابط بدون مسافة (قوس/تنصيص إغلاق،
# علامات عربية) ومو فعليًا جزء منه
TRAILING_URL_PUNCT = ".,!?؛،؟\u061f)]}»\u201d\u2019'"
QUALITY_REGEX = re.compile(r"\b(240|360|480|720|1080|1440|2160)\b")
# كلمة gif / جيف لوحدها (نبحث عنها بالنص بعد إزالة الروابط، عشان ما
# تتطابق مع رابط فيه كلمة gif مثل .../funny.gif)
GIF_REGEX = re.compile(r"(?i)(?<![\w])(gif|جيف)(?![\w])")
# كلمة معاينة / preview بعد الرابط → المعاينة فقط (بدون إرسال الفيديو)
PREVIEW_REGEX = re.compile(r"(?i)(?<![\w])(معاين[ةه]|preview)(?![\w])")
# كلمة mp3 / صوت / audio → تحميل الصوت فقط
AUDIO_REGEX = re.compile(r"(?i)(?<![\w])(mp3|audio|صوت)(?![\w])")
# كلمة ترجمة / translate → ترجمة كلام الفيديو للعربية (SRT + فيديو مترجم)
TRANSLATE_REGEX = re.compile(r"(?i)(?<![\w])(ترجم[ةه]?|translate)(?![\w])")
TRANSLATE_CMD_PATTERN = r"(?i)^(ترجم[ةه]?|translate)$"
TRANSLATE_ON_PATTERN = r"(?i)^(تفعيل|تشغيل|فعّل|فعل)\s+(ال)?ترجم[ةه]$"
TRANSLATE_OFF_PATTERN = r"(?i)^(تعطيل|ايقاف|إيقاف|وقف|عطّل|عطل)\s+(ال)?ترجم[ةه]$"
TRANSLATE_MENU_PATTERN = r"(?i)^((ال)?ترجم[ةه]\s+(ال)?حال[ةه]|حال[ةه]\s+(ال)?ترجم[ةه]|الترجم[ةه]|الترجمه)$"
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
GIF_MAX_SECONDS = _env_int("GIF_MAX_SECONDS", 30, 1)
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
GIF_MODE_TIMEOUT_MIN = _env_int("GIF_MODE_TIMEOUT_MIN", 15, 1)
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
GIF_MAX_INPUT_MB = _env_int("GIF_MAX_INPUT_MB", 200, 1)

# ===================== ميزة المعاينة (Preview) =====================
# معاينة = GIF قصير (mp4 صامت يعرضه تيليجرام كـ GIF) يلخّص الفيديو من بدايته
# لنهايته: نقتطع عدة مقاطع قصيرة موزّعة بالتساوي على طول الفيديو (أول مقطع
# من البداية وآخر مقطع ينتهي بنهاية الفيديو، ولا يقل عددها عن 4) ونلصقها
# بالترتيب بملف واحد.
# الإعدادات (التفعيل/الدقة/المدة) مستقلة تمامًا عن جودة الفيديو المختارة،
# وتُحفظ بشكل دائم بالرسالة المثبّتة بـ Saved Messages (راجع save_preview_settings).
PREVIEW_MIN_SECONDS = 5
PREVIEW_MAX_SECONDS = 180
PREVIEW_MIN_SEGMENTS = 4
PREVIEW_MAX_SEGMENTS = 24
PREVIEW_SEGMENT_TARGET = 2.5  # الطول المثالي للمقطع الواحد بالثواني
PREVIEW_MIN_SIDE = 240        # أقل طول للضلع الأطول (ما نصغّر أكثر من هذا)
PREVIEW_SEGMENT_TIMEOUT = 300  # مهلة ترميز المقطع الواحد (ثانية) - Render المجاني بطيء
PREVIEW_PROMPT_TTL = 120       # مهلة انتظار ردك على سؤال الدقة/المدة (ثانية)
try:
    PREVIEW_MAX_SIDE = max(PREVIEW_MIN_SIDE, int(os.environ.get("PREVIEW_MAX_SIDE", "1920")))
except ValueError:
    PREVIEW_MAX_SIDE = 1920
try:
    PREVIEW_MAX_INPUT_MB = int(os.environ.get("PREVIEW_MAX_INPUT_MB", "300"))
except ValueError:
    PREVIEW_MAX_INPUT_MB = 300

# --- اختيار مقاطع "نظيفة" (يتجنب الأسود/الثابت/المكرر) ---
# لكل مقطع مخطَّط، نحلّل عدة مواقع مرشّحة قريبة من موقعه المخطَّط بـ ffmpeg
# (إطارات رمادية مصغّرة 48x48 بدون صوت - سريع جدًا) ونختار أول موقع مقبول.
# لو ما لقينا مقبولًا نختار الأفضل المتاح (أفضل جهد، ما نفشل المعاينة أبدًا).
PREVIEW_SMART_PICK = os.environ.get("PREVIEW_SMART_PICK", "1").strip().lower() not in (
    "0", "false", "no", "off", "لا",
)
PREVIEW_PROBE_SIDE = 48          # أبعاد إطار التحليل (مربع رمادي)
PREVIEW_PROBE_FPS = 2            # إطارات بالثانية داخل نافذة التحليل
PREVIEW_PROBE_TIMEOUT = 25       # مهلة تحليل نافذة واحدة (ثانية)
PREVIEW_PROBE_BUDGET = 120       # أقصى وقت إجمالي للتحليل قبل الرجوع للمخطَّط
PREVIEW_MAX_CANDIDATES = 6       # أقصى مواقع مرشّحة لكل مقطع
PREVIEW_SHIFT_FRACTIONS = (0.0, 0.2, -0.2, 0.4, -0.4, 0.6)  # نسبة من المسافة بين المقاطع
PREVIEW_BLACK_LEVEL = 18         # متوسط السطوع (0-255) أقل منه = مظلم/أسود
PREVIEW_DARK_FRAC = 0.4          # نسبة إطارات مظلمة تُرفض عندها النافذة
PREVIEW_FLAT_STD = 6.0           # انحراف معياري أقل منه = لون مسطّح/شاشة عنوان
PREVIEW_STATIC_DIFF = 1.5        # متوسط فرق بين إطارين متتاليين أقل منه = ثابتة
PREVIEW_DUP_DIFF = 8.0           # فرق عن مقطع سابق أقل منه = مشهد مكرر

# مستويات الدقة: scale = نسبة من دقة الفيديو الأصلي (على حسب كل مقطع)،
# fps/crf = سلاسة وضغط الترميز. الأعلى دقة = دقة الفيديو نفسه (بحد
# PREVIEW_MAX_SIDE وبدون تكبير أبدًا).
PREVIEW_LEVELS = {
    1: {"name": "أعلى دقة (بدقة الفيديو نفسه)", "scale": 1.0, "fps": 24, "crf": 23},
    2: {"name": "دقة عالية", "scale": 0.75, "fps": 24, "crf": 24},
    3: {"name": "متوسطة", "scale": 0.5, "fps": 20, "crf": 26},
    4: {"name": "أقل من متوسطة", "scale": 0.35, "fps": 16, "crf": 28},
    5: {"name": "ضعيفة", "scale": 0.25, "fps": 12, "crf": 30},
}
# الإعدادات الحالية (تُحمَّل من الرسالة المحفوظة وقت التشغيل)
# translate = ترجمة تلقائية لكل فيديو (رابط أو مرسل) بدون كتابة كلمة ترجمة (أمر تفعيل الترجمة)
preview_settings = {"enabled": False, "level": 3, "seconds": 0, "translate": False}  # seconds=0 → تلقائي
preview_store_msg_id = None
PREVIEW_STORE_TAG = "#preview_settings"
# سؤال دقة/مدة مفتوح بانتظار ردك: chat_id -> {"kind": "level"|"seconds", "expires": ...}
pending_preview_prompts: dict = {}


def sanitize_preview_settings(data) -> dict:
    """ينظّف قاموس إعدادات (من الرسالة المحفوظة) لقيم صالحة فقط."""
    out = dict(preview_settings)
    if not isinstance(data, dict):
        return out
    if isinstance(data.get("enabled"), bool):
        out["enabled"] = data["enabled"]
    if isinstance(data.get("translate"), bool):
        out["translate"] = data["translate"]
    try:
        level = int(data.get("level", out["level"]))
        if level in PREVIEW_LEVELS:
            out["level"] = level
    except (TypeError, ValueError):
        pass
    try:
        seconds = int(data.get("seconds", out["seconds"]))
        if seconds == 0 or PREVIEW_MIN_SECONDS <= seconds <= PREVIEW_MAX_SECONDS:
            out["seconds"] = seconds
    except (TypeError, ValueError):
        pass
    return out


def auto_preview_seconds(duration: float) -> int:
    """مدة المعاينة التلقائية حسب طول الفيديو (من 20 ثانية إلى 3 دقائق):
    حتى دقيقتين → 20 ث | حتى 10 د → 30 ث | حتى 30 د → 45 ث |
    حتى ساعة → دقيقة | حتى ساعتين → دقيقتان | أكثر → 3 دقائق."""
    if duration <= 120:
        return 20
    if duration <= 600:
        return 30
    if duration <= 1800:
        return 45
    if duration <= 3600:
        return 60
    if duration <= 7200:
        return 120
    return 180


def plan_preview(duration: float, seconds_setting: int = 0):
    """يخطط مقاطع المعاينة: قائمة (بداية، طول) بالثواني، مرتبة من أول
    الفيديو لآخره وموزّعة بالتساوي. أول مقطع يبدأ من 0، وآخر مقطع ينتهي
    عند نهاية الفيديو. عدد المقاطع لا يقل عن 4 (ولا يزيد عن 24).
    لو الفيديو أقصر من مدة المعاينة نفسها، تكون المعاينة هي الفيديو كله
    (مقطع واحد). يرجّع None لو المدة مجهولة."""
    if not duration or duration <= 0:
        return None
    target = seconds_setting or auto_preview_seconds(duration)
    target = max(PREVIEW_MIN_SECONDS, min(PREVIEW_MAX_SECONDS, target))
    if duration <= target + 1:
        return [(0.0, round(float(duration), 2))]
    n = round(target / PREVIEW_SEGMENT_TARGET)
    n = max(PREVIEW_MIN_SEGMENTS, min(PREVIEW_MAX_SEGMENTS, n))
    seg = target / n
    step = (duration - seg) / (n - 1)
    last_start = max(0.0, duration - seg - 0.2)  # نترك هامش صغير قبل النهاية
    return [
        (round(min(i * step, last_start), 2), round(seg, 2)) for i in range(n)
    ]


def preview_scale_factor(level: int, long_side: int = 0, override=None) -> float:
    """نسبة تصغير المعاينة بالنسبة لدقة الملف المتوفر. لا تكبّر أبدًا،
    ولا تتجاوز PREVIEW_MAX_SIDE، ولا تصغّر الضلع الأطول لأقل من
    PREVIEW_MIN_SIDE (إلا لو الفيديو نفسه أصغر)."""
    factor = override if override else PREVIEW_LEVELS.get(level, PREVIEW_LEVELS[3])["scale"]
    factor = min(float(factor), 1.0)
    if long_side:
        factor = min(factor, PREVIEW_MAX_SIDE / long_side)
        factor = max(factor, min(1.0, PREVIEW_MIN_SIDE / long_side))
    return factor


def pick_preview_download(probe: dict, level: int):
    """لوضع \"المعاينة فقط\": نحدد أقل صيغة فيديو تكفي لدقة المعاينة
    المطلوبة (بدل تحميل أعلى جودة كاملة) توفيرًا للباندويدث.
    يرجّع (format_selector، نسبة التصغير بالنسبة للملف المُحمَّل)."""
    factor = PREVIEW_LEVELS.get(level, PREVIEW_LEVELS[3])["scale"]
    heights = sorted(probe.get("heights") or [], reverse=True)
    if not heights:
        return "bestvideo/best", None
    top = heights[0]
    wanted = top * factor
    candidates = [h for h in heights if h >= wanted]
    chosen = min(candidates) if candidates else top
    relative = min(1.0, wanted / chosen)
    return f"bestvideo[height<={chosen}]/best[height<={chosen}]/best", relative


def _remote_input_opts(path: str) -> list:
    """خيارات فحص أصغر لمصادر البث (http): ffmpeg بالافتراضي يقرأ عدة ميجا
    للفحص الأولي عند كل فتح، وهذا يضاعف البيانات المقروءة من تيليجرام."""
    if isinstance(path, str) and path.startswith("http"):
        return ["-probesize", "262144", "-analyzeduration", "500000"]
    return []


def _num(value, cast=float, default=0):
    try:
        return cast(value)
    except (TypeError, ValueError):
        return default


def probe_media(path: str) -> dict:
    """يقرأ أبعاد ومدة ملف عبر ffprobe (يرجّع {} لو فشل)."""
    try:
        result = subprocess.run(
            [
                "ffprobe", "-v", "error", *_remote_input_opts(path),
                "-select_streams", "v:0",
                "-show_entries", "stream=width,height:format=duration",
                "-of", "json", path,
            ],
            capture_output=True, timeout=30,
        )
        data = json.loads(result.stdout or b"{}")
        stream = (data.get("streams") or [{}])[0]
        fmt = data.get("format") or {}
        return {
            "width": _num(stream.get("width"), int),
            "height": _num(stream.get("height"), int),
            "duration": _num(fmt.get("duration"), float),
        }
    except Exception:
        logger.exception("تعذر قراءة بيانات الملف عبر ffprobe")
        return {}


def _run_ffmpeg(cmd: list, cancel_event, timeout: int, capture: bool = False):
    """يشغّل ffmpeg ويراقب الإلغاء (الغاء) والمهلة كل نصف ثانية.
    capture=True يرجّع مخرجات stdout (بايتات) - تُستخدم لتحليل الإطارات."""
    proc = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE if capture else subprocess.DEVNULL,
        stderr=subprocess.PIPE,
    )
    started = time.monotonic()
    while True:
        try:
            out, err = proc.communicate(timeout=0.5)
            break
        except subprocess.TimeoutExpired:
            if cancel_event is not None and cancel_event.is_set():
                proc.kill()
                proc.communicate()
                raise RuntimeError(CANCELLED_MARKER)
            if time.monotonic() - started > timeout:
                proc.kill()
                proc.communicate()
                raise RuntimeError("انتهت مهلة تجهيز المعاينة (السيرفر بطيء أو الفيديو ثقيل)")
    if proc.returncode != 0:
        raise RuntimeError(
            "فشل ffmpeg: " + (err or b"").decode("utf-8", "ignore")[-200:]
        )
    return out or b""


def analyze_window(filepath: str, start: float, length: float, cancel_event=None):
    """يحلّل نافذة زمنية من الفيديو بـ ffmpeg (إطارات رمادية 48x48 خام) ويرجّع
    قاموس مقاييس: bright (متوسط السطوع)، dark_frac (نسبة الإطارات المظلمة)،
    std (التباين داخل الإطار)، motion (الحركة بين الإطارات)، sig (إطار
    وسطي للمقارنة مع مقاطع ثانية). يرجّع None لو ما كفت الإطارات."""
    side = PREVIEW_PROBE_SIDE
    fsize = side * side
    out = _run_ffmpeg(
        [
            "ffmpeg", "-hide_banner", "-loglevel", "error",
            *_remote_input_opts(filepath),
            "-ss", f"{max(0.0, start):.2f}", "-i", filepath,
            "-t", f"{length:.2f}", "-an", "-sn",
            "-vf", f"fps={PREVIEW_PROBE_FPS},scale={side}:{side}:flags=area,format=gray",
            "-frames:v", "24", "-f", "rawvideo", "-pix_fmt", "gray", "-",
        ],
        cancel_event, PREVIEW_PROBE_TIMEOUT, capture=True,
    )
    frames = [out[i:i + fsize] for i in range(0, len(out) - fsize + 1, fsize)]
    if len(frames) < 3:
        return None
    n = len(frames)
    means = [sum(f) / fsize for f in frames]
    stds = [
        (sum((p - m) ** 2 for p in f) / fsize) ** 0.5 for f, m in zip(frames, means)
    ]
    diffs = [
        sum(abs(a - b) for a, b in zip(f1, f2)) / fsize
        for f1, f2 in zip(frames, frames[1:])
    ]
    return {
        "bright": sum(means) / n,
        "dark_frac": sum(1 for m in means if m < PREVIEW_BLACK_LEVEL) / n,
        "std": sum(stds) / n,
        "motion": sum(diffs) / len(diffs),
        "sig": frames[n // 2],
    }


def _sig_distance(a: bytes, b: bytes) -> float:
    return sum(abs(x - y) for x, y in zip(a, b)) / max(1, len(a))


def score_window(metrics: dict, prev_sigs: list):
    """يقيّم نافذة: يرجّع (ok، درجة). كل معيار بين 0 و1 (1 = ممتاز):
    سطوع (مو أسود)، تباين (مو لون مسطّح)، حركة (مو ثابتة)، واختلاف عن المقاطع
    المختارة قبلها (مو مكررة). ok = كل المعايير ممتازة. الدرجة (أضعف معيار،
    المجموع) تُستخدم لاختيار الأفضل لو ما فيه نافذة ok."""
    c_bright = min(1.0, metrics["bright"] / PREVIEW_BLACK_LEVEL)
    if metrics["dark_frac"] >= PREVIEW_DARK_FRAC:
        c_bright = min(c_bright, 0.5)
    c_flat = min(1.0, metrics["std"] / PREVIEW_FLAT_STD)
    c_motion = min(1.0, metrics["motion"] / PREVIEW_STATIC_DIFF)
    if prev_sigs:
        dist = min(_sig_distance(metrics["sig"], p) for p in prev_sigs)
        c_dup = min(1.0, dist / PREVIEW_DUP_DIFF)
    else:
        c_dup = 1.0
    parts = (c_bright, c_flat, c_motion, c_dup)
    return min(parts) >= 1.0, (min(parts), sum(parts))


def pick_clean_segments(
    filepath: str, segments: list, duration: float, cancel_event=None, progress=None
):
    """يعدّل مواقع بداية المقاطع المخطَّطة لتجنّب اللقطات السوداء/الثابتة/
    المكررة. لكل مقطع نجرّب مواقع مرشّحة قريبة من موقعه (الأصلي أول) ضمن
    حدود تحافظ على الترتيب وعدم التداخل، ونأخذ أول موقع مقبول (أو الأفضل لو
    ما فيه). طول كل مقطع ما يتغير. يرجّع (المقاطع الجديدة، عدد المعدّلة)."""
    n = len(segments)
    if n < 2 or duration <= 0:
        return segments, 0
    deadline = time.monotonic() + PREVIEW_PROBE_BUDGET
    chosen, sigs, adjusted = [], [], 0
    consecutive_fails = 0
    # مع المعاينات الطويلة (مقاطع كثيرة) نقلّل المرشّحين لكل مقطع عشان وقت
    # التحليل ما يتضاعف على السيرفر الضعيف
    max_cands = PREVIEW_MAX_CANDIDATES if n <= 12 else 3
    fractions = PREVIEW_SHIFT_FRACTIONS[:max_cands]

    for i, (start, length) in enumerate(segments):
        step = (segments[i + 1][0] - start) if i + 1 < n else (start - segments[i - 1][0])
        lo = (chosen[-1][0] + chosen[-1][1] + 0.1) if chosen else 0.0
        hi = (segments[i + 1][0] - length - 0.1) if i + 1 < n else (duration - length - 0.2)
        hi = max(hi, lo)
        cands = []
        for frac in fractions:
            cand = round(min(max(start + frac * step, lo), hi), 2)
            if all(abs(cand - c) > 0.4 for c in cands):
                cands.append(cand)

        best = None  # (درجة، موقع، مقاييس)
        for cand in cands:
            if cancel_event is not None and cancel_event.is_set():
                raise RuntimeError(CANCELLED_MARKER)
            if time.monotonic() > deadline:
                break
            try:
                metrics = analyze_window(filepath, cand, length, cancel_event)
            except RuntimeError as e:
                if str(e) == CANCELLED_MARKER:
                    raise
                logger.warning(f"تعذر تحليل نافذة المعاينة عند {cand}s: {str(e)[:120]}")
                consecutive_fails += 1
                if consecutive_fails >= 3:
                    # الملف غالبًا غير قابل للتحليل - ما نكرر عشرات المحاولات
                    raise RuntimeError("تكرر فشل تحليل المعاينة")
                continue
            if metrics is None:
                continue
            consecutive_fails = 0
            ok, score = score_window(metrics, sigs)
            if best is None or score > best[0]:
                best = (score, cand, metrics)
            if ok:
                break

        pick = best[1] if best else cands[0]
        if best:
            sigs.append(best[2]["sig"])
        if abs(pick - start) > 0.05:
            adjusted += 1
        chosen.append((pick, length))
        if progress:
            progress(i + 1, n)
    return chosen, adjusted


def make_preview(
    filepath: str,
    level: int,
    seconds_setting: int = 0,
    duration_hint: float = 0,
    scale_override=None,
    cancel_event=None,
    progress=None,
    work_dir=None,
    smart=None,
):
    """يبني المعاينة: يرمّز كل مقطع بنفسه (بحث سريع -ss قبل -i، ومقطع واحد
    بالمرة = ذاكرة قليلة تناسب Render المجاني) ثم يلصقها بالترتيب بدون
    إعادة ترميز. يرجّع قاموسًا: path/width/height/duration/segments/size.
    progress(i, n) اختياري لتحديث النسبة."""
    info = probe_media(filepath)
    duration = info.get("duration") or duration_hint or 0
    segments = plan_preview(duration, seconds_setting)
    if not segments:
        raise RuntimeError("ما قدرت أعرف مدة الفيديو لتجهيز المعاينة")

    # اختيار ذكي: تجنّب اللقطات السوداء/الثابتة/المكررة (فشله لا يمنع المعاينة)
    smart_allowed = PREVIEW_SMART_PICK if smart is None else smart
    smart_on = smart_allowed and len(segments) > 1
    analysis_steps = len(segments) if smart_on else 0
    total_steps = analysis_steps + len(segments)
    adjusted = 0
    if smart_on:
        try:
            segments, adjusted = pick_clean_segments(
                filepath, segments, duration, cancel_event,
                (lambda i, n: progress(i, total_steps)) if progress else None,
            )
            logger.info(f"اختيار المعاينة الذكي: عُدّل {adjusted} من {len(segments)} مقطع")
        except RuntimeError as e:
            if str(e) == CANCELLED_MARKER:
                raise
            logger.warning(f"تخطّينا الاختيار الذكي للمعاينة: {e}")
        except Exception:
            logger.exception("خطأ بالاختيار الذكي للمعاينة - استُخدمت المواقع المخطَّطة")

    long_side = max(info.get("width", 0), info.get("height", 0))
    factor = preview_scale_factor(level, long_side, scale_override)
    params = PREVIEW_LEVELS.get(level, PREVIEW_LEVELS[3])
    # scale بالنسبة المئوية من أبعاد الإطار الفعلية (يشتغل صح مع الفيديو
    # العمودي/المدوّر) مع جعل الأبعاد زوجية (شرط H.264)
    vf = (
        f"fps={params['fps']},"
        f"scale=w='trunc(iw*{factor:.4f}/2)*2':h='trunc(ih*{factor:.4f}/2)*2',"
        "setsar=1"
    )
    # filepath ممكن يكون رابط بث محلي (http://127.0.0.1...) فنحتاج مجلد عمل صريح
    work_dir = work_dir or os.path.dirname(os.path.abspath(filepath))
    seg_paths = [os.path.join(work_dir, f"_pv_{i}.mp4") for i in range(len(segments))]
    out_path = os.path.join(work_dir, "_preview.mp4")
    list_path = os.path.join(work_dir, "_pv_list.txt")

    try:
        for i, (start, length) in enumerate(segments):
            _run_ffmpeg(
                [
                    "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
                    *_remote_input_opts(filepath),
                    "-ss", f"{start:.2f}", "-i", filepath,
                    "-t", f"{length:.2f}", "-an", "-vf", vf,
                    "-c:v", "libx264", "-preset", "veryfast",
                    "-crf", str(params["crf"]), "-pix_fmt", "yuv420p",
                    seg_paths[i],
                ],
                cancel_event, PREVIEW_SEGMENT_TIMEOUT,
            )
            if not os.path.exists(seg_paths[i]) or os.path.getsize(seg_paths[i]) == 0:
                raise RuntimeError("تعذر استخراج أحد مقاطع المعاينة")
            if progress:
                progress(analysis_steps + i + 1, total_steps)

        if len(seg_paths) == 1:
            os.replace(seg_paths[0], out_path)
        else:
            with open(list_path, "w", encoding="utf-8") as f:
                for sp in seg_paths:
                    f.write(f"file '{sp}'\n")
            _run_ffmpeg(
                [
                    "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
                    "-f", "concat", "-safe", "0", "-i", list_path,
                    "-c", "copy", "-movflags", "+faststart", out_path,
                ],
                cancel_event, 120,
            )
    finally:
        for sp in seg_paths + [list_path]:
            try:
                os.remove(sp)
            except OSError:
                pass

    if not os.path.exists(out_path) or os.path.getsize(out_path) == 0:
        raise RuntimeError("المعاينة الناتجة فاضية")
    out_info = probe_media(out_path)
    return {
        "path": out_path,
        "width": out_info.get("width") or 0,
        "height": out_info.get("height") or 0,
        "duration": out_info.get("duration") or sum(l for _, l in segments),
        "segments": len(segments),
        "adjusted": adjusted,
        "size": os.path.getsize(out_path),
    }


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
        # لو حددت ALLOWED_USER_IDS، فقط هذي الأرقام تقدر تشغّل البوت،
        # وإلا أي عضو بالمجموعة الخاصة مقبول
        if ALLOWED_USER_IDS and getattr(event, "sender_id", None) not in ALLOWED_USER_IDS:
            return False
        return True
    return False


def clean_url(url: str) -> str:
    """ينظّف الرابط المُكتشف من رموز التحكم الاتجاهي المخفية (تسبب عدم
    التعرف على الرابط أو فشل التحميل بصمت لما يختلط عربي/إنجليزي)، ويشيل
    أي علامة ترقيم ملتصقة بنهايته (قوس إغلاق، نقطة، فاصلة عربية...) مو
    فعليًا جزء من الرابط."""
    url = BIDI_CONTROL_CHARS.sub("", url)
    return url.rstrip(TRAILING_URL_PUNCT)


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
    # نخلي Telethon ينتظر تلقائيًا لو FloodWait قصير (≤60 ثانية - الافتراضي).
    # هذا ضروري لرفع الملفات الكبيرة: بدونه أي Flood قصير بين أجزاء الرفع
    # كان يفشل العملية كلها بعد ما ينتهي التحميل. تعديلات رسالة الحالة
    # تحميها safe_edit بمهلة قصيرة (ما تعطّل الرفع)، والانتظار الأطول من
    # 60 ثانية يوصل لكودنا ونتعامل معه عبر safe_*.
    flood_sleep_threshold=60,
)

# قائمة العمليات الجارية حاليًا (تحميل/إرسال) - كل عملية عندها
# threading.Event خاص فيها، لو انضبط (set) نوقف التحميل من داخل
# progress_hook مباشرة. بما إن الاستخدام شخصي (حساب واحد بس)، قائمة
# بسيطة كافية بدون تعقيد إضافي.
active_operations = []
# آخر 10 عمليات انتهت (نجاح/فشل/إلغاء) مع توقيت الانتهاء - يخلي أمر
# "حالة" يقدر يجاوب "خلصت/فشلت" حتى بعد ما تختفي من active_operations،
# بدل ما يبين وكأنه ما فيه فرق بين "خلص بنجاح" و"فشل بصمت".
recent_operations = collections.deque(maxlen=10)


def record_finished(op: dict, outcome: str, detail: str = ""):
    """يسجّل نتيجة عملية انتهت بـ recent_operations. outcome: "done"
    (نجحت وأُرسلت) / "failed" (خطأ) / "cancelled" (ألغاها المستخدم)."""
    recent_operations.append({
        "url": op.get("url", "؟"),
        "outcome": outcome,
        "detail": detail,
        "finished_at": time.monotonic(),
    })
CANCELLED_MARKER = "USER_CANCELLED_OPERATION"
assert translator.CANCELLED_MARKER == CANCELLED_MARKER  # نفس علامة الإلغاء بالوحدتين

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


def _thumb_frame_quality(filepath: str, t: float):
    """يقيّم إطارًا واحدًا عند الزمن t بـ ffmpeg (رمادي 48x48 خام): يرجّع
    (متوسط السطوع، التباين) أو None لو تعذر."""
    side = PREVIEW_PROBE_SIDE
    out = _run_ffmpeg(
        [
            "ffmpeg", "-hide_banner", "-loglevel", "error",
            "-ss", f"{max(0.0, t):.2f}", "-i", filepath, "-an", "-sn",
            "-frames:v", "1", "-vf", f"scale={side}:{side}:flags=area,format=gray",
            "-f", "rawvideo", "-pix_fmt", "gray", "-",
        ],
        None, 15, capture=True,
    )
    if len(out) < side * side:
        return None
    px = out[: side * side]
    mean = sum(px) / len(px)
    std = (sum((p - mean) ** 2 for p in px) / len(px)) ** 0.5
    return mean, std


def pick_thumbnail_time(filepath: str, duration: float = 0) -> float:
    """يختار زمن صورة مصغّرة "حيّة" (مو سوداء ولا لون مسطّح): يجرّب الثانية 1
    ثم نقاطًا موزّعة (10%/25%/50%/75%) ويأخذ أول إطار مقبول، أو الأفضل لو
    ما فيه. أي خطأ → الثانية 1 (السلوك القديم)."""
    try:
        if not duration:
            duration = probe_media(filepath).get("duration") or 0
        times = [1.0]
        if duration > 0:
            times = [min(1.0, duration * 0.1)] + [duration * f for f in (0.1, 0.25, 0.5, 0.75)]
        uniq = []
        for t in times:
            t = round(max(0.0, min(t, max(0.0, duration - 0.3))) if duration > 0 else t, 2)
            if all(abs(t - u) > 0.5 for u in uniq):
                uniq.append(t)
        best = None
        for t in uniq:
            q = _thumb_frame_quality(filepath, t)
            if q is None:
                continue
            mean, std = q
            score = (min(1.0, mean / PREVIEW_BLACK_LEVEL), min(1.0, std / PREVIEW_FLAT_STD), std)
            if best is None or score > best[0]:
                best = (score, t)
            if score[0] >= 1.0 and score[1] >= 1.0:
                return t
        return best[1] if best else 1.0
    except Exception:
        logger.warning("تعذر اختيار زمن الصورة المصغّرة - سنستخدم الثانية 1")
        return 1.0


def generate_thumbnail(filepath: str, duration: float = 0):
    """يولّد صورة مصغّرة (thumbnail) عبر ffmpeg: يختار إطارًا غير أسود/مسطّح
    (pick_thumbnail_time) ثم يستخرجه بـ -ss قبل -i (بحث سريع بدون فك تشفير
    كل ما قبله). أي فشل يرجّع None والإرسال يكمل بدون صورة."""
    thumb_path = filepath + "_thumb.jpg"
    try:
        t = pick_thumbnail_time(filepath, duration)
        subprocess.run(
            [
                "ffmpeg", "-y",
                "-ss", f"{t:.2f}",    # بحث سريع قبل فتح الملف
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

    # حماية ضد الروبوتات (Cloudflare وأمثاله) - يصعب تجاوزها آليًا وبشكل
    # عام ما نحاول، فنوضح للمستخدم السبب بدل تكرار المحاولة بلا فائدة
    bot_protection_signals = [
        "cloudflare", "unusual traffic", "verify you are human", "captcha",
        "just a moment", "attention required", "access denied", "403: forbidden",
        "forbidden",
    ]
    if any(sig in msg for sig in bot_protection_signals):
        return (
            "🛡️ هذا الموقع يستخدم حماية ضد الروبوتات (Cloudflare أو مشابه) "
            "يصعب تجاوزها آليًا. جرّب رابط من موقع ثاني أو حمّله يدويًا "
            "بالمتصفح."
        )

    # مشاكل شبكة/سيرفر مؤقتة (بطء، ازدحام، حظر مؤقت) - غالبًا تُحل بمجرد
    # إعادة المحاولة بعد شوي، عكس الحالات الدائمة أعلاه
    transient_signals = [
        "timed out", "timeout", "connection reset", "connection aborted",
        "temporary failure", "try again", "503", "502", "504",
        "too many requests", "429", "connection refused", "read timed out",
    ]
    if any(sig in msg for sig in transient_signals):
        return (
            "⏳ مشكلة مؤقتة من طرف السيرفر (بطيء أو مزدحم حاليًا) - جرّب "
            "إرسال نفس الرابط بعد شوي."
        )

    # أي خطأ ثاني غير معروف: نعرض جزء مختصر بدل النص التقني الكامل
    return f"❌ تعذّر التحميل لسبب غير معروف. (تفاصيل مختصرة: {raw_error[:150]})"


async def safe_edit(status_msg, text: str):
    """يعدّل رسالة الحالة، ويتجاهل أخطاء FloodWaitError (تيلجرام يحد
    عدد التعديلات المسموحة بفترة قصيرة) بدل ما يفشل العملية كلها.
    لو status_msg نفسها None (مثلاً safe_respond فشلت بإنشائها أصلًا
    بسبب ازدحام)، نتجاهل بصمت بدل كسر الكود بخطأ AttributeError."""
    if status_msg is None:
        return
    try:
        # مهلة قصيرة: لو تيليجرام طلب انتظار (Flood) نتنازل عن هذا التحديث
        # بدل ما يتكدّس (التحديث التالي يعوّضه) ولا يعطّل العملية.
        await asyncio.wait_for(status_msg.edit(text), timeout=15)
    except asyncio.TimeoutError:
        logger.warning("تعديل رسالة الحالة تأخر (على الأرجح Flood) - تجاهلناه")
    except FloodWaitError as e:
        logger.warning(f"FloodWaitError عند تعديل الرسالة - تجاهلناها ({e.seconds}s)")
    except Exception:
        logger.exception("خطأ غير متوقع أثناء تعديل الرسالة")


async def safe_send(chat_id, text: str):
    """نفس فكرة safe_respond بالضبط، لكن لمواضع ما عندها event (مثل
    قائمة اختيار الجودة أو جواب رقم غير صالح) وتحتاج ترسل بمعرّف
    المحادثة (chat_id) مباشرة عبر client.send_message."""
    try:
        return await client.send_message(chat_id, text)
    except FloodWaitError as e:
        logger.warning(f"FloodWaitError عند الإرسال - {e.seconds}s")
        if e.seconds <= 60:
            await asyncio.sleep(e.seconds + 1)
            try:
                return await client.send_message(chat_id, text)
            except Exception:
                logger.exception("فشل الإرسال حتى بعد الانتظار")
                return None
        return None
    except Exception:
        logger.exception("خطأ غير متوقع أثناء الإرسال")
        return None


async def safe_respond(event, text: str = ""):
    """إرسال رسالة جديدة (event.respond) مع تحمّل FloodWaitError بدل ما
    يكسر المعالج (handler) بالكامل بصمت.

    قبل هذا الإصلاح: أي FloodWaitError من event.respond() مباشر (مو
    بالتعديل) كان يطلع كـ "Unhandled exception" بسجلات Render ويوقف
    المعالج قبل ما يرد على المستخدم - يعطي انطباع إن البوت "علّق" أو
    توقف عن الرد تمامًا، رغم إنه شغّال فعليًا وبس مزدحم مؤقتًا.

    لو الانتظار المطلوب قصير (≤60 ثانية) ننتظر ونعيد المحاولة مرة وحدة؛
    غير كذا نتنازل ونسجل بالسجلات (الانتظار الطويل يعني تجاهل هذا الرد
    أفضل من تجميد المحادثة بالكامل). يرجّع الرسالة المُرسلة، أو None لو
    فشل الإرسال نهائيًا (المستدعي اللي يحتاج .edit() لازم يتحقق من None
    أول - استخدم safe_edit() اللي أصلًا يتحمّل None بأمان لو زودناها)."""
    try:
        return await event.respond(text)
    except FloodWaitError as e:
        logger.warning(f"FloodWaitError عند الرد - {e.seconds}s")
        if e.seconds <= 60:
            await asyncio.sleep(e.seconds + 1)
            try:
                return await event.respond(text)
            except Exception:
                logger.exception("فشل الرد حتى بعد الانتظار")
                return None
        return None
    except Exception:
        logger.exception("خطأ غير متوقع أثناء الرد")
        return None


# ===================== معاينة بدون تنزيل كامل (بث بالأجزاء) =====================
# بدل ما ننزّل الفيديو المرسل كاملًا من تيليجرام لسيرفر Render ثم نقص منه
# المعاينة، نشغّل سيرفر HTTP محلي صغير (127.0.0.1 فقط، غير مكشوف للخارج)
# يمرّر لـ ffmpeg الفيديو على شكل أجزاء عند الطلب (HTTP Range) عبر
# client.iter_download. ffmpeg يقفز لمواضع المقاطع ويقرأ منها فقط، فنوفّر
# الوقت والبيانات (خصوصًا بالفيديوهات الطويلة). لو فشل البث لأي سبب نرجع
# تلقائيًا للتنزيل الكامل.
PREVIEW_STREAM = os.environ.get("PREVIEW_STREAM", "1").strip().lower() not in (
    "0", "false", "no", "off", "لا",
)
# الملفات الأصغر من هذا الحد (ميجا) تُنزَّل كاملة (أسرع وأبسط من البث)
PREVIEW_STREAM_MIN_MB = _env_int("PREVIEW_STREAM_MIN_MB", 50, 0)
# الاختيار الذكي يحلّل نوافذ كثيرة (كل نافذة تقرأ بيانات)، فمع البث يكون
# معطّلًا افتراضيًا لتوفير القراءة. فعّله بـ PREVIEW_STREAM_SMART=1
PREVIEW_STREAM_SMART = os.environ.get("PREVIEW_STREAM_SMART", "0").strip().lower() in (
    "1", "true", "yes", "on", "نعم",
)
STREAM_REQUEST_SIZE = 256 * 1024  # يقبل القسمة على 4096 (شرط تيليجرام)
# ffmpeg يفتح الرابط من جديد لكل مقطع ويعيد قراءة ترويسة الملف (بداية الملف،
# أو نهايته لو فهرس moov بالآخر) - نخزّنها بالذاكرة (أول/آخر ميجا فقط)
STREAM_CACHE_EDGE = 1024 * 1024
stream_sources: dict = {}  # token -> {"doc", "size", "mime", "fetched"}
STREAM_PORT = None
_stream_server = None


def register_stream_source(doc) -> str:
    """يسجّل ملف تيليجرام (Document) للبث المحلي ويرجّع رمزًا عشوائيًا."""
    token = secrets.token_urlsafe(16)
    stream_sources[token] = {
        "doc": doc,
        "size": int(doc.size),
        "mime": getattr(doc, "mime_type", None) or "video/mp4",
        "fetched": 0,
        "cache": {},
    }
    return token


def parse_http_range(value, size: int):
    """يحلّل ترويسة Range. يرجّع (بداية، نهاية) شاملة، أو None لو غير صالح.
    بدون ترويسة → الملف كله."""
    if not value:
        return 0, size - 1
    m = re.match(r"(?i)^\s*bytes=(\d*)-(\d*)\s*$", value)
    if not m or (not m.group(1) and not m.group(2)):
        return None
    if m.group(1):
        start = int(m.group(1))
        end = min(int(m.group(2)), size - 1) if m.group(2) else size - 1
    else:  # bytes=-N → آخر N بايت
        start = max(0, size - int(m.group(2)))
        end = size - 1
    if start >= size or start > end:
        return None
    return start, end


async def _iter_source(src, offset: int):
    """يعطي أجزاء الملف ابتداءً من offset (محاذي لحجم الطلب): أول/آخر ميجا من
    الكاش لو موجود، والباقي من تيليجرام. src["fetched"] يعدّ فقط ما نزل فعليًا."""
    size, cache = src["size"], src["cache"]
    while offset < size and offset in cache:
        chunk = cache[offset]
        offset += len(chunk)
        yield chunk
    if offset >= size:
        return
    it = client.iter_download(
        src["doc"], offset=offset, request_size=STREAM_REQUEST_SIZE, file_size=size
    )
    try:
        async for chunk in it:
            if offset < STREAM_CACHE_EDGE or offset + len(chunk) > size - STREAM_CACHE_EDGE:
                cache[offset] = chunk
            offset += len(chunk)
            src["fetched"] += len(chunk)
            yield chunk
    finally:
        try:
            await it.close()
        except Exception:
            pass


async def _stream_handle(reader, writer):
    """يخدم طلب GET/HEAD واحد لملف تيليجرام مسجّل، مع دعم Range."""
    async def reply(status_line: str, extra: str = ""):
        writer.write(
            f"HTTP/1.1 {status_line}\r\n{extra}Connection: close\r\n\r\n".encode("latin-1")
        )
        await writer.drain()

    try:
        request_line = await asyncio.wait_for(reader.readline(), 15)
        parts = request_line.decode("latin-1").split()
        if len(parts) < 2:
            return
        method, path = parts[0].upper(), parts[1]
        headers = {}
        while True:
            line = await asyncio.wait_for(reader.readline(), 15)
            if line in (b"\r\n", b"\n", b""):
                break
            key, _, val = line.decode("latin-1").partition(":")
            headers[key.strip().lower()] = val.strip()

        src = None
        if path.startswith("/tg/") and method in ("GET", "HEAD"):
            src = stream_sources.get(path[4:].split("?")[0])
        if src is None:
            await reply("404 Not Found", "Content-Length: 0\r\n")
            return

        size = src["size"]
        rng = parse_http_range(headers.get("range"), size)
        if rng is None:
            await reply("416 Range Not Satisfiable",
                        f"Content-Range: bytes */{size}\r\nContent-Length: 0\r\n")
            return
        start, end = rng
        partial = "range" in headers
        head = (
            f"Content-Type: {src['mime']}\r\nAccept-Ranges: bytes\r\n"
            f"Content-Length: {end - start + 1}\r\n"
        )
        if partial:
            head += f"Content-Range: bytes {start}-{end}/{size}\r\n"
        await reply("206 Partial Content" if partial else "200 OK", head)
        if method == "HEAD":
            return

        # نقلّل القراءة المسبقة: لو المخازن (buffers) كبيرة نسحب من تيليجرام
        # ميجابايتات قبل ما ffmpeg يطلبها، وغالبًا يقفز بعدها لمقطع ثاني
        # ويرميها. نحدّد مخزن الإرسال ومخزن الكتابة بحجم صغير.
        try:
            sock = writer.get_extra_info("socket")
            if sock is not None:
                sock.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 32 * 1024)
            writer.transport.set_write_buffer_limits(high=32 * 1024, low=8 * 1024)
        except Exception:
            pass

        # تيليجرام يشترط أن يكون offset من مضاعفات حجم الطلب - نبدأ من أقرب
        # حد سابق ونتجاوز البايتات الزايدة بأول جزء
        aligned = start - (start % STREAM_REQUEST_SIZE)
        skip = start - aligned
        remaining = end - start + 1
        it = _iter_source(src, aligned)
        try:
            async for chunk in it:
                if skip:
                    chunk, skip = chunk[skip:], 0
                if len(chunk) > remaining:
                    chunk = chunk[:remaining]
                writer.write(chunk)
                await writer.drain()
                remaining -= len(chunk)
                if remaining <= 0:
                    break
        finally:
            await it.aclose()
    except (ConnectionError, asyncio.TimeoutError):
        pass  # ffmpeg قطع الاتصال (طبيعي: قفز لموضع ثاني أو انتهى)
    except asyncio.CancelledError:
        raise
    except Exception:
        logger.exception("خطأ ببث الفيديو المحلي للمعاينة")
    finally:
        try:
            writer.close()
        except Exception:
            pass


async def start_stream_server():
    """يشغّل سيرفر البث المحلي على 127.0.0.1 ومنفذ عشوائي حر."""
    global STREAM_PORT, _stream_server
    _stream_server = await asyncio.start_server(_stream_handle, "127.0.0.1", 0)
    STREAM_PORT = _stream_server.sockets[0].getsockname()[1]
    logger.info(f"سيرفر بث المعاينة المحلي يعمل على 127.0.0.1:{STREAM_PORT}")


# ===================== المعاينة: الحفظ الدائم والإرسال والأوامر =====================
def _preview_store_text() -> str:
    return (
        "⚙️ إعدادات المعاينة والترجمة - لا تحذف هذي الرسالة (البوت يحفظ فيها إعداداتك "
        f"عشان ما تضيع مع إعادة التشغيل) {PREVIEW_STORE_TAG}\n"
        + json.dumps(preview_settings, ensure_ascii=False)
    )


def parse_preview_store_text(text: str):
    """يستخرج قاموس الإعدادات من نص الرسالة المحفوظة (أو None)."""
    if not text or PREVIEW_STORE_TAG not in text:
        return None
    start = text.find("{", text.find(PREVIEW_STORE_TAG))
    end = text.rfind("}")
    if start == -1 or end <= start:
        return None
    try:
        return json.loads(text[start:end + 1])
    except ValueError:
        return None


async def load_preview_settings():
    """وقت التشغيل: يدوّر على رسالة الإعدادات المحفوظة بـ Saved Messages
    ويطبّقها. Render المجاني يمسح ملفات السيرفر مع كل إعادة تشغيل، فنحفظ
    الإعدادات بتيليجرام نفسه عشان تبقى دائمة."""
    global preview_store_msg_id
    try:
        found = None
        async for m in client.iter_messages("me", search=PREVIEW_STORE_TAG, limit=10):
            if m.out and PREVIEW_STORE_TAG in (m.raw_text or ""):
                found = m
                break
        if found is None:  # احتياط: البحث بالهاشتاغ أحيانًا ما يرجّع نتيجة
            async for m in client.iter_messages("me", limit=100):
                if m.out and PREVIEW_STORE_TAG in (m.raw_text or ""):
                    found = m
                    break
        if found is None:
            logger.info("ما فيه إعدادات معاينة محفوظة - نستخدم الافتراضي")
            return
        parsed = parse_preview_store_text(found.raw_text)
        if parsed is not None:
            preview_settings.update(sanitize_preview_settings(parsed))
            preview_store_msg_id = found.id
            logger.info(f"إعدادات المعاينة المحمّلة: {preview_settings}")
    except Exception:
        logger.exception("تعذر تحميل إعدادات المعاينة المحفوظة - نستخدم الافتراضي")


async def save_preview_settings() -> bool:
    """يحفظ الإعدادات الحالية بالرسالة المحفوظة (يعدّلها، أو ينشئها أول مرة).
    يرجّع True لو انحفظت."""
    global preview_store_msg_id
    text = _preview_store_text()
    try:
        if preview_store_msg_id:
            try:
                await client.edit_message("me", preview_store_msg_id, text)
                return True
            except MessageNotModifiedError:
                return True
            except Exception:
                logger.warning("تعذر تعديل رسالة الإعدادات (يمكن انحذفت) - ننشئ جديدة")
                preview_store_msg_id = None
        msg = await client.send_message("me", text)
        preview_store_msg_id = msg.id
        bot_sent_ids.append((msg.chat_id, msg.id))
        return True
    except FloodWaitError as e:
        logger.warning(f"FloodWaitError عند حفظ إعدادات المعاينة ({e.seconds}s)")
        return False
    except Exception:
        logger.exception("تعذر حفظ إعدادات المعاينة")
        return False


async def build_and_send_preview(
    chat_id,
    src_path: str,
    title: str,
    operation: dict,
    cancel_event,
    duration_hint: float = 0,
    scale_override=None,
    reply_to=None,
    work_dir=None,
    smart=None,
    stream_token=None,
):
    """يبني المعاينة من الملف ويرسلها (كـ GIF متحرك) للمحادثة. يرفع
    RuntimeError(CANCELLED_MARKER) لو ألغى المستخدم."""
    previous_stage = operation.get("stage")
    operation["stage"] = "converting"
    operation["percent"] = 0.0

    def on_progress(done: int, total: int):
        operation["percent"] = done / total * 100

    result = await asyncio.to_thread(
        make_preview,
        src_path,
        preview_settings["level"],
        preview_settings["seconds"],
        duration_hint,
        scale_override,
        cancel_event,
        on_progress,
        work_dir,
        smart,
    )
    thumb_path = await asyncio.to_thread(generate_thumbnail, result["path"])
    head = f"🖼️ معاينة — {title[:200]}" if title else "🖼️ معاينة"
    caption = (
        f"{head}\n🎬 {result['segments']} مقاطع · ⏱️ {int(round(result['duration']))} ثانية"
        f" · 📐 {result['width']}x{result['height']} · 📦 {format_size(result['size'])}"
    )
    if stream_token and stream_token in stream_sources:
        s = stream_sources[stream_token]
        caption += (
            f"\n📥 قُرئ من تيليجرام {format_size(s['fetched'])} من "
            f"{format_size(s['size'])} (بدون تنزيل كامل)"
        )
    operation["stage"] = "uploading"
    await send_bot_file(
        chat_id,
        result["path"],
        caption=caption,
        reply_to=reply_to,
        supports_streaming=True,
        thumb=thumb_path,
        attributes=[
            DocumentAttributeVideo(
                duration=int(round(result["duration"])),
                w=result["width"] or 640,
                h=result["height"] or 360,
                supports_streaming=True,
            ),
            DocumentAttributeAnimated(),
        ],
    )
    stats["total_bytes_sent"] += result["size"]
    operation["stage"] = previous_stage
    return result


def build_preview_menu_text() -> str:
    level = preview_settings["level"]
    seconds = preview_settings["seconds"]
    state = "مفعّلة ✅" if preview_settings["enabled"] else "معطّلة ⛔"
    duration_line = (
        "تلقائية (من 20 ثانية إلى 3 دقائق حسب طول الفيديو)" if not seconds else f"{seconds} ثانية"
    )
    return (
        "🖼️ **المعاينة** — GIF مختصر يلخّص الفيديو من بدايته لنهايته "
        f"(لا يقل عن {PREVIEW_MIN_SEGMENTS} مقاطع بالترتيب)\n\n"
        f"• الحالة: {state}\n"
        f"• الدقة: {level} — {PREVIEW_LEVELS[level]['name']}\n"
        f"• المدة: {duration_line}\n\n"
        "**الأوامر:**\n"
        "• `تفعيل المعاينة` → ترسل لك معاينة مع كل فيديو يتحمّل، ومعاينة لأي "
        "فيديو ترسله للبوت\n"
        "• `تعطيل المعاينة` → إيقاف الميزة\n"
        "• `دقة المعاينة` → اختيار الدقة (أو مباشرة: `دقة المعاينة 2`)\n"
        f"• `مدة المعاينة` → من {PREVIEW_MIN_SECONDS} إلى {PREVIEW_MAX_SECONDS} "
        "ثانية أو تلقائي (أو مباشرة: `مدة المعاينة 20`)\n"
        "• `الرابط معاينة` → المعاينة فقط بدون الفيديو (يحمّل أقل دقة تكفيها)\n"
        "• فيديو مرسل وبوصفه `معاينة` → معاينته حتى لو الميزة معطّلة\n\n"
        "(الإعدادات تُحفظ بشكل دائم، ودقة المعاينة مستقلة عن جودة الفيديو اللي تختارها)"
    )


def build_level_prompt() -> str:
    current = preview_settings["level"]
    lines = ["🎚️ اختر دقة المعاينة (رد برقم الخيار):\n"]
    for num, params in PREVIEW_LEVELS.items():
        mark = " ✅ (الحالية)" if num == current else ""
        lines.append(f"{num}. {params['name']}{mark}")
    lines.append(
        "\n(الدقة نسبة من دقة كل فيديو نفسه، وما تتجاوز دقة الملف المحمّل)"
    )
    return "\n".join(lines)


def build_seconds_prompt() -> str:
    seconds = preview_settings["seconds"]
    current = "تلقائي" if not seconds else f"{seconds} ثانية"
    return (
        f"⏱️ أرسل مدة المعاينة بالثواني (من {PREVIEW_MIN_SECONDS} إلى "
        f"{PREVIEW_MAX_SECONDS})، أو `تلقائي`.\n(الحالية: {current})"
    )


async def _apply_preview_setting(event, key: str, value, label: str):
    """يطبّق إعداد جديد ويحفظه ويرد بتأكيد."""
    preview_settings[key] = value
    saved = await save_preview_settings()
    note = "محفوظ بشكل دائم" if saved else "⚠️ طُبّق لكن تعذر الحفظ الدائم (يرجع للقديم بعد إعادة التشغيل)"
    await safe_respond(event, f"✅ {label}\n({note})")


def _open_preview_prompt(chat_id, kind: str):
    pending_preview_prompts[chat_id] = {
        "kind": kind,
        "expires": time.monotonic() + PREVIEW_PROMPT_TTL,
    }


@client.on(events.NewMessage(chats=ALLOWED_CHATS, pattern=r"(?i)^((ال)?معاين[ةه]|preview)$"))
async def handle_preview_menu(event):
    if not is_allowed_trigger(event):
        return
    await safe_respond(event, build_preview_menu_text())


@client.on(events.NewMessage(chats=ALLOWED_CHATS, pattern=r"(?i)^(تفعيل|تشغيل|فعّل|فعل)\s+(ال)?معاين[ةه]$"))
async def handle_preview_on(event):
    if not is_allowed_trigger(event):
        return
    await _apply_preview_setting(
        event, "enabled", True,
        "تم تفعيل المعاينة - بترسل لك معاينة مع كل فيديو يتحمّل، ولأي فيديو ترسله للبوت.",
    )


@client.on(events.NewMessage(chats=ALLOWED_CHATS, pattern=r"(?i)^(تعطيل|ايقاف|إيقاف|وقف|عطّل|عطل)\s+(ال)?معاين[ةه]$"))
async def handle_preview_off(event):
    if not is_allowed_trigger(event):
        return
    await _apply_preview_setting(event, "enabled", False, "تم تعطيل المعاينة.")


@client.on(events.NewMessage(chats=ALLOWED_CHATS, pattern=r"(?i)^دق[ةه]\s+(ال)?معاين[ةه](?:\s+(\d+))?$"))
async def handle_preview_level(event):
    if not is_allowed_trigger(event):
        return
    arg = event.pattern_match.group(2)
    if arg is None:
        _open_preview_prompt(event.chat_id, "level")
        await safe_respond(event, build_level_prompt())
        return
    level = int(arg)
    if level not in PREVIEW_LEVELS:
        await safe_respond(event, f"❌ رقم غير صالح. اختر من 1 إلى {len(PREVIEW_LEVELS)}.")
        return
    pending_preview_prompts.pop(event.chat_id, None)
    await _apply_preview_setting(
        event, "level", level, f"دقة المعاينة: {level} — {PREVIEW_LEVELS[level]['name']}"
    )


@client.on(events.NewMessage(chats=ALLOWED_CHATS, pattern=r"(?i)^مد[ةه]\s+(ال)?معاين[ةه](?:\s+(\d+|تلقائي|تلقائى|auto))?$"))
async def handle_preview_duration(event):
    if not is_allowed_trigger(event):
        return
    arg = event.pattern_match.group(2)
    if arg is None:
        _open_preview_prompt(event.chat_id, "seconds")
        await safe_respond(event, build_seconds_prompt())
        return
    await _set_preview_seconds(event, arg)


async def _set_preview_seconds(event, arg: str) -> bool:
    if arg.lower() in ("تلقائي", "تلقائى", "auto"):
        pending_preview_prompts.pop(event.chat_id, None)
        await _apply_preview_setting(event, "seconds", 0, "مدة المعاينة: تلقائية (من 20 ثانية إلى 3 دقائق حسب طول الفيديو)")
        return True
    seconds = int(arg)
    if not PREVIEW_MIN_SECONDS <= seconds <= PREVIEW_MAX_SECONDS:
        await safe_respond(
            event, f"❌ المدة لازم تكون من {PREVIEW_MIN_SECONDS} إلى {PREVIEW_MAX_SECONDS} ثانية."
        )
        return False
    pending_preview_prompts.pop(event.chat_id, None)
    await _apply_preview_setting(event, "seconds", seconds, f"مدة المعاينة: {seconds} ثانية")
    return True


@client.on(events.NewMessage(chats=ALLOWED_CHATS, pattern=r"(?i)^(\d{1,3}|تلقائي|تلقائى|auto)$"))
async def handle_preview_reply(event):
    """يلتقط ردك (رقم أو تلقائي) على سؤال دقة/مدة المعاينة المفتوح فقط."""
    if not is_allowed_trigger(event):
        return
    chat_id = event.chat_id
    pending = pending_preview_prompts.get(chat_id)
    if not pending:
        return
    if time.monotonic() > pending["expires"]:
        pending_preview_prompts.pop(chat_id, None)
        return
    # سؤال جودة فيديو مفتوح؟ الأرقام له (handle_message) مو لنا
    future = pending_quality_futures.get(chat_id)
    if future is not None and not future.done():
        return
    text = (event.raw_text or "").strip()
    if pending["kind"] == "level":
        if text.isdigit() and int(text) in PREVIEW_LEVELS:
            pending_preview_prompts.pop(chat_id, None)
            level = int(text)
            await _apply_preview_setting(
                event, "level", level,
                f"دقة المعاينة: {level} — {PREVIEW_LEVELS[level]['name']}",
            )
        else:
            await safe_respond(event, f"❌ رد برقم من 1 إلى {len(PREVIEW_LEVELS)}.")
    else:
        await _set_preview_seconds(event, text)


@client.on(events.NewMessage(chats=ALLOWED_CHATS))
async def handle_uploaded_preview(event):
    """فيديو مرسل للبوت → يرسل معاينته، لو ميزة المعاينة مفعّلة أو لو كتبت
    `معاينة` بوصف الفيديو. وضع GIF (أو كلمة gif بالوصف) له الأولوية، ويتجاهل
    أي فيديو أرسله البوت نفسه (نفس حماية handle_uploaded_video)."""
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
    if translate_wanted_for_text(event.chat_id, caption_no_urls):
        return  # الترجمة (بالكلمة أو التلقائية): لها معالجها الخاص (handle_uploaded_translate)
    asked = bool(PREVIEW_REGEX.search(caption_no_urls))
    if not (asked or preview_settings["enabled"]):
        return
    if is_gif_mode(event.chat_id) or GIF_REGEX.search(caption_no_urls):
        return

    await asyncio.sleep(2.5)  # عشان رقم رسالة البوت نفسه (لو هو المرسل) يتسجل أول
    if (event.chat_id, msg.id) in bot_sent_ids:
        return

    # مع البث بالأجزاء ما ننزّل الفيديو كاملًا، فحد الحجم ما يسري عليه؛
    # الحد (PREVIEW_MAX_INPUT_MB) يخص فقط حالة التنزيل الكامل.
    stream_ok = bool(
        PREVIEW_STREAM and STREAM_PORT and doc.size
        and doc.size >= PREVIEW_STREAM_MIN_MB * 1024 * 1024
    )
    too_big_msg = (
        f"⚠️ حجم الفيديو {format_size(doc.size)} أكبر من الحد {PREVIEW_MAX_INPUT_MB} ميجا "
        "للتنزيل الكامل، وتعذر استخدام البث بالأجزاء. "
        "(الحد يتغيّر بمتغير PREVIEW_MAX_INPUT_MB)"
    )
    if not stream_ok and doc.size and doc.size > PREVIEW_MAX_INPUT_MB * 1024 * 1024:
        await safe_respond(event, too_big_msg)
        return

    vattr = next(
        (a for a in doc.attributes if isinstance(a, DocumentAttributeVideo)), None
    )
    duration = int(vattr.duration) if vattr and vattr.duration else 0

    status = await safe_respond(event, "🖼️ جاري تجهيز معاينة الفيديو...\n(أرسل \"الغاء\" للإيقاف)")
    tmp_dir = tempfile.mkdtemp(prefix="ytdlp_")
    cancel_event = threading.Event()
    operation = {
        "cancel_event": cancel_event,
        "url": "فيديو مرسل ← معاينة",
        "tmp_dir": tmp_dir,
        "stage": "queued",
        "percent": 0.0,
        "started": time.monotonic(),
    }
    active_operations.append(operation)

    def download_progress(current: int, total: int):
        if cancel_event.is_set():
            raise RuntimeError(CANCELLED_MARKER)
        if total:
            operation["percent"] = current / total * 100

    slot_held = False
    try:
        await acquire_job_slot(status, "فيديو مرسل ← معاينة", cancel_event)
        slot_held = True

        # الأفضل: بث بالأجزاء - ffmpeg يقرأ من تيليجرام المقاطع المطلوبة فقط
        # بدون تنزيل الفيديو كاملًا. لو فشل (أو الملف صغير) → تنزيل كامل.
        preview_sent = False
        if stream_ok:
            token = register_stream_source(doc)
            operation["stage"] = "converting"
            try:
                await build_and_send_preview(
                    event.chat_id,
                    f"http://127.0.0.1:{STREAM_PORT}/tg/{token}",
                    "", operation, cancel_event,
                    duration_hint=duration, reply_to=msg.id,
                    work_dir=tmp_dir, smart=PREVIEW_STREAM_SMART,
                    stream_token=token,
                )
                preview_sent = True
            except Exception as e:
                if str(e) == CANCELLED_MARKER:
                    raise
                logger.warning(f"فشل البث بالأجزاء للمعاينة - نرجع للتنزيل الكامل: {str(e)[:150]}")
            finally:
                stream_sources.pop(token, None)

        if not preview_sent:
            if doc.size and doc.size > PREVIEW_MAX_INPUT_MB * 1024 * 1024:
                record_finished(operation, "failed", "أكبر من حد التنزيل الكامل")
                await safe_edit(status, too_big_msg)
                return
            operation["stage"] = "downloading"
            operation["percent"] = 0.0
            src_path = await client.download_media(
                msg, file=tmp_dir, progress_callback=download_progress
            )
            if not src_path or not os.path.exists(src_path):
                raise FileNotFoundError("تعذر تنزيل الفيديو")
            await build_and_send_preview(
                event.chat_id, src_path, "", operation, cancel_event,
                duration_hint=duration, reply_to=msg.id,
            )
        stats["completed_downloads"] += 1
        record_finished(operation, "done")
        if status is not None:
            try:
                await status.delete()
            except FloodWaitError:
                pass
    except RecursionError:
        stats["failed_downloads"] += 1
        logger.exception("RecursionError أثناء تجهيز معاينة فيديو مرسل")
        record_finished(operation, "failed", "تكرار/إعادة توجيهات غير طبيعي")
        await safe_edit(status, "❌ حدث خطأ داخلي غير متوقع أثناء تجهيز المعاينة.")
    except RuntimeError as e:
        if str(e) == CANCELLED_MARKER:
            record_finished(operation, "cancelled")
            await safe_edit(status, "🛑 تم إلغاء تجهيز المعاينة.")
        else:
            stats["failed_downloads"] += 1
            logger.exception("فشل تجهيز معاينة فيديو مرسل")
            record_finished(operation, "failed", str(e)[:150])
            await safe_edit(status, f"❌ تعذر تجهيز المعاينة: {str(e)[:150]}")
    except Exception as e:
        stats["failed_downloads"] += 1
        logger.exception("خطأ غير متوقع أثناء تجهيز معاينة فيديو مرسل")
        record_finished(operation, "failed", str(e)[:150])
        await safe_edit(status, f"❌ حدث خطأ غير متوقع: {str(e)[:150]}")
    finally:
        if slot_held:
            job_slots.release()
        if operation in active_operations:
            active_operations.remove(operation)
        shutil.rmtree(tmp_dir, ignore_errors=True)


# ======================================================================
# ترجمة كلام الفيديو للعربية (SRT + فيديو بترجمة مدموجة) - المنطق بـ translator.py
# ======================================================================
async def run_translation_job(
    chat_id, src_path: str, title: str, duration: float, operation: dict,
    cancel_event, status, burn_height=None, burn=None, reply_to=None,
):
    """يشغّل خط الترجمة على فيديو محلي ثم يرسل ملف SRT أولًا (يوصلك النص
    حتى لو فشل رفع الفيديو) وبعده الفيديو المترجم. يرفع UserFacingError
    برسالة عربية لأخطاء الترجمة المفهومة. المستدعي مسؤول عن الطابور
    (job_slots) وتنظيف operation['tmp_dir']."""
    operation["stage"] = "converting"
    operation["percent"] = 0.0
    work_dir = tempfile.mkdtemp(prefix="tr_", dir=operation["tmp_dir"])

    async def on_progress(text, pct):
        operation["percent"] = pct
        await safe_edit(status, f"{text}\n\n(أرسل \"الغاء\" لإيقاف العملية)")

    try:
        result = await translator.translate_video(
            src_path, work_dir, title or "video", cancel_event=cancel_event,
            on_progress=on_progress, burn=burn, burn_height=burn_height,
            duration_hint=duration,
        )
    except translator.TranslateError as e:
        raise UserFacingError(str(e))

    operation["stage"] = "uploading"
    operation["percent"] = 0.0
    await safe_edit(status, "📤 جاري إرسال الترجمة...")

    caption = (
        f"🌐 ترجمة عربية · {result['cues']} شاشة · "
        f"اللغة الأصلية: {result['language_ar']}"
    )
    if result["untranslated"]:
        caption += f"\n⚠️ {result['untranslated']} جملة ما انترجمت وبقيت بلغتها الأصلية"
    if result["used_fallback"]:
        caption += "\nℹ️ استُخدم نموذج ترجمة احتياطي (حصة النموذج الأساسي خلصت)"
    await send_bot_file(
        chat_id, result["srt_path"], caption=caption, force_document=True,
        reply_to=reply_to,
    )

    vpath = result["video_path"]
    note = result["burn_note"]
    if vpath:
        vsize = os.path.getsize(vpath)
        if vsize > MAX_FILE_SIZE:
            note = "الفيديو المترجم أكبر من حد الإرسال، وهذا ملف الترجمة."
        else:
            meta = await asyncio.to_thread(probe_media, vpath)
            thumb = await asyncio.to_thread(
                generate_thumbnail, vpath, meta.get("duration") or duration or 0
            )

            def upload_progress(current: int, total: int):
                if cancel_event.is_set():
                    raise RuntimeError(CANCELLED_MARKER)
                if total > 0:
                    operation["percent"] = current / total * 100

            await safe_edit(status, "📤 جاري إرسال الفيديو المترجم...")
            await send_bot_file(
                chat_id, vpath,
                caption=f"🎬 {title}\n🌐 مترجم للعربية · 📦 {format_size(vsize)}".strip()[:1000],
                attributes=[DocumentAttributeVideo(
                    duration=int(meta.get("duration") or duration or 0),
                    w=meta.get("width") or 640, h=meta.get("height") or 360,
                    supports_streaming=True,
                )],
                thumb=thumb, supports_streaming=True, reply_to=reply_to,
                progress_callback=upload_progress,
            )
            stats["total_bytes_sent"] += vsize
    if note:
        await safe_send(chat_id, f"ℹ️ {note}")


def translate_default_on() -> bool:
    """هل \"وضع الترجمة التلقائية\" شغّال فعليًا؟ (مفعّل بالأمر + مفتاح Groq مضبوط)."""
    return bool(preview_settings.get("translate")) and translator.is_configured()


def translate_wanted_for_text(chat_id, text_no_urls: str) -> bool:
    """هل نترجم هذي الرسالة (رابط أو وصف فيديو)؟
    • كلمة ترجمة صريحة ← نعم دائمًا (حتى لو الميزة معطّلة).
    • الترجمة التلقائية مفعّلة ← نعم، إلا لو كتبت كلمة أمر ثاني صريحة
      (gif / mp3 / معاينة)، أو كنت بوضع GIF (وضع مؤقت اخترته بنفسك).
    • غير ذلك ← لا، والبوت يشتغل بأوامره العادية."""
    if TRANSLATE_REGEX.search(text_no_urls):
        return True
    if not translate_default_on():
        return False
    if (
        GIF_REGEX.search(text_no_urls)
        or PREVIEW_REGEX.search(text_no_urls)
        or AUDIO_REGEX.search(text_no_urls)
        or is_gif_mode(chat_id)
    ):
        return False
    return True


async def translate_video_message(event, source_msg):
    """يترجم فيديو (أو ملف صوت) موجود برسالة تيليجرام: ينزّله، يترجمه،
    ويرسل النتيجة كرد عليه."""
    if not translator.is_configured():
        await safe_respond(event, "⚠️ " + translator.SETUP_HINT)
        return
    doc = source_msg.document
    mime = (getattr(doc, "mime_type", "") or "") if doc is not None else ""
    is_audio = mime.startswith("audio/")
    if doc is None or not (mime.startswith("video/") or is_audio) or source_msg.gif:
        await safe_respond(
            event, "⚠️ الترجمة تشتغل على فيديو (أو ملف صوت). رد بكلمة `ترجمة` على الفيديو نفسه."
        )
        return
    if doc.size and doc.size > translator.MAX_INPUT_MB * 1024 * 1024:
        await safe_respond(
            event,
            f"⚠️ حجم الملف {format_size(doc.size)} أكبر من الحد "
            f"{translator.MAX_INPUT_MB} ميجا للترجمة (يتغير بمتغير TRANSLATE_MAX_INPUT_MB).",
        )
        return
    attr = next(
        (a for a in doc.attributes
         if isinstance(a, (DocumentAttributeVideo, DocumentAttributeAudio))), None
    )
    duration = int(getattr(attr, "duration", 0) or 0)
    if duration and duration > translator.MAX_MINUTES * 60:
        await safe_respond(
            event,
            f"⚠️ الفيديو ({duration // 60} دقيقة) أطول من الحد {translator.MAX_MINUTES} "
            "دقيقة للترجمة (يتغير بمتغير TRANSLATE_MAX_MINUTES).",
        )
        return
    fname = getattr(getattr(source_msg, "file", None), "name", None) or ""
    title = os.path.splitext(fname)[0] or "video"

    status = await safe_respond(event, "🌐 جاري تجهيز الترجمة...\n(أرسل \"الغاء\" للإيقاف)")
    tmp_dir = tempfile.mkdtemp(prefix="ytdlp_")
    cancel_event = threading.Event()
    operation = {
        "cancel_event": cancel_event,
        "url": "فيديو مرسل ← ترجمة",
        "tmp_dir": tmp_dir,
        "stage": "queued",
        "percent": 0.0,
        "started": time.monotonic(),
    }
    active_operations.append(operation)

    def download_progress(current: int, total: int):
        if cancel_event.is_set():
            raise RuntimeError(CANCELLED_MARKER)
        if total:
            operation["percent"] = current / total * 100

    slot_held = False
    try:
        await acquire_job_slot(status, "فيديو مرسل ← ترجمة", cancel_event)
        slot_held = True
        operation["stage"] = "downloading"
        await safe_edit(status, "📥 جاري تنزيل الفيديو للترجمة...\n(أرسل \"الغاء\" للإيقاف)")
        src_path = await client.download_media(
            source_msg, file=tmp_dir, progress_callback=download_progress
        )
        if not src_path or not os.path.exists(src_path):
            raise FileNotFoundError("تعذر تنزيل الفيديو")
        await run_translation_job(
            event.chat_id, src_path, title, duration, operation, cancel_event,
            status, burn=False if is_audio else None, reply_to=source_msg.id,
        )
        stats["completed_downloads"] += 1
        record_finished(operation, "done")
        if status is not None:
            try:
                await status.delete()
            except FloodWaitError:
                pass
    except UserFacingError as e:
        stats["failed_downloads"] += 1
        record_finished(operation, "failed", str(e)[:150])
        await safe_edit(status, f"⚠️ {e}")
    except RecursionError:
        stats["failed_downloads"] += 1
        logger.exception("RecursionError أثناء ترجمة فيديو مرسل")
        record_finished(operation, "failed", "خطأ داخلي (تكرار)")
        await safe_edit(status, "❌ حدث خطأ داخلي غير متوقع أثناء الترجمة.")
    except RuntimeError as e:
        if str(e) == CANCELLED_MARKER:
            record_finished(operation, "cancelled")
            await safe_edit(status, "🛑 تم إلغاء الترجمة.")
        else:
            stats["failed_downloads"] += 1
            logger.exception("فشل ترجمة فيديو مرسل")
            record_finished(operation, "failed", str(e)[:150])
            await safe_edit(status, f"❌ تعذرت الترجمة: {str(e)[:150]}")
    except Exception as e:
        stats["failed_downloads"] += 1
        logger.exception("خطأ غير متوقع أثناء ترجمة فيديو مرسل")
        record_finished(operation, "failed", str(e)[:150])
        await safe_edit(status, f"❌ حدث خطأ غير متوقع: {str(e)[:150]}")
    finally:
        if slot_held:
            job_slots.release()
        if operation in active_operations:
            active_operations.remove(operation)
        shutil.rmtree(tmp_dir, ignore_errors=True)


def build_translate_menu_text() -> str:
    on = bool(preview_settings.get("translate"))
    state = "مفعّلة ✅" if on else "معطّلة ⛔"
    key = "مضبوط ✅" if translator.is_configured() else "غير مضبوط ⛔ (اضبط GROQ_API_KEY)"
    return (
        "🌐 **الترجمة للعربية**\n\n"
        f"• الترجمة التلقائية: {state}\n"
        f"• مفتاح Groq: {key}\n\n"
        "**الأوامر:**\n"
        "• `تفعيل الترجمة` → أي رابط ترسله يُحمَّل ويُترجم تلقائيًا (بدون كتابة \"ترجمة\")، "
        "وأي فيديو ترسله للبوت يُترجم\n"
        "• `تعطيل الترجمة` → إيقاف الترجمة التلقائية\n"
        "• `الرابط ترجمة` / رد بكلمة `ترجمة` على فيديو / فيديو ووصفه `ترجمة` → "
        "ترجمة لمرة وحدة، تشتغل دائمًا حتى لو الميزة معطّلة\n\n"
        "**ملاحظات:**\n"
        "• لو الترجمة التلقائية مفعّلة وكتبت مع الرابط `gif` أو `mp3` أو `معاينة` "
        "يتنفذ هذا الأمر بدل الترجمة\n"
        "• وضع GIF (لو مفعّل) له الأولوية على الترجمة التلقائية\n"
        "• لو الميزة معطّلة، البوت يشتغل بأوامره العادية (تحميل/GIF/mp3/معاينة)\n"
        "• الإعداد يُحفظ بشكل دائم"
    )


@client.on(events.NewMessage(chats=ALLOWED_CHATS, pattern=TRANSLATE_MENU_PATTERN))
async def handle_translate_menu(event):
    if not is_allowed_trigger(event):
        return
    await safe_respond(event, build_translate_menu_text())


@client.on(events.NewMessage(chats=ALLOWED_CHATS, pattern=TRANSLATE_ON_PATTERN))
async def handle_translate_on(event):
    if not is_allowed_trigger(event):
        return
    if not translator.is_configured():
        await safe_respond(event, "⚠️ ما أقدر أفعّل الترجمة التلقائية: " + translator.SETUP_HINT)
        return
    await _apply_preview_setting(
        event, "translate", True,
        "تم تفعيل الترجمة - أي رابط ترسله يُحمَّل ويُترجم تلقائيًا، "
        "وأي فيديو ترسله للبوت يُترجم. (للأوامر الثانية اكتب معه gif أو mp3 أو معاينة)",
    )


@client.on(events.NewMessage(chats=ALLOWED_CHATS, pattern=TRANSLATE_OFF_PATTERN))
async def handle_translate_off(event):
    if not is_allowed_trigger(event):
        return
    await _apply_preview_setting(
        event, "translate", False,
        "تم تعطيل الترجمة التلقائية - رجع البوت لأوامره العادية "
        "(وتقدر تترجم لمرة وحدة بكلمة `ترجمة`).",
    )


@client.on(events.NewMessage(chats=ALLOWED_CHATS, pattern=TRANSLATE_CMD_PATTERN))
async def handle_translate_command(event):
    """رد بكلمة `ترجمة` على أي فيديو بالمحادثة (حتى اللي أرسله البوت نفسه)."""
    if not is_allowed_trigger(event):
        return
    reply = await event.get_reply_message() if event.is_reply else None
    if reply is None:
        await safe_respond(
            event,
            "ℹ️ لترجمة فيديو للعربية:\n"
            "• رد بكلمة `ترجمة` على الفيديو\n"
            "• أو أرسل `الرابط ترجمة`\n"
            "• أو أرسل الفيديو ووصفه `ترجمة`",
        )
        return
    await translate_video_message(event, reply)


@client.on(events.NewMessage(chats=ALLOWED_CHATS))
async def handle_uploaded_translate(event):
    """فيديو مرسل → يترجمه لو وصفه فيه كلمة ترجمة، أو لو الترجمة التلقائية
    مفعّلة (ما لم تكتب أمرًا صريحًا ثانيًا: gif / معاينة / وضع GIF)."""
    if not is_allowed_trigger(event):
        return
    msg = event.message
    doc = msg.document
    if doc is None:
        return
    mime = getattr(doc, "mime_type", "") or ""
    if not mime.startswith("video/") or msg.gif or msg.video_note:
        return
    caption_no_urls = URL_REGEX.sub(" ", event.raw_text or "")
    if not translate_wanted_for_text(event.chat_id, caption_no_urls):
        return
    await asyncio.sleep(2.5)  # عشان رقم رسالة البوت نفسه (لو هو المرسل) يتسجل أول
    if (event.chat_id, msg.id) in bot_sent_ids:
        return
    await translate_video_message(event, msg)


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
            await safe_respond(event, "ℹ️ ما فيه أي تحميل جارٍ حاليًا لإلغائه.")
        return

    count = len(active_operations)
    for op in list(active_operations):
        op["cancel_event"].set()

    await safe_respond(event, f"🛑 يتم إلغاء {count} عملية جارية...")


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
    status = await safe_respond(event, "🧹 جاري تنظيف الملفات المؤقتة...")
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
        await safe_respond(event, 
            f"⚠️ فيه {len(active_operations)} عملية تحميل شغّالة حاليًا. "
            "أرسل \"الغاء\" أول لو تبي توقفها، أو أرسل \"تأكيد إعادة التشغيل\" "
            "للمتابعة رغم ذلك."
        )
        return

    await safe_respond(event, "🔄 جاري إعادة تشغيل السيرفر... البوت بيرجع يشتغل خلال دقيقة تقريبًا.")
    await asyncio.sleep(1.5)  # نضمن وصول الرسالة قبل إيقاف العملية
    logger.info("إعادة تشغيل مطلوبة يدويًا - إيقاف العملية الآن")
    os._exit(0)


@client.on(events.NewMessage(chats=ALLOWED_CHATS, pattern=r"(?i)^تأكيد إعادة التشغيل$"))
async def handle_force_restart(event):
    """تأكيد إعادة التشغيل رغم وجود تحميلات شغّالة - تُفقد هذي
    التحميلات الجارية بدون استكمال."""
    if not is_allowed_trigger(event):
        return
    await safe_respond(event, "🔄 جاري إعادة التشغيل رغم العمليات الجارية...")
    await asyncio.sleep(1.5)
    os._exit(0)


STAGE_LABELS = {
    "queued": "🕐 بالطابور",
    "downloading": "⏳ جاري التحميل",
    "converting": "🎞️ جاري التحويل",
    "uploading": "📤 جاري الإرسال",
}
OUTCOME_LABELS = {
    "done": "✅ اكتملت",
    "failed": "❌ فشلت",
    "cancelled": "🛑 أُلغيت",
}


def fmt_elapsed(seconds: float) -> str:
    """مدة قصيرة مقروءة (\"منذ 45 ثانية\" / \"منذ 3 دقائق\")، تُستخدم
    بأمر \"حالة\" لتوضيح عمر كل عملية (شغّالة أو منتهية حديثًا)."""
    seconds = int(seconds)
    if seconds < 60:
        return f"منذ {seconds} ثانية"
    minutes = seconds // 60
    if minutes < 60:
        return f"منذ {minutes} دقيقة"
    return f"منذ {minutes // 60} ساعة"


def build_status_text() -> str:
    """هذا هو جوهر أمر \"حالة\": يجاوب بالضبط على السؤال اللي يطرحه
    المستخدم لما يطوّل تحميل - هل هو لسه شغّال (تحميل/تحويل/إرسال،
    بأي نسبة)، خلص بنجاح، أو فشل بخطأ؟ بدون هذا، أمر \"حالة\" القديم كان
    يقول بس \"ما فيه تحميل شغّال\" في الحالتين (نجح أو فشل بصمت)،
    فالمستخدم ما يقدر يميّز بينهم."""
    lines = ["📊 **حالة السيرفر**\n"]

    if active_operations:
        lines.append(f"⏳ عمليات شغّالة الآن: {len(active_operations)}")
        for op in active_operations:
            stage = STAGE_LABELS.get(op.get("stage", "downloading"), "⏳ جاري التحميل")
            percent = op.get("percent", 0.0)
            elapsed = fmt_elapsed(time.monotonic() - op.get("started", time.monotonic()))
            percent_note = "" if op.get("stage") == "queued" else f" {percent:.0f}%"
            lines.append(f"  • {stage}{percent_note} - {op['url'][:60]} ({elapsed})")
    else:
        lines.append("⏳ ما فيه أي عملية شغّالة حاليًا")

    recent = list(recent_operations)[-5:]
    if recent:
        lines.append("\n🕓 آخر العمليات المنتهية:")
        for rec in reversed(recent):
            outcome = OUTCOME_LABELS.get(rec["outcome"], rec["outcome"])
            elapsed = fmt_elapsed(time.monotonic() - rec["finished_at"])
            detail = f" - {rec['detail']}" if rec.get("detail") else ""
            lines.append(f"  • {outcome} - {rec['url'][:60]} ({elapsed}){detail}")

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

    return "\n".join(lines)


@client.on(events.NewMessage(chats=ALLOWED_CHATS, pattern=r"(?i)^(الحالة|حالة|الحاله|حاله|status)$"))
async def handle_status(event):
    """يعرض حالة السيرفر الحالية: العمليات الشغّالة (تحميل/تحويل/إرسال
    بالنسبة والوقت)، آخر العمليات المنتهية (نجحت/فشلت/أُلغيت)، مساحة
    القرص، واستهلاك الذاكرة - يفيد لما تحميل يطوّل وتبي تعرف هل البوت
    لسه شغّال عليه، خلص، أو واجه خطأ."""
    if not is_allowed_trigger(event):
        return
    await safe_respond(event, build_status_text())


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
    await safe_respond(event, text)


@client.on(events.NewMessage(chats=ALLOWED_CHATS, pattern=r"(?i)^(مساعدة|help)$"))
async def handle_help(event):
    """يعرض قائمة كل الأوامر والكلمات المتاحة بالبوت (رسالة أولى)، ثم
    الإعدادات الحالية ومتغيرات البيئة اللي تغيّرها من Render (رسالة ثانية)."""
    if not is_allowed_trigger(event):
        return
    await safe_respond(event, build_help_text())
    await safe_respond(event, build_settings_text())


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
        "• `معاينة` → معاينة الفيديو فقط بدون إرساله (راجع قسم المعاينة)\n"
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
        "🖼️ **المعاينة** (GIF يلخّص الفيديو من بدايته لنهايته)\n"
        "• `معاينة` → قائمة أوامر المعاينة وحالتها\n"
        "• `تفعيل المعاينة` / `تعطيل المعاينة` → مع كل فيديو يتحمّل أو يُرسل للبوت\n"
        "• `دقة المعاينة` → اختيار الدقة من 5 مستويات (محفوظة بشكل دائم)\n"
        f"• `مدة المعاينة` → من {PREVIEW_MIN_SECONDS} إلى {PREVIEW_MAX_SECONDS} ثانية أو تلقائي\n"
        "• `الرابط معاينة` → المعاينة فقط بدون الفيديو\n\n"
        "🌐 **ترجمة كلام الفيديو للعربية** (ملف SRT + فيديو مترجم)\n"
        "• `الرابط ترجمة` → يحمّل الفيديو ويترجم كلامه (أي لغة ← عربي) بتوقيت مزامن\n"
        "• رد بكلمة `ترجمة` على أي فيديو بالمحادثة، أو أرسل فيديو ووصفه `ترجمة`\n"
        "• `تفعيل الترجمة` → كل رابط أو فيديو ترسله يُترجم تلقائيًا بدون كتابة ترجمة\n"
        "• `تعطيل الترجمة` → رجوع للأوامر العادية (كلمة `ترجمة` تبقى تشتغل لمرة وحدة)\n"
        "• `الترجمة` → حالة الترجمة وأوامرها\n"
        f"• حتى {translator.MAX_MINUTES} دقيقة للترجمة، ودمجها بالفيديو لغاية "
        f"{translator.BURN_MAX_MINUTES} دقائق (بعدها يرسل ملف SRT فقط)\n"
        "• تحتاج مفتاح مجاني `GROQ_API_KEY` من console.groq.com\n\n"
        "**أوامر التحكم:**\n"
        "• `الغاء` - يوقف أي تحميل شغّال أو ينتظر بالطابور\n"
        "• `تنظيف` - يمسح الملفات المؤقتة المتراكمة\n"
        "• `اعادة تشغيل` - يعيد تشغيل السيرفر بالكامل\n"
        "• `حالة` (أو `الحالة`/`حاله`) - تحميلات شغّالة بنسبتها الحية "
        "(تحميل/تحويل/إرسال)، آخر العمليات المنتهية (نجحت/فشلت/أُلغيت)، "
        "طابور، قرص، ذاكرة\n"
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
    if GROUP_CHAT_ID:
        group_line = "مضبوط ✅"
    elif GROUP_REQUESTED:
        group_line = "معطّلة ⛔ (القيمة لازم تكون رقمًا صحيحًا)"
    else:
        group_line = "غير مضبوط"
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
        "**المعاينة:**\n"
        f"• الحالة: {'مفعّلة ✅' if preview_settings['enabled'] else 'معطّلة ⛔'} · "
        f"الدقة: {preview_settings['level']} ({PREVIEW_LEVELS[preview_settings['level']]['name']}) · "
        f"المدة: {'تلقائية' if not preview_settings['seconds'] else str(preview_settings['seconds']) + ' ثانية'} "
        "(تتغيّر بالأوامر وتُحفظ دائمًا، مو من Render)\n"
        f"• `PREVIEW_MAX_SIDE` = {PREVIEW_MAX_SIDE} - أقصى طول للضلع الأطول بالمعاينة\n"
        f"• `PREVIEW_MAX_INPUT_MB` = {PREVIEW_MAX_INPUT_MB} - أقصى حجم لفيديو مرسل تُصنع له معاينة بالتنزيل الكامل (البث بالأجزاء ما يتأثر به)\n"
        f"• `PREVIEW_SMART_PICK` = {'مفعّل ✅' if PREVIEW_SMART_PICK else 'معطّل ⛔'} - "
        "تجنّب اللقطات السوداء/الثابتة/المكررة بالمعاينة\n"
        f"• `PREVIEW_STREAM` = {'مفعّل ✅' if PREVIEW_STREAM else 'معطّل ⛔'} - "
        "معاينة الفيديو المرسل بدون تنزيله كاملًا (بث بالأجزاء)\n"
        f"• `PREVIEW_STREAM_MIN_MB` = {PREVIEW_STREAM_MIN_MB} - الملفات الأصغر تُنزَّل كاملة\n"
        f"• `PREVIEW_STREAM_SMART` = {'مفعّل ✅' if PREVIEW_STREAM_SMART else 'معطّل ⛔'} - "
        "الاختيار الذكي مع البث (يقرأ بيانات أكثر)\n\n"
        "**الترجمة للعربية:**\n"
        f"• الترجمة التلقائية: {'مفعّلة ✅' if preview_settings.get('translate') else 'معطّلة ⛔'} "
        "(بالأوامر `تفعيل الترجمة` / `تعطيل الترجمة`، تُحفظ دائمًا)\n"
        f"• `GROQ_API_KEY` = {'مضبوط ✅' if translator.is_configured() else 'غير مضبوط ⛔ (ضروري للترجمة)'}\n"
        f"• `TRANSLATE_MAX_MINUTES` = {translator.MAX_MINUTES} · "
        f"`TRANSLATE_MAX_INPUT_MB` = {translator.MAX_INPUT_MB}\n"
        f"• `TRANSLATE_BURN` = {'مفعّل ✅' if translator.BURN_DEFAULT else 'معطّل ⛔'} · "
        f"`TRANSLATE_BURN_HEIGHT` = {translator.BURN_HEIGHT} · "
        f"`TRANSLATE_BURN_MAX_MINUTES` = {translator.BURN_MAX_MINUTES}\n"
        "• `TRANSLATE_STT_MODEL` / `TRANSLATE_LLM_MODEL` - نماذج التفريغ والترجمة\n\n"
        "**الأمان والمجموعة:**\n"
        f"• `GROUP_CHAT_ID` = {group_line} - "
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
    await safe_respond(event, 
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
        await safe_respond(event, "✅ تم الخروج من وضع GIF - رجعنا لتحميل الروابط العادي.")
    else:
        await safe_respond(event, "ℹ️ وضع GIF مو مفعّل أصلاً - أنت بالوضع العادي.")


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
    if translate_wanted_for_text(event.chat_id, caption_no_urls):
        return  # الترجمة (بالكلمة أو التلقائية): لها معالجها الخاص (handle_uploaded_translate)
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
        await safe_respond(event, 
            "⚠️ مدى القص غير صحيح - النهاية لازم تكون بعد البداية "
            "(مثال: `gif 10-20`)."
        )
        return
    caption = re.sub(r"\s+", " ", GIF_REGEX.sub(" ", caption_rest)).strip()

    if doc.size and doc.size > GIF_MAX_INPUT_MB * 1024 * 1024:
        await safe_respond(event, 
            f"⚠️ الفيديو أكبر من {GIF_MAX_INPUT_MB} ميجا، تعذر تحويله إلى GIF."
        )
        return

    vattr = next(
        (a for a in doc.attributes if isinstance(a, DocumentAttributeVideo)), None
    )
    duration = int(vattr.duration) if vattr and vattr.duration else 0
    width = int(vattr.w) if vattr and vattr.w else 0
    height = int(vattr.h) if vattr and vattr.h else 0

    status = await safe_respond(event, "🎞️ جاري تحويل الفيديو إلى GIF...\n(أرسل \"الغاء\" للإيقاف)")
    tmp_dir = tempfile.mkdtemp(prefix="ytdlp_")
    cancel_event = threading.Event()
    operation = {
        "cancel_event": cancel_event,
        "url": "فيديو مرسل ← GIF",
        "tmp_dir": tmp_dir,
        "stage": "queued",
        "percent": 0.0,
        "started": time.monotonic(),
    }
    active_operations.append(operation)

    def download_progress(current: int, total: int):
        if cancel_event.is_set():
            raise RuntimeError(CANCELLED_MARKER)
        if total:
            operation["percent"] = current / total * 100

    slot_held = False
    try:
        waited = await acquire_job_slot(status, "فيديو مرسل ← GIF", cancel_event)
        slot_held = True
        operation["stage"] = "downloading"
        if waited:
            await safe_edit(status, "🎞️ جاري تحويل الفيديو إلى GIF...")
        src_path = await client.download_media(
            msg, file=tmp_dir, progress_callback=download_progress
        )
        if not src_path or not os.path.exists(src_path):
            raise FileNotFoundError("تعذر تنزيل الفيديو")

        operation["stage"] = "converting"
        operation["percent"] = 0.0
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

        operation["stage"] = "uploading"
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
        record_finished(operation, "done")
        if status is not None:
            try:
                await status.delete()
            except FloodWaitError:
                pass
    except UserFacingError as e:
        stats["failed_downloads"] += 1
        record_finished(operation, "failed", str(e)[:150])
        await safe_edit(status, f"⚠️ {e}")
    except RecursionError:
        stats["failed_downloads"] += 1
        logger.exception("RecursionError أثناء تحويل فيديو مرسل إلى GIF")
        record_finished(operation, "failed", "إعادة توجيهات/تكرار غير طبيعي")
        await safe_edit(status, "❌ حدث خطأ داخلي غير متوقع أثناء التحويل.")
    except RuntimeError as e:
        if str(e) == CANCELLED_MARKER:
            record_finished(operation, "cancelled")
            await safe_edit(status, "🛑 تم إلغاء التحويل.")
        else:
            stats["failed_downloads"] += 1
            logger.exception("فشل تحويل فيديو مرسل إلى GIF")
            record_finished(operation, "failed", str(e)[:150])
            await safe_edit(status, f"❌ تعذر تحويل الفيديو إلى GIF: {str(e)[:150]}")
    except Exception as e:
        stats["failed_downloads"] += 1
        logger.exception("خطأ غير متوقع أثناء تحويل فيديو مرسل إلى GIF")
        record_finished(operation, "failed", str(e)[:150])
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
                await safe_send(
                    chat_id, f"❌ رقم غير صالح. رد برقم من 1 إلى {max_option}."
                )
            return
        if URL_REGEX.search(text):
            # رابط جديد وسؤال الجودة لسه مفتوح - ننبّه بدل ما نتجاهله بصمت
            await safe_send(
                chat_id,
                "⏳ فيه سؤال جودة مفتوح - جاوبه برقم الخيار أو أرسل \"الغاء\" "
                "أول، وبعدها أرسل الرابط الجديد.",
            )
            return
        # أي نص ثاني (أوامر مثل \"حالة\" أو \"gif\"، أو كلام عادي) يتعامل معه
        # معالجه الخاص - ما نعتبره جواب خاطئ على السؤال.
        return

    urls = [normalize_url(clean_url(u)) for u in URL_REGEX.findall(text)]
    if not urls:
        return

    # نبحث عن الجودة وكلمة gif بالنص بعد إزالة الروابط، عشان رقم أو
    # كلمة داخل الرابط نفسه (مثل /video/480/) ما تنحسب كطلب من المستخدم
    text_no_urls = URL_REGEX.sub(" ", text)
    # كلمة mp3/صوت صريحة تتغلب على وضع GIF (طلب صوت فقط لهذا الرابط)
    # كلمة معاينة/preview = المعاينة فقط بدون الفيديو (تتغلب على gif/mp3)
    # كلمة ترجمة تتغلب على كل شي ثاني (gif/mp3/معاينة) لهذا الرابط
    as_translate = translate_wanted_for_text(chat_id, text_no_urls)
    as_preview = bool(PREVIEW_REGEX.search(text_no_urls)) and not as_translate
    as_audio = (
        bool(AUDIO_REGEX.search(text_no_urls)) and not as_preview and not as_translate
    )
    as_gif = (
        (bool(GIF_REGEX.search(text_no_urls)) or is_gif_mode(chat_id))
        and not as_audio and not as_preview and not as_translate
    )
    if as_translate and not translator.is_configured():
        await safe_respond(event, "⚠️ " + translator.SETUP_HINT)
        return
    if as_gif and is_gif_mode(chat_id):
        touch_gif_mode(chat_id)

    # مدى القص (10-20) يُقرأ فقط لطلبات GIF، ونشيله من النص قبل قراءة
    # الجودة عشان مدى مثل 360-370 ما ينحسب طلب جودة 360.
    clip = None
    if as_gif:
        clip, text_no_urls = parse_clip_range(text_no_urls)
        if clip == "bad":
            await safe_respond(event, 
                "⚠️ مدى القص غير صحيح - النهاية لازم تكون بعد البداية "
                "(مثال: `gif 10-20`)."
            )
            return

    quality_match = QUALITY_REGEX.search(text_no_urls)
    quality = int(quality_match.group(1)) if quality_match else None

    if len(urls) > 1:
        await safe_respond(event, f"📋 لقيت {len(urls)} روابط، رح أعالجهم بالترتيب...")

    for url in urls:
        await process_single_url(
            event, url, quality, as_gif, clip, as_audio, as_preview, as_translate
        )


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

    await safe_send(chat_id, prompt)

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
        await safe_send(
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
    as_preview: bool = False,
    as_translate: bool = False,
):
    """يحمّل رابط واحد ويرسله، مع تحديث حي لنسبة التقدم بنفس الرسالة.
    quality: أعلى ارتفاع مسموح (مثل 720)، أو None لأعلى جودة متوفرة
    (لو None، يسأل المستخدم أولاً عن الجودات الحقيقية المتوفرة - إلا
    لو فيه جودة وحدة بس متوفرة، بهالحالة ما فيه داعي نسأل)."""
    if quality is None and not as_gif and not as_audio and not as_preview and not as_translate:
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
                await safe_respond(event, f"🛑 تم تجاهل هذا الرابط.\n{url}")
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
    elif as_preview:
        quality_label += " 🖼️ (معاينة فقط)"
    elif as_translate:
        quality_label += " 🌐 (ترجمة للعربية)"
    status = await safe_respond(event, 
        f"⏳ جاري التحميل...{quality_label} 0%\n{url}\n\n"
        "(أرسل \"الغاء\" لإيقاف هذا التحميل)"
    )

    tmp_dir = tempfile.mkdtemp(prefix="ytdlp_")
    output_template = os.path.join(tmp_dir, "%(title).80s.%(ext)s")

    loop = asyncio.get_event_loop()
    progress_state = {"last_percent": -100, "last_edit_time": 0.0}
    cancel_event = threading.Event()
    operation = {
        "cancel_event": cancel_event,
        "url": url,
        "tmp_dir": tmp_dir,
        "stage": "queued",
        "percent": 0.0,
        "started": time.monotonic(),
    }
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

                operation["percent"] = percent  # نحدّث كل مرة (أمر "حالة" يقرأها مباشرة)
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
    elif as_translate:
        # الترجمة: ما نحتاج جودة عالية (الصوت هو المهم، والفيديو المترجم
        # أصلًا يُصغَّر لـ TRANSLATE_BURN_HEIGHT) - نوفّر الباندويدث.
        cap = quality or translator.BURN_HEIGHT
        fmt = f"bestvideo[height<={cap}]+bestaudio/best[height<={cap}]/best"
    elif as_preview:
        # المعاينة فقط: فيديو بدون صوت، والدقة المناسبة تُحدَّد بعد استعلام
        # الجودات داخل try (pick_preview_download) توفيرًا للباندويدث
        fmt = "bestvideo/best"
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
        # إعادة محاولة تلقائية لمشاكل الشبكة المؤقتة (بطء/ازدحام السيرفر)
        # قبل ما نستسلم ونعرض رسالة فشل - يقلل الحاجة لإعادة الإرسال يدويًا
        "socket_timeout": 30,
        "retries": 5,
        "fragment_retries": 10,
        "extractor_retries": 3,
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
        operation["stage"] = "downloading"
        if waited:
            await safe_edit(
                status,
                f"⏳ جاري التحميل...{quality_label} 0%\n{url}\n\n"
                "(أرسل \"الغاء\" لإيقاف هذا التحميل)",
            )

        preview_scale = None
        if as_preview:
            try:
                preview_probe = await asyncio.to_thread(probe_formats, url)
            except Exception:
                logger.exception("تعذر جلب الجودات لتحديد أنسب تنزيل للمعاينة")
                preview_probe = {"heights": [], "sizes": {}, "duration": 0}
            ydl_opts["format"], preview_scale = pick_preview_download(
                preview_probe, preview_settings["level"]
            )

        download_started_at = time.time()
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = await asyncio.to_thread(ydl.extract_info, url, download=True)
            filename = ydl.prepare_filename(info)
            if not os.path.exists(filename):
                base, _ = os.path.splitext(filename)
                filename = base + ".mp4"
            if not os.path.exists(filename):
                # نادرًا، الاسم الفعلي اللي كتبه yt-dlp (بعد الدمج/الترميم
                # النهائي) يختلف عن توقّع prepare_filename() - نلتقط أحدث
                # ملف كُتب بمجلد التحميل المؤقت بدل ما نفشل فورًا.
                candidates = [
                    f for f in glob.glob(os.path.join(tmp_dir, "*"))
                    if os.path.isfile(f) and os.path.getmtime(f) >= download_started_at - 2
                ]
                if candidates:
                    filename = max(candidates, key=os.path.getmtime)

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

        # ---- الترجمة ----
        if as_translate:
            await run_translation_job(
                event.chat_id, filename, info.get("title") or "",
                int(info.get("duration") or 0), operation, cancel_event, status,
                burn_height=quality,
            )
            stats["completed_downloads"] += 1
            record_finished(operation, "done")
            if status is not None:
                try:
                    await status.delete()
                except FloodWaitError:
                    pass
            return

        # ---- المعاينة ----
        if as_preview:
            # معاينة فقط: نبنيها ونرسلها ونوقف (بدون إرسال الفيديو)
            await safe_edit(status, f"🖼️ جاري تجهيز المعاينة...\n{url}")
            try:
                await build_and_send_preview(
                    event.chat_id, filename, info.get("title") or "", operation,
                    cancel_event, int(info.get("duration") or 0), preview_scale,
                )
            except RuntimeError as e:
                if str(e) == CANCELLED_MARKER:
                    raise
                raise UserFacingError(f"تعذر تجهيز المعاينة: {str(e)[:120]}")
            stats["completed_downloads"] += 1
            record_finished(operation, "done")
            if status is not None:
                try:
                    await status.delete()
                except FloodWaitError:
                    pass
            return
        if preview_settings["enabled"] and not as_audio and not as_gif:
            # المعاينة مفعّلة: نرسلها أول، وبعدها الفيديو. لو فشلت ما نمنع الفيديو.
            await safe_edit(status, f"🖼️ جاري تجهيز المعاينة...\n{url}")
            try:
                await build_and_send_preview(
                    event.chat_id, filename, info.get("title") or "", operation,
                    cancel_event, int(info.get("duration") or 0),
                )
            except Exception as e:
                if str(e) == CANCELLED_MARKER:
                    raise
                logger.exception("تعذر تجهيز المعاينة - نكمل بإرسال الفيديو")
                await safe_send(
                    event.chat_id, "⚠️ تعذر تجهيز المعاينة، بيوصلك الفيديو بدونها."
                )
            operation["stage"] = "downloading"

        gif_length = 0
        if as_gif:
            operation["stage"] = "converting"
            operation["percent"] = 0.0
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

        operation["stage"] = "uploading"
        operation["percent"] = 0.0
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
                operation["percent"] = percent  # نحدّث كل مرة (أمر "حالة" يقرأها مباشرة)
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
        record_finished(operation, "done")
        if status is not None:
            try:
                await status.delete()
            except FloodWaitError:
                pass

    except UserFacingError as e:
        stats["failed_downloads"] += 1
        record_finished(operation, "failed", str(e)[:150])
        await safe_edit(status, f"⚠️ {e}\n{url}")
    except RecursionError:
        # RecursionError فرعي من RuntimeError بايثون - لازم يُلتقط قبله
        # (وإلا معالج RuntimeError تحته يمسكه برسالة "خطأ غير متوقع" مبهمة
        # ما توضح إن السبب فعليًا من الموقع نفسه لا من الرابط أو البوت).
        stats["failed_downloads"] += 1
        logger.exception("RecursionError - على الأغلب سلسلة إعادة توجيهات طويلة/حلقية بالموقع")
        record_finished(operation, "failed", "إعادة توجيهات/تكرار غير طبيعي بالموقع")
        await safe_edit(
            status,
            "❌ هذا الموقع يستخدم إعادة توجيهات (redirects) كثيرة جدًا أو "
            f"حلقية، وتعذر التعامل معها.\n{url}",
        )
    except RuntimeError as e:
        if str(e) == CANCELLED_MARKER:
            record_finished(operation, "cancelled")
            await safe_edit(status, f"🛑 تم إلغاء العملية بنجاح.\n{url}")
        else:
            stats["failed_downloads"] += 1
            logger.exception("خطأ غير متوقع")
            record_finished(operation, "failed", str(e)[:150])
            await safe_edit(status, f"❌ حدث خطأ غير متوقع: {str(e)[:150]}\n{url}")
    except yt_dlp.utils.DownloadError as e:
        if CANCELLED_MARKER in str(e):
            record_finished(operation, "cancelled")
            await safe_edit(status, f"🛑 تم إلغاء العملية بنجاح.\n{url}")
        else:
            stats["failed_downloads"] += 1
            record_finished(operation, "failed", friendly_error_message(str(e))[:150])
            await safe_edit(status, f"{friendly_error_message(str(e))}\n{url}")
    except Exception as e:
        # نفس دالة رسائل yt-dlp الودية تنفع هنا كذلك: أخطاء الشبكة
        # (اتصال، مهلة، حماية Cloudflare) أحيانًا توصل كاستثناء بايثون
        # عادي (requests.exceptions.*، socket.timeout) مو كـ
        # yt_dlp.utils.DownloadError، فنستفيد من نفس الفحص بدل تكراره.
        stats["failed_downloads"] += 1
        logger.exception("خطأ غير متوقع")
        record_finished(operation, "failed", friendly_error_message(str(e))[:150])
        await safe_edit(status, f"{friendly_error_message(str(e))}\n{url}")
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
    if PREVIEW_STREAM:
        await start_stream_server()
    await client.start()
    global SELF_ENTITY
    SELF_ENTITY = await client.get_me()
    is_premium = apply_account_limits(SELF_ENTITY)
    await load_preview_settings()
    logger.info(
        "ميزة ترجمة الفيديو: "
        + ("جاهزة ✅" if translator.is_configured() else "غير مفعّلة (اضبط GROQ_API_KEY)")
    )
    logger.info(
        f"نوع الحساب: {'Premium' if is_premium else 'عادي'} | أقصى حجم للملف: "
        f"{MAX_FILE_SIZE // (1024 * 1024)} ميجا | أقصى عمليات متزامنة: "
        f"{MAX_CONCURRENT_JOBS}"
    )
    if GROUP_REQUESTED and not GROUP_CHAT_ID:
        logger.warning("المجموعة الخاصة معطّلة (راجع خطأ GROUP_CHAT_ID أعلاه) - البوت يعمل بـ Saved Messages فقط")
    if GROUP_CHAT_ID:
        logger.info(
            f"البوت (Telethon) يعمل الآن... أرسل رابطًا في Saved Messages "
            f"أو بالمجموعة الخاصة (GROUP_CHAT_ID={GROUP_CHAT_ID})"
        )
    else:
        logger.info("البوت (Telethon) يعمل الآن... أرسل رابطًا في Saved Messages")
    await client.run_until_disconnected()


# بعض المواقع تستخدم سلسلة إعادة توجيهات (redirects) طويلة قبل الوصول
# للفيديو الفعلي، وبعض إصدارات yt-dlp تتعامل معها بشكل تكراري (recursive)
# داخل urllib - فتتجاوز حد بايثون الافتراضي (1000) وتفشل بـ RecursionError
# حتى لو السلسلة نفسها صحيحة ومنتهية (مو حلقة لا نهائية فعلية). نرفع الحد
# عشان نعطي هذي الحالات فرصة تكتمل، مع بقاء حماية ضد التكرار اللانهائي
# الحقيقي (حد أعلى، مو معطّل بالكامل).
sys.setrecursionlimit(10_000)

if __name__ == "__main__":
    asyncio.run(main())
