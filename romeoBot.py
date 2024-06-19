import os
import telebot
import MySQLdb
from telebot import types
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()
BOT_TOKEN = os.environ.get('BOT_TOKEN')
bot = telebot.TeleBot(BOT_TOKEN)

user_state = {}

# Define states
STATE_DEFAULT = 0
STATE_CARI_MHS = 1
STATE_CARI_MATKUL = 2

def connect_db():
    return MySQLdb.connect(host="127.0.0.1", user="root", password="", database="db_romeoBot", port=3306)

def inbox(username, message, date):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO inbox (username, message, date) VALUES (%s, %s, %s)", (username,  message, date))
    conn.commit()
    conn.close()

def outbox(username, message, date):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO outbox (username, message, date) VALUES (%s, %s, %s)", (username,  message, date))
    conn.commit()
    conn.close()

def get_mahasiswa_by_nim(nim):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM mahasiswa WHERE nim = %s", (nim,))
    mahasiswa = cursor.fetchone()
    conn.close()
    return mahasiswa

def get_matkul_by_name(matkul_name):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM matkul WHERE nama LIKE %s", ('%' + matkul_name + '%',))
    matkul = cursor.fetchall()
    conn.close()
    return matkul

@bot.message_handler(commands=['cari_mhs'])
def cari_mahasiswa(m):
    answer = "Masukkan NIM mahasiswa yang ingin Anda cari:"
    bot.send_message(m.chat.id, answer)
    username = m.from_user.username
    message = m.text
    date = datetime.now()
    inbox(username, message, date)
    outbox(username, answer, date)
    bot.register_next_step_handler(m, process_nim_input)

def process_nim_input(m):
    nim = m.text
    mahasiswa = get_mahasiswa_by_nim(nim)
    if mahasiswa:
        info_mahasiswa = f"NIM: {mahasiswa[0]}\nNama: {mahasiswa[1]}\nJurusan: {mahasiswa[2]}"
        bot.send_message(m.chat.id, info_mahasiswa)
        user_state[m.chat.id] = STATE_DEFAULT
    else:
        bot.send_message(m.chat.id, "Maaf, mahasiswa dengan NIM tersebut tidak ditemukan.")

@bot.message_handler(commands=['cari_matkul'])
def cari_matkul(m):
    answer = "Masukkan nama mata kuliah yang ingin Anda cari:"
    bot.send_message(m.chat.id, answer)
    username = m.from_user.username
    message = m.text
    date = datetime.now()
    inbox(username, message, date)
    outbox(username, answer, date)
    bot.register_next_step_handler(m, process_matkul_name_input)

def process_matkul_name_input(m):
    matkul_name = m.text
    mata_kuliah = get_matkul_by_name(matkul_name)
    if mata_kuliah:
        info_matkul = "\n".join([f"ID Matkul: {matkul[0]}\nNama Matkul: {matkul[1]}" for matkul in mata_kuliah])
        bot.send_message(m.chat.id, info_matkul)
        user_state[m.chat.id] = STATE_DEFAULT

    else:
        bot.send_message(m.chat.id, "Maaf, mata kuliah dengan nama tersebut tidak ditemukan.")

#start
@bot.message_handler(commands=['start', 'hello'])
def start(m):
    answer ="Hello, my name is romeo, im Raden Dean Diningrat's Bot. u wanna see smth? if u want, type /show_menu"
    bot.send_message(m.chat.id, answer)
    username = m.from_user.username
    message = m.text
    date = datetime.now()
    inbox(username, message, date)
    outbox(username, answer, date)

# show menu
@bot.message_handler(commands=['show_menu'])
def handle_show_menu(m):
    user_state[m.chat.id] = STATE_DEFAULT
    show_menu(m)

@bot.message_handler(func=lambda message: True)
def handle_menu(m):
    if m.chat.id not in user_state:
        user_state[m.chat.id] = STATE_DEFAULT

    if user_state[m.chat.id] == STATE_DEFAULT:
        option = m.text
        data = get_data_from_database(option, m)
        if data is not None:
            bot.send_message(m.chat.id, data)
    elif user_state[m.chat.id] == STATE_CARI_MHS:
        process_nim_input(m)
    elif user_state[m.chat.id] == STATE_CARI_MATKUL:
        process_matkul_name_input(m)

def show_menu(m):
    options = get_menu_options()
    markup = types.ReplyKeyboardMarkup(row_width=1)
    for option in options:
        option_text = str(option[1]) 
        markup.add(types.KeyboardButton(option_text)) 
    bot.send_message(m.chat.id, "Pilih salah satu menu:", reply_markup=markup)
    username = m.from_user.username
    message = m.text
    date = datetime.now()
    inbox(username, message, date)
    outbox(username, "Show menu", date)

def get_menu_options():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM menu_options")
    options = cursor.fetchall()
    conn.close()
    return options

def get_data_from_database(option, m):
    if option == "cari_mhs":
        user_state[m.chat.id] = STATE_CARI_MHS
        return "Enter the student's NIM:"
    elif option == "cari_matkul":
        user_state[m.chat.id] = STATE_CARI_MATKUL
        return "Enter the name of the course you want to search:"
    else:
        return "Sorry, the command is not recognized."

bot.polling()
