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
# تنظیمات هاردکد شده (غیرقابل پاک شدن با ری‌استارت)
# ==========================================
# اضافه کردن -100 به ابتدای آیدی چنل‌ها (استاندارد API تلگرام)
TARGET_CHANNELS = [-1003382427670, -1002790319024]
NOTIFICATION_USER = '@luv_potion'

# متغیر برای روشن/خاموش کردن مانیتور چنل (پیش‌فرض: روشن)
monitoring_is_active = True

# ==========================================
# بخش اول: گوش دادن به پیام‌ها و کلیک سریع (ربات بازی)
# ==========================================
@client.on(events.NewMessage(chats=CHAT_TARGET))
async def click_button_handler(event):
    if event.message.buttons:
        await asyncio.sleep(1) 
        msg_text = event.message.text or ""
        
        if 'گربه خیابونی' in msg_text:
            try:
                await event.message.click(0)
                print("🐈 ✅ پیام 'گربه خیابونی' شکار شد!")
                return
            except Exception as e:
                pass

        for row in event.message.buttons:
            for button in row:
                btn_text = button.text or ""
                
                if 'پیشی بخوره' in btn_text or 'بده' in btn_text:
                    try:
                        await button.click()
                        print("🐟 ✅ روی دکمه 'بده پیشی بخوره' کلیک شد!")
                        return 
                    except Exception as e:
                        pass
                
                elif 'برداشت' in btn_text or 'پوینت' in btn_text:
                    try:
                        await button.click()
                        print("💰 ✅ روی دکمه 'برداشت میو پوینت ها' کلیک شد!")
                        return 
                    except Exception as e:
                        pass

# ==========================================
# بخش دوم: دستورات روشن و خاموش کردن (/on و /off)
# ==========================================
# این دستورات رو می‌تونید هم تو سیو مسیج (me) بفرستید هم از طرف @luv_potion
@client.on(events.NewMessage(chats=['me', NOTIFICATION_USER]))
async def toggle_monitoring(event):
    global monitoring_is_active
    text = event.raw_text.strip().lower()

    if text == '/on':
        monitoring_is_active = True
        await event.reply("✅ مانیتور کردن دو چنل روشن شد.")
    
    elif text == '/off':
        monitoring_is_active = False
        await event.reply("❌ مانیتور کردن دو چنل خاموش شد. (ربات بازی همچنان روشنه)")

# ==========================================
# بخش سوم: چک کردن دقیقاً همون دو چنل مشخص شده
# ==========================================
@client.on(events.NewMessage(chats=TARGET_CHANNELS))
async def watch_specific_channels_handler(event):
    # اگه مانیتور چنل‌ها خاموش بود، بی‌خیال شو
    if not monitoring_is_active:
        return

    try:
        chat = await event.get_chat()
        username = chat.username if chat.username else None
        chat_id_str = str(chat.id)

        # ساخت لینک پیام
        if username:
            msg_link = f"https://t.me/{username}/{event.id}"
            channel_display = f"@{username}"
        else:
            clean_id = chat_id_str.replace("-100", "")
            msg_link = f"https://t.me/c/{clean_id}/{event.id}"
            channel_display = "کانال خصوصی"

        alert_text = (
            f"این چنل یه پیام جدید گذاشته:\n"
            f"نام: {chat.title}\n"
            f"آیدی: {channel_display}\n\n"
            f"🔗 ورود به چنل و دیدن پیام:\n{msg_link}\n\n"
            f"و با هر پیامش اینو بگه"
        )
        
        # ارسال پیام به آیدی لشن شده
        await client.send_message(NOTIFICATION_USER, alert_text)
            
    except Exception as e:
        print(f"Error checking specific channels: {e}")

# ==========================================
# بخش چهارم: ارسال پیام‌های زمان‌بندی شده
# ==========================================
async def meow_job():
    while True:
        try:
            await client.send_message(CHAT_TARGET, 'میو')
        except Exception:
            pass
        await asyncio.sleep(290) 

async def fish_job():
    await asyncio.sleep(5) 
    while True:
        try:
            await client.send_message(CHAT_TARGET, 'ماهی')
        except Exception:
            pass
        await asyncio.sleep(3600) 

async def pishi_job():
    await asyncio.sleep(15) 
    while True:
        try:
            await client.send_message(CHAT_TARGET, 'پیشی')
        except Exception:
            pass
        await asyncio.sleep(18000) 

# ==========================================
# بخش پنجم: وب سرور رندر و اجرای اصلی
# ==========================================
async def handle(request):
    return web.Response(text="Bot is running! (Hardcoded Channels + Game)")

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
    print("✅ یوزربات متصل شد! آماده کار...")

    asyncio.create_task(meow_job())
    asyncio.create_task(fish_job())
    asyncio.create_task(pishi_job())
    
    await client.run_until_disconnected()

if __name__ == '__main__':
    asyncio.run(main())
