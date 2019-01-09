import re

from telegram import ChatAction, ParseMode

from storer import Storer
from utils import (chars_keyboard, default_keyboard, get_inline_keyboard,
                   get_response, get_schedule, get_user_history,
                   get_user_stations, get_stations_by_char)

storer = Storer('bot.db')

users = storer.restore('users')


def start(bot, update):
    user_id = update.message.from_user.id

    if user_id not in users:
        users[user_id] = {'routes': [], 'history': []}
        storer.store('users', users)

    msg = 'Местоположение трамваев в Екатеринбурге'
    bot.sendMessage(update.message.chat_id, msg, reply_markup=default_keyboard)


def entered_char(bot, update):
    chat_id = update.message.chat_id

    bot.sendMessage(chat_id,
                    get_stations_by_char(update.message.text),
                    parse_mode=ParseMode.HTML)


def message(bot, update):
    text = update.message.text
    chat_id = update.message.chat_id
    user_id = update.message.from_user.id

    bot.sendChatAction(chat_id, ChatAction.TYPING)

    if 'Найти' in text:
        bot.sendMessage(chat_id, "Выберите первую букву остановки:", reply_markup=chars_keyboard)

    elif 'Мои остановки' in text:
        bot.sendMessage(chat_id, get_user_stations(user_id), parse_mode=ParseMode.HTML)

    elif 'История' in text:
        bot.sendMessage(chat_id, get_user_history(user_id), parse_mode=ParseMode.HTML)

    elif text == '↩️':
        bot.sendMessage(chat_id, "Главное меню", reply_markup=default_keyboard)

    else:
        entered_char(bot, update)


def station(bot, update):
    user_id = update.message.from_user.id
    chat_id = update.message.chat_id
    station_id = re.sub(r'/st_', '', update.message.text)

    bot.sendChatAction(chat_id, ChatAction.TYPING)

    # Update user history
    users[user_id]['history'].insert(0, station_id)
    storer.store('users', users)

    # Get html from ETTU
    html = get_response(station_id)

    if "error" in html:
        bot.sendMessage(chat_id, "На данный момент эта информация недоступна.")
    else:
        bot.sendMessage(chat_id, get_schedule(html),
                        parse_mode=ParseMode.MARKDOWN,
                        reply_markup=get_inline_keyboard(station_id))


def update_schedule(bot, update):
    query = update.callback_query

    html = get_response(query.data)

    bot.edit_message_text(get_schedule(html), query.message.chat_id, query.message.message_id,
                          parse_mode=ParseMode.MARKDOWN,
                          reply_markup=get_inline_keyboard(query.data))


def favorite(bot, update):
    station_id = re.sub(r'/fav_', '', update.message.text)
    user_id = update.message.from_user.id

    if station_id in users[user_id]['routes']:
        users[user_id]['routes'].remove(station_id)
        msg = 'Остановка удалена из избранного'
    else:
        users[user_id]['routes'].append(station_id)
        storer.store('users', users)
        msg = 'Остановка добавлена в избранное'

    bot.sendMessage(update.message.chat_id, msg, parse_mode=ParseMode.HTML)
