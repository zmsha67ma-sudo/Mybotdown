FROM python:3.11-slim
RUN apt-get update && apt-get install -y ffmpeg git && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY telethon_bot.py .
# نحدّث yt-dlp لأحدث نسخة من GitHub عند كل تشغيل فعلي للحاوية (مو
# بس وقت بناء الصورة) - هذا يضمن نستخدم آخر إصلاحات الموقع (مثل
# مواقع غيّرت بنية صفحاتها) بدون ما نحتاج نتذكر "Clear build cache"
# يدويًا كل مرة. لو فشل التحديث لأي سبب (مثلاً انقطاع شبكة لحظي)،
# نكمل بالنسخة الموجودة بدل ما نوقف تشغيل البوت بالكامل.
CMD ["sh", "-c", "pip install --no-cache-dir --upgrade --force-reinstall --no-deps git+https://github.com/yt-dlp/yt-dlp.git@master || echo 'تعذر تحديث yt-dlp - سيتم المتابعة بالنسخة الحالية'; exec python telethon_bot.py"]
