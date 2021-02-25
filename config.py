import sys                            # default lib
import telebot                        # pyTelegramBotApi

import mysql.connector                # mysql-connector-python
from mysql.connector import errorcode

try:
    db = mysql.connector.connect(
      host="localhost",
      user="root",
      passwd="",
      port="3306",
      database="sinoptik"
    )
except mysql.connector.Error as err:
  if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
    print("Что-то не так с вашим именем пользователя или паролем")
    sys.exit()
  elif err.errno == errorcode.ER_BAD_DB_ERROR:
    print("База данных не существует")
    sys.exit()
  else:
    print(err)
    sys.exit()

cursor = db.cursor()

# Telegram token
bot = telebot.TeleBot('Telegram your token', parse_mode='HTML')