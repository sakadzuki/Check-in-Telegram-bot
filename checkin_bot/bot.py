import config
import telebot
import replies
import geo

bot = telebot.TeleBot(config.token)

# приветствие в ответ на /start
@bot.message_handler(commands=['start'])
def hello_message(message):
    hello = 'Здравствуйте! Здесь Вы можете подтвердить свое нахождение рядом с вузом\n'
    msg = bot.send_message(message.chat.id, hello + replies.commands_message())

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

if __name__ == '__main__':
    bot.infinity_polling()
