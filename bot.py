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
# بخش اول: گوش دادن به پیام‌ها و کلیک هوشمند
# ==========================================
@client.on(events.NewMessage(chats=CHAT_TARGET))
async def click_button_handler(event):
    """این تابع پیام‌ها را چک کرده و روی دکمه‌ها کلیک می‌کند"""
    if event.message.buttons:
        # ۱ ثانیه تاخیر برای اینکه تلگرام درخواست را مسدود نکند
        await asyncio.sleep(1) 
        
        msg_text = event.message.text or ""
        
        # ------------------------------------------------
        # ۱. شکار گربه خیابونی
        # ------------------------------------------------
        if 'گربه خیابونی' in msg_text:
            try:
                await event.message.click(0) # کلیک روی اولین دکمه
                print("🐈 ✅ روی دکمه 'گربه خیابونی' کلیک شد!")
            except Exception as e:
                print(f"❌ خطا در گربه خیابونی: {e}")
            return

        # ------------------------------------------------
        # ۲. پیام ماهی (کلیک قطعی روی دومین دکمه)
        # ------------------------------------------------
        # کلماتی که همیشه تو پیام ماهی هست رو چک میکنه
        if 'فرصت تصمیم گیری' in msg_text or 'گرفتید' in msg_text or 'ارزش غذایی' in msg_text:
            try:
                # عدد 1 یعنی "دومین گزینه". بدون توجه به متن دکمه، دومی رو میزنه!
                await event.message.click(1) 
                print("🐟 ✅ مستقیماً روی دومین گزینه (بده پیشی بخوره) کلیک شد!")
            except Exception as e:
                print(f"❌ خطا در کلیک ماهی: {e}")
            return

        # ------------------------------------------------
        # ۳. پیام برداشت (کلیک قطعی روی اولین دکمه)
        # ------------------------------------------------
        if 'میو پوینت' in msg_text or 'تولید شده' in msg_text or 'گشنمیووو' in msg_text:
            try:
                # عدد 0 یعنی "اولین گزینه" که همون برداشت هست
                await event.message.click(0)
                print("💰 ✅ مستقیماً روی اولین گزینه (برداشت) کلیک شد!")
            except Exception as e:
                print(f"❌ خطا در کلیک برداشت: {e}")
            return

# ==========================================
# بخش دوم: تسک‌های زمان‌بندی شده (میو، ماهی، پیشی)
# ==========================================

async def meow_job():
    """هر ۵ دقیقه (۲۹۰ ثانیه) میگه 'میو'"""
    while True:
        try:
            await client.send_message(CHAT_TARGET, 'میو')
            print("😺 پیام 'میو' ارسال شد.")
        except Exception as e:
            print(f"خطا در ارسال میو: {e}")
        await asyncio.sleep(290) 

async def fish_job():
    """هر ۱ ساعت (۳۶۰۰ ثانیه) میگه 'ماهی'"""
    await asyncio.sleep(5) # ۵ ثانیه تاخیر اولیه
    while True:
        try:
            await client.send_message(CHAT_TARGET, 'ماهی')
            print("🎣 پیام 'ماهی' ارسال شد.")
        except Exception as e:
            print(f"خطا در ارسال ماهی: {e}")
        await asyncio.sleep(3600) 

async def pishi_job():
    """هر ۵ ساعت (۱۸۰۰۰ ثانیه) میگه 'پیشی'"""
    await asyncio.sleep(15) # ۱۵ ثانیه تاخیر اولیه
    while True:
        try:
            await client.send_message(CHAT_TARGET, 'پیشی')
            print("🐱 پیام 'پیشی' ارسال شد.")
        except Exception as e:
            print(f"خطا در ارسال پیشی: {e}")
        await asyncio.sleep(18000) 

# ==========================================
# بخش سوم: وب سرور رندر و اجرای اصلی
# ==========================================
async def handle(request):
    """جلوگیری از خاموش شدن سرور رندر"""
    return web.Response(text="Bot is running! It securely clicks the 2nd button for fish.")

async def main():
    app = web.Application()
    app.router.add_get('/', handle)
    runner = web.AppRunner(app)
    await runner.setup()
    
    port = int(os.environ.get('PORT', 8080))
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()
    print(f"✅ وب‌سرور روی پورت {port} اجرا شد.")
    
    await client.start()
    print("✅ یوزربات متصل شد! تایمرهای میو، ماهی و پیشی فعال شدند...")

    # استارت کردن هر ۳ زمان‌بندی
    asyncio.create_task(meow_job())
    asyncio.create_task(fish_job())
    asyncio.create_task(pishi_job())
    
    await client.run_until_disconnected()

if __name__ == '__main__':
    asyncio.run(main())
