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

client = TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH)

# ==========================================
# تابع برای کلیک مداوم روی گربه خیابونی (هر ۳ ثانیه)
# ==========================================
async def click_street_cat_loop(message):
    print("🐈 ✅ گربه خیابونی پیدا شد! شروع کلیک مداوم هر ۳ ثانیه...")
    while True:
        try:
            # کلیک روی اولین دکمه (ایندکس 0)
            await message.click(0)
            await asyncio.sleep(3) # صبر به مدت ۳ ثانیه
        except Exception as e:
            # وقتی دکمه از کار بیفته یا پیام پاک بشه، حلقه متوقف میشه
            print(f"❌ دکمه گربه خیابونی منقضی شد یا ارور داد: {e}")
            break

# ==========================================
# بخش گوش دادن به پیام‌ها و کلیک دکمه‌ها
# ==========================================
@client.on(events.NewMessage(chats=CHAT_TARGET))
async def click_button_handler(event):
    if event.message.buttons:
        await asyncio.sleep(1) 
        msg_text = event.message.text or ""
        
        # ۱. هندلر گربه خیابونی (اجرای تابع کلیک مداوم)
        if 'گربه خیابونی' in msg_text:
            # ایجاد یک تسک پس‌زمینه برای کلیک هر 3 ثانیه
            asyncio.create_task(click_street_cat_loop(event.message))
            return

        # ۲. هندلر ماهی و پیشی
        for row in event.message.buttons:
            for button in row:
                btn_text = button.text or ""
                
                # پیدا کردن گزینه دوم (بده پیشی بخوره)
                if 'پیشی بخوره' in btn_text or 'بده' in btn_text:
                    try:
                        await button.click()
                        print("🐟 ✅ روی دکمه 'بده پیشی بخوره' کلیک شد!")
                        return 
                    except Exception as e:
                        print(f"❌ خطا در کلیک ماهی: {e}")
                
                # دکمه برداشت برای پیشی
                elif 'برداشت' in btn_text or 'پوینت' in btn_text:
                    try:
                        await button.click()
                        print("💰 ✅ روی دکمه 'برداشت میو پوینت ها' کلیک شد!")
                        return 
                    except Exception as e:
                        print(f"❌ خطا در کلیک برداشت: {e}")

# ==========================================
# بخش ارسال پیام‌های زمان‌بندی شده
# ==========================================
async def meow_job():
    # هر ۴ دقیقه و ۳۰ ثانیه (۲۷۰ ثانیه)
    while True:
        try:
            await client.send_message(CHAT_TARGET, 'میو')
        except Exception:
            pass
        await asyncio.sleep(270) 

async def fish_job():
    # هر ۱ ساعت (۳۶۰۰ ثانیه)
    await asyncio.sleep(5) 
    while True:
        try:
            await client.send_message(CHAT_TARGET, 'ماهی')
        except Exception:
            pass
        await asyncio.sleep(3600) 

async def pishi_job():
    # هر ۲ ساعت (۷۲۰۰ ثانیه)
    await asyncio.sleep(15) 
    while True:
        try:
            await client.send_message(CHAT_TARGET, 'پیشی')
        except Exception:
            pass
        await asyncio.sleep(7200) 

# ==========================================
# بخش وب سرور رندر و اجرای اصلی
# ==========================================
async def handle(request):
    return web.Response(text="Bot is running! (Only Game: Meow, Fish, Pishi, Street Cat)")

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
    print("✅ یوزربات متصل شد! آماده برای بازی...")

    # اجرای تسک‌های زمان‌بندی شده
    asyncio.create_task(meow_job())
    asyncio.create_task(fish_job())
    asyncio.create_task(pishi_job())
    
    await client.run_until_disconnected()

if __name__ == '__main__':
    asyncio.run(main())
