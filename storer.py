import logging
import shelve

logger = logging.getLogger(__name__)


class Storer:
    def __init__(self, filename):
        self.filename = filename

        if self.restore('users') is None:
            self.store('users', {})

    def init_user(self, user_id):
        users = self.restore('users')

        if user_id not in users:
            users[user_id] = {'routes': [], 'history': []}

        self.store('users', users)

        return users

    def update_history(self, user_id, station_id):
        users = self.init_user(user_id)

        users[user_id]['history'].insert(0, station_id)

        self.store('users', users)

    def favorite(self, user_id, station_id):
        users = self.init_user(user_id)

        if station_id in users[user_id]['routes']:
            users[user_id]['routes'].remove(station_id)
            msg = 'Остановка удалена из избранного'
        else:
            users[user_id]['routes'].append(station_id)
            msg = 'Остановка добавлена в избранное'

        self.store('users', users)

        return msg

    def store(self, key, obj):
        db = shelve.open(self.filename)

        db[key] = obj
        db.close()

    def restore(self, key):
        db = shelve.open(self.filename)

        if key in db:
            obj = db[key]
        else:
            obj = None

        db.close()

        return obj
