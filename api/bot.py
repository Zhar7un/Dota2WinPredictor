import telebot
import telebot.types as types
from enum import Enum
import json


class Team(Enum):
    RADIANT = "radiant"
    DIRE = "dire"

    def __str__(self):
        return self.value.capitalize()


class PrimaryAttribute(Enum):
    STRENGTH = "str"
    AGILITY = "agi"
    INTELLIGENCE = "int"
    UNIVERSAL = "all"

    def __str__(self):
        return self.name.capitalize()


bot = telebot.TeleBot('6864316084:AAFdBTKzjB7UgOPmQ-t4cdZau-dPZOPLpJI')
teams = {
    Team.RADIANT: [],
    Team.DIRE: []
}
current_team = None
current_page = 0

with open('../common/heroes.json', 'r') as file:
    heroes_data = json.load(file)

heroes_by_primary_attr = {attribute: [] for attribute in PrimaryAttribute}

for hero_data in heroes_data.values():
    heroes_by_primary_attr[PrimaryAttribute(hero_data["primary_attr"])].append(hero_data["localized_name"])
for heroes_names in heroes_by_primary_attr.values():
    heroes_names.sort()


def create_keyboard(message):
    global current_page, heroes_by_primary_attr
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    attribute = list(heroes_by_primary_attr.keys())[current_page]

    for hero_name in heroes_by_primary_attr[attribute]:

        button = types.InlineKeyboardButton(text=hero_name, callback_data=hero_name)
        keyboard.add(button)

    # Додайте кнопки для перемикання сторінок
    prev_button = types.InlineKeyboardButton(text='⬅️', callback_data='prev')
    next_button = types.InlineKeyboardButton(text='➡️', callback_data='next')

    keyboard.add(prev_button, next_button)
    return keyboard


@bot.message_handler(commands=['start'])
def handle_start(message):
    bot.send_message(message.chat.id,
                     "Привіт, гравці Dota 2! Я ваш особистий пророк перемог"
                     " на основі вибору героїв! З моєю допомогою ви можете зазирнути у майбутнє та отримати прогноз "
                     "на результат вашого матчу. Готові дізнатися, хто має перевагу? "
                     "Надішліть мені склад команд і я передбачу, хто має більше шансів на перемогу!🏆🎮")
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    item1 = types.KeyboardButton("/radiant")
    item2 = types.KeyboardButton("/dire")
    item3 = types.KeyboardButton("/predict")

    markup.add(item1, item2, item3)
    bot.send_message(message.chat.id, "Виберіть команду:", reply_markup=markup)


@bot.message_handler(commands=['radiant', 'dire'])
def handle_radiant_or_dire(message):
    global teams, current_team
    current_team = Team(message.text.lstrip('/'))
    bot.send_message(message.chat.id, f"Оберіть героїв команди {current_team}.")
    keyboard = create_keyboard(message)
    attribute = list(heroes_by_primary_attr.keys())[current_page]
    bot.send_message(message.chat.id, f"{attribute}:", reply_markup=keyboard)


@bot.message_handler(commands=['predict'])
def handle_predict(message):
    global teams
    for team, pick in teams.items():
        if len(pick) < 5:
            bot.send_message(message.chat.id, f"Обрано недостаньо героїв команди {current_team}.")
            return


@bot.callback_query_handler(func=lambda call: call.data in {'prev', 'next'})
def handle_pagination(call):
    global current_page

    if call.data == 'prev':
        current_page = (current_page + 1) % 4
    elif call.data == 'next':
        current_page = (current_page - 1) % 4

    keyboard = create_keyboard(call.message)
    attribute = list(heroes_by_primary_attr.keys())[current_page]
    bot.edit_message_text(text=f"{attribute}:",
                          chat_id=call.message.chat.id,
                          message_id=call.message.message_id,
                          reply_markup=keyboard)


@bot.message_handler(func=lambda message: True)
def handle_text(message):
    bot.send_message(message.chat.id, "Натисніть /start, щоб розпочати.")


if __name__ == "__main__":
    bot.polling(none_stop=True)
