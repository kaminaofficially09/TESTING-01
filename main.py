
import os
import telebot
import json
import requests
import logging
import time
from pymongo import MongoClient
from datetime import datetime, timedelta
import certifi
import random
from subprocess import Popen
from threading import Thread
import asyncio
import aiohttp
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
import uuid

loop = asyncio.get_event_loop()

TOKEN = '7954860124:AAGtdELkkMxt_rze2uir1yWcZSlcz6qQ9-Y'
MONGO_URI = 'mongodb+srv://harry:Sachdeva@cluster1.b02ct.mongodb.net/?retryWrites=true&w=majority&appName=Cluster1'
FORWARD_CHANNEL_ID = -1002151412648
CHANNEL_ID = -1002151412648
ERROR_CHANNEL_ID = -1002151412648

ADMIN_IDS = [5344691638, 7885196586]

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

client = MongoClient(MONGO_URI, tlsCAFile=certifi.where())
db = client['Harvinder']
users_collection = db.users

bot = telebot.TeleBot(TOKEN)
REQUEST_INTERVAL = 1

blocked_ports = [8700, 20000, 443, 17500, 9031, 20002, 20001]  # Blocked ports list
proxy_list = [
        "https://43.134.234.74:443", "https://175.101.18.21:5678", "https://179.189.196.52:5678", 
        "https://162.247.243.29:80", "https://173.244.200.154:44302", "https://173.244.200.156:64631", 
        "https://207.180.236.140:51167", "https://123.145.4.15:53309", "https://36.93.15.53:65445", 
        "https://1.20.207.225:4153", "https://83.136.176.72:4145", "https://115.144.253.12:23928", 
        "https://78.83.242.229:4145", "https://128.14.226.130:60080", "https://194.163.174.206:16128", 
        "https://110.78.149.159:4145", "https://190.15.252.205:3629", "https://101.43.191.233:2080", 
        "https://202.92.5.126:44879", "https://221.211.62.4:1111", "https://58.57.2.46:10800", 
        "https://45.228.147.239:5678", "https://43.157.44.79:443", "https://103.4.118.130:5678", 
        "https://37.131.202.95:33427", "https://172.104.47.98:34503", "https://216.80.120.100:3820", 
        "https://182.93.69.74:5678", "https://8.210.150.195:26666", "https://49.48.47.72:8080", 
        "https://37.75.112.35:4153", "https://8.218.134.238:10802", "https://139.59.128.40:2016", 
        "https://45.196.151.120:5432", "https://24.78.155.155:9090", "https://212.83.137.239:61542", 
        "https://46.173.175.166:10801", "https://103.196.136.158:7497", "https://82.194.133.209:4153", 
        "https://210.4.194.196:80", "https://88.248.2.160:5678", "https://116.199.169.1:4145", 
        "https://77.99.40.240:9090", "https://143.255.176.161:4153", "https://172.99.187.33:4145", 
        "https://43.134.204.249:33126", "https://185.95.227.244:4145", "https://197.234.13.57:4145", 
        "https://81.12.124.86:5678", "https://101.32.62.108:1080", "https://192.169.197.146:55137", 
        "https://82.117.215.98:3629", "https://202.162.212.164:4153", "https://185.105.237.11:3128", 
        "https://123.59.100.247:1080", "https://192.141.236.3:5678", "https://182.253.158.52:5678", 
        "https://164.52.42.2:4145", "https://185.202.7.161:1455", "https://186.236.8.19:4145", 
        "https://36.67.147.222:4153", "https://118.96.94.40:80", "https://27.151.29.27:2080", 
        "https://181.129.198.58:5678", "https://200.105.192.6:5678", "https://103.86.1.255:4145", 
        "https://171.248.215.108:1080", "https://181.198.32.211:4153", "https://188.26.5.254:4145", 
        "https://34.120.231.30:80", "https://103.23.100.1:4145", "https://194.4.50.62:12334", 
        "https://201.251.155.249:5678", "https://37.1.211.58:1080", "https://86.111.144.10:4145", 
        "https://80.78.23.49:1080"
    ]

def send_error_message(error, chat_id=None, user_id=None):
    """Sends an error message to the error channel."""
    error_message = f"Error: {error}\n"
    if chat_id:
        error_message += f"Chat ID: {chat_id}\n"
    if user_id:
        error_message += f"User ID: {user_id}\n"
    try:
        bot.send_message(ERROR_CHANNEL_ID, error_message)
    except Exception as e:
        logging.error(f"Failed to send error message to error channel: {e}")

def get_proxy():
    """Returns a random proxy from the proxy list."""
    return random.choice(proxy_list)

def update_proxy():
    """Updates the bot's proxy."""
    try:
        proxy = get_proxy()
        telebot.apihelper.proxy = {'https': proxy}
        logging.info(f"Proxy updated to: {proxy}")
    except Exception as e:
        logging.error(f"Failed to update proxy: {e}")
        send_error_message(f"Failed to update proxy: {e}")

def is_admin(user_id):
    """Checks if a user ID is in the list of admin IDs."""
    return user_id in ADMIN_IDS

@bot.message_handler(commands=['update_proxy'])
def update_proxy_command(message):
    """Handles the /update_proxy command."""
    chat_id = message.chat.id
    user_id = message.from_user.id

    try:
        update_proxy()
        bot.send_message(chat_id, "Proxy updated successfully.")
    except Exception as e:
        logging.error(f"Error updating proxy for user {user_id}: {e}")
        send_error_message(f"Failed to update proxy for user {user_id}: {e}", chat_id=chat_id, user_id=user_id)
        bot.send_message(chat_id, f"Failed to update proxy: {e}")

@bot.message_handler(commands=['approve', 'disapprove'])
def handle_user_approval(message):
    """Handles the /approve and /disapprove commands for admin users."""
    user_id = message.from_user.id
    chat_id = message.chat.id
    
    if not is_admin(user_id):
        bot.reply_to(message, "*You are not authorized to use this command.*", parse_mode='Markdown')
        return

    cmd_parts = message.text.split()
    if len(cmd_parts) < 2:
        bot.reply_to(message, "*Invalid command format. Use /approve <user_id> <plan> <days> or /disapprove <user_id>.*", parse_mode='Markdown')
        return
    
    action = cmd_parts[0]
    try:
        target_user_id = int(cmd_parts[1])
    except ValueError:
        bot.reply_to(message, "*Invalid User ID. Must be an integer.*", parse_mode='Markdown')
        return

    if action == '/approve':
        if len(cmd_parts) < 4:
            bot.reply_to(message, "*Invalid command format for /approve. Use /approve <user_id> <plan> <days>*", parse_mode='Markdown')
            return
        try:
            plan = int(cmd_parts[2])
            days = int(cmd_parts[3])
        except ValueError:
            bot.reply_to(message, "*Invalid plan or days format. Must be an integer.*", parse_mode='Markdown')
            return
        
        valid_until = (datetime.now() + timedelta(days=days)).date().isoformat()
        users_collection.update_one(
            {"user_id": target_user_id},
            {"$set": {"plan": plan, "valid_until": valid_until}},
            upsert=True
        )
        msg_text = f"*User {target_user_id} approved with plan {plan} for {days} days.*"
    elif action == '/disapprove':
        users_collection.update_one(
            {"user_id": target_user_id},
            {"$set": {"plan": 0, "valid_until": None}},
            upsert=True
        )
        msg_text = f"*User {target_user_id} disapproved.*"
    else:
        bot.reply_to(message, "*Invalid action. Use /approve or /disapprove.*", parse_mode='Markdown')
        return
    
    bot.reply_to(message, msg_text, parse_mode='Markdown')
    bot.send_message(CHANNEL_ID, msg_text, parse_mode='Markdown')
@bot.message_handler(commands=['genkey'])
def genkey_command(message):
    """Handles the /genkey command, generating unique keys."""
    user_id = message.from_user.id
    chat_id = message.chat.id
    
    if not is_admin(user_id):
        bot.reply_to(message, "*You are not authorized to use this command.*", parse_mode='Markdown')
        return
    
    key = str(uuid.uuid4())
    
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("Copy Key", callback_data=f'copy_key:{key}'))
    bot.send_message(chat_id, f"*Generated Key:*\n`{key}`", reply_markup = markup, parse_mode='Markdown')


@bot.callback_query_handler(func=lambda call: call.data.startswith('copy_key:'))
def copy_key_callback(call):
    """Handles the callback query for the "Copy Key" button"""
    key = call.data.split(':')[1]
    bot.answer_callback_query(call.id, text=f"Key copied to your clipboard:\n {key}", show_alert=True)
    #bot.send_message(call.message.chat.id, f"*Key copied to your clipboard:\n {key}*", parse_mode='Markdown')


@bot.message_handler(commands=['redeem'])
def redeem_command(message):
    """Handles the /redeem command to add to the user plan."""
    user_id = message.from_user.id
    chat_id = message.chat.id
    
    cmd_parts = message.text.split()
    if len(cmd_parts) < 2:
        bot.reply_to(message, "*Invalid format. Use /redeem <key>*", parse_mode='Markdown')
        return

    key = cmd_parts[1]
    
    # Replace with logic to validate the key
    if key == "testkey":
        valid_until = (datetime.now() + timedelta(days=30)).date().isoformat()
        users_collection.update_one(
            {"user_id": user_id},
            {"$set": {"plan": 2, "valid_until": valid_until}},
             upsert = True
         )
        bot.send_message(chat_id, f"*Key redeemed successfully for 30 days with Instant++ plan!*", parse_mode='Markdown')
    else:
        bot.reply_to(message, "*Invalid key.*", parse_mode='Markdown')
        
        
        
# Welcome Message
@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("𝗔𝘁𝘁𝗮𝗰𝗸 🚀", "𝗚𝗲𝗻𝗸𝗲𝘆 🔑", "𝗥𝗲𝗱𝗲𝗲𝗺 🔐", "𝐀𝐜𝐜𝐨𝐮𝐧𝐭🏦", "𝐇𝐞𝐥𝐩❓","𝐂𝐚𝐧𝐚𝐫𝐲 📟")
    bot.send_message(message.chat.id, "⚡ 𝗣𝗿𝗶𝗺𝗶𝘂𝗺 𝗨𝘀𝗲𝗿 ⚡", reply_markup=markup)

@bot.message_handler(func=lambda message: True)
def handle_text(message):
    if message.text == "𝗔𝘁𝘁𝗮𝗰𝗸 🚀":
        #bot.reply_to(message, "*𝐔𝐬𝐞 𝐋𝐞𝐬𝐬 𝐓𝐡𝐚𝐧 𝟑𝟎𝟎 𝐒𝐞𝐜𝐨𝐧𝐝*", parse_mode='Markdown')
        handle_attack(message)
       # bot.reply_to(message, "🚀 Use /attack <IP> <Port> <Time>")
    elif message.text == "𝗥𝗲𝗱𝗲𝗲𝗺 🔐":
        bot.reply_to(message, "Use /redeem <key>")
    elif message.text == "𝗚𝗲𝗻𝗸𝗲𝘆 🔑":
        bot.reply_to(message, "𝗨𝘀𝗲 /genkey")        
   # elif message.text == "𝐀𝐜𝐜𝐨𝐮𝐧𝐭🏦":
       # user_id = message.from_user.id
     #   user_data = users_collection.find_one({"user_id": user_id})
      #  if user_data:
       #     plan = user_data.get('plan', 'N/A')
          #  valid_until = user_data.get('valid_until', 'N/A')
           # bot.reply_to(message, f"Plan: {plan}\nValid Until: {valid_until}")
        else:
            bot.reply_to(message, "🔑 𝗡𝗢 𝗔𝗖𝗖𝗢𝗨𝗡𝗧")
            
    elif message.text == "𝐂𝐚𝐧𝐚𝐫𝐲 📟":
        canary_command(message)
    elif message.text == "𝐇𝐞𝐥𝐩❓":
        bot.reply_to(message, "https://t.me/Bgmi_owner_420")
    else:
        bot.reply_to(message, "Invalid option.")
        
    
@bot.message_handler(func=lambda message: True)
def handle_messages(message):
    """Handles all messages received by the bot."""
    user_id = message.from_user.id
    chat_id = message.chat.id
    if message.text == "Instant Plan 🧡":
        bot.reply_to(message, "*Instant Plan selected*", parse_mode='Markdown')
    elif message.text == "𝗔𝘁𝘁𝗮𝗰𝗸 🚀":
        bot.reply_to(message, "*𝗔𝘁𝘁𝗮𝗰𝗸 selected. Please provide IP, Port, Time, Threads and Method*", parse_mode='Markdown')
        bot.register_next_step_handler(message, process_attack_parameters)
  #  elif message.text == "Canary Download✔️":
        #bot.send_message(chat_id, "*Please use the following link for Canary Download: https://t.me/DarkDdosHack/88*", parse_mode='Markdown')
    elif message.text == "𝐀𝐜𝐜𝐨𝐮𝐧𝐭🏦":
        user_id = message.from_user.id
        user_data = users_collection.find_one({"user_id": user_id})
        if user_data:
            username = message.from_user.username
            plan = user_data.get('plan', 'N/A')
            valid_until = user_data.get('valid_until', 'N/A')
            current_time = datetime.now().isoformat()
            response = (f"*USERNAME: {username}\n"
                        f"Plan: {plan}\n"
                        f"Valid Until: {valid_until}\n"
                        f"Current Time: {current_time}*")
        else:
            response = "*No account information found. Please contact the administrator.*"
        bot.reply_to(message, response, parse_mode='Markdown')
   # elif message.text == "Help❓":
      #  bot.reply_to(message, "*@DarkDdosHack*", parse_mode='Markdown')
    elif message.text == "Contact admin✔️":
        bot.reply_to(message, "*@DarkDdosHack*", parse_mode='Markdown')
    else:
        bot.reply_to(message, "*Invalid option*", parse_mode='Markdown')
        
@bot.message_handler(commands=['canary'])
def canary_command(message):
    response = ("*📥 Download the HttpCanary APK Now! 📥*\n\n"
                "*🔍 Track IP addresses with ease and stay ahead of the game! 🔍*\n"
                "*💡 Utilize this powerful tool wisely to gain insights and manage your network effectively. 💡*\n\n"
                "*Choose your platform:*")

    markup = types.InlineKeyboardMarkup()
    button1 = types.InlineKeyboardButton(
        text="📱 𝗗𝗼𝘄𝗻𝗹𝗼𝗮𝗱 𝗙𝗼𝗿 𝗔𝗻𝗱𝗿𝗼𝗶𝗱 📱",
        url="https://t.me/c/DarkDdosHack/88")
    button2 = types.InlineKeyboardButton(
        text="🍎 𝗗𝗼𝘄𝗻𝗹𝗼𝗮𝗱 𝗳𝗼𝗿 𝗶𝗢𝗦 🍎",
        url="https://apps.apple.com/in/app/surge-5/id1442620678")

    markup.add(button1)
    markup.add(button2)

    try:
        bot.send_message(message.chat.id,
                         response,
                         parse_mode='Markdown',
                         reply_markup=markup)
    except Exception as e:
        logging.error(f"Error while processing /canary command: {e}")

def process_attack_parameters(message):
    try:
        parts = message.text.split()
        if len(parts) != 5:
            bot.reply_to(message, "*Invalid format. Please provide IP, Port, Time, Threads and Method separated by spaces.*", parse_mode='Markdown')
            return

        ip, port, time_duration, threads, method = parts
        
        # Validate input
        try:
           int(port)
           int(time_duration)
           int(threads)
        except ValueError:
           bot.reply_to(message, "*Invalid input. Port, Time and Threads must be integers.*", parse_mode='Markdown')
           return

        if not (1 <= int(port) <= 65535):
            bot.reply_to(message, "*Invalid port number. Must be between 1 and 65535.*", parse_mode='Markdown')
            return
        if not (1 <= int(threads) <= 1000):
             bot.reply_to(message, "*Invalid threads number. Must be between 1 and 1000.*", parse_mode='Markdown')
             return
        if not (1 <= int(time_duration) <= 3600):
              bot.reply_to(message, "*Invalid time number. Must be between 1 and 3600.*", parse_mode='Markdown')
              return
        # Run attack
        bot.reply_to(message, "*Starting attack...*", parse_mode='Markdown')
        attack_result = run_attack(ip, port, time_duration, threads, method)
        bot.reply_to(message, attack_result, parse_mode='Markdown')
    except Exception as e:
       logging.error(f"Error handling attack params: {e}")
       bot.reply_to(message, f"*Error processing attack parameters: {e}*", parse_mode='Markdown')

if __name__ == '__main__':
    update_proxy()
    asyncio_thread = Thread(target=start_asyncio_thread, daemon=True)
    asyncio_thread.start()
    logging.info("Starting Codespace activity keeper and Telegram bot...")
    while True:
        try:
            bot.polling(none_stop=True)
        except Exception as e:
            logging.error(f"An error occurred while polling: {e}")
        logging.info(f"Waiting for {REQUEST_INTERVAL} seconds before the next request...")
        time.sleep(REQUEST_INTERVAL)
