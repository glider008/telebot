import telebot
import sqlite3
from config_admin import TOKEN, ADMIN_TELEGRAM_ID
import datetime
import time
bot = telebot.TeleBot(TOKEN)

# Обработчик команды /start
@bot.message_handler(commands=['start'])
def send_welcome(message):
    if str(message.from_user.id) != ADMIN_TELEGRAM_ID:
        bot.reply_to(message, "Вы не являетесь администратором бота!")
    else:
        markup = telebot.types.ReplyKeyboardMarkup(row_width=1)
        markup.add(telebot.types.KeyboardButton('Зарегистрировать'))
        markup.add(telebot.types.KeyboardButton('Пробный Период'))
        markup.add(telebot.types.KeyboardButton('Удалить'))
        markup.add(telebot.types.KeyboardButton('Проверить'))
        markup.add(telebot.types.KeyboardButton('Изменить'))

        bot.reply_to(message, "Добро пожаловать, Сэр! Вот мои функционалы:", reply_markup=markup)


# Обработчик кнопки "Зарегистрировать"
@bot.message_handler(func=lambda message: message.text == "Зарегистрировать")
def register_seller(message):
    bot.reply_to(message, "Введите telegram id продавца:")
    bot.register_next_step_handler(message, get_seller_telegram_id)

def get_seller_telegram_id(message):
    telegram_id = message.text
    bot.reply_to(message, "Введите имя продавца:")
    bot.register_next_step_handler(message, get_seller_name, telegram_id)

def get_seller_name(message, telegram_id):
    name = message.text
    bot.reply_to(message, "Введите номер телефона продавца:")
    bot.register_next_step_handler(message, get_seller_phone_number, telegram_id, name)

def get_seller_phone_number(message, telegram_id, name):
    phone_number = message.text
    bot.reply_to(message, "Введите API Kaspistore продавца:")
    bot.register_next_step_handler(message, add_seller_to_db, telegram_id, name, phone_number)

def add_seller_to_db(message, telegram_id, name, phone_number):
    kaspistore_api = message.text
    try:
        # Создаем таблицу в базе данных kaspibot.db
        conn = sqlite3.connect('kaspibot.db')
        cursor = conn.cursor()
        cursor.execute("CREATE TABLE IF NOT EXISTS sellers (id INTEGER PRIMARY KEY AUTOINCREMENT, telegram_id TEXT, name TEXT, phone_number TEXT, kaspistore_api TEXT)")
        conn.commit()
        
        # Добавляем запись в таблицу в базе данных kaspibot.db
        cursor.execute("INSERT INTO sellers (telegram_id, name, phone_number, kaspistore_api) VALUES (?, ?, ?, ?)", (telegram_id, name, phone_number, kaspistore_api))
        conn.commit()
        
        # Создаем таблицу в базе данных kaspiusers.db
        conn = sqlite3.connect('kaspiusers.db')
        cursor = conn.cursor()
        cursor.execute("CREATE TABLE IF NOT EXISTS sellers (id INTEGER PRIMARY KEY AUTOINCREMENT, telegram_id TEXT, name TEXT, phone_number TEXT, kaspistore_api TEXT)")
        conn.commit()
        
         # Добавляем запись в таблицу в базе данных kaspiusers.db
        cursor.execute("INSERT INTO sellers (telegram_id, name, phone_number, kaspistore_api) VALUES (?, ?, ?, ?)", (telegram_id, name, phone_number, kaspistore_api))
        conn.commit()

        bot.reply_to(message, "Продавец успешно зарегистрирован!")
    except:
        bot.reply_to(message, "Произошла ошибка при добавлении в базу данных.")
    finally:
        conn.close()


# Обпаботчик кнопки "Пробный период"
@bot.message_handler(func=lambda message: message.text == "Пробный Период")
def register_seller(message):
    bot.reply_to(message, "Введите telegram id продавца:")
    bot.register_next_step_handler(message, get_seller_telegram_id)

def get_seller_telegram_id(message):
    telegram_id = message.text
    bot.reply_to(message, "Введите имя продавца:")
    bot.register_next_step_handler(message, get_seller_name, telegram_id, )

def get_seller_name(message, telegram_id, ):
    name = message.text
    bot.reply_to(message, "Введите номер телефона продавца:")
    bot.register_next_step_handler(message, get_seller_phone_number, telegram_id, name,)

def get_seller_phone_number(message, telegram_id, name, ):
    phone_number = message.text
    bot.reply_to(message, "Введите API Kaspistore продавца:")
    bot.register_next_step_handler(message, add_seller_to_db, telegram_id, name, phone_number, )


def add_seller_to_db(message, telegram_id, name, phone_number, ):
    kaspistore_api = message.text
    try:
        # Создаем таблицу в базе данных kaspibot.db
        conn = sqlite3.connect('kaspibot.db')
        cursor = conn.cursor()
        cursor.execute("CREATE TABLE IF NOT EXISTS trial_users (id INTEGER PRIMARY KEY AUTOINCREMENT, telegram_id TEXT, name TEXT, phone_number TEXT, kaspistore_api TEXT, trial_expiry INTEGER)")
        conn.commit()


        # Вычисляем время окончания пробного периода
        trial_expiry = int(time.time()) + 120  # 2 minutes in seconds

        # Добавляем запись в таблицу в базе данных kaspibot.db
        cursor.execute("INSERT INTO trial_users (telegram_id, name, phone_number, kaspistore_api, trial_expiry) VALUES (?, ?, ?, ?, ?)", (telegram_id, name, phone_number, kaspistore_api, trial_expiry))
        conn.commit()

        # Создаем таблицу в базе данных kaspiusers.db
        conn = sqlite3.connect('kaspiusers.db')
        cursor = conn.cursor()
        cursor.execute("CREATE TABLE IF NOT EXISTS trial_users (id INTEGER PRIMARY KEY AUTOINCREMENT, telegram_id TEXT, name TEXT, phone_number TEXT, kaspistore_api TEXT, trial_expiry INTEGER)")
        conn.commit()

        # Добавляем запись в таблицу в базе данных kaspiusers.db
        cursor.execute("INSERT INTO trial_users (telegram_id, name, phone_number, kaspistore_api, trial_expiry) VALUES (?, ?, ?, ?, ?)", (telegram_id, name, phone_number, kaspistore_api, trial_expiry))
        conn.commit()

        bot.reply_to(message, f"Продавец успешно зарегистрирован на 2-минутный пробный период! Он истекает через {2} минут.")
    except:
        bot.reply_to(message, "Произошла ошибка при добавлении в базу данных.")
    finally:
        conn.close()


# Обработчик кнопки "Удалить"
@bot.message_handler(func=lambda message: message.text == "Удалить")
def delete_seller(message):
    bot.reply_to(message, "Введите telegram id продавца, которого хотите удалить:")
    bot.register_next_step_handler(message, remove_seller_from_db)

def remove_seller_from_db(message):
    telegram_id = message.text
    try:
        conn = sqlite3.connect('kaspibot.db')
        cursor = conn.cursor()
        cursor.execute("DELETE FROM sellers WHERE telegram_id = ?", (telegram_id,))
        conn.commit()
        #Удаляем и из БД kaspiusers.db
        conn = sqlite3.connect('kaspiusers.db')
        cursor = conn.cursor()
        cursor.execute("DELETE FROM sellers WHERE telegram_id = ?", (telegram_id,))
        conn.commit()
        bot.reply_to(message, "Продавец успешно удален!")
    except:
        bot.reply_to(message, "Произошла ошибка при удалении из базы данных.")
    finally:
        conn.close()

        
 # Обработчик кнопки "Проверить"
@bot.message_handler(func=lambda message: message.text == "Проверить")
def show_sellers(message):
    try:
        conn = sqlite3.connect('kaspibot.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM sellers")
        sellers = cursor.fetchall()
        if len(sellers) > 0:
            sellers_list = "Список зарегистрированных продавцов:\n\n"
            for seller in sellers:
                sellers_list += f"id: {seller[0]}\nTelegram id: {seller[1]}\nИмя: {seller[2]}\nНомер телефона: {seller[3]}\nAPI Kaspistore: {seller[4]}\n\n"
            bot.reply_to(message, sellers_list)
        else:
            bot.reply_to(message, "Нет зарегистрированных продавцов.")
    except:
        bot.reply_to(message, "Произошла ошибка при обращении к базе данных.")
    finally:
        conn.close()

# Обработчик кнопки "Изменить"
@bot.message_handler(func=lambda message: message.text == "Изменить")
def update_seller(message):
    bot.reply_to(message, "Введите telegram id продавца, которого хотите изменить:")
    bot.register_next_step_handler(message, get_seller_telegram_id_for_update)

def get_seller_telegram_id_for_update(message):
    telegram_id = message.text
    try:
        conn = sqlite3.connect('kaspibot.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM sellers WHERE telegram_id = ?", (telegram_id,))
        seller = cursor.fetchone()
        if seller is not None:
            bot.reply_to(message, f"Текущий API Kaspistore продавца: {seller[4]}\nВведите новый API Kaspistore:")
            bot.register_next_step_handler(message, get_new_seller_kaspistore_api, telegram_id, seller[3])
        #Изменим Данные из БД kaspiusers.db
        conn = sqlite3.connect('kaspiusers.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM sellers WHERE telegram_id = ?", (telegram_id,))
        seller = cursor.fetchone()
        if seller is not None:
            bot.reply_to(message, f"Текущий API Kaspistore продавца: {seller[4]}\nВведите новый API Kaspistore:")
            bot.register_next_step_handler(message, get_new_seller_kaspistore_api, telegram_id, seller[3])
        else:
            bot.reply_to(message, "Продавец с таким telegram id не найден.")
    except:
        bot.reply_to(message, "Произошла ошибка при обращении к базе данных.")
    finally:
        conn.close()

def get_new_seller_kaspistore_api(message, telegram_id, phone_number):
    kaspistore_api = message.text
    try:
        conn = sqlite3.connect('kaspibot.db')
        cursor = conn.cursor()
        cursor.execute("UPDATE sellers SET kaspistore_api = ? WHERE telegram_id = ?", (kaspistore_api, telegram_id))
        conn.commit()
        #Изменим Данные из БД kaspiusers.db
        conn = sqlite3.connect('kaspiusers.db')
        cursor = conn.cursor()
        cursor.execute("UPDATE sellers SET kaspistore_api = ? WHERE telegram_id = ?", (kaspistore_api, telegram_id))
        conn.commit()
        bot.reply_to(message, "API Kaspistore продавца успешно изменен!")
        bot.reply_to(message, f"Текущий номер телефона продавца: {phone_number}\nВведите новый номер телефона продавца:")
        bot.register_next_step_handler(message, get_new_seller_phone_number, telegram_id)
    except:
        bot.reply_to(message, "Произошла ошибка при обращении к базе данных.")
    finally:
        conn.close()

def get_new_seller_phone_number(message, telegram_id):
    phone_number = message.text
    try:
        conn = sqlite3.connect('kaspibot.db')
        cursor = conn.cursor()
        cursor.execute("UPDATE sellers SET phone_number = ? WHERE telegram_id = ?", (phone_number, telegram_id))
        conn.commit()
        #Изменим Данные из БД kaspiusers.db
        conn = sqlite3.connect('kaspiusers.db')
        cursor = conn.cursor()
        cursor.execute("UPDATE sellers SET phone_number = ? WHERE telegram_id = ?", (phone_number, telegram_id))
        conn.commit()
        bot.reply_to(message, "Номер телефона продавца успешно изменен!")
    except:
        bot.reply_to(message, "Произошла ошибка при обращении к базе данных.")
    finally:
        conn.close()


# Запуск бота
bot.polling()
