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
    chat_id = message.from_user.id # получаем идентификатор пользователя
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
    else:
        bot.send_message(message.chat.id, address + ' - не могу найти адрес')


@bot.message_handler(content_types=["location"])
def answer(message):
    gps1 = (message.location.longitude, message.location.latitude)
    # gps2 = geo.get_gps(config.main_address)
    gps2 = config.main_gps # координаты вуза
    distance = geo.haversine(gps1[0], gps1[1], gps2[0], gps2[1]) # получаем расстояние
    # проверка расстояния
    print(gps1, ' - ', distance)
    bot.send_message(message.chat.id, ' - ' + str(distance) + ' км')

if __name__ == '__main__':
    bot.infinity_polling()
