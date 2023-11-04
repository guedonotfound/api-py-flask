import telebot
import main

CHAVE_API = "6553689684:AAHyV36Ht9-o1G7fLnIhYaMprIT0fdXzrnA"

bot = telebot.TeleBot(CHAVE_API)

user_requests = {}
chat_sup_id = -4031347674
chat_ins_id = -4007534836

@bot.message_handler(commands=["opcao1"])
def opcao1(message):
    user_id = message.chat.id
    user_data = user_requests.get(user_id, {})
    bot.send_message(
        user_id, "Acesso liberado para {} (código {})!".format(
            user_data.get("user", ""), user_data.get("code", "")
        )
    )
    original_message_id = user_requests.get(user_id, {}).get("message_id")
    if original_message_id:
        bot.delete_message(user_id, original_message_id)
    main.get_access('Y', user_requests.get(user_id, {}))

@bot.message_handler(commands=["opcao2"])
def opcao2(message):
    user_id = message.chat.id
    user_data = user_requests.get(user_id, {})
    bot.send_message(
        user_id, "Acesso revogado para {} (código {})!".format(
            user_data.get("user", ""), user_data.get("code", "")
        )
    )
    original_message_id = user_requests.get(user_id, {}).get("message_id")
    if original_message_id:
        bot.delete_message(user_id, original_message_id)
    main.get_access('N', user_requests.get(user_id, {}))

@bot.message_handler(commands=["Supervisao_realizada"])
def part_verified(message):
    original_message_id = user_requests.get(chat_sup_id, {}).get("message_id")
    serial_num = user_requests.get(chat_sup_id, {}).get("serial_num")
    texto = f"✅ - {serial_num}"
    bot.reply_to(message, texto)
    bot.delete_message(chat_sup_id, original_message_id)

@bot.message_handler(commands=["Inspec_realizada"])
def part_verified(message):
    original_message_id = user_requests.get(chat_ins_id, {}).get("message_id")
    serial_num = user_requests.get(chat_ins_id, {}).get("serial_num")
    texto = f"✅ - {serial_num}"
    bot.reply_to(message, texto)
    bot.delete_message(chat_ins_id, original_message_id)

def send_denied_inspec(code, inspec, part):
    texto = ("O inspetor " + inspec + " (código " + code +
             ") reprovou a peça com número de série " + part +
             " e a mesma requer atenção!" + """
             /Supervisao_realizada - Peça já verificada""")
    msg = bot.send_message(chat_sup_id, texto)
    user_requests[chat_sup_id] = {"message_id": msg.message_id, "serial_num" : part}

def send_denied_verify(part):
    texto = ("A peça com número de série " + part +
             "passou pela esteira e foi reprovada." + """
    
    Por favor, verificar!

             /Inspecao_realizada - Peça já verificada""")
    msg = bot.send_message(chat_ins_id, texto)
    user_requests[chat_ins_id] = {"message_id": msg.message_id, "serial_num" : part}

def send_message_to_chat(user, code):
    texto = ("O usuário " + user + " (código " + str(code) +
             ") está solicitando liberação para acessar o sistema." + """
             /opcao1 - Liberar acesso
             /opcao2 - Não liberar acesso""")
    msg = bot.send_message(chat_sup_id, texto)
    print(msg)
    user_requests[chat_sup_id] = {"user": user, "code": code, "message_id": msg.message_id}

@bot.message_handler()
def responder(message):
    msg = message.chat.id
    print(msg)

def run_telegram_bot():
    print("Iniciando bot do Telegram")
    bot.polling()
