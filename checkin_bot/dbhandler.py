import sqlite3

class DBHandler:
    # конструктор - создание объекта с подключением к БД
    def __init__(self, database):  # подключение к бд
        self.connection = sqlite3.connect(database)
        self.cursor = self.connection.cursor()

    # проверка, есть ли пользователь с указанным id в БД
    def check_user(self, chat_id):
        with self.connection:
            if len(self.cursor.execute('SELECT * FROM user WHERE chat_id = ?', (chat_id,)).fetchall()) > 0:
                return True
            else:
                return False

    # добавить нового пользователя в таблицу users
    def add_user(self, chat_id, name='', group='', mode=1):
        with self.connection:
            self.cursor.execute('INSERT INTO user ("chat_id", "name", "group", "mode") VALUES (?, ?, ?, ?)', (chat_id, name, group, mode,))
            self.connection.commit()  # сохраняем изменения

    def select_users(self):
        with self.connection:
            return self.cursor.execute('SELECT * FROM user').fetchall()

    def get_user_mode(self, chat_id):
        with self.connection:
            return self.cursor.execute('SELECT * FROM user WHERE chat_id = ?', (chat_id,)).fetchall()[0][2]

    # задать данные пользователя - имя, группа
    def set_user_data(self, chat_id, name, group):
        self.cursor.execute('UPDATE user SET name = ?, "group" = ? WHERE chat_id = ?', (name, group, chat_id,))
        self.connection.commit()  # сохраняем изменения

    # добавить чек-ин
    def add_checkin(self, chat_id, datetime, distance, result):
        with self.connection:
            self.cursor.execute('INSERT INTO checkin ("user_chat_id", "datetime", "distance", "result") VALUES (?, ?, ?, ?)', (chat_id, datetime, distance, result,))
            self.connection.commit()  # сохраняем изменения

    # получить список чек-инов для пользователя
    # если result задан, можно отфильтировать чек-ины по результату (УСПЕШНО/НЕУДАЧНО)
    def get_checkins(self, chat_id, result=''):
        with self.connection:
            if result == '':
                return self.cursor.execute('SELECT * FROM checkin WHERE user_chat_id = ?', (chat_id,)).fetchall()
            else:
                return self.cursor.execute('SELECT * FROM checkin WHERE user_chat_id = ? AND result = ?', (chat_id, result)).fetchall()

    # обновить режим работы бота для пользователя
    def set_user_mode(self, chat_id, mode):
        self.cursor.execute('UPDATE user SET mode = ? WHERE chat_id = ?', (mode, chat_id,))
        self.connection.commit()  # сохраняем изменения

    # получить данные пользователя (имя, группа)
    def get_user_data(self, chat_id):
        with self.connection:
            user = self.cursor.execute('SELECT * FROM user WHERE chat_id = ?', (chat_id,)).fetchall()[0]
            name = user[3]
            group = user[4]
            return name, group

    # закрытие подключения
    def close(self):
        self.connection.close()