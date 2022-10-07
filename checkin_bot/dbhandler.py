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

    # добавить чек-ин
    def add_checkin(self, chat_id, datetime, distance, result):
        with self.connection:
            self.cursor.execute('INSERT INTO checkin ("chat_id", "datetime", "distance", "result") VALUES (?, ?, ?, ?)', (chat_id, datetime, distance, result,))
            self.connection.commit()  # сохраняем изменения

    # закрытие подключения
    def close(self):
        self.connection.close()