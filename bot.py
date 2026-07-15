import os
import asyncio
from aiohttp import web
from telethon import TelegramClient
from telethon.sessions import StringSession

# دریافت اطلاعات از متغیرهای محیطی
API_ID = int(os.environ.get('API_ID', 0))
API_HASH = os.environ.get('API_HASH', '')
SESSION_STRING = os.environ.get('SESSION_STRING', '')
CHAT_TARGET = os.environ.get('CHAT_TARGET', '')

# تبدیل آیدی‌های عددی به int (چون متغیرهای محیطی به صورت متن دریافت می‌شوند)
if CHAT_TARGET.lstrip('-').isdigit():
    CHAT_TARGET = int(CHAT_TARGET)

# تنظیم کلاینت تلگرام
client = TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH)

async def meow_job():
    """این تابع هر ۵ دقیقه پیام را ارسال می‌کند"""
    await client.connect()
    print("✅ ربات تلگرام متصل شد و در حال کار است.")
    
    while True:
        try:
            await client.send_message(CHAT_TARGET, 'میو')
            print("پیام 'میو' ارسال شد.")
        except Exception as e:
            print(f"خطا در ارسال پیام: {e}")
        
        # صبر به مدت 5 دقیقه (300 ثانیه)
        await asyncio.sleep(300)

async def handle(request):
    """یک صفحه وب ساده برای اینکه رندر بداند سرور زنده است"""
    return web.Response(text="Meow Bot is Running Perfectly!")

async def main():
    # راه‌اندازی سرور وبِ سبک با aiohttp
    app = web.Application()
    app.router.add_get('/', handle)
    
    runner = web.AppRunner(app)
    await runner.setup()
    
    # دریافت پورتی که رندر به ما اختصاص می‌دهد
    port = int(os.environ.get('PORT', 8080))
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()
    print(f"✅ وب‌سرور روی پورت {port} اجرا شد.")
    
    # اجرای حلقه بی‌نهایت ربات تلگرام در پس‌زمینه
    await meow_job()

if __name__ == '__main__':
    # اجرای اصلی برنامه
    asyncio.run(main())
