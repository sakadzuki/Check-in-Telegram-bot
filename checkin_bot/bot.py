import config
import telebot
import replies
import geo
from dbhandler import DBHandler

bot = telebot.TeleBot(config.token)

# приветствие в ответ на /start
@bot.message_handler(commands=['start'])
def hello_message(message):
    hello = 'Здравствуйте! Здесь Вы можете подтвердить свое нахождение рядом с вузом\n'
    chat_id = message.chat.id # получаем идентификатор пользователя
    db = DBHandler(config.db_path) # подключаемся к БД
    if db.check_user(chat_id): # если пользователь есть в БД
        # проверяем, представлялся ли он
        print('has ', chat_id)
    else:
        db.add_user(chat_id) # добавляем нового пользователя
        print('added: ', chat_id)
        hello += '\nПришлите ваши имя и группу одним сообщением через запятую'
    db.close()
    bot.send_message(message.chat.id, hello)

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
    db.close()
    checkins_str = checkins_to_str(checkins) # преобразуем в строку
    bot.send_message(message.chat.id, 'История чек-инов:')
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

@bot.message_handler(content_types=["text"])
def answer(message):
    address = message.text
    gps1 = geo.get_gps(address) # получаем положение в виде координат
    if gps1 != None:
        # gps2 = geo.get_gps(config.main_address)
        gps2 = config.main_gps # координаты вуза
        distance = geo.haversine(gps1[0], gps1[1], gps2[0], gps2[1]) # получаем расстояние
        # проверка расстояния
        print(address, ' - ', distance)
        bot.send_message(message.chat.id, address + ' - ' + str(distance) + ' км')
        checkin_handle(message, distance) # обработка чек-ина
    else:
        bot.send_message(message.chat.id, address + ' - не могу найти адрес')


@bot.message_handler(content_types=["location"])
def answer(message):
    gps1 = (message.location.longitude, message.location.latitude)
    # gps2 = geo.get_gps(config.main_address)
    gps2 = config.main_gps # координаты вуза
    distance = geo.haversine(gps1[0], gps1[1], gps2[0], gps2[1]) # получаем расстояние
    bot.send_message(message.chat.id, str(distance) + ' км')
    checkin_handle(message, distance)



if __name__ == '__main__':
    bot.infinity_polling()
