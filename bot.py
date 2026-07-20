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
# متغیرهای مربوط به چنل‌ها و مقصد پیام‌ها
# ==========================================
monitored_channels = set()
notification_target = 'me'  # پیش‌فرض: پیام‌های ذخیره‌شده (Saved Messages)

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
# بخش دوم: مدیریت چنل‌ها (/set, /check, delete, delete all, افزودن)
# ==========================================
@client.on(events.NewMessage(chats='me'))
async def manage_channels_handler(event):
    global notification_target
    
    text = event.raw_text.strip()
    text_lower = text.lower()

    # ۱. تغییر مقصد پیام‌ها (مثلاً /set @username)
    if text_lower.startswith('/set '):
        target = text[5:].strip()
        notification_target = target
        
        if target.lower() == 'me':
            await event.reply("✅ مقصد پیام‌ها تغییر کرد. از این به بعد آلارم‌ها به **همینجا (سیو مسیج)** ارسال میشن.")
        else:
            await event.reply(f"✅ مقصد پیام‌ها تغییر کرد. از این به بعد آلارم‌های چنل به جای سیو مسیج، به پیوی **{target}** ارسال میشن.")
        return

    # ۲. بررسی وضعیت و چنل‌های ثبت شده
    if text_lower == '/check':
        target_display = notification_target if notification_target != 'me' else "(ارسال به همینجا - سیو مسیج)"
        
        if not monitored_channels:
            msg = f"📭 لیست چنل‌ها خالیه و هیچ چنلی ست نشده!\n\n🎯 مقصد پیام‌ها: {target_display}"
        else:
            msg = "📋 لیست چنل‌هایی که در حال چک شدن هستن:\n\n"
            for ch in monitored_channels:
                msg += f"▪️ {ch}\n"
            msg += f"\n🎯 مقصد پیام‌ها: {target_display}"
            
        await event.reply(msg)
        return

    # ۳. پاک کردن کل چنل‌ها به صورت یکجا
    if text_lower == 'delete all':
        monitored_channels.clear()
        await event.reply("🗑 ✅ تمام چنل‌ها با موفقیت از لیست حذف شدند!")
        return

    # ۴. پاک کردن یک چنل خاص (مثلا delete @username)
    if text_lower.startswith('delete '):
        target = text[7:].strip().replace('@', '') 
        
        if target in monitored_channels:
            monitored_channels.remove(target)
            await event.reply(f"❌ چنل {target} از لیست حذف شد و دیگه چک نمیشه.")
        else:
            target_id = f"-100{target}" if not target.startswith('-100') else target
            if target_id in monitored_channels:
                monitored_channels.remove(target_id)
                await event.reply(f"❌ چنل {target_id} از لیست حذف شد و دیگه چک نمیشه.")
            else:
                await event.reply("⚠️ این چنل اصلاً تو لیست نبود.")
        return

    # ۵. ست کردن چنل جدید (با فوروارد یا ارسال آیدی)
    channel_id_or_user = None

    if event.fwd_from and event.fwd_from.from_id:
        if isinstance(event.fwd_from.from_id, PeerChannel):
            channel_id_or_user = f"-100{event.fwd_from.from_id.channel_id}"
            
    elif text.startswith('@') or text.startswith('-100'):
        channel_id_or_user = text.replace('@', '') 

    if channel_id_or_user:
        monitored_channels.add(channel_id_or_user)
        await event.reply(f"✅ چنل با موفقیت ست شد و چک می‌شود!\n(آیدی ثبت شده: {channel_id_or_user})")

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
            
            # ساخت لینک برای کلیک کردن و رفتن به همون پیام تو چنل
            if username:
                # اگه چنل پابلیک باشه
                msg_link = f"https://t.me/{username}/{event.id}"
                channel_display = f"@{username}"
            else:
                # اگه چنل پرایوت باشه
                clean_id = chat_id_str.replace("-100", "")
                msg_link = f"https://t.me/c/{clean_id}/{event.id}"
                channel_display = "کانال خصوصی"

            # متن نهایی پیام
            alert_text = (
                f"این چنل یه پیام جدید گذاشته:\n"
                f"نام: {chat.title}\n"
                f"آیدی: {channel_display}\n\n"
                f"🔗 ورود به چنل و دیدن پیام:\n{msg_link}\n\n"
                f"و با هر پیامش اینو بگه"
            )
            
            try:
                await client.send_message(notification_target, alert_text)
            except Exception as target_error:
                await client.send_message('me', f"❌ نتونستم آلارم رو به {notification_target} بفرستم!\nخطا: {target_error}")
                
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
    return web.Response(text="Bot is running completely (Game + Channel Monitor + Check CMD + Delete All)")

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
