import telebot
from telebot import types
import random
import string
import main

CHAVE_API = "6553689684:AAHyV36Ht9-o1G7fLnIhYaMprIT0fdXzrnA"
link = "https://t.me/rogetiobot"

bot = telebot.TeleBot(CHAVE_API)

user_requests = {}
chat_sup_id = -1002056135520
chat_ins_id = -4007534836
chat_user_id = None

@bot.message_handler(commands=["Supervisao_realizada"])
def part_verified(message):
    original_message_id = user_requests.get(chat_sup_id, {}).get("message_id")
    serial_num = user_requests.get(chat_sup_id, {}).get("serial_num")
    text = f"✅ - {serial_num}"
    bot.reply_to(message, text)
    bot.delete_message(chat_sup_id, original_message_id)

@bot.message_handler(commands=["Inspec_realizada"])
def part_verified(message):
    original_message_id = user_requests.get(chat_ins_id, {}).get("message_id")
    serial_num = user_requests.get(chat_ins_id, {}).get("serial_num")
    text = f"✅ - {serial_num}"
    bot.reply_to(message, text)
    bot.delete_message(chat_ins_id, original_message_id)

def send_denied_inspec(code, inspec, part):
    text = ("O inspetor " + inspec + " (código " + code +
             ") reprovou a peça com número de série " + part +
             " e a mesma requer atenção!" + """
             /Supervisao_realizada - Peça já verificada""")
    msg = bot.send_message(chat_sup_id, text)
    user_requests[chat_sup_id] = {"message_id": msg.message_id, "serial_num" : part}

def send_denied_verify(part):
    text = ("A peça com número de série " + part +
             "passou pela esteira e foi reprovada." + """
    
    Por favor, verificar!

             /Inspecao_realizada - Peça já verificada""")
    msg = bot.send_message(chat_ins_id, text)
    user_requests[chat_ins_id] = {"message_id": msg.message_id, "serial_num" : part}

'''@bot.message_handler()
def responder(message):
    msg = message.chat.id
    print(msg)'''

def send_password_message(chat_id, code):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button1 = types.KeyboardButton("Fui eu")
    button2 = types.KeyboardButton("Não fui eu")
    keyboard.add(button1, button2)
    text = "Olá! Verifiquei que você solicitou a alteração de sua senha. Foi você mesmo?"
    msg = bot.send_message(chat_id, text, reply_markup=keyboard)
    user_requests[chat_user_id] = {"message_id": msg.message_id, "code": code}

@bot.message_handler(func=lambda message: message.text == "Fui eu")
def handle_fui_eu(message):
    user_id = message.chat.id
    code = user_requests.get(chat_user_id, {}).get("code")
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button3 = types.KeyboardButton("Já anotei")
    keyboard.add(button3)
    password = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(6))
    main.change_password(password, code)
    text = "Sua senha foi alterada para: ```" + password + "```"
    msg = bot.send_message(message.chat.id, text, reply_markup=keyboard)
    original_message_id = user_requests.get(user_id, {}).get("message_id")
    if original_message_id:
        bot.delete_message(user_id, original_message_id)
    user_requests[chat_user_id] = {"message_id": msg.message_id}
    
@bot.message_handler(func=lambda message: message.text == "Já anotei")
def handle_ja_anotei(message):
    user_id = message.chat.id
    original_message_id = user_requests.get(user_id, {}).get("message_id")
    remove_keyboard = types.ReplyKeyboardRemove()
    text = "Obrigado! Recomendamos fortemente que altere a senha assim que acessar o sistema"
    bot.send_message(message.chat.id, text, reply_markup=remove_keyboard)
    original_message_id = user_requests.get(user_id, {}).get("message_id")
    if original_message_id:
        bot.delete_message(user_id, original_message_id)

@bot.message_handler(func=lambda message: message.text == "Não fui eu")
def handle_nao_fui_eu(message):
    user_id = message.chat.id
    remove_keyboard = types.ReplyKeyboardRemove()
    text = "Sua senha não foi altereda e você pode ignorar essa mensagem"
    bot.send_message(message.chat.id, text, reply_markup=remove_keyboard)
    original_message_id = user_requests.get(user_id, {}).get("message_id")
    if original_message_id:
        bot.delete_message(user_id, original_message_id)


def run_telegram_bot():
    print("Iniciando bot do Telegram")
    bot.polling()
