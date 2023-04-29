import sqlite3
import telebot
from config_users import TOKEN
from telebot import types
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
import hashlib
import sqlite3
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


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

# Обработчик нажатия на кнопку "войти в кабинет"
@bot.callback_query_handler(func=lambda call: call.data == 'login')
def login_handler(call):
    # Отправляем сообщение с запросом логина
    bot.send_message(call.message.chat.id, "Введите логин:")
    # Задаем следующее состояние - запрос логина
    bot.register_next_step_handler(call.message, login_next_handler)


# Обработчик ввода логина
def login_next_handler(message):
    if message.text.lower() == 'отмена':
        bot.send_message(message.chat.id, "Вы отменили ввод логина.", reply_markup=types.ReplyKeyboardRemove())
        return
    call_data = {}
    call_data['login'] = message.text
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    keyboard.add(types.KeyboardButton('Отмена'))
    bot.send_message(message.chat.id, "Введите пароль:", reply_markup=keyboard)
    bot.register_next_step_handler(message, password_handler, call_data=call_data)


# Обработчик ввода пароля
def password_handler(message, call_data):
    if message.text.lower() == 'отмена':
        bot.send_message(message.chat.id, "Вы отменили ввод пароля.", reply_markup=types.ReplyKeyboardRemove())
        return

    db_conn = sqlite3.connect('kaspiusers.db', check_same_thread=False)
    cursor = db_conn.cursor()
    cursor.execute("SELECT password FROM data WHERE chat_id=?", (message.chat.id,))
    password = cursor.fetchone()
    db_conn.close()

    # Проверяем правильность введенного пароля
    if not password or message.text != password[0]:
        bot.send_message(message.chat.id, "Неправильный пароль. Введите логин и пароль заново.")
        # Возвращаемся к началу, запросу логина
        bot.register_next_step_handler(message, login_next_handler)
        return

    # Пароль верный, отсылаем сообщение об успешной авторизации
    bot.send_message(message.chat.id, "Вы успешно авторизовались!")

    # Создаем экземпляр драйвера Chrome
    options = Options()
    options.headless = True
    driver = webdriver.Chrome(options=options)

    # Переходим на страницу логина
    driver.get("https://kaspi.kz/mc/#/login")

    # Находим поле ввода логина и заполняем его
    login_field = driver.find_element_by_xpath("//input[@placeholder='Логин']")
    login_field.send_keys(login)

    # Находим поле ввода пароля и заполняем его
    password_field = driver.find_element_by_xpath("//input[@placeholder='Пароль']")
    password_field.send_keys(password)

    # Находим кнопку "Войти" и нажимаем на нее
    login_button = driver.find_element_by_xpath("//button[@type='submit']")
    login_button.click()

    # Ждем пока загрузится страница с результатом проверки
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, "//div[@class='mc-dashboard-container']"))
    )

    # Проверяем результат авторизации
    if driver.current_url == "https://kaspi.kz/mc/#/dashboard":
        bot.send_message(message.chat.id, "Вы успешно авторизовались!")
    else:
        bot.send_message(message.chat.id, "Неправильный логин или пароль")

    driver.quit()


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