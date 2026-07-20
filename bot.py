import os
import asyncio
import json
from aiohttp import web
from telethon import TelegramClient, events
from telethon.sessions import StringSession
from telethon.tl.types import PeerChannel

# دریافت اطلاعات از سرور رندر
API_ID = int(os.environ.get('API_ID', 2040))
API_HASH = os.environ.get('API_HASH', 'b18441a1ff607e10a989891a5462e627')
SESSION_STRING = os.environ.get('SESSION_STRING', '')
CHAT_TARGET = os.environ.get('CHAT_TARGET', '')

if CHAT_TARGET.lstrip('-').isdigit():
    CHAT_TARGET = int(CHAT_TARGET)

client = TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH)

# ==========================================
# سیستم ذخیره‌سازی دائمی چنل‌ها در فایل
# ==========================================
CHANNELS_FILE = 'channels.json'
TARGET_FILE = 'target.txt'

def load_channels():
    if os.path.exists(CHANNELS_FILE):
        try:
            with open(CHANNELS_FILE, 'r') as f:
                return set(json.load(f))
        except:
            return set()
    return set()

def save_channels(channels):
    with open(CHANNELS_FILE, 'w') as f:
        json.dump(list(channels), f)

def load_target():
    if os.path.exists(TARGET_FILE):
        with open(TARGET_FILE, 'r') as f:
            return f.read().strip()
    return 'me'

def save_target(target):
    with open(TARGET_FILE, 'w') as f:
        f.write(target)

# بارگذاری اطلاعات هنگام روشن شدن ربات
monitored_channels = load_channels()
notification_target = load_target()

# ==========================================
# بخش اول: گوش دادن به پیام‌ها و کلیک سریع
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
# بخش دوم: مدیریت چنل‌ها
# ==========================================
@client.on(events.NewMessage(chats='me'))
async def manage_channels_handler(event):
    global notification_target
    
    text = event.raw_text.strip()
    text_lower = text.lower()

    if text_lower.startswith('/set '):
        target = text[5:].strip()
        notification_target = target
        save_target(target) # ذخیره در فایل
        
        if target.lower() == 'me':
            await event.reply("✅ مقصد پیام‌ها تغییر کرد. ارسال به: **(سیو مسیج)**")
        else:
            await event.reply(f"✅ مقصد پیام‌ها تغییر کرد. ارسال به پیوی: **{target}**")
        return

    if text_lower == '/check':
        target_display = notification_target if notification_target != 'me' else "(سیو مسیج)"
        
        if not monitored_channels:
            msg = f"📭 لیست چنل‌ها خالیه!\n\n🎯 مقصد پیام‌ها: {target_display}"
        else:
            msg = "📋 لیست چنل‌هایی که در حال چک شدن هستن:\n\n"
            for ch in monitored_channels:
                msg += f"▪️ {ch}\n"
            msg += f"\n🎯 مقصد پیام‌ها: {target_display}"
            
        await event.reply(msg)
        return

    if text_lower == 'delete all':
        monitored_channels.clear()
        save_channels(monitored_channels) # ذخیره تغییرات
        await event.reply("🗑 ✅ تمام چنل‌ها با موفقیت پاک شدند!")
        return

    if text_lower.startswith('delete '):
        target = text[7:].strip().replace('@', '') 
        
        if target in monitored_channels:
            monitored_channels.remove(target)
            save_channels(monitored_channels)
            await event.reply(f"❌ چنل {target} از لیست حذف شد.")
        else:
            target_id = f"-100{target}" if not target.startswith('-100') else target
            if target_id in monitored_channels:
                monitored_channels.remove(target_id)
                save_channels(monitored_channels)
                await event.reply(f"❌ چنل {target_id} از لیست حذف شد.")
            else:
                await event.reply("⚠️ این چنل تو لیست نبود.")
        return

    channel_id_or_user = None

    if event.fwd_from and event.fwd_from.from_id:
        if isinstance(event.fwd_from.from_id, PeerChannel):
            channel_id_or_user = f"-100{event.fwd_from.from_id.channel_id}"
            
    elif text.startswith('@') or text.startswith('-100'):
        channel_id_or_user = text.replace('@', '') 

    if channel_id_or_user:
        monitored_channels.add(channel_id_or_user)
        save_channels(monitored_channels) # ذخیره تغییرات در فایل
        await event.reply(f"✅ چنل با موفقیت ست شد!\n(آیدی ثبت شده: {channel_id_or_user})")

# ==========================================
# بخش سوم: چک کردن چنل‌ها برای پیام جدید
# ==========================================
@client.on(events.NewMessage())
async def watch_channels_handler(event):
    if not event.is_channel or event.is_group:
        return

    try:
        chat_id_str = str(event.chat_id)
        chat = await event.get_chat()
        username = chat.username if chat.username else None

        if chat_id_str in monitored_channels or (username and username in monitored_channels):
            
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
            
            try:
                await client.send_message(notification_target, alert_text)
            except Exception as e:
                print(f"Error sending to target: {e}")
                
    except Exception as e:
        print(f"Error: {e}")

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
    return web.Response(text="Bot is running! (Memory Loss Protected)")

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
