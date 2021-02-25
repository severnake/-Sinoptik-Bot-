import emoji                    # emoji lib
from config import cursor, bot
from functions import *

# Если нет таблицы users в базе, создать
cursor.execute("CREATE TABLE IF NOT EXISTS users (id INT AUTO_INCREMENT PRIMARY KEY, \
                telegram_user_id INT(11) UNIQUE, city VARCHAR(255))")

# /start, /help
@bot.message_handler(commands=['start', 'help'])
def main(message):
  msg = bot.send_message(message.chat.id,
  emoji.emojize('Привет! Я бот погоды :cloud: , напишите мне свой город. :smile:', use_aliases=True))
  bot.register_next_step_handler(msg, process_city_step)

def process_city_step(message):
  try:
    bot.send_message(message.chat.id, emoji.emojize(':cloud: Погода на 10 дней.\n')
      + echoWeather( message.text.lower() ))

    existsUserAndCity(message.from_user.id, message.text.lower())

    msg = bot.send_message(message.chat.id, "Выберите: ", reply_markup=keyboard_main())
    bot.register_next_step_handler(msg, process_select_step)

  except Exception as e:
    bot.reply_to(message, 'Вы ввели не существующий город или город не на русском языке.')

def weather(message):
  user_id = message.from_user.id

  cursor.execute("SELECT city FROM users WHERE telegram_user_id = {0}".format(user_id))
  city = cursor.fetchone()[0] # кортеж

  msg = bot.send_message(message.chat.id, emoji.emojize(':cloud: Погода на 10 дней.\n')
          + echoWeather(city), reply_markup=keyboard_main())
  bot.register_next_step_handler(msg, process_select_step)

def process_select_step(message):
  try:
    if (message.text == 'Узнать погоду'):
      weather(message)
    elif (message.text == 'Другой город'):
      main(message)
    else:
      main(message)

  except Exception as e:
    bot.reply_to(message, 'ooops!')

# Enable saving next step handlers to file "./.handlers-saves/step.save".
# Delay=2 means that after any change in next step handlers (e.g. calling register_next_step_handler())
# saving will hapen after delay 2 seconds.
bot.enable_save_next_step_handlers(delay=2)

# Load next_step_handlers from save file (default "./.handlers-saves/step.save")
# WARNING It will work only if enable_save_next_step_handlers was called!
bot.load_next_step_handlers()

if __name__ == '__main__':
  bot.polling(none_stop=True)