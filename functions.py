import requests                                     # default lib
import datetime                                     # default lib

from config import db, cursor
from telebot import types                           # keyboard

from bs4 import BeautifulSoup as BS                 # parse HTML
from dateutil.relativedelta import relativedelta    # python-dateutil

def keyboard_main():
  '''Клавиатура.'''
  markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
  itembtn1 = types.KeyboardButton('Узнать погоду')
  itembtn2 = types.KeyboardButton('Другой город')
  markup.add(itembtn1, itembtn2)

  return markup

def getNowDate():
  '''Получить текущую дату.'''
  now = datetime.datetime.now()
  d = f'{now.year}-{now.month}-{now.day}'
  
  return d

def getNextDay(day = 1):
  '''Получить следующий день.'''
  now = datetime.datetime.now()
  next_day = now + relativedelta(days=+day)
  next_day = str(next_day).split(' ')[0] # y-m-d

  return next_day

def existsUserAndCity(user_id, msgText):
  '''
    Проверка есть ли пользователь в базе,
    если есть, обновить город.
  '''
  sql = "SELECT * FROM users WHERE telegram_user_id = {0}".format(user_id)
  cursor.execute(sql)
  existsUser = cursor.fetchone()

  # Если нету, добавить в базу
  if (existsUser == None):
    sql = "INSERT INTO users (telegram_user_id, city) VALUES (%s, %s)"
    val = (user_id, msgText)
    cursor.execute(sql, val)
  elif (bool(existsUser) == True):
    sql = "UPDATE users SET city = %s WHERE telegram_user_id = %s"
    val = (msgText, user_id)
    cursor.execute(sql, val)

  # Принять изменения
  db.commit()

def parseSinoptik(city = 'никополь'):
  '''Функция принимает city, парсинг погоды на 10-дней.'''
  r = requests.get(f'https://sinoptik.ua/погода-{city}/10-дней')

  return BS(r.content, 'html.parser')

def parseSinoptikDesc(city = 'никополь', date = getNowDate()):
  '''
    Функция принимает city и date,
    делаем ajax запрос на получение описания дня.
  '''
  r = requests.get(f'https://sinoptik.ua/погода-{city}/{date}?ajax=GetForecast')

  return BS(r.content, 'html.parser')

def echoDesc(city, nextDay):
  '''Парсить ajax запрос.'''
  html = parseSinoptikDesc(city, nextDay)
  main = html.select_one(".wDescription .description").text

  # Обрезать лишние символы
  return main.strip(' \t\n\r')

def getDescriptions(city):
  '''Получить описание каждого дня.'''
  result = []

  for x in range(10):
    result.append( echoDesc(city, getNextDay(x)) )

  return result

def echoWeather(city):
  '''Вывести погоду.'''
  html = parseSinoptik(city)
  mains = html.select(".main")
  descriptions = getDescriptions(city)
  result = []

  # Обращаться к описанию дня по индексу
  # в массиве descriptions
  for index, main in enumerate(mains):
    day = main.select_one('.day-link').text
    date = main.select_one('.date').text
    month = main.select_one('.month').text
    t_min = main.select_one('.temperature .min').text
    t_max = main.select_one('.temperature .max').text

    result.append(f'{day} - <b>{date} {month.title()}</b>:\n{t_min}, {t_max}\n<i>{descriptions[index]}</i>\n\n')

  return f'<b>{city.title()}</b>\n\n' + "".join(result)

__version__ = '1.0'