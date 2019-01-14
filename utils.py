import re

import requests
from telegram import (InlineKeyboardButton, InlineKeyboardMarkup,
                      ReplyKeyboardMarkup)

from stations import invert_stations, stations
from storer import Storer

storer = Storer('bot.db')


def get_inline_keyboard(station_id):
    return InlineKeyboardMarkup(
        [[InlineKeyboardButton('Обновить 🔄', callback_data=station_id)]]
    )


def get_response(station_id):
    url = 'http://online.ettu.ru/station/{}'.format(station_id)
    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.86 '
                      'Safari/537.36',
    }
    res = requests.get(url, headers=headers).text

    return res


def get_schedule(html):
    # Route name
    route = re.findall('<p>(.*)</p>(.*)<img', html, re.DOTALL)[0][0].strip()
    route = re.sub('<[^<]+?>', '', route)

    tram_list = []

    if "мин" in html:
        tram_numbers = re.findall('center;"><b>(\d+)', html)
        a = re.findall('right;">(.*)</div>', html)

        i = 0
        for n in tram_numbers:
            tram_list.append('***{}*** - {} - {}\n'.format(n, a[i], a[i + 1]))

            i += 2
    else:
        tram_list = 'Нет трамваев'

    return '***{}***\n\n{}'.format(route, ''.join(tram_list))


def get_user_stations(uid):
    users = storer.restore('users')

    if len(users[uid]['routes']):
        _list = []

        for s in users[uid]['routes']:
            _list.append('🚃 <b>{0}</b>\n'
                         '<i>Выбрать:</i> /st_{1}\n'
                         '<i>Удалить:</i> /fav_{1}\n\n'.format(stations[int(s)], s))

        msg = '<b>Ваши остановки</b> \n\n' + ''.join(_list)

    else:
        msg = 'Список ваших остановок пуст'

    return msg


def get_user_history(uid):
    users = storer.restore('users')

    if len(users[uid]['history']):

        _list = []
        history = users[uid]['history'][:5]

        for s in history:
            _list.append('🚃 <b>{0}</b>\n'
                         '<i>Выбрать:</i> /st_{1}\n'
                         '<i>В избранное:</i> /fav_{1}\n\n'.format(stations[int(s)], s))

        msg = '<b>Ваша история</b> \n\n' + ''.join(_list)
    else:
        msg = 'История пуста'

    return msg


def get_stations_by_char(char):
    _list = []

    for st in invert_stations:
        if st[0][:1] == char:
            _list.append('🚃 <b>{0}</b>\n'
                         '<i>Выбрать:</i> /st_{1}\n'
                         '<i>В избранное:</i> /fav_{1}\n\n'.format(st[0], st[1]))

    if len(_list):
        msg = '<b>Остановки на {}</b> \n\n{}'.format(char, ''.join(_list))
    else:
        msg = 'Не найдено'

    return msg


default_keyboard = [
    ['Найти 🔎'],
    ['Мои остановки 📖'],
    ['История 📝']
]

chars = [['1', '4', '7', 'А', 'Б'], ['В', 'Г', 'Д', 'Е', 'Ж'],
         ['З', 'И', 'К', 'Л', 'М'], ['Н', 'О', 'П', 'Р', 'С'],
         ['Т', 'У', 'Ф', 'Х', 'Ц'], ['Ч', 'Ш', 'Щ', 'Э', 'Ю'], ['Я', '↩️']]

default_keyboard = ReplyKeyboardMarkup(default_keyboard, resize_keyboard=True)
chars_keyboard = ReplyKeyboardMarkup(chars)
