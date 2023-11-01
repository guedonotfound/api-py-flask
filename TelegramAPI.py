import telebot

CHAVE_API = "6553689684:AAHyV36Ht9-o1G7fLnIhYaMprIT0fdXzrnA"

bot = telebot.TeleBot(CHAVE_API)

user_states = {}
user_responses = {}

@bot.message_handler(commands=["opcao1"])
def opcao1(message):
    user_id = message.chat.id
    if user_states.get(user_id) == "Aguardando_Opcao":
        bot.send_message(user_id, "Acesso liberado!")
        user_states[user_id] = "Bloqueado"
    else:
        texto = "Você já respondeu a essa mensagem, ela foi apagada para  evitar esse problema."
        bot.send_message(user_id, texto)
        if user_states.get(user_id) == "Bloqueado" and user_responses.get(user_id):
            bot.delete_message(user_id, user_responses[user_id])

@bot.message_handler(commands=["opcao2"])
def opcao2(message):
    user_id = message.chat.id
    if user_states.get(user_id) == "Aguardando_Opcao":
        bot.send_message(user_id, "Acesso revogado!")
        user_states[user_id] = "Bloqueado"
    else:
        texto = "Você já respondeu a essa mensagem, ela foi apagada para evitar esse problema."
        bot.send_message(user_id, texto)
        if user_states.get(user_id) == "Bloqueado" and user_responses.get(user_id):
            bot.delete_message(user_id, user_responses[user_id])

@bot.message_handler(func=lambda message: user_states.get(message.chat.id) != "Bloqueado")
def responder(message):
    user_id = message.chat.id
    user_states[user_id] = "Aguardando_Opcao"
    user = "Gabriel Ambrogi"
    code = "003"
    texto = ("O usuário " + user + " (código " + code +
        ") está solicitando liberação para acessar o sistema." + """
        /opcao1 - Liberar acesso
        /opcao2 - Não liberar acesso""")
    msg = bot.send_message(user_id, texto)
    user_responses[user_id] = msg.message_id

bot.polling()
