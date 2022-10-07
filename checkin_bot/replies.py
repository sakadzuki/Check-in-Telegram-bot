from datetime import datetime
import config

def commands_message():
    msg = '\n/history - история чек-инов\n/history_accepted - история успешных чек-инов\n/edit - редактировать данные профиля'
    msg += '\n\nПришлите мне свою локацию для того, чтобы отметиться на ' + config.main_address
    return msg

def timestamp_to_datestr(timestamp):
    datestr = datetime.fromtimestamp(timestamp).strftime('%d.%m.%Y %H:%M:%S')
    return datestr