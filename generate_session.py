"""
شغّل هذا الملف على جهازك الشخصي (كمبيوتر) مرة واحدة فقط.
الهدف: تسجيل الدخول بحسابك في تيلجرام والحصول على "Session String" -
وهو رمز طويل يخلي البوت يدخل بحسابك بدون ما تكتب كودك كل مرة.

قبل التشغيل:
    pip install telethon

ثم شغّل:
    python generate_session.py

بيطلب منك:
1. API_ID و API_HASH (تاخذهم من https://my.telegram.org)
2. رقم هاتفك (مع رمز الدولة، مثال: +9665xxxxxxxx)
3. كود التحقق اللي بيوصلك على تيلجرام

في النهاية بيطبع لك Session String طويل - انسخه واحفظه، بتحتاجه
كمتغير بيئة SESSION_STRING على Render.

⚠️ هذا الرمز يعادل كلمة سر حسابك بالكامل - لا تشاركه مع أي أحد ولا
ترفعه على GitHub أبدًا.
"""

from telethon.sync import TelegramClient
from telethon.sessions import StringSession

print("=" * 60)
print("توليد Session String لحساب تيلجرام")
print("=" * 60)

api_id = input("أدخل API_ID: ").strip()
api_hash = input("أدخل API_HASH: ").strip()

with TelegramClient(StringSession(), int(api_id), api_hash) as client:
    session_string = client.session.save()
    print("\n" + "=" * 60)
    print("✅ نجح تسجيل الدخول! انسخ السطر التالي بالكامل واحفظه:")
    print("=" * 60)
    print(session_string)
    print("=" * 60)
