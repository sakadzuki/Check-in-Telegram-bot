from math import radians, cos, sin, asin, sqrt
from geopandas.tools import geocode

# получить gps-координаты
def get_gps(address):
    try:
        location = geocode(address, provider="nominatim", user_agent='atms')
        point = location.geometry.iloc[0]
        if point.is_empty:
            # попробовать с адресом без указания номера дома/строения
            address = address[:address.rfind(' ')]
            location = geocode(address, provider="nominatim", user_agent='atms')
            point = location.geometry.iloc[0]
            if point.is_empty: # если все равно не нашли адрес
                return None
        return (point.x, point.y)
    except Exception:
        print('Ошибка при определении gps-координат для адреса:', address)
        return None

# функция гаверсинуса - определение расстояния между координатами
def haversine(lon1, lat1, lon2, lat2):
    r = 6371  # радиус Земли
    # градусы в радианы
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    # применяем формулу
    dlon = lon2 - lon1 # разность между соотетствующим величинами
    dlat = lat2 - lat1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    return c * r # получаем расстояние в километрах

