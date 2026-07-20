import os
import asyncio
from aiohttp import web
from telethon import TelegramClient, events
from telethon.sessions import StringSession
from telethon.tl.types import PeerChannel

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
# متغیر برای ذخیره چنل‌هایی که باید چک شوند
# ==========================================
monitored_channels = set()

# ==========================================
# بخش اول: گوش دادن به پیام‌ها و کلیک سریع (ربات بازی)
# ==========================================
@client.on(events.NewMessage(chats=CHAT_TARGET))
async def click_button_handler(event):
    """این تابع بلافاصله پیام‌ها رو بررسی میکنه و دکمه رو میزنه"""
    if event.message.buttons:
        await asyncio.sleep(1) 
        msg_text = event.message.text or ""
        
        if 'گربه خیابونی' in msg_text:
            try:
                await event.message.click(0)
                print("🐈 ✅ پیام 'گربه خیابونی' شکار شد!")
                return
            except Exception as e:
                print(f"❌ خطا در شکار گربه خیابونی: {e}")

        for row in event.message.buttons:
            for button in row:
                btn_text = button.text or ""
                
                if 'پیشی بخوره' in btn_text or 'بده' in btn_text:
                    try:
                        await button.click()
                        print("🐟 ✅ روی دکمه 'بده پیشی بخوره' کلیک شد!")
                        return 
                    except Exception as e:
                        print(f"❌ خطا در کلیک ماهی: {e}")
                
                elif 'برداشت' in btn_text or 'پوینت' in btn_text:
                    try:
                        await button.click()
                        print("💰 ✅ روی دکمه 'برداشت میو پوینت ها' کلیک شد!")
                        return 
                    except Exception as e:
                        print(f"❌ خطا در کلیک برداشت: {e}")

# ==========================================
# بخش دوم: مدیریت چنل‌ها (potion, اضافه کردن, delete)
# ==========================================
# این بخش فقط به پیام‌هایی که در "پیام‌های ذخیره شده" (me) می‌فرستید واکنش نشان می‌دهد
@client.on(events.NewMessage(chats='me'))
async def manage_channels_handler(event):
    text = event.raw_text.strip()
    text_lower = text.lower()

    # ۱. هندلر برای potion
    if text_lower == 'potion':
        await event.reply("پدب رو چک کن")
        return

    # ۲. هندلر برای پاک کردن چنل (مثلا delete @username)
    if text_lower.startswith('delete '):
        target = text[7:].strip().replace('@', '') # کلمه بعد از delete رو میگیره و @ رو حذف میکنه
        
        if target in monitored_channels:
            monitored_channels.remove(target)
            await event.reply(f"❌ چنل {target} از لیست حذف شد و دیگه چک نمیشه.")
        else:
            # بررسی حالت آیدی عددی
            target_id = f"-100{target}" if not target.startswith('-100') else target
            if target_id in monitored_channels:
                monitored_channels.remove(target_id)
                await event.reply(f"❌ چنل {target_id} از لیست حذف شد و دیگه چک نمیشه.")
            else:
                await event.reply("⚠️ این چنل اصلاً تو لیست نبود.")
        return

    # ۳. هندلر برای ست کردن چنل جدید
    channel_id_or_user = None

    # بررسی اینکه آیا فوروارد شده است؟
    if event.fwd_from and event.fwd_from.from_id:
        if isinstance(event.fwd_from.from_id, PeerChannel):
            channel_id_or_user = f"-100{event.fwd_from.from_id.channel_id}"
            
    # بررسی اینکه آیا متنی حاوی آیدی ارسال شده؟
    elif text.startswith('@') or text.startswith('-100'):
        channel_id_or_user = text.replace('@', '') # ذخیره بدون @

    if channel_id_or_user:
        monitored_channels.add(channel_id_or_user)
        await event.reply(f"✅ چنل با موفقیت ست شد و چک می‌شود!\n(آیدی ثبت شده: {channel_id_or_user})")


# ==========================================
# بخش سوم: چک کردن چنل‌ها برای پیام جدید
# ==========================================
@client.on(events.NewMessage())
async def watch_channels_handler(event):
    # اگر پیام در چنل نبود بی‌خیال شو
    if not event.is_channel or event.is_group:
        return

    try:
        chat_id_str = str(event.chat_id)
        chat = await event.get_chat()
        username = chat.username if chat.username else None

        # بررسی اینکه آیا این چنل در لیست ما هست یا نه
        if chat_id_str in monitored_channels or (username and username in monitored_channels):
            # ارسال پیام به پیوی خودتون (Saved Messages)
            alert_text = f"این چنل ({chat.title or username}) یه پیام جدید داره\nو با هر پیامش اینو بگه"
            await client.send_message('me', alert_text)
            
            # اگه خواستی خود پیامِ چنل هم برات فوروارد بشه خط پایین رو از کامنت دربیار:
            # await event.forward_to('me')
    except Exception as e:
        print(f"Error checking channel msg: {e}")

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
    return web.Response(text="Bot is running completely (Game + Channel Monitor)")

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
