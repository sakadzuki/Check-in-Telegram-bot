import config
import telebot
import replies
import geo
from enum import Enum
from dbhandler import DBHandler

# режимы работы бота с пользователем
class Modes(Enum):
    none = 0
    wait_name = 1
    wait_location = 2

bot = telebot.TeleBot(config.token) # создаем бота

# приветствие в ответ на /start
@bot.message_handler(commands=['start'])
def hello_message(message):
    bot.send_message(message.chat.id, 'Здравствуйте! Здесь Вы можете подтвердить свое нахождение рядом с вузом\n')
    bot.send_message(message.chat.id, replies.commands_message())
    chat_id = message.chat.id # получаем идентификатор пользователя
    db = DBHandler(config.db_path) # подключаемся к БД
    if db.check_user(chat_id): # если пользователь есть в БД
        # проверяем, представлялся ли он
        if db.get_user_mode(chat_id) == Modes.wait_name:
            bot.send_message(message.chat.id, 'Пришлите Ваши имя и группу одним сообщением через запятую')
    else:
        db.add_user(chat_id) # добавляем нового пользователя
        bot.send_message(message.chat.id, 'Пришлите Ваши имя и группу одним сообщением через запятую')
    db.close()

# преобразовать список чек-инов в строки для отправки сообщения
def checkins_to_str(checkins):
    clist = ''
    for i in range(len(checkins)):
        c = checkins[i]
        clist += '{}. {:.2f} км - {}\n'.format(c[2], c[3], c[4])
    return clist

# отправка серии сообщений, когда message > 4096 символов
def send_long_message(chat_id, message):
    while (len(message) > 4096):
        bigpart = message[:4096]
        pos = bigpart.rfind('\n')
        sending = bigpart[:pos]
        bot.send_message(chat_id, sending)
        rest = bigpart[pos + 1:]
        message = rest + message[4096:]
    if (len(message) > 0):
        bot.send_message(chat_id, message)

# история чек-инов пользователя
@bot.message_handler(commands=['history'])
def history_message(message):
    db = DBHandler(config.db_path)
    checkins = db.get_checkins(message.chat.id) # получаем список чек-инов
    name, group = db.get_user_data(message.chat.id)
    db.close()
    checkins_str = checkins_to_str(checkins) # преобразуем в строку
    bot.send_message(message.chat.id, 'История чек-инов для пользователя ' + name + ', ' + group)
    if len(checkins_str) > 4096: # если треюуется серия сообщений
        send_long_message(message.chat.id, checkins_str)
    else:
        bot.send_message(message.chat.id, checkins_str)

# история успешных чек-инов пользователя
@bot.message_handler(commands=['history_accepted'])
def history_message(message):
    db = DBHandler(config.db_path)
    checkins = db.get_checkins(message.chat.id, 'УСПЕШНО') # выборка успешных чек-инов
    db.close()
    checkins_str = checkins_to_str(checkins)
    bot.send_message(message.chat.id, 'История успешных чек-инов:')
    if len(checkins_str) > 4096:
        send_long_message(message.chat.id, checkins_str)
    else:
        bot.send_message(message.chat.id, checkins_str)

# обработка чек-ина при получении расстояния
def checkin_handle(message, distance):
    if (distance < config.acceptable_distance):  # если расстояние не превышает приемлемое
        result = 'УСПЕШНО'  # успешный чек-ин
    else:
        result = 'НЕУДАЧНО'
    bot.send_message(message.chat.id, result)  # сообщение с результатом
    db = DBHandler(config.db_path)  # подключаемся к БД
    date = replies.timestamp_to_datestr(message.date)  # дата сообщения
    db.add_checkin(message.chat.id, date, distance, result)  # добавляем данные о чек-ине
    db.close()

# обработка сообщения с текстом
@bot.message_handler(content_types=["text"])
def answer(message):
    db = DBHandler(config.db_path)
    user_mode = db.get_user_mode(message.chat.id)

    if user_mode == Modes.wait_name.value: # если от пользователя ожидается имя, группа
        user_data = message.text.split(',') # пробуем получить данные пользователя через запятую
        if len(user_data) > 0:
            group = ''
            name = user_data[0]
            if len(user_data) > 1:
                group = user_data[1]
            db.set_user_data(message.chat.id, name, group) # обновляем данные пользователя
            db.set_user_mode(message.chat.id, Modes.wait_location.value) # дальше будем ожидать от пользователя локацию
            bot.send_message(message.chat.id, 'Данные пользователя обновлены')
        db.close()
    else: # иначе предполагаем, что получили текстом адрес
        db.close()
        address = message.text
        gps1 = geo.get_gps(address) # получаем положение в виде координат
        if gps1 != None: # если адрес был получен
            # gps2 = geo.get_gps(config.main_address)
            gps2 = config.main_gps # координаты вуза
            distance = geo.haversine(gps1[0], gps1[1], gps2[0], gps2[1]) # получаем расстояние
            # проверка расстояния
            print(address, ' - ', distance)
            bot.send_message(message.chat.id, address + ' - ' + str(distance) + ' км')
            checkin_handle(message, distance) # обработка чек-ина
        else:
            bot.send_message(message.chat.id, address + ' - не могу найти адрес')


# обработчик на случай, если пользователь прислал локацию
@bot.message_handler(content_types=["location"])
def answer(message):
    gps1 = (message.location.longitude, message.location.latitude)
    # gps2 = geo.get_gps(config.main_address)
    gps2 = config.main_gps # координаты вуза
    distance = geo.haversine(gps1[0], gps1[1], gps2[0], gps2[1]) # получаем расстояние
    bot.send_message(message.chat.id, str(distance) + ' км')
    checkin_handle(message, distance)



if __name__ == '__main__':
    bot.infinity_polling() # запускаем бота
