import telebot

bot = telebot.TeleBot('6864316084:AAFdBTKzjB7UgOPmQ-t4cdZau-dPZOPLpJI')

# Обробник команди /start
@bot.message_handler(commands=['start'])
def handle_start(message):
    bot.send_message(message.chat.id,
                     "Привіт, гравці Dota 2! Я ваш особистий пророк перемог"
                     " на основі вибору героїв! З моєю допомогою ви можете зазирнути у майбутнє та отримати прогноз "
                     "на результат вашого матчу. Готові дізнатися, хто має перевагу? "
                     "Надішліть мені склад команд і я передбачу, хто має більше шансів на перемогу!🏆🎮")

# Обробник текстових повідомлень
@bot.message_handler(func=lambda message: True)
def handle_text(message):
    bot.send_message(message.chat.id,
                     "Якщо ви розкажете мені анекдот, я намагатимусь знайти йому глибокий філософський сенс.")


if __name__ == "__main__":
    bot.polling(none_stop=True)
