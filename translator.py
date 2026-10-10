"""
ترجمة كلام أي فيديو إلى العربية مع ترجمة مزامنة (SRT + فيديو بترجمة مدموجة).

المراحل:
1) ffmpeg يستخرج الصوت (mono 16kHz mp3 منخفض الحجم) ويقسّمه لأجزاء.
2) تفريغ الكلام بـ Whisper عبر Groq API (مجاني بحدود) → جمل مع وقت بداية/نهاية.
3) ترجمة الجمل للعربية بنموذج لغوي (Groq) مع الحفاظ على نفس التوقيت.
4) بناء ملف SRT (تقسيم الجمل الطويلة لأسطر مقروءة).
5) دمج الترجمة بالفيديو بـ ffmpeg (اختياري، يعيد ترميز الفيديو).

الوحدة تعتمد على مكتبة بايثون القياسية فقط (بدون مكتبات إضافية)، وما تعرف شيء
عن تيليجرام - الربط بالبوت يتم بـ telethon_bot.py.

متغيرات البيئة (كلها اختيارية ما عدا المفتاح):
- GROQ_API_KEY: مفتاح مجاني من console.groq.com (بدون بطاقة)
- TRANSLATE_API_BASE: افتراضي https://api.groq.com/openai/v1
- TRANSLATE_STT_MODEL: افتراضي whisper-large-v3-turbo
- TRANSLATE_LLM_MODEL: افتراضي openai/gpt-oss-120b (بدل llama-3.3-70b-versatile اللي أوقفته Groq بتاريخ 2026-08-16)
- TRANSLATE_LLM_FALLBACK_MODEL: افتراضي openai/gpt-oss-20b (بدل llama-3.1-8b-instant الموقوف؛ يُستخدم لو خلصت حصة الأول)
- TRANSLATE_MAX_MINUTES: أقصى مدة فيديو للترجمة (افتراضي 30)
- TRANSLATE_MAX_INPUT_MB: أقصى حجم فيديو مرسل يُنزَّل للترجمة (افتراضي 300)
- TRANSLATE_BURN: 1/0 دمج الترجمة بالفيديو (افتراضي 1)
- TRANSLATE_BURN_HEIGHT: أقصى ارتفاع للفيديو المترجم (افتراضي 480)
- TRANSLATE_BURN_MAX_MINUTES: أقصى مدة لدمج الترجمة بالفيديو (افتراضي 10)
- TRANSLATE_BURN_PRESET: سرعة ترميز x264 (افتراضي superfast؛ ultrafast أسرع لكن حجمه أكبر بكثير)
- TRANSLATE_BURN_CRF: جودة الفيديو المدموج، رقم أكبر = حجم أصغر (افتراضي 28)
- TRANSLATE_FONT_PERCENT: حجم خط الترجمة المدموجة كنسبة % من الضلع القصير للفيديو (افتراضي 8)
- TRANSLATE_SYNC_OFFSET_MS: إزاحة توقيت الترجمة بالميلي ثانية لضبط المزامنة (سالب = أبكر، موجب = أتأخر؛ افتراضي 0)
- TRANSLATE_FONT: خط الترجمة المدموجة (افتراضي Noto Sans Arabic)
"""

import asyncio
import json
import logging
import os
import re
import subprocess
import textwrap
import threading
import time
import urllib.error
import urllib.request
import uuid

logger = logging.getLogger(__name__)

# نفس القيمة اللي يستخدمها البوت لإيقاف العمليات (RuntimeError بهذا النص)
CANCELLED_MARKER = "USER_CANCELLED_OPERATION"


class TranslateError(Exception):
    """خطأ مفهوم للمستخدم: النص عربي جاهز للعرض كما هو."""


# ---------------------------------------------------------------- الإعدادات
def _env_int(name: str, default: int, minimum: int = 0) -> int:
    raw = os.environ.get(name, "").strip()
    if not raw:
        return default
    try:
        return max(minimum, int(raw))
    except ValueError:
        logger.warning(f"قيمة {name} غير صحيحة ('{raw}') - نستخدم الافتراضي {default}")
        return default


def _env_flag(name: str, default: bool) -> bool:
    raw = os.environ.get(name, "").strip().lower()
    if not raw:
        return default
    return raw not in ("0", "false", "no", "off", "لا")


API_KEY = os.environ.get("GROQ_API_KEY", "").strip()
API_BASE = os.environ.get("TRANSLATE_API_BASE", "https://api.groq.com/openai/v1").strip().rstrip("/")
STT_MODEL = os.environ.get("TRANSLATE_STT_MODEL", "whisper-large-v3-turbo").strip()
LLM_MODEL = os.environ.get("TRANSLATE_LLM_MODEL", "openai/gpt-oss-120b").strip()
LLM_FALLBACK_MODEL = os.environ.get("TRANSLATE_LLM_FALLBACK_MODEL", "openai/gpt-oss-20b").strip()
MAX_MINUTES = _env_int("TRANSLATE_MAX_MINUTES", 30, 1)
MAX_INPUT_MB = _env_int("TRANSLATE_MAX_INPUT_MB", 300, 1)
BURN_DEFAULT = _env_flag("TRANSLATE_BURN", True)
BURN_HEIGHT = _env_int("TRANSLATE_BURN_HEIGHT", 480, 144)
BURN_MAX_MINUTES = _env_int("TRANSLATE_BURN_MAX_MINUTES", 10, 1)
BURN_PRESET = os.environ.get("TRANSLATE_BURN_PRESET", "superfast").strip() or "superfast"
BURN_CRF = _env_int("TRANSLATE_BURN_CRF", 28, 18)
FONT_PERCENT = _env_int("TRANSLATE_FONT_PERCENT", 8, 3)
SYNC_OFFSET_MS = _env_int("TRANSLATE_SYNC_OFFSET_MS", 0, -10000)
FONT_NAME = os.environ.get("TRANSLATE_FONT", "Noto Sans Arabic").strip() or "Noto Sans Arabic"

CHUNK_SECONDS = 600          # كل جزء صوت 10 دقائق (≈2.4MB بـ 32kbps، بعيد عن حد 25MB)
BATCH_SEGMENTS = 25          # جمل لكل طلب ترجمة
BATCH_CHARS = 3000
MAX_WAIT_SECONDS = 70        # أقصى انتظار لإعادة محاولة بعد 429

SETUP_HINT = (
    "ميزة الترجمة تحتاج مفتاح API مجاني من Groq:\n"
    "1) افتح console.groq.com وسجّل (بدون بطاقة)\n"
    "2) API Keys ← Create API Key\n"
    "3) على Render ← Environment ضيف متغير: GROQ_API_KEY = المفتاح\n"
    "وبعدها يعيد النشر تلقائيًا."
)


def is_configured() -> bool:
    return bool(API_KEY)


def settings_summary() -> dict:
    return {
        "configured": is_configured(),
        "stt": STT_MODEL, "llm": LLM_MODEL, "fallback": LLM_FALLBACK_MODEL,
        "max_minutes": MAX_MINUTES, "max_input_mb": MAX_INPUT_MB,
        "burn": BURN_DEFAULT, "burn_height": BURN_HEIGHT,
        "burn_max_minutes": BURN_MAX_MINUTES,
    }


# أسماء اللغات (Whisper يرجّع الاسم بالإنجليزي) → عربي للعرض
LANG_AR = {
    "english": "الإنجليزية", "chinese": "الصينية", "german": "الألمانية",
    "spanish": "الإسبانية", "russian": "الروسية", "korean": "الكورية",
    "french": "الفرنسية", "japanese": "اليابانية", "portuguese": "البرتغالية",
    "turkish": "التركية", "polish": "البولندية", "italian": "الإيطالية",
    "dutch": "الهولندية", "hindi": "الهندية", "persian": "الفارسية",
    "urdu": "الأردية", "indonesian": "الإندونيسية", "thai": "التايلندية",
    "vietnamese": "الفيتنامية", "hebrew": "العبرية", "ukrainian": "الأوكرانية",
    "greek": "اليونانية", "swedish": "السويدية", "romanian": "الرومانية",
    "czech": "التشيكية", "hungarian": "المجرية", "malay": "الملايوية",
    "bengali": "البنغالية", "tagalog": "التاغالوغية", "swahili": "السواحيلية",
}


def lang_label(language: str) -> str:
    key = (language or "").strip().lower()
    return LANG_AR.get(key) or (language or "غير معروفة")


def is_arabic_language(language: str) -> bool:
    key = (language or "").strip().lower()
    return key in ("arabic", "ar") or key.startswith("arab")


# ------------------------------------------------------------ أدوات عامة
def _check_cancel(cancel_event):
    if cancel_event is not None and cancel_event.is_set():
        raise RuntimeError(CANCELLED_MARKER)


def _sleep_checking(seconds: float, cancel_event):
    """انتظار على شكل خطوات قصيرة عشان "الغاء" يشتغل فورًا."""
    end = time.monotonic() + seconds
    while time.monotonic() < end:
        _check_cancel(cancel_event)
        time.sleep(min(0.5, max(0.0, end - time.monotonic())))


def _run_cmd(cmd: list, cancel_event, timeout: int, capture: bool = False) -> bytes:
    """يشغّل أمر (ffmpeg/ffprobe) ويراقب الإلغاء والمهلة."""
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
                raise TranslateError("انتهت مهلة المعالجة (السيرفر بطيء أو الفيديو ثقيل).")
    if proc.returncode != 0:
        raise TranslateError(
            "فشل ffmpeg: " + (err or b"").decode("utf-8", "ignore")[-200:]
        )
    return out or b""


def probe_duration(path: str) -> float:
    try:
        res = subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration",
             "-of", "default=nw=1:nk=1", path],
            capture_output=True, timeout=30,
        )
        return float((res.stdout or b"0").decode().strip() or 0)
    except Exception:
        return 0.0


def probe_has_audio(path: str) -> bool:
    try:
        res = subprocess.run(
            ["ffprobe", "-v", "error", "-select_streams", "a",
             "-show_entries", "stream=index", "-of", "csv=p=0", path],
            capture_output=True, timeout=30,
        )
        return bool((res.stdout or b"").strip())
    except Exception:
        return True  # لو فشل الفحص، نجرّب الاستخراج ونشوف


def _to_int(x) -> int:
    try:
        return int(float(x))
    except (TypeError, ValueError):
        return 0


def probe_media(path: str) -> dict:
    """يرجّع أبعاد الفيديو (بعد تدويره لو فيه rotation) وبت ريت الفيديو والصوت وكودك الصوت.
    أي قيمة غير معروفة = 0 / فاضي."""
    info = {"width": 0, "height": 0, "v_bps": 0, "a_codec": "", "a_bps": 0}
    try:
        res = subprocess.run(
            ["ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", path],
            capture_output=True, timeout=30,
        )
        data = json.loads((res.stdout or b"{}").decode("utf-8", "ignore") or "{}")
    except Exception:
        return info
    fmt = data.get("format") or {}
    dur = 0.0
    try:
        dur = float(fmt.get("duration") or 0)
    except (TypeError, ValueError):
        pass
    v = a = None
    for st in data.get("streams") or []:
        kind = st.get("codec_type")
        if kind == "video" and v is None and not (st.get("disposition") or {}).get("attached_pic"):
            v = st
        elif kind == "audio" and a is None:
            a = st
    v_bps = 0
    if v:
        w, h = _to_int(v.get("width")), _to_int(v.get("height"))
        rot = _to_int((v.get("tags") or {}).get("rotate"))
        for sd in v.get("side_data_list") or []:
            if "rotation" in sd:
                rot = _to_int(sd.get("rotation"))
        if abs(rot) % 180 == 90:
            w, h = h, w
        info["width"], info["height"] = w, h
        v_bps = _to_int(v.get("bit_rate"))
    if a:
        info["a_codec"] = (a.get("codec_name") or "").lower()
        info["a_bps"] = _to_int(a.get("bit_rate"))
    if not v_bps:
        total = _to_int(fmt.get("bit_rate"))
        if not total and dur > 0:
            total = int(_to_int(fmt.get("size")) * 8 / dur)
        if total:
            v_bps = max(0, total - (info["a_bps"] or 128000))
    info["v_bps"] = v_bps
    return info


def scaled_size(w: int, h: int, limit: int) -> tuple:
    """نفس حساب فلتر scale بدالة الدمج (الضلع القصير لا يتجاوز limit، أبعاد زوجية)."""
    if w <= 0 or h <= 0:
        return 0, 0
    if w > h:
        nh = (min(h, limit) // 2) * 2
        nw = int(round(w * nh / h / 2.0)) * 2
    else:
        nw = (min(w, limit) // 2) * 2
        nh = int(round(h * nw / w / 2.0)) * 2
    return max(2, nw), max(2, nh)


def safe_filename(name: str, default: str = "video") -> str:
    name = re.sub(r"[\\/:*?\"<>|\x00-\x1f]", " ", name or "")
    name = re.sub(r"\s+", " ", name).strip(" .")
    return (name[:60] or default)


# ------------------------------------------------------------ استخراج الصوت
def extract_audio_chunks(src: str, out_dir: str, cancel_event, chunk_seconds: int = CHUNK_SECONDS):
    """يرجّع قائمة (مسار، إزاحة بالثواني، مدة). الصوت mono 16kHz mp3 32kbps."""
    if not probe_has_audio(src):
        raise TranslateError("هذا الفيديو ما فيه مسار صوت، ما عندي شي أترجمه.")
    pattern = os.path.join(out_dir, "a_%03d.mp3")
    _run_cmd(
        [
            "ffmpeg", "-y", "-v", "error", "-i", src, "-vn", "-ac", "1", "-ar", "16000",
            "-c:a", "libmp3lame", "-b:a", "32k",
            "-f", "segment", "-segment_time", str(chunk_seconds),
            "-reset_timestamps", "1", pattern,
        ],
        cancel_event, timeout=900,
    )
    files = sorted(
        f for f in os.listdir(out_dir) if f.startswith("a_") and f.endswith(".mp3")
    )
    if not files:
        raise TranslateError("تعذر استخراج الصوت من الفيديو.")
    chunks, offset = [], 0.0
    for name in files:
        path = os.path.join(out_dir, name)
        dur = probe_duration(path)
        if dur <= 0.2:
            continue
        chunks.append((path, offset, dur))
        offset += dur
    if not chunks:
        raise TranslateError("الصوت المستخرج فاضي.")
    return chunks


# ---------------------------------------------------------------- HTTP
class _ApiError(Exception):
    def __init__(self, status: int, body: str, retry_after: float = 0.0):
        super().__init__(f"HTTP {status}: {body[:200]}")
        self.status = status
        self.body = body
        self.retry_after = retry_after


def _http(req: urllib.request.Request, timeout: int) -> dict:
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        body = ""
        try:
            body = e.read().decode("utf-8", "ignore")
        except Exception:
            pass
        retry_after = 0.0
        try:
            retry_after = float(e.headers.get("retry-after", 0) or 0)
        except (TypeError, ValueError):
            retry_after = 0.0
        raise _ApiError(e.code, body, retry_after)
    except urllib.error.URLError as e:
        raise _ApiError(0, f"network: {e.reason}")
    except (TimeoutError, OSError) as e:
        raise _ApiError(0, f"network: {e}")


def _build_multipart(fields: list, file_field: str, file_path: str):
    boundary = "----tr" + uuid.uuid4().hex
    parts = []
    for name, value in fields:
        parts.append(
            f"--{boundary}\r\nContent-Disposition: form-data; name=\"{name}\"\r\n\r\n{value}\r\n".encode()
        )
    with open(file_path, "rb") as fh:
        data = fh.read()
    parts.append(
        (f"--{boundary}\r\nContent-Disposition: form-data; name=\"{file_field}\"; "
         f"filename=\"{os.path.basename(file_path)}\"\r\nContent-Type: audio/mpeg\r\n\r\n").encode()
        + data + b"\r\n"
    )
    parts.append(f"--{boundary}--\r\n".encode())
    return b"".join(parts), f"multipart/form-data; boundary={boundary}"


def _raise_for_final(e: _ApiError, what: str):
    """يحوّل خطأ API نهائي لرسالة عربية مفهومة."""
    if e.status in (401, 403):
        raise TranslateError("مفتاح GROQ_API_KEY غير صحيح أو مرفوض. تأكد منه بإعدادات Render.")
    if e.status == 429:
        raise TranslateError(
            f"وصلت حد الاستخدام المجاني لخدمة {what} حاليًا. "
            "جرّب بعد شوي (الحد بالساعة/اليوم)، أو أرسل فيديو أقصر."
        )
    if e.status == 413:
        raise TranslateError("جزء الصوت أكبر من الحد المسموح للخدمة.")
    if e.status == 0:
        raise TranslateError(f"تعذر الاتصال بخدمة {what} (مشكلة شبكة مؤقتة). أعد المحاولة بعد شوي.")
    raise TranslateError(f"خدمة {what} رجّعت خطأ ({e.status}): {e.body[:120]}")


def _with_retries(fn, what: str, cancel_event, attempts: int = 4):
    last = None
    for i in range(attempts):
        _check_cancel(cancel_event)
        try:
            return fn()
        except _ApiError as e:
            last = e
            retriable = e.status in (0, 429, 500, 502, 503, 504)
            if not retriable or i == attempts - 1:
                break
            wait = e.retry_after if e.retry_after > 0 else min(5 * (2 ** i), 30)
            if wait > MAX_WAIT_SECONDS:
                break  # انتظار طويل (حد يومي مثلًا) - ما نعلّق البوت عليه
            logger.warning(f"{what}: {e} - إعادة محاولة بعد {wait:.0f} ث")
            _sleep_checking(wait + 0.5, cancel_event)
    _raise_for_final(last, what)


# ------------------------------------------------------------ التفريغ (STT)
def transcribe_chunk(path: str, cancel_event=None) -> dict:
    """يرجّع {"language": str, "segments": [...], "words": [{"word","start","end"}]}.
    نطلب توقيت الكلمات مع الجمل عشان نضبط بدايات ونهايات الترجمة بدقة."""
    if not API_KEY:
        raise TranslateError(SETUP_HINT)

    def make_call(with_words: bool):
        def call():
            fields = [
                ("model", STT_MODEL),
                ("response_format", "verbose_json"),
                ("timestamp_granularities[]", "segment"),
            ]
            if with_words:
                fields.append(("timestamp_granularities[]", "word"))
            fields.append(("temperature", "0"))
            body, ctype = _build_multipart(fields, "file", path)
            req = urllib.request.Request(
                f"{API_BASE}/audio/transcriptions", data=body, method="POST",
                headers={"Authorization": f"Bearer {API_KEY}", "Content-Type": ctype,
                         "User-Agent": "telethon-video-bot/1.0"},
            )
            return _http(req, timeout=180)
        return call

    try:
        data = _with_retries(make_call(True), "التفريغ الصوتي", cancel_event)
    except TranslateError as e:
        if "(400)" not in str(e):
            raise
        logger.warning("التفريغ بتوقيت الكلمات مرفوض - نكمل بتوقيت الجمل فقط")
        data = _with_retries(make_call(False), "التفريغ الصوتي", cancel_event)
    segs = data.get("segments")
    if not segs and (data.get("text") or "").strip():
        segs = [{"start": 0.0, "end": float(data.get("duration") or 0) or 5.0,
                 "text": data["text"]}]
    return {"language": data.get("language") or "", "segments": segs or [],
            "words": data.get("words") or []}


def _attach_words(segs: list, words: list, offset: float) -> None:
    """يضبط بداية/نهاية كل جملة على أول وآخر كلمة فعلية فيها (توقيت الكلمات أدق من الجمل)،
    ويحفظ توقيت الكلمات لتوزيع الترجمة الطويلة على شاشات بدقة."""
    if not segs or not words:
        return
    ws = []
    for w in words:
        try:
            a = float(w.get("start")) + offset
            b = float(w.get("end")) + offset
        except (TypeError, ValueError, AttributeError):
            continue
        txt = re.sub(r"\s+", "", str(w.get("word") or ""))
        if not txt:
            continue
        ws.append((a, max(a, b), txt))
    ws.sort(key=lambda x: x[0])
    buckets = [[] for _ in segs]
    j = 0
    for a, b, txt in ws:
        mid = (a + b) / 2.0
        best, best_d = None, 1e9
        for k in range(max(0, j - 2), len(segs)):
            seg = segs[k]
            if mid < seg["start"]:
                d = seg["start"] - mid
            elif mid > seg["end"]:
                d = mid - seg["end"]
            else:
                d = 0.0
            if d < best_d:
                best, best_d = k, d
            if seg["start"] > mid and seg["start"] - mid > best_d:
                break
        if best is not None and best_d <= 1.5:
            buckets[best].append((a, b, len(txt)))
            j = best
    for seg, bucket in zip(segs, buckets):
        if not bucket:
            continue
        start = min(x[0] for x in bucket)
        end = max(x[1] for x in bucket)
        if end - start < 0.2:
            continue
        if abs(start - seg["start"]) > 4.0 or abs(end - seg["end"]) > 4.0:
            continue  # فرق كبير = غالبًا ربط كلمات غلط، نبقي توقيت الجملة
        seg["start"], seg["end"] = start, end
        seg["words"] = bucket


def clean_segments(raw: list, offset: float = 0.0, words: list = None) -> list:
    """يشيل الهلوسات المعروفة (صمت/تكرار) ويضيف إزاحة الجزء."""
    out = []
    for s in raw or []:
        text = re.sub(r"\s+", " ", (s.get("text") or "")).strip()
        if not text:
            continue
        no_speech = float(s.get("no_speech_prob") or 0)
        logprob = float(s.get("avg_logprob") or 0)
        compress = float(s.get("compression_ratio") or 0)
        if no_speech > 0.6 and logprob < -1.0:
            continue
        if compress > 2.4:
            continue
        start = float(s.get("start") or 0) + offset
        end = float(s.get("end") or 0) + offset
        if end <= start:
            end = start + 1.0
        if out and out[-1]["text"] == text and start - out[-1]["end"] < 1.0:
            out[-1]["end"] = max(out[-1]["end"], end)  # تكرار متتالي → ندمجه
            continue
        out.append({"start": start, "end": end, "text": text})
    _attach_words(out, words, offset)
    return out


# ---------------------------------------------------------------- الترجمة
_SYSTEM_PROMPT = (
    "You are a professional subtitle translator. Translate each numbered segment of "
    "spoken dialogue from {lang} into natural, clear Arabic (Modern Standard Arabic "
    "with a simple conversational tone) suitable for on-screen subtitles.\n"
    "Rules:\n"
    "- Translate faithfully, keep the speaker's tone and meaning; do not censor, "
    "summarize, explain or add comments.\n"
    "- Keep exactly one output item per input item, with the same id. Never merge, "
    "split, skip or reorder items. Each item must stand alone as a subtitle line.\n"
    "- Keep names, brands and technical terms; write numbers as digits.\n"
    "- Lines may alternate between different speakers (e.g. a man and a woman); keep "
    "gender, politeness and context consistent with the 'previous' lines if given.\n"
    "- Output ONLY a JSON object: {{\"segments\": [{{\"i\": <id>, \"ar\": \"<Arabic text>\"}}]}}"
)


def _chat_json(messages: list, models: list, cancel_event) -> dict:
    """يطلب JSON من النموذج؛ لو الأول مشغول/خلصت حصته ننتقل للاحتياطي."""
    last_err = None
    for idx, model in enumerate(models):
        def call(model=model):
            payload = {
                "model": model, "messages": messages, "temperature": 0.2,
                "response_format": {"type": "json_object"},
            }
            req = urllib.request.Request(
                f"{API_BASE}/chat/completions", data=json.dumps(payload).encode("utf-8"),
                method="POST",
                headers={"Authorization": f"Bearer {API_KEY}",
                         "Content-Type": "application/json",
                         "User-Agent": "telethon-video-bot/1.0"},
            )
            return _http(req, timeout=120)

        try:
            data = _with_retries(call, "الترجمة", cancel_event, attempts=3)
        except TranslateError as e:
            last_err = e
            if idx < len(models) - 1:
                logger.warning(f"فشل نموذج الترجمة {model}: {e} - ننتقل للاحتياطي")
                continue
            raise
        try:
            content = data["choices"][0]["message"]["content"]
            parsed = json.loads(content)
            return {"model": model, "data": parsed}
        except (KeyError, IndexError, TypeError, json.JSONDecodeError):
            last_err = TranslateError("رد الترجمة غير مفهوم (تنسيق خاطئ).")
            if idx < len(models) - 1:
                continue
            raise last_err
    raise last_err or TranslateError("فشلت الترجمة.")


def _extract_map(parsed: dict) -> dict:
    items = parsed.get("segments")
    if items is None and isinstance(parsed, dict):
        items = next((v for v in parsed.values() if isinstance(v, list)), None)
    result = {}
    for it in items or []:
        if not isinstance(it, dict):
            continue
        try:
            i = int(it.get("i"))
        except (TypeError, ValueError):
            continue
        ar = it.get("ar")
        if isinstance(ar, str) and ar.strip():
            result[i] = re.sub(r"\s+", " ", ar).strip()
    return result


def translate_segments(segments: list, language: str, cancel_event=None, progress_cb=None) -> dict:
    """يضيف حقل ar لكل جملة. يرجّع إحصائيات: untranslated, used_fallback."""
    models = [m for m in (LLM_MODEL, LLM_FALLBACK_MODEL) if m]
    sys_prompt = _SYSTEM_PROMPT.format(lang=lang_label_en(language))
    batches, cur, cur_chars = [], [], 0
    for idx, seg in enumerate(segments):
        if cur and (len(cur) >= BATCH_SEGMENTS or cur_chars + len(seg["text"]) > BATCH_CHARS):
            batches.append(cur)
            cur, cur_chars = [], 0
        cur.append(idx)
        cur_chars += len(seg["text"])
    if cur:
        batches.append(cur)

    used_fallback = False
    previous = []
    for b_num, batch in enumerate(batches):
        _check_cancel(cancel_event)
        todo = list(batch)
        for attempt in range(2):  # الثانية فقط للجمل الناقصة
            if not todo:
                break
            user_payload = {
                "source_language": lang_label_en(language),
                "previous": previous[-3:],
                "segments": [{"i": i, "t": segments[i]["text"]} for i in todo],
            }
            res = _chat_json(
                [{"role": "system", "content": sys_prompt},
                 {"role": "user", "content": json.dumps(user_payload, ensure_ascii=False)}],
                models, cancel_event,
            )
            if res["model"] != models[0]:
                used_fallback = True
                models = [res["model"]]  # نكمل بالاحتياطي بدل إعادة فشل الأول كل مرة
            got = _extract_map(res["data"])
            for i in todo:
                if i in got:
                    segments[i]["ar"] = got[i]
            todo = [i for i in todo if "ar" not in segments[i]]
        previous = [
            {"src": segments[i]["text"], "ar": segments[i].get("ar", "")}
            for i in batch if segments[i].get("ar")
        ]
        if progress_cb:
            progress_cb((b_num + 1) / len(batches) * 100)

    untranslated = 0
    for seg in segments:
        if "ar" not in seg:
            seg["ar"] = seg["text"]  # نبقي الأصل بدل ما نخسر التوقيت
            untranslated += 1
    return {"untranslated": untranslated, "used_fallback": used_fallback}


def lang_label_en(language: str) -> str:
    return (language or "").strip().title() or "the source language (auto-detected)"


# ---------------------------------------------------------------- SRT
def format_srt_time(seconds: float) -> str:
    seconds = max(0.0, seconds)
    ms = int(round(seconds * 1000))
    h, ms = divmod(ms, 3_600_000)
    m, ms = divmod(ms, 60_000)
    s, ms = divmod(ms, 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


LINE_WIDTH = 34      # حرف بالسطر (يناسب شاشة الجوال)
CUE_LINES = 2


def _balanced_lines(part: str, line_width: int = None) -> list:
    """يقسّم نصًا قصيرًا لسطر أو سطرين متوازنين (بدون سطر يتيم)."""
    lw = line_width or LINE_WIDTH
    if len(part) <= lw:
        return [part]
    width = -(-len(part) // 2) + 2
    while width < len(part):
        lines = textwrap.wrap(part, width=width, break_long_words=False,
                              break_on_hyphens=False)
        if len(lines) <= CUE_LINES:
            return lines
        width += 2
    return [part]


def split_text_for_cues(text: str, line_width: int = None) -> list:
    """يقسّم النص لعدة شاشات متقاربة الطول، كل شاشة سطر أو سطرين."""
    lw = line_width or LINE_WIDTH
    text = re.sub(r"\s+", " ", text).strip()
    max_chars = max(10, lw * CUE_LINES - 6)
    if len(text) <= max_chars:
        return [text]
    n = -(-len(text) // max_chars)
    target = len(text) / n
    parts, cur, cur_len = [], [], 0
    for word in text.split():
        if cur and cur_len + len(word) + 1 > target * 1.08 and len(parts) < n - 1:
            parts.append(" ".join(cur))
            cur, cur_len = [], 0
        cur.append(word)
        cur_len += len(word) + 1
    parts.append(" ".join(cur))
    return parts


def _time_at(seg: dict, frac: float, as_end: bool) -> float:
    """الزمن المقابل لنسبة frac (0..1) من نص الجملة. لو عندنا توقيت الكلمات نستخدمه
    (يراعي الوقفات وسرعة الكلام)، وإلا توزيع خطي بين بداية الجملة ونهايتها."""
    frac = min(1.0, max(0.0, frac))
    words = seg.get("words")
    if not words:
        return seg["start"] + (seg["end"] - seg["start"]) * frac
    if frac <= 0.0:
        return words[0][0]
    if frac >= 1.0:
        return words[-1][1]
    total = sum(w[2] for w in words) or 1
    acc = 0.0
    for ws, we, wl in words:
        lo, hi = acc / total, (acc + wl) / total
        if (as_end and lo < frac <= hi) or (not as_end and lo <= frac < hi):
            return ws + (frac - lo) / max(1e-9, hi - lo) * (we - ws)
        acc += wl
    return words[-1][1]


def build_cues(segments: list, line_width: int = None) -> list:
    """يقسّم كل جملة طويلة لعدة شاشات ترجمة (حسب طول النص) بتوقيت مبني على توقيت
    الكلمات الفعلي، ويطبّق إزاحة المزامنة TRANSLATE_SYNC_OFFSET_MS."""
    cues = []
    for seg in segments:
        parts = split_text_for_cues(seg["ar"], line_width)
        total_chars = sum(len(p) for p in parts) or 1
        acc = 0
        for part in parts:
            f0 = acc / total_chars
            acc += len(part)
            f1 = acc / total_chars
            start = _time_at(seg, f0, False)
            end = _time_at(seg, f1, True)
            if end <= start:
                end = start + 0.3
            cues.append({"start": start, "end": end,
                         "text": "\n".join(_balanced_lines(part, line_width))})
    cues.sort(key=lambda c: c["start"])
    for i, cue in enumerate(cues):
        nxt = cues[i + 1]["start"] if i + 1 < len(cues) else None
        if cue["end"] - cue["start"] < 0.8:
            cue["end"] = cue["start"] + 0.8
        if nxt is not None and cue["end"] > nxt:
            cue["end"] = max(cue["start"] + 0.2, nxt - 0.02)
    if SYNC_OFFSET_MS:
        shift = SYNC_OFFSET_MS / 1000.0
        for cue in cues:
            cue["start"] = max(0.0, cue["start"] + shift)
            cue["end"] = max(cue["start"] + 0.2, cue["end"] + shift)
    return cues


def cues_to_srt(cues: list) -> str:
    out = []
    for n, c in enumerate(cues, 1):
        out.append(f"{n}\n{format_srt_time(c['start'])} --> {format_srt_time(c['end'])}\n{c['text']}\n")
    return "\n".join(out)


# ------------------------------------------------------- دمج الترجمة بالفيديو
def _filter_path(path: str) -> str:
    """مسار ملف داخل فلتر ffmpeg: نهرّب الرموز الخاصة."""
    p = path.replace("\\", "/")
    for ch in (":", "'", ",", "[", "]", ";"):
        p = p.replace(ch, "\\" + ch)
    return p


def _ass_time(t: float) -> str:
    cs = int(round(max(0.0, t) * 100))
    h, cs = divmod(cs, 360000)
    m, cs = divmod(cs, 6000)
    sec, cs = divmod(cs, 100)
    return f"{h}:{m:02d}:{sec:02d}.{cs:02d}"


def write_ass(cues: list, path: str, width: int, height: int, font_px: int, font_name: str) -> None:
    """يكتب ملف ASS بأبعاد الفيديو الفعلية، فحجم الخط (font_px) بالبكسل بالضبط
    ونسبته للشاشة ثابتة بغض النظر عن أبعاد الفيديو."""
    outline = max(2, int(round(font_px * 0.08)))
    margin_v = max(10, int(round(height * 0.06)))
    margin_h = max(10, int(round(width * 0.05)))
    lines = [
        "[Script Info]",
        "ScriptType: v4.00+",
        f"PlayResX: {width}",
        f"PlayResY: {height}",
        "WrapStyle: 0",
        "ScaledBorderAndShadow: yes",
        "",
        "[V4+ Styles]",
        "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, "
        "BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, "
        "BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding",
        f"Style: Default,{font_name},{font_px},&H00FFFFFF,&H00FFFFFF,&H00000000,&H80000000,"
        f"-1,0,0,0,100,100,0,0,1,{outline},0,2,{margin_h},{margin_h},{margin_v},-1",  # Encoding=-1: libass يكتشف اتجاه النص (RTL) فتجي الفواصل بمكانها
        "",
        "[Events]",
        "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text",
    ]
    for c in cues:
        text = (c["text"].replace("\\", "/").replace("{", "(").replace("}", ")")
                .replace("\n", "\\N"))
        lines.append(
            f"Dialogue: 0,{_ass_time(c['start'])},{_ass_time(c['end'])},Default,,0,0,0,,{text}"
        )
    with open(path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")


def burn_subtitles(src: str, sub_path: str, out_path: str, height: int, duration: float,
                   cancel_event=None, progress_cb=None, info: dict = None):
    """يدمج الترجمة بالفيديو (يعيد الترميز). height = أقصى ارتفاع للضلع القصير.
    sub_path: ملف .ass (حجم الخط مضبوط بالبكسل) أو .srt (احتياط لو تعذر فحص الأبعاد).
    الحجم: CRF مع سقف بت ريت مبني على بت ريت الفيديو الأصلي، والصوت يُنسخ لو AAC خفيف،
    فالناتج ما يتضخم عن الأصل."""
    info = info or {}
    h = max(144, int(height))
    scale = (
        f"scale=w='if(gt(iw,ih),-2,trunc(min(iw,{h})/2)*2)':"
        f"h='if(gt(iw,ih),trunc(min(ih,{h})/2)*2,-2)'"
    )
    if sub_path.lower().endswith(".ass"):
        sub_filter = f"ass=filename='{_filter_path(sub_path)}'"
    else:
        style = (
            f"FontName={FONT_NAME},FontSize={int(round(288 * FONT_PERCENT / 100))},"
            "PrimaryColour=&H00FFFFFF,OutlineColour=&H00000000,BackColour=&H80000000,"
            "BorderStyle=1,Outline=2,Shadow=0,Alignment=2,MarginV=16,Bold=1,Encoding=-1"
        )
        sub_filter = f"subtitles=filename='{_filter_path(sub_path)}':force_style='{style}'"
    vf = f"{scale},{sub_filter}"

    v_args = ["-c:v", "libx264", "-preset", BURN_PRESET, "-crf", str(BURN_CRF),
              "-pix_fmt", "yuv420p"]
    v_bps = int(info.get("v_bps") or 0)
    if v_bps > 0:
        in_px = int(info.get("width") or 0) * int(info.get("height") or 0)
        ow, oh = scaled_size(int(info.get("width") or 0), int(info.get("height") or 0), h)
        ratio = min(1.0, (ow * oh) / in_px) if in_px > 0 and ow and oh else 1.0
        cap_k = max(120, int(v_bps * ratio * 0.9 / 1000))
        v_args += ["-maxrate", f"{cap_k}k", "-bufsize", f"{cap_k * 2}k"]
    a_bps = int(info.get("a_bps") or 0)
    if info.get("a_codec") == "aac" and 0 < a_bps <= 160000:
        a_args = ["-c:a", "copy"]
    else:
        a_args = ["-c:a", "aac", "-b:a", "80k"]
    cmd = (
        ["ffmpeg", "-y", "-v", "error", "-nostats", "-progress", "pipe:1",
         "-i", src, "-map", "0:v:0", "-map", "0:a?", "-vf", vf]
        + v_args + a_args + ["-movflags", "+faststart", out_path]
    )
    err_path = out_path + ".err"
    timeout = max(900, int(duration * 10) + 300)
    with open(err_path, "wb") as errf:
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=errf)
    state = {"t": 0.0}

    def reader():
        try:
            for raw in proc.stdout:
                line = raw.decode("utf-8", "ignore").strip()
                if line.startswith("out_time_us=") or line.startswith("out_time_ms="):
                    try:
                        state["t"] = int(line.split("=", 1)[1]) / 1_000_000
                    except ValueError:
                        pass
        except Exception:
            pass

    t = threading.Thread(target=reader, daemon=True)
    t.start()
    started = time.monotonic()
    try:
        while proc.poll() is None:
            time.sleep(0.5)
            if cancel_event is not None and cancel_event.is_set():
                proc.kill()
                proc.wait()
                raise RuntimeError(CANCELLED_MARKER)
            if time.monotonic() - started > timeout:
                proc.kill()
                proc.wait()
                raise TranslateError("انتهت مهلة دمج الترجمة بالفيديو (السيرفر بطيء).")
            if progress_cb and duration > 0:
                progress_cb(min(99.0, state["t"] / duration * 100))
    finally:
        t.join(timeout=2)
    if proc.returncode != 0:
        try:
            with open(err_path, "rb") as fh:
                detail = fh.read().decode("utf-8", "ignore")[-200:]
        except OSError:
            detail = ""
        raise TranslateError(f"فشل دمج الترجمة: {detail}")
    try:
        os.remove(err_path)
    except OSError:
        pass
    if not os.path.exists(out_path) or os.path.getsize(out_path) < 1024:
        raise TranslateError("الفيديو الناتج بعد الدمج تالف أو فاضي.")


# ---------------------------------------------------------------- المنسّق
async def _poll(fn, state: dict, on_progress, interval: float = 4.0):
    """يشغّل دالة بطيئة بثريد، ويستدعي on_progress كل بضع ثوانٍ."""
    fut = asyncio.ensure_future(asyncio.to_thread(fn))
    while not fut.done():
        await asyncio.wait({fut}, timeout=interval)
        if not fut.done() and on_progress:
            await on_progress(state.get("text", ""), state.get("pct", 0.0))
    return await fut


async def translate_video(src_path: str, work_dir: str, title: str, *, cancel_event=None,
                          on_progress=None, burn=None, burn_height=None,
                          duration_hint: float = 0.0) -> dict:
    """المنسّق الكامل. on_progress(text, percent) دالة async اختيارية.
    يرجّع dict: language, language_ar, srt_path, video_path (أو None),
    segments, cues, untranslated, used_fallback, burn_note."""
    if not API_KEY:
        raise TranslateError(SETUP_HINT)
    burn = BURN_DEFAULT if burn is None else burn
    burn_height = burn_height or BURN_HEIGHT

    async def report(text, pct):
        if on_progress:
            await on_progress(text, pct)

    duration = duration_hint or await asyncio.to_thread(probe_duration, src_path)
    if duration and duration > MAX_MINUTES * 60:
        raise TranslateError(
            f"الفيديو أطول من الحد ({MAX_MINUTES} دقيقة) للترجمة. "
            "(الحد يتغير بمتغير TRANSLATE_MAX_MINUTES)"
        )

    # 1) استخراج الصوت
    await report("🎧 جاري استخراج الصوت...", 3)
    chunks = await asyncio.to_thread(
        extract_audio_chunks, src_path, work_dir, cancel_event
    )

    # 2) التفريغ
    segments, language = [], ""
    for n, (path, offset, _dur) in enumerate(chunks, 1):
        _check_cancel(cancel_event)
        await report(f"📝 جاري تفريغ الكلام ({n}/{len(chunks)})...", 5 + 35 * (n - 1) / len(chunks))
        res = await asyncio.to_thread(transcribe_chunk, path, cancel_event)
        if not language and res["language"] and res["segments"]:
            language = res["language"]
        segments.extend(clean_segments(res["segments"], offset, res.get("words")))
    if not segments:
        raise TranslateError("ما لقيت كلام واضح بالفيديو (موسيقى/صمت فقط، أو الصوت ضعيف جدًا).")
    if is_arabic_language(language):
        raise TranslateError("الكلام بالفيديو عربي أصلًا، ما يحتاج ترجمة.")

    # 3) الترجمة
    state = {"text": "🌐 جاري الترجمة للعربية...", "pct": 40.0}

    def tr_progress(p):
        state["pct"] = 40 + 20 * p / 100

    await report(state["text"], 40)
    stats = await _poll(
        lambda: translate_segments(segments, language, cancel_event, tr_progress),
        state, lambda text, pct: report(text, pct),
    )

    # 4) SRT
    cues = build_cues(segments)
    base = safe_filename(title)
    srt_path = os.path.join(work_dir, f"{base}.ar.srt")
    with open(srt_path, "w", encoding="utf-8") as fh:
        fh.write(cues_to_srt(cues))

    result = {
        "language": language, "language_ar": lang_label(language),
        "srt_path": srt_path, "video_path": None,
        "segments": len(segments), "cues": len(cues),
        "untranslated": stats["untranslated"], "used_fallback": stats["used_fallback"],
        "burn_note": "",
    }

    # 5) دمج الترجمة (اختياري)
    if not burn:
        return result
    if duration and duration > BURN_MAX_MINUTES * 60:
        result["burn_note"] = (
            f"الفيديو أطول من {BURN_MAX_MINUTES} دقائق، فأرسلت ملف الترجمة فقط "
            "(دمجها يحتاج معالجة ثقيلة على السيرفر؛ الحد TRANSLATE_BURN_MAX_MINUTES)."
        )
        return result
    out_path = os.path.join(work_dir, f"{base}.ar.mp4")
    # نجهّز ملف ASS بأبعاد الفيديو الناتج عشان حجم الخط يكون مضبوط ومقروء
    info = await asyncio.to_thread(probe_media, src_path)
    sub_path = srt_path
    ow, oh = scaled_size(info["width"], info["height"], burn_height)
    if ow and oh:
        try:
            font_px = max(18, int(round(min(ow, oh) * FONT_PERCENT / 100.0)))
            line_w = max(14, min(LINE_WIDTH, int((ow * 0.90) / (font_px * 0.55))))
            burn_cues = cues if line_w == LINE_WIDTH else build_cues(segments, line_w)
            ass_path = os.path.join(work_dir, f"{base}.ar.ass")
            write_ass(burn_cues, ass_path, ow, oh, font_px, FONT_NAME)
            sub_path = ass_path
        except Exception as e:  # احتياط: نرجع لملف SRT لو فشل تجهيز ASS
            logger.warning(f"تعذر تجهيز ASS ({e}) - نستخدم SRT")
    bstate = {"text": "🎬 جاري دمج الترجمة بالفيديو...", "pct": 60.0}

    def b_progress(p):
        bstate["pct"] = 60 + 40 * p / 100
        bstate["text"] = f"🎬 جاري دمج الترجمة بالفيديو... {p:.0f}%"

    await report(bstate["text"], 60)
    try:
        await _poll(
            lambda: burn_subtitles(src_path, sub_path, out_path, burn_height,
                                   duration or 0.0, cancel_event, b_progress, info),
            bstate, lambda text, pct: report(text, pct),
        )
        result["video_path"] = out_path
    except TranslateError as e:
        # فشل الدمج ما يضيّع الترجمة: نرسل ملف SRT ونوضح السبب
        logger.warning(f"فشل دمج الترجمة: {e}")
        result["burn_note"] = f"تعذر دمج الترجمة بالفيديو ({str(e)[:100]})، وهذا ملف الترجمة."
    return result
