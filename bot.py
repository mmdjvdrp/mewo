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
# بخش اول: گوش دادن به پیام‌ها و کلیک سریع
# ==========================================
@client.on(events.NewMessage(chats=CHAT_TARGET))
async def click_button_handler(event):
    """این تابع بلافاصله پیام‌ها رو بررسی میکنه و دکمه رو میزنه"""
    if event.message.buttons:
        # تأخیر رو به 1 ثانیه کاهش دادیم که ماهی فرار نکنه!
        await asyncio.sleep(1) 
        
        msg_text = event.message.text or ""
        
        # ۱. شکار گربه خیابونی
        if 'گربه خیابونی' in msg_text:
            try:
                await event.message.click(0)
                print("🐈 ✅ پیام 'گربه خیابونی' شکار شد!")
                return
            except Exception as e:
                print(f"❌ خطا در شکار گربه خیابونی: {e}")

        # ۲. بررسی دکمه‌ها برای ماهی و پیشی
        for row in event.message.buttons:
            for button in row:
                btn_text = button.text or ""
                
                # بررسی هوشمندتر برای کلیک روی دکمه ماهی
                if 'پیشی بخوره' in btn_text or 'بده' in btn_text:
                    try:
                        await button.click()
                        print("🐟 ✅ روی دکمه 'بده پیشی بخوره' کلیک شد تا ماهی فرار نکنه!")
                        return 
                    except Exception as e:
                        print(f"❌ خطا در کلیک ماهی: {e}")
                
                # بررسی هوشمندتر برای برداشت پوینت‌ها
                elif 'برداشت' in btn_text or 'پوینت' in btn_text:
                    try:
                        await button.click()
                        print("💰 ✅ روی دکمه 'برداشت میو پوینت ها' کلیک شد!")
                        return 
                    except Exception as e:
                        print(f"❌ خطا در کلیک برداشت: {e}")

# ==========================================
# بخش دوم: ارسال پیام‌های زمان‌بندی شده (میو، ماهی، پیشی)
# ==========================================

async def meow_job():
    """هر ۵ دقیقه (حدود ۲۹۰ ثانیه) میگه 'میو'"""
    while True:
        try:
            await client.send_message(CHAT_TARGET, 'میو')
            print("😺 پیام 'میو' ارسال شد.")
        except Exception as e:
            print(f"خطا در ارسال میو: {e}")
        await asyncio.sleep(290) 

async def fish_job():
    """هر ۱ ساعت (۳۶۰۰ ثانیه) میگه 'ماهی'"""
    await asyncio.sleep(5) # ۵ ثانیه تاخیر اولیه که با میو تداخل نکنه
    while True:
        try:
            await client.send_message(CHAT_TARGET, 'ماهی')
            print("🎣 پیام 'ماهی' ارسال شد.")
        except Exception as e:
            print(f"خطا در ارسال ماهی: {e}")
        await asyncio.sleep(3600) 

async def pishi_job():
    """هر ۵ ساعت (۱۸۰۰۰ ثانیه) میگه 'پیشی'"""
    await asyncio.sleep(15) # ۱۵ ثانیه تاخیر اولیه که با بقیه تداخل نکنه
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
    return web.Response(text="Meow Bot is Running 3 Jobs (Meow, Fish, Pishi) and Clicking Fast!")

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
    print("✅ یوزربات متصل شد! آماده برای ارسال میو، ماهی، پیشی و کلیک روی دکمه‌ها...")

    # اجرای هر ۳ تسک همزمان در پس‌زمینه
    asyncio.create_task(meow_job())
    asyncio.create_task(fish_job())
    asyncio.create_task(pishi_job())
    
    await client.run_until_disconnected()

if __name__ == '__main__':
    asyncio.run(main())
