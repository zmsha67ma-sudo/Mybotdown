# بوت تيلجرام لتحميل الفيديوهات — النشر على Render.com (مجاني، بدون بطاقة بنكية)

بوت يستقبل رابط (X/تويتر ومئات المواقع الأخرى) ويحمّل الفيديو بأعلى جودة
عبر yt-dlp ثم يرسله لك على تيلجرام. هذا الدليل يشرح النشر على **Render.com**
باستخدام خطته المجانية (Web Service) التي **لا تتطلب بطاقة بنكية**.

> ملاحظة: Render لا يوفر "Background Worker" مجاني، لذلك البوت مبني على
> وضع **webhook** بدل polling ليعمل كـ Web Service عادي (مجاني).
> العيب الوحيد: الخدمة تنام بعد ~15 دقيقة من عدم الاستخدام، وأول رسالة
> بعدها تاخذ بضع ثوانٍ إضافية لإيقاظها — طبيعي وما يحتاج تدخل منك.

---

## 1. إنشاء البوت والحصول على التوكن

1. افتح تيلجرام وابحث عن **@BotFather**.
2. أرسل `/newbot` واتبع التعليمات (اسم ثم يوزر ينتهي بـ `bot`).
3. احتفظ بالتوكن الذي يعطيك إياه، شكله:
   `123456789:AAExxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`

---

## 2. رفع الكود على GitHub

Render ينشر مباشرة من مستودع GitHub، فأول شي ترفع الملفات هناك:

1. أنشئ حساب مجاني على https://github.com إذا ما عندك.
2. أنشئ مستودع (Repository) جديد، مثلاً باسم `telegram-video-bot`.
3. ارفع فيه: `bot.py` و `requirements.txt`.
4. أضف ملف ثالث اسمه `runtime.txt` يحتوي على سطر واحد:
   ```
   python-3.11.9
   ```

---

## 3. إنشاء حساب Render ونشر الخدمة

1. اذهب إلى https://render.com وسجّل حساب مجاني — تقدر تسجل مباشرة عبر
   حساب GitHub، **بدون أي بطاقة بنكية**.
2. من لوحة التحكم: **New → Web Service**.
3. اختر مستودع GitHub اللي رفعت فيه الكود واربطه.
4. في إعدادات الخدمة:
   - **Name:** أي اسم تحبه
   - **Region:** أقرب منطقة لك
   - **Runtime:** Python 3
   - **Build Command:**
     ```
     pip install -r requirements.txt && apt-get update && apt-get install -y ffmpeg
     ```
   - **Start Command:**
     ```
     python bot.py
     ```
   - **Instance Type:** اختر **Free**
5. في قسم **Environment Variables** أضف:
   - `BOT_TOKEN` = التوكن اللي أخذته من BotFather
6. اضغط **Create Web Service**.

Render رح يبني وينشر الخدمة تلقائيًا، وبيعطيك رابط عام شكله:
`https://telegram-video-bot-xxxx.onrender.com`

هذا الرابط يتوفر تلقائيًا في متغير `RENDER_EXTERNAL_URL` داخل بيئة التشغيل،
والكود مبرمج يستخدمه تلقائيًا لضبط الـ webhook مع تيلجرام — ما تحتاج تسوي شي يدوي إضافي.

---

## 4. التأكد إن البوت شغّال

1. من تبويب **Logs** في Render، تابع حتى تشوف رسالة:
   ```
   تشغيل Webhook على https://.../123456789:AAExxxx...
   ```
2. افتح تيلجرام وابحث عن بوتك وأرسل `/start`.
3. أرسل رابط فيديو من X وشوف إذا حمّله ورجعه لك.

---

## 5. إذا فشل تثبيت ffmpeg (بديل Docker)

بعض حسابات Render لا تسمح بتنفيذ `apt-get` مباشرة أثناء البناء. إذا صار
هذا، استخدم Docker بدل ذلك:

1. أنشئ ملف `Dockerfile` في نفس المستودع:
   ```dockerfile
   FROM python:3.11-slim
   RUN apt-get update && apt-get install -y ffmpeg && rm -rf /var/lib/apt/lists/*
   WORKDIR /app
   COPY requirements.txt .
   RUN pip install --no-cache-dir -r requirements.txt
   COPY bot.py .
   CMD ["python", "bot.py"]
   ```
2. عند إنشاء الخدمة على Render، اختر **Runtime: Docker** بدل Python،
   وباقي الخطوات نفسها.

---

## حدود الحجم

- الحد الأقصى لحجم الفيديو اللي يقدر البوت يرسله هو **50 ميجا**
  (قيد Bot API الرسمي لتيلجرام، مو قيد من عندنا).
- رفعه إلى 2 جيجا يتطلب Local Bot API Server على VPS خاص، وهذا غير متاح
  على خطة Render المجانية. لو احتجته لاحقًا راجعني.

---

## ملاحظات مهمة

- بعض روابط X تتطلب تسجيل دخول لمشاهدتها — yt-dlp ما يقدر يحملها بدون كوكيز صالحة.
- احترم حقوق النشر: لا تعيد رفع أو توزّع محتوى غيرك تجاريًا بدون إذن.
- حدّث yt-dlp بشكل دوري في requirements.txt لأن مواقع التواصل تغيّر بنيتها باستمرار.
