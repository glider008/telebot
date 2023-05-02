import sqlite3
import telebot
from config_users import TOKEN
from telebot import types
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
import hashlib
from selenium.webdriver.chrome.options import Options
from selenium import webdriver

bot = telebot.TeleBot(TOKEN)

# Обработчик команды /start
@bot.message_handler(commands=['start'])
def start_handler(message):
    # Создание кнопки "Войти в кабинет"
    login_button = types.InlineKeyboardButton('Войти в кабинет', callback_data='login')

    # Создание клавиатуры с кнопкой "Войти в кабинет"
    keyboard = types.InlineKeyboardMarkup().add(login_button)

    db_conn = sqlite3.connect('kaspibot.db', check_same_thread=False)
    cursor = db_conn.cursor()
    cursor.execute("SELECT * FROM sellers WHERE telegram_id=?", (message.from_user.id,))
    seller_data = cursor.fetchone()
    db_conn.close()

    if not seller_data:
        bot.reply_to(message, "Вы не зарегистрированы в системе. Свяжитесь с Администратором @karikbol.")
        return

    bot.send_message(message.chat.id, "Добро пожаловать, " + message.from_user.first_name , reply_markup=keyboard)

# Обработчик нажатия кнопки "Войти в кабинет"
@bot.callback_query_handler(func=lambda call: call.data == 'login')
def login_callback_handler(call):
    # Получаем данные продавца из базы данных
    db_conn = sqlite3.connect('kaspibot.db', check_same_thread=False)
    cursor = db_conn.cursor()
    cursor.execute("SELECT * FROM sellers WHERE telegram_id=?", (call.from_user.id,))
    seller_data = cursor.fetchone()
    db_conn.close()

    if not seller_data:
        bot.send_message(call.message.chat.id, "Вы не зарегистрированы в системе. Свяжитесь с Администратором @karikbol.")
        return

    # Задаем следующее состояние - запрос логина
    bot.send_message(call.message.chat.id, "Введите логин:")
    bot.register_next_step_handler(call.message, login_next_handler)

# Обработчик ввода логина
def login_next_handler(message):
    # Запрашиваем у пользователя ввод пароля
    bot.send_message(message.chat.id, "Введите пароль:")
    # Сохраняем введенный логин в словаре call_data
    call_data = {"login": message.text}
    # Задаем следующее состояние - запрос пароля
    bot.register_next_step_handler(message, password_handler, call_data=call_data)


# обработчик ввода пароля
def password_handler(message, call_data):
    # настройки webdriver
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # запуск в фоновом режиме, без открытия окна браузера
    driver = webdriver.Chrome(options=chrome_options)

    # открываем страницу для входа
    driver.get('https://kaspi.kz/mc/#/login')

    # находим поля для ввода логина и пароля, вводим значения
    username_input = driver.find_element_by_name('username')
    password_input = driver.find_element_by_name('Пароль')
    username_input.send_keys(call_data["login"])
    password_input.send_keys(message.text)

    # нажимаем кнопку входа
    login_button = driver.find_element_by_css_selector('.login-form button[type="submit"]')
    login_button.click()

    # проверяем, успешен ли вход
    success = False
    try:
        success_message = driver.find_element_by_css_selector('.success-message').text
        if success_message == 'Вы успешно вошли в Кабинет':
            success = True
    except:
        pass

    # закрываем браузер и сообщаем результат пользователю
    driver.quit()

    if success:
        bot.send_message(message.chat.id, "Поздравляем! Вы успешно вошли в Кабинет")
        # сохраним telegram_id с правильным вводенной логином и парольем в таблицу "data" в БД "kaspiusers.db"
        db_conn = sqlite3.connect('kaspiusers.db', check_same_thread=False)
        cursor = db_conn.cursor()
        cursor.execute("CREATE TABLE IF NOT EXISTS data (login TEXT PRIMARY KEY, password TEXT, telegram_id INTEGER)")
        cursor.execute("INSERT INTO data (login, password, telegram_id) VALUES (?, ?, ?)",
                       (call_data["login"], message.text, message.from_user.id))
        db_conn.commit()
        db_conn.close()
    else:
        bot.send_message(message.chat.id, "Логин или пароль неверны. Повторите попытку.")
        # отправим кнопку "войти в кабинет" с сообщением "Логин или пароль не верно повторите попытку"
        login_button = types.InlineKeyboardButton('Войти в кабинет', callback_data='login')
        keyboard = types.InlineKeyboardMarkup().add(login_button)
        bot.send_message(message.chat.id, "Логин или пароль неверны. Повторите попытку.", reply_markup=keyboard)





# Обработчик всех остальных сообщений, если продавец не зарегистрирован
@bot.message_handler(func=lambda message: True)
def handle_unregistered(message):
    db_conn = sqlite3.connect('kaspibot.db', check_same_thread=False)
    cursor = db_conn.cursor()
    cursor.execute("SELECT * FROM sellers WHERE telegram_id=?", (message.from_user.id,))
    seller_data = cursor.fetchone()
    db_conn.close()

    if not seller_data:
        bot.reply_to(message, "Вы не зарегистрированы в системе. Свяжитесь с Администратором @karikbol.")
        return

# Запуск бота
bot.polling()
