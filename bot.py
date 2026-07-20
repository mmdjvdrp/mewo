import os
import asyncio
from aiohttp import web
from telethon import TelegramClient, events
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

# ==========================================
# بخش اول: گوش دادن به پیام‌ها و کلیک هوشمند روی دکمه‌ها
# ==========================================
@client.on(events.NewMessage(chats=CHAT_TARGET))
async def click_button_handler(event):
    """این تابع پیام‌های جدید رو چک می‌کنه و دکمه‌های خاص رو فشار می‌ده"""
    if event.message.buttons:
        # 2 ثانیه صبر می‌کنه که شبیه انسان باشه
        await asyncio.sleep(2) 
        
        # تمام دکمه‌های زیر پیام رو یکی یکی بررسی می‌کنه
        for row in event.message.buttons:
            for button in row:
                
                # اگر متن دکمه شامل "بده پیشی بخوره" بود:
                if 'بده پیشی بخوره' in button.text:
                    try:
                        await button.click()
                        print("🐟 ✅ روی دکمه 'بده پیشی بخوره' با موفقیت کلیک شد!")
                        return # خروج از حلقه بعد از کلیک
                    except Exception as e:
                        print(f"❌ خطا در کلیک ماهی: {e}")
                
                # اگر متن دکمه شامل "برداشت میو پوینت ها" بود:
                elif 'برداشت میو پوینت ها' in button.text:
                    try:
                        await button.click()
                        print("💰 ✅ روی دکمه 'برداشت میو پوینت ها' با موفقیت کلیک شد!")
                        return # خروج از حلقه بعد از کلیک
                    except Exception as e:
                        print(f"❌ خطا در کلیک برداشت: {e}")

# ==========================================
# بخش دوم: ارسال پیام‌های زمان‌بندی شده
# ==========================================
async def pishi_job():
    """ارسال پیام پیشی برای باز شدن منوی برداشت"""
    while True:
        try:
            # در عکس شما کلمه "پیشی" را فرستاده بودید، من هم همین را قرار دادم
            await client.send_message(CHAT_TARGET, 'پیشی')
            print("🐱 پیام 'پیشی' با موفقیت ارسال شد.")
        except Exception as e:
            print(f"خطا در ارسال پیام پیشی: {e}")
        
        # توقف به مدت ۲۷۵ ثانیه (حدود ۴.۵ دقیقه)
        await asyncio.sleep(275) 

async def fish_job():
    """ارسال پیام ماهی برای دریافت ماهی (هر ۱ ساعت)"""
    # 10 ثانیه صبر می‌کنه تا با پیام پیشی تداخل نداشته باشه
    await asyncio.sleep(10) 
    while True:
        try:
            await client.send_message(CHAT_TARGET, 'ماهی')
            print("🎣 پیام 'ماهی' با موفقیت ارسال شد.")
        except Exception as e:
            print(f"خطا در ارسال پیام ماهی: {e}")
        
        # توقف به مدت ۱ ساعت (۳۶۰۰ ثانیه)
        await asyncio.sleep(3600) 

# ==========================================
# بخش سوم: وب سرور رندر و اجرای اصلی
# ==========================================
async def handle(request):
    """یک صفحه وب ساده برای اینکه سرور رندر خاموش نشود"""
    return web.Response(text="Meow Bot is Running Perfectly with Smart Button Clicker!")

async def main():
    app = web.Application()
    app.router.add_get('/', handle)
    runner = web.AppRunner(app)
    await runner.setup()
    
    port = int(os.environ.get('PORT', 8080))
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()
    print(f"✅ وب‌سرور روی پورت {port} اجرا شد.")
    
    # روشن کردن کلاینت تلگرام
    await client.start()
    print("✅ یوزربات تلگرام متصل شد و در حال کار است.")

    # اجرای تسک‌های ارسال پیام در پس‌زمینه
    asyncio.create_task(pishi_job())
    asyncio.create_task(fish_job())
    
    # روشن نگه داشتن ربات
    await client.run_until_disconnected()

if __name__ == '__main__':
    asyncio.run(main())
