import telebot
import telebot.types as types
from enum import Enum
import json
import xgboost as xgb
from parsing.preprocessing import preprocess
import pickle
import pandas as pd
import numpy as np


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


drop_features = ["move_speed", "last_hits_per_min", "hero_damage_per_min",
                 "gold_per_min", "kills_per_min", "attack_rate", "hero_healing_per_min", "lane_efficiency",
                 "lhten", "xp_per_min", "stuns_per_min", "deaths", "last_hits", "net_worth", "assists", "hero_healing",
                 "roshan_kills", "attack_range", "firstblood_claimed"]
bot = telebot.TeleBot('6864316084:AAFdBTKzjB7UgOPmQ-t4cdZau-dPZOPLpJI')
teams = {
    Team.RADIANT: [],
    Team.DIRE: []
}
current_team = None
current_page = 0
messages_ids_to_delete = []

with open('../common/heroes.json', 'r') as file:
    heroes_data = json.load(file)

with open("../model/heroes_properties.pickle", "rb") as file:
    heroes_properties = pickle.load(file)

model = xgb.Booster(model_file="../model/model")
heroes_by_primary_attr = {attribute: [] for attribute in PrimaryAttribute}

for hero_data in heroes_data.values():
    heroes_by_primary_attr[PrimaryAttribute(hero_data["primary_attr"])].append(hero_data["localized_name"])
for heroes_names in heroes_by_primary_attr.values():
    heroes_names.sort()

heroes_ids = {hero["localized_name"]: hero["id"] for hero in heroes_data.values()}


def predict(radiant_pick, dire_pick):
    vector = preprocess([pd.Series(radiant_pick)], [pd.Series(dire_pick)], heroes_properties).drop(
        columns=drop_features)
    xgb_vector = xgb.DMatrix(vector.values, feature_names=list(vector.columns))
    return model.predict(xgb_vector).round(decimals=3)[0]


def delete_messages(chat_id):
    global messages_ids_to_delete
    for message_id in messages_ids_to_delete:
        bot.delete_message(chat_id, message_id)
    messages_ids_to_delete.clear()


def create_keyboard(message):
    global current_page, heroes_by_primary_attr
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    attribute = list(heroes_by_primary_attr.keys())[current_page]

    for hero_name in heroes_by_primary_attr[attribute]:
        button = types.InlineKeyboardButton(text=hero_name, callback_data=hero_name)
        keyboard.add(button)

    prev_button = types.InlineKeyboardButton(text='⬅️', callback_data='prev')
    next_button = types.InlineKeyboardButton(text='➡️', callback_data='next')
    keyboard.add(prev_button, next_button)
    keyboard.add(types.InlineKeyboardButton(text='🗑️️', callback_data='clear'))
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
    global teams, current_team, messages_ids_to_delete
    messages_ids_to_delete.clear()
    current_team = Team(message.text.lstrip('/'))
    bot.send_message(message.chat.id, f"Оберіть героїв команди {current_team}.")
    keyboard = create_keyboard(message)
    attribute = list(heroes_by_primary_attr.keys())[current_page]
    bot.send_message(message.chat.id, f"{attribute}:", reply_markup=keyboard)
    message_id = None
    if teams[current_team]:
        message_id = bot.send_message(message.chat.id, f"Поточний вибір героїв команди {current_team}:"
                                                       f" {', '.join(teams[current_team])}.").message_id
    else:
        message_id = bot.send_message(message.chat.id, f"Наразі жодного героя команди {current_team} не обрано.").message_id
    messages_ids_to_delete.append(message_id)


@bot.message_handler(commands=['predict'])
def handle_predict(message):
    global teams
    for team, pick in teams.items():
        if len(pick) < 5:
            bot.send_message(message.chat.id, f"Обрано недостаньо героїв команди {current_team}.")
            return
    radiant_pick = [heroes_ids[hero] for hero in teams[Team.RADIANT]]
    dire_pick = [heroes_ids[hero] for hero in teams[Team.DIRE]]
    radiant_win_prob = predict(radiant_pick, dire_pick)
    if radiant_win_prob > 0.5:
        bot.send_message(message.chat.id, f"Radiant переможуть з вірогідністю {radiant_win_prob}.")
    else:
        bot.send_message(message.chat.id, f"Dire переможуть з вірогідністю {1 - radiant_win_prob}.")


@bot.callback_query_handler(func=lambda call: call.data in heroes_ids)
def handle_hero_selection(call):
    global teams, current_team, messages_ids_to_delete
    delete_messages(call.message.chat.id)
    message_id = None
    if call.data in ["a"]:
        print(call.data)
        print(np.array(list(teams.values())).flatten())
    else:
        teams[current_team].append(call.data)
        messages_ids_to_delete.append(
            bot.send_message(call.message.chat.id, f"До команди {current_team} "
                                                   f"було обрано героя: {call.data}").message_id
        )
    messages_ids_to_delete.append(
        bot.send_message(call.message.chat.id, f"Вибір героїв команди {current_team}: "
                                               f" {', '.join(teams[current_team])}.").message_id
    )


@bot.callback_query_handler(func=lambda call: call.data in {'prev', 'next'})
def handle_pagination(call):
    global current_page

    if call.data == 'next':
        current_page = (current_page + 1) % 4
    elif call.data == 'prev':
        current_page = (current_page - 1) % 4

    keyboard = create_keyboard(call.message)
    attribute = list(heroes_by_primary_attr.keys())[current_page]
    bot.edit_message_text(text=f"{attribute}:",
                          chat_id=call.message.chat.id,
                          message_id=call.message.message_id,
                          reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: call.data == 'clear')
def handle_pick_clear(call):
    global current_team, teams, messages_ids_to_delete
    delete_messages(call.message.chat.id)
    messages_ids_to_delete.clear()
    teams[current_team].clear()
    messages_ids_to_delete.append(
        bot.send_message(call.message.chat.id, f"Вибір героїв команди {current_team} було очищено.").message_id
    )


@bot.message_handler(func=lambda message: True)
def handle_text(message):
    bot.send_message(message.chat.id, "Натисніть /start, щоб розпочати.")


if __name__ == "__main__":
    bot.polling(none_stop=True)
