from datetime import datetime

def commands_message():
    msg = '\n/checkin - проверить присутствие'
    return msg

def timestamp_to_datestr(timestamp):
    datestr = datetime.fromtimestamp(timestamp).strftime('%d.%m.%Y %H:%M:%S')
    return datestr