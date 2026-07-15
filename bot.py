import os
import asyncio
from aiohttp import web
from telethon import TelegramClient
from telethon.sessions import StringSession

# دریافت اطلاعات از سرور رندر
API_ID = int(os.environ.get('API_ID', 2040))
API_HASH = os.environ.get('API_HASH', 'b18441a1ff607e10a989891a5462e627')
SESSION_STRING = os.environ.get('SESSION_STRING', '')
CHAT_TARGET = os.environ.get('CHAT_TARGET', '')

# تبدیل آیدی‌های عددی به int
if CHAT_TARGET.lstrip('-').isdigit():
    CHAT_TARGET = int(CHAT_TARGET)

# تنظیم کلاینت تلگرام با استفاده از سشنی که گرفتید
client = TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH)

async def meow_job():
    """این تابع هر ۵ دقیقه پیام را ارسال می‌کند"""
    await client.connect()
    print("✅ ربات تلگرام متصل شد و در حال کار است.")
    
    while True:
        try:
            await client.send_message(CHAT_TARGET, 'میو')
            print("پیام 'میو' با موفقیت ارسال شد.")
        except Exception as e:
            print(f"خطا در ارسال پیام: {e}")
        
        # توقف به مدت ۵ دقیقه (۳۰۰ ثانیه)
        await asyncio.sleep(290)

async def handle(request):
    """یک صفحه وب ساده برای اینکه سرور رندر خاموش نشود"""
    return web.Response(text="Meow Bot is Running Perfectly!")

async def main():
    app = web.Application()
    app.router.add_get('/', handle)
    runner = web.AppRunner(app)
    await runner.setup()
    
    port = int(os.environ.get('PORT', 8080))
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()
    print(f"✅ وب‌سرور روی پورت {port} اجرا شد.")
    
    await meow_job()

if __name__ == '__main__':
    asyncio.run(main())
