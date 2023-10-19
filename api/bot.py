import telebot

bot = telebot.TeleBot('6864316084:AAFdBTKzjB7UgOPmQ-t4cdZau-dPZOPLpJI')

# Обробник команди /start
@bot.message_handler(commands=['start'])
def handle_start(message):
    bot.send_message(message.chat.id, "Вітаю, це мій перший бот!")

# Обробник текстових повідомлень
@bot.message_handler(func=lambda message: True)
def handle_text(message):
    bot.send_message(message.chat.id,
                     "Якщо ви розкажете мені анекдот, я намагатимусь знайти йому глибокий філософський сенс.")


if __name__ == "__main__":
    bot.polling(none_stop=True)
