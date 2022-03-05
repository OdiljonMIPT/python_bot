import telebot
import sqlite3
from time import sleep
from config import (token, admins, chat_id)
from telebot import types
#import pandas as pd
from openpyxl.workbook import Workbook
import requests
import gspread
from oauth2client.service_account import ServiceAccountCredentials

scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name('credentials.json', scope)
client = gspread.authorize(creds)
sheet = client.open("DB").worksheet("база")

USER_DATA = []
NUMOFTHREADS = 9

names = {}
surnames = {}
books = {}
phones = {}
locates = {}

bot = telebot.TeleBot(token, threaded=True, num_threads=NUMOFTHREADS)


# DATABASE
def database():
    db = sqlite3.connect('data.db', check_same_thread=False)
    sql = db.cursor()
    sql.execute('''CREATE TABLE IF NOT EXISTS users(
        user_id INTEGER,
        name TEXT,
        surname TEXT,
        phone_num TEXT,
        book TEXT)''')
    sql.close()
    db.close()


database()


def get_address_from_coords(coords):
    PARAMS = {
        "apikey": "7d26f81e-ec8b-4744-b94c-6fcddfbc5d56",
        "format": "json",
        "lang": "ru_RU",
        "kind": "house",
        "geocode": coords
    }

    try:
        r = requests.get(url="https://geocode-maps.yandex.ru/1.x/", params=PARAMS)
        json_data = r.json()
        address_str = json_data["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]["metaDataProperty"][
            "GeocoderMetaData"]["AddressDetails"]["Country"]["AddressLine"]
        return address_str

    except Exception as e:
        return "Не могу определить адрес по этой локации/координатам.\n\Отправьте локацию"


def get_user_id(user_id, user_data_):
    for index, user_data in enumerate(user_data_):
        if user_id in user_data:
            return index
    USER_DATA.append([user_id, 0, 0, 0])
    return get_user_id(user_id, USER_DATA)


def sleep_for(user_index):
    global USER_DATA
    total_sec = int(USER_DATA[user_index][1]) * 60 + \
                int(USER_DATA[user_index][2]) * 60 * 60 + \
                int(USER_DATA[user_index][3]) * 60 * 60 * 24
    sleep(total_sec)


#def get_excel_users():
    #cnxn = sqlite3.connect('data.db')
    #cursor = cnxn.cursor()
    #script = """SELECT * FROM users"""

    #cursor.execute(script)

    #columns = [desc[0] for desc in cursor.description]
    #data = cursor.fetchall()
    #df = pd.DataFrame(list(data), columns=columns)

    #writer = pd.ExcelWriter('users.xlsx')
    #df.to_excel(writer, sheet_name='bar')
    #writer.save()

    #return 'users.xlsx'


@bot.message_handler(commands=['start'])
def instart(message):
    try:
        global USER_DATA
        user_id = get_user_id(message.chat.id, USER_DATA)
        for index in range(1, 4):
            USER_DATA[user_id][index] = 0
        user_id = USER_DATA[user_id]
        db = sqlite3.connect('data.db')
        sql = db.cursor()

        sql.execute("INSERT INTO users(user_id) VALUES(?)", (message.from_user.id,))
        db.commit()

        msg = bot.send_message(message.chat.id,
                               f"*Assalomu Aleykum!* \n\n Ismingizni yozib qoldiring:",
                               parse_mode='Markdown')
        bot.register_next_step_handler(msg, USR_name_func)

        sql.close()
        db.close()

    except Exception as e:
        print(e)


@bot.message_handler(content_types=['text'])
def intext(message):
    if message.text.lower() == 'admin':
        if message.chat.id in admins:
            help_ = types.InlineKeyboardMarkup()
            help_.add(types.InlineKeyboardButton(text='Инструкции по использ.', callback_data='help'))
            help_.add(types.InlineKeyboardButton(text='Рассылка', callback_data='rassylka'))
            help_.add(types.InlineKeyboardButton(text='Статистика', callback_data='stat'))
            bot.send_chat_action(message.chat.id, 'typing')
            bot.send_message(message.chat.id, text="*Добро пожаловать в админку*", parse_mode='Markdown',
                             reply_markup=help_)
    elif message.text.lower() == 'zerobooks21':
        help_ = types.InlineKeyboardMarkup()
        help_.add(types.InlineKeyboardButton(text='Инструкции по использ.', callback_data='help'))
        help_.add(types.InlineKeyboardButton(text='Рассылка', callback_data='rassylka'))
        help_.add(types.InlineKeyboardButton(text='Статистика', callback_data='stat'))
        bot.send_chat_action(message.chat.id, 'typing')
        bot.send_message(message.chat.id, text="*Добро пожаловать в админку*", parse_mode='Markdown',
                         reply_markup=help_)


@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    #if call.data == 'excel':
        #bot.send_chat_action(call.message.chat.id, 'upload_document')
        #doc = open(get_excel_users(), 'rb')
        #bot.send_document(call.message.chat.id, doc)
    if call.data == 'help':
        adbck = types.InlineKeyboardMarkup(row_width=1)
        adbck.add(types.InlineKeyboardButton(text="Назад ↩️", callback_data='back_to_admin'))
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="@prosto_ya_2002",
                              reply_markup=adbck)
    elif call.data == 'rassylka':
        choose = types.InlineKeyboardMarkup()
        choose.add(types.InlineKeyboardButton(text='фото', callback_data='photo'),
                   types.InlineKeyboardButton(text='видео', callback_data='video'))
        choose.add(types.InlineKeyboardButton(text='cообщение(text)', callback_data='text'),
                   types.InlineKeyboardButton(text='документ(file)', callback_data='file'))
        choose.add(types.InlineKeyboardButton(text='аудио/голос', callback_data='audio/voice'))
        choose.add(types.InlineKeyboardButton(text='видеосообщение(videonote)', callback_data='videonote'))
        choose.add(types.InlineKeyboardButton(text='⏪ ⏪ ⏪', callback_data='back_to_admin'))

        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text='Выберите:',
                              reply_markup=choose)
    elif call.data == 'stat':
        db = sqlite3.connect('data.db', check_same_thread=False)
        sql = db.cursor()
        sql.execute("SELECT COUNT(*) FROM users")
        q = sql.fetchall()
        adbck = types.InlineKeyboardMarkup(row_width=1)
        adbck.add(types.InlineKeyboardButton(text="Назад ↩️", callback_data='back_to_admin'))
        for i in q:
            bot.edit_message_text(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                text="👤 В боте: " + str(i[0]) + f" человек",
                reply_markup=adbck)

    elif call.data == 'back_to_admin':
        help_ = types.InlineKeyboardMarkup()
        help_.add(types.InlineKeyboardButton(text='Инструкции по использ.', callback_data='help'))
        help_.add(types.InlineKeyboardButton(text='Рассылка', callback_data='rassylka'))
        help_.add(types.InlineKeyboardButton(text='Статистика', callback_data='stat'))
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text="*Добро пожаловать в админку*", parse_mode='Markdown', reply_markup=help_)
    elif call.data == 'photo':
        bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
        send_to_all_photo(call.message)
    elif call.data == 'video':
        bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
        send_to_all_video(call.message)
    elif call.data == 'text':
        bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
        send_to_all_text(call.message)
    elif call.data == 'file':
        bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
        send_to_all_file(call.message)
    elif call.data == 'audio/voice':
        bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
        send_to_all_audio(call.message)
    elif call.data == 'videonote':
        bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
        send_to_all_videonote(call.message)


def linky(message):
    with sqlite3.connect("data.db") as con:
        cur = con.cursor()

    yt = message.text
    cur.execute("SELECT youtube FROM links")
    con.commit()

    if cur.fetchone() is None:
        cur.execute("INSERT INTO links(youtube) VALUES(?)", (yt,))
        con.commit()
    else:
        cur.execute("UPDATE links SET youtube = (?)", (yt,))
        con.commit()

    help_ = types.InlineKeyboardMarkup()
    help_.add(types.InlineKeyboardButton(text='Инструкции по использ.', callback_data='help'))
    help_.add(types.InlineKeyboardButton(text='Рассылка', callback_data='rassylka'))
    help_.add(types.InlineKeyboardButton(text='Статистика', callback_data='stat'))

    bot.send_message(message.chat.id, f"Link updated: {yt}", reply_markup=help_)


def USR_name_func(message):
    try:
        with sqlite3.connect("data.db") as con:
            cur = con.cursor()

        name = message.text
        user_id = message.from_user.id
        names[str(message.from_user.id) + "name"] = name
        print(names)

        cur.execute("UPDATE users SET name = (?) WHERE user_id = (?)", (name, user_id,))
        con.commit()
        msg = bot.send_message(user_id,
                               f"Familiyangiz:")
        bot.register_next_step_handler(msg, USR_surname_func)
    except Exception as e:
        print(e)


def USR_surname_func(message):
    try:
        with sqlite3.connect("data.db") as con:
            cur = con.cursor()

        surname = message.text
        user_id = message.from_user.id
        surnames[str(message.from_user.id) + "surname"] = surname
        print(surnames)

        cur.execute("UPDATE users SET surname = (?) WHERE user_id = (?)", (surname, user_id,))
        con.commit()
        cont = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
        cont.add(types.KeyboardButton(text="Telefon raqamni yuborish", request_contact=True))
        msg = bot.send_message(user_id,
                               f"Telefon raqamingizni yuboring:", parse_mode='Markdown', reply_markup=cont)
        bot.register_next_step_handler(msg, num_USR_func)
    except Exception as e:
        print(e)


def num_USR_func(message):
    try:
        with sqlite3.connect("data.db") as con:
            cur = con.cursor()

        user_id = message.from_user.id

        remove = types.ReplyKeyboardRemove()
        cont = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
        cont.add(types.KeyboardButton(text="Telefon raqamni yuborish", request_contact=True))

        if message.content_type == 'contact':
            if message.contact != None:
                number_of_user = message.contact.phone_number
                phones[str(message.from_user.id) + "number"] = number_of_user
                print(phones)
                cur.execute("UPDATE users SET phone_num = (?) WHERE user_id = (?)",
                            (message.contact.phone_number, user_id,))
                con.commit()

                markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
                itembtn1 = types.KeyboardButton('HR MENEJER-KORPORATIV MUNOSABATLAR YARATUVCHISI')
                markup.add(itembtn1)
                msg = bot.send_message(user_id, "Qaysi kitobga buyurtma bermoqchisiz?", reply_markup=markup)
                bot.register_next_step_handler(msg, process_book_step)

            else:
                msg = bot.send_message(user_id, f"_Хатолик :( Илтимос бошидан!❌_", parse_mode='Markdown',
                                       reply_markup=cont)
                bot.register_next_step_handler(msg, num_USR_func)
        elif message.content_type == 'text':
            msg = bot.send_message(user_id, f"_Хатолик :( Илтимос бошидан!❌_", parse_mode='Markdown',
                                   reply_markup=cont)
            bot.register_next_step_handler(msg, num_USR_func)

    except Exception as e:
        raise e


def process_book_step(message):
    try:
        with sqlite3.connect("data.db") as con:
            cur = con.cursor()

        user_id = message.from_user.id
        book_of_user = message.text
        books[str(message.from_user.id) + "book"] = book_of_user
        cur.execute("UPDATE users SET book = (?) WHERE user_id = (?)", (book_of_user, user_id,))
        con.commit()
        location = types.ReplyKeyboardMarkup(resize_keyboard=True)
        location.add(types.KeyboardButton('Manzilni yuborish', request_location=True))
        msg = bot.send_message(message.chat.id, "Kitob yetkaziladigan manzilni yuboring (lokatsiya):",
                               reply_markup=location)
        bot.register_next_step_handler(msg, ask_ur_location)
    except Exception as e:
        raise e


def ask_ur_location(message):
    if message.content_type == 'location':
        current_position = (message.location.longitude, message.location.latitude)
        coords = f"{current_position[0]},{current_position[1]}"
        address_str = get_address_from_coords(coords)

        location_of_user = address_str
        print(location_of_user)
        locates[str(message.from_user.id) + "locate"] = location_of_user
        print(locates)
        remove = types.ReplyKeyboardRemove(True)

        name = names[str(message.from_user.id) + 'name']
        surname = surnames[str(message.from_user.id) + 'surname']
        number = phones[str(message.from_user.id) + 'number']
        book = books[str(message.from_user.id) + 'book']
        locat = locates[str(message.from_user.id) + 'locate']

        bot.send_message(chat_id,
                         f"👤Name: {name}\n"
                         f"👤Surname: {surname}\n"
                         f"📞Phone: {number}\n"
                         f"📚Book: {book}\n"
                         f"🏛Location: {locat}",
                         reply_markup=remove)
        sheet.insert_row([name, surname, number, book, locat], 2)
        bot.forward_message(chat_id, message.from_user.id, message.message_id)
        bot.send_message(message.chat.id, "So'rovingiz qabul qilindi. Tez orada menejerimiz sizga aloqaga chiqadi☺️",
                         reply_markup=remove)


def send_to_all_photo(message):
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    cancel = types.KeyboardButton('⏪ Отмена')
    markup.add(cancel)
    msg = bot.send_photo(
        chat_id=message.chat.id,
        photo='https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSYuueBO_Rhjv8O4w1pE99q4t6BD9hrT96w_Q&usqp=CAU',
        caption=f"<i>Заголовок(text)</i>\n\n<code>название кнопки + link</code>",
        reply_markup=markup,
        parse_mode='html')
    bot.register_next_step_handler(msg, message_everyone_photo)


def send_to_all_video(message):
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    cancel = types.KeyboardButton('⏪ Отмена')
    markup.add(cancel)
    msg = bot.send_photo(
        chat_id=message.chat.id,
        photo='https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSYuueBO_Rhjv8O4w1pE99q4t6BD9hrT96w_Q&usqp=CAU',
        caption=f"Video\n\n<i>Заголовок(text)</i>\n\n<code>название кнопки + link</code>",
        reply_markup=markup,
        parse_mode='html')
    bot.register_next_step_handler(msg, message_everyone_video)


def send_to_all_text(message):
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    cancel = types.KeyboardButton('⏪ Отмена')
    markup.add(cancel)
    msg = bot.send_message(
        chat_id=message.chat.id,
        text=f"<i>Заголовок(text)</i>\n\n<code>название кнопки + link</code>",
        reply_markup=markup,
        parse_mode='html')
    bot.register_next_step_handler(msg, message_everyone_text)


def send_to_all_file(message):
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    cancel = types.KeyboardButton('⏪ Отмена')
    markup.add(cancel)
    msg = bot.send_message(
        chat_id=message.chat.id,
        text=f"<b>Document</b>\n\n<i>Заголовок(text)</i>\n\n<code>название кнопки + link</code>",
        reply_markup=markup,
        parse_mode='html')
    bot.register_next_step_handler(msg, message_everyone_file)


def send_to_all_audio(message):
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    cancel = types.KeyboardButton('⏪ Отмена')
    markup.add(cancel)
    msg = bot.send_message(
        chat_id=message.chat.id,
        text=f"<b>Audio / Voice</b>\n\n<i>Заголовок(text)</i>\n\n<code>название кнопки + link</code>",
        reply_markup=markup,
        parse_mode='html')
    bot.register_next_step_handler(msg, message_everyone_audio)


def send_to_all_videonote(message):
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    cancel = types.KeyboardButton('⏪ Отмена')
    markup.add(cancel)
    msg = bot.send_message(
        chat_id=message.chat.id,
        text=f"Video Note (Видеосообщение)\n\n<i>Заголовок(text)</i>\n\n<code>название кнопки + link</code>",
        reply_markup=markup,
        parse_mode='html')
    bot.register_next_step_handler(msg, message_everyone_videonote)


def message_everyone_photo(message):
    if message.text == "⏪ Отмена":
        remove = types.ReplyKeyboardRemove()
        name = message.from_user.first_name
        help_ = types.InlineKeyboardMarkup()
        help_.add(types.InlineKeyboardButton(text='Инструкции по использ.', callback_data='help'))
        help_.add(types.InlineKeyboardButton(text='Рассылка', callback_data='rassylka'))
        help_.add(types.InlineKeyboardButton(text='Статистика', callback_data='stat'))
        bot.send_message(message.chat.id, '....', reply_markup=remove)
        bot.send_message(message.chat.id, 'Привет {0}, вы в админ панеле'.format(message.from_user.first_name),
                         reply_markup=help_)
    else:
        if message.content_type == "photo":
            photo = message.photo[-1].file_id
            if message.caption != None:
                matched_lines = [line for line in message.caption.split('\n') if " + " in line]
                not_matched_lines = [lines for lines in message.html_caption.split('\n') if not " + " in lines]
                markup = types.InlineKeyboardMarkup(row_width=1)
                if len(matched_lines) > 0:
                    for row in matched_lines:
                        link = row.split(' + ')[1]
                        name = row.split(" + ")[0]
                        ban = types.InlineKeyboardButton(text=f'{name}', url=f'{link}')
                        markup.add(ban)
                    capt = '\n'.join(not_matched_lines)
                else:
                    capt = message.html_caption
            else:
                markup = types.InlineKeyboardMarkup(row_width=1)
                capt = message.html_caption
            remove = types.ReplyKeyboardRemove()
            bot.send_message(message.chat.id, f"Loading... / Sending...", reply_markup=remove)
            photo_to_all(message, markup, capt, photo)
        else:
            markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
            cancel = types.KeyboardButton('⏪ Отмена')
            markup.add(cancel)
            msg = bot.send_photo(
                chat_id=message.chat.id,
                photo='https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSYuueBO_Rhjv8O4w1pE99q4t6BD9hrT96w_Q&usqp=CAU',
                caption=f"<i>Заголовок(text)</i>\n\n<code>название кнопки + link</code>",
                reply_markup=markup,
                parse_mode='html')
            bot.register_next_step_handler(msg, message_everyone_photo)


def message_everyone_video(message):
    if message.text == "⏪ Отмена":
        remove = types.ReplyKeyboardRemove()
        name = message.from_user.first_name
        help_ = types.InlineKeyboardMarkup()
        help_.add(types.InlineKeyboardButton(text='Инструкции по использ.', callback_data='help'))
        help_.add(types.InlineKeyboardButton(text='Рассылка', callback_data='rassylka'))
        help_.add(types.InlineKeyboardButton(text='Статистика', callback_data='stat'))
        bot.send_message(message.chat.id, '....', reply_markup=remove)
        bot.send_message(message.chat.id, 'Привет {0}, вы в админ панеле'.format(message.from_user.first_name),
                         reply_markup=help_)
    else:
        if message.content_type == "video":
            video = message.video.file_id
            if message.caption != None:
                matched_lines = [line for line in message.caption.split('\n') if " + " in line]
                not_matched_lines = [lines for lines in message.html_caption.split('\n') if not " + " in lines]
                markup = types.InlineKeyboardMarkup(row_width=1)
                if len(matched_lines) > 0:
                    for row in matched_lines:
                        link = row.split(' + ')[1]
                        name = row.split(" + ")[0]
                        ban = types.InlineKeyboardButton(text=f'{name}', url=f'{link}')
                        markup.add(ban)
                    capt = '\n'.join(not_matched_lines)
                else:
                    capt = message.html_caption
            else:
                markup = types.InlineKeyboardMarkup(row_width=1)
                capt = message.html_caption
            remove = types.ReplyKeyboardRemove()
            bot.send_message(message.chat.id, f"Loading... / Sending...", reply_markup=remove)
            video_to_all(message, markup, capt, video)
        else:
            markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
            cancel = types.KeyboardButton('⏪ Отмена')
            markup.add(cancel)
            msg = bot.send_photo(
                chat_id=message.chat.id,
                photo='https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSYuueBO_Rhjv8O4w1pE99q4t6BD9hrT96w_Q&usqp=CAU',
                caption=f"<i>Заголовок(text)</i>\n\n<code>название кнопки + link</code>",
                reply_markup=markup,
                parse_mode='html')
            bot.register_next_step_handler(msg, message_everyone_video)


def message_everyone_text(message):
    if message.text == "⏪ Отмена":
        remove = types.ReplyKeyboardRemove()
        name = message.from_user.first_name
        help_ = types.InlineKeyboardMarkup()
        help_.add(types.InlineKeyboardButton(text='Инструкции по использ.', callback_data='help'))
        help_.add(types.InlineKeyboardButton(text='Рассылка', callback_data='rassylka'))
        help_.add(types.InlineKeyboardButton(text='Статистика', callback_data='stat'))
        bot.send_message(message.chat.id, '....', reply_markup=remove)
        bot.send_message(message.chat.id, 'Привет {0}, вы в админ панеле'.format(message.from_user.first_name),
                         reply_markup=help_)
    else:
        if message.content_type == "text":
            text = message.html_text
            matched_lines = [line for line in message.text.split('\n') if " + " in line]
            not_matched_lines = [lines for lines in message.html_text.split('\n') if not " + " in lines]
            markup = types.InlineKeyboardMarkup(row_width=1)
            if len(matched_lines) > 0:
                for row in matched_lines:
                    link = row.split(' + ')[1]
                    name = row.split(" + ")[0]
                    ban = types.InlineKeyboardButton(text=f'{name}', url=f'{link}')
                    markup.add(ban)
                text = '\n'.join(not_matched_lines)
            else:
                markup = types.InlineKeyboardMarkup(row_width=1)
                text = message.html_text
            remove = types.ReplyKeyboardRemove()
            bot.send_message(message.chat.id, f"Loading... / Sending...", reply_markup=remove)
            text_to_all(message, markup, text)
        else:
            markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
            cancel = types.KeyboardButton('⏪ Отмена')
            markup.add(cancel)
            msg = bot.send_message(
                chat_id=message.chat.id,
                text=f"<i>Заголовок(text)</i>\n\n<code>название кнопки + link</code>",
                reply_markup=markup,
                parse_mode='html')
            bot.register_next_step_handler(msg, message_everyone_text)


def message_everyone_file(message):
    if message.text == "⏪ Отмена":
        remove = types.ReplyKeyboardRemove()
        name = message.from_user.first_name
        help_ = types.InlineKeyboardMarkup()
        help_.add(types.InlineKeyboardButton(text='Инструкции по использ.', callback_data='help'))
        help_.add(types.InlineKeyboardButton(text='Рассылка', callback_data='rassylka'))
        help_.add(types.InlineKeyboardButton(text='Статистика', callback_data='stat'))
        bot.send_message(message.chat.id, '....', reply_markup=remove)
        bot.send_message(message.chat.id, 'Привет {0}, вы в админ панеле'.format(message.from_user.first_name),
                         reply_markup=help_)
    else:
        if message.content_type == "document":
            document = message.document.file_id
            if message.caption != None:
                matched_lines = [line for line in message.caption.split('\n') if " + " in line]
                not_matched_lines = [lines for lines in message.caption.split('\n') if not " + " in lines]
                markup = types.InlineKeyboardMarkup(row_width=1)
                if len(matched_lines) > 0:
                    for row in matched_lines:
                        link = row.split(' + ')[1]
                        name = row.split(" + ")[0]
                        ban = types.InlineKeyboardButton(text=f'{name}', url=f'{link}')
                        markup.add(ban)
                    capt = '\n'.join(not_matched_lines)
                else:
                    capt = message.caption
            else:
                markup = types.InlineKeyboardMarkup(row_width=1)
                capt = message.caption
            remove = types.ReplyKeyboardRemove()
            bot.send_message(message.chat.id, f"Loading... / Sending...", reply_markup=remove)
            file_to_all(message, markup, capt, document)
        else:
            markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
            cancel = types.KeyboardButton('⏪ Отмена')
            markup.add(cancel)
            msg = bot.send_message(
                chat_id=message.chat.id,
                text=f"<i>Заголовок(text)</i>\n\n<code>название кнопки + link</code>",
                reply_markup=markup,
                parse_mode='html')
            bot.register_next_step_handler(msg, message_everyone_file)


def message_everyone_audio(message):
    if message.text == "⏪ Отмена":
        remove = types.ReplyKeyboardRemove()
        name = message.from_user.first_name
        help_ = types.InlineKeyboardMarkup()
        help_.add(types.InlineKeyboardButton(text='Инструкции по использ.', callback_data='help'))
        help_.add(types.InlineKeyboardButton(text='Рассылка', callback_data='rassylka'))
        help_.add(types.InlineKeyboardButton(text='Статистика', callback_data='stat'))
        bot.send_message(message.chat.id, '....', reply_markup=remove)
        bot.send_message(message.chat.id, 'Привет {0}, вы в админ панеле'.format(message.from_user.first_name),
                         reply_markup=help_)
    else:
        if message.content_type == "audio":
            audio = message.audio.file_id
            if message.caption != None:
                matched_lines = [line for line in message.caption.split('\n') if " + " in line]
                not_matched_lines = [lines for lines in message.html_caption.split('\n') if not " + " in lines]
                markup = types.InlineKeyboardMarkup(row_width=1)
                if len(matched_lines) > 0:
                    for row in matched_lines:
                        link = row.split(' + ')[1]
                        name = row.split(" + ")[0]
                        ban = types.InlineKeyboardButton(text=f'{name}', url=f'{link}')
                        markup.add(ban)
                    capt = '\n'.join(not_matched_lines)
                else:
                    capt = message.html_caption
            else:
                markup = types.InlineKeyboardMarkup(row_width=1)
                capt = message.html_caption
            remove = types.ReplyKeyboardRemove()
            bot.send_message(message.chat.id, f"Loading... / Sending...", reply_markup=remove)
            audio_to_all(message, markup, capt, audio)
        elif message.content_type == "voice":
            voice = message.voice.file_id
            if message.caption != None:
                matched_lines = [line for line in message.caption.split('\n') if " + " in line]
                not_matched_lines = [lines for lines in message.html_caption.split('\n') if not " + " in lines]
                markup = types.InlineKeyboardMarkup(row_width=1)
                if len(matched_lines) > 0:
                    for row in matched_lines:
                        link = row.split(' + ')[1]
                        name = row.split(" + ")[0]
                        ban = types.InlineKeyboardButton(text=f'{name}', url=f'{link}')
                        markup.add(ban)
                    capt = '\n'.join(not_matched_lines)
                else:
                    capt = message.html_caption
            else:
                markup = types.InlineKeyboardMarkup(row_width=1)
                capt = message.html_caption
            remove = types.ReplyKeyboardRemove()
            bot.send_message(message.chat.id, f"Loading... / Sending...", reply_markup=remove)
            audio_to_all(message, markup, capt, voice)
        else:
            markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
            cancel = types.KeyboardButton('⏪ Отмена')
            markup.add(cancel)
            msg = bot.send_message(
                chat_id=message.chat.id,
                text=f"<b>Audio / Voice</b>\n\n<i>Заголовок(text)</i>\n\n<code>название кнопки + link</code>",
                reply_markup=markup,
                parse_mode='html')
            bot.register_next_step_handler(msg, message_everyone_audio)


def message_everyone_videonote(message):
    if message.text == "⏪ Отмена":
        remove = types.ReplyKeyboardRemove()
        name = message.from_user.first_name
        help_ = types.InlineKeyboardMarkup()
        help_.add(types.InlineKeyboardButton(text='Инструкции по использ.', callback_data='help'))
        help_.add(types.InlineKeyboardButton(text='Рассылка', callback_data='rassylka'))
        help_.add(types.InlineKeyboardButton(text='Статистика', callback_data='stat'))
        bot.send_message(message.chat.id, '....', reply_markup=remove)
        bot.send_message(message.chat.id, 'Привет {0}, вы в админ панеле'.format(message.from_user.first_name),
                         reply_markup=help_)
    else:
        if message.content_type == "video_note":
            videonote = message.video_note.file_id
            markup = types.InlineKeyboardMarkup(row_width=1)
            remove = types.ReplyKeyboardRemove()
            bot.send_message(message.chat.id, f"Loading... / Sending...", reply_markup=remove)
            videonote_to_all(message, markup, videonote)
        else:
            markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
            cancel = types.KeyboardButton('⏪ Отмена')
            markup.add(cancel)
            msg = bot.send_message(
                chat_id=message.chat.id,
                text=f"Video Note (Видеосообщение)\n\n<i>Заголовок(text)</i>\n\n<code>название кнопки + link</code>",
                reply_markup=markup,
                parse_mode='html')
            bot.register_next_step_handler(msg, message_everyone_videonote)


def photo_to_all(message, markup, capt, photo):
    num = 0
    num_error = 0
    with sqlite3.connect("data.db") as con:
        cur = con.cursor()

    cur.execute("SELECT user_id FROM users")
    con.commit()

    Lmy = cur.fetchall()
    for i in Lmy:
        try:
            if message.content_type == "photo":
                bot.send_photo(i[0], photo, caption=capt, parse_mode='html', reply_markup=markup)
                num += 1
        except Exception as ex:
            num_error += 1
            print(ex)
    if num == 0:
        result = f"Такой ссылки нет или вы ошиблись."
    else:
        if num_error == 0:
            result = f"Сообщение успешно дошло до {str(num)} человек."
        else:
            result = f"Сообщение успешно дошло до {str(num)} человек и по какой-то причине не дошло до {str(num_error)} человек."
    choose = types.InlineKeyboardMarkup()
    choose.add(types.InlineKeyboardButton(text='фото', callback_data='photo'),
               types.InlineKeyboardButton(text='видео', callback_data='video'))
    choose.add(types.InlineKeyboardButton(text='cообщение(text)', callback_data='text'),
               types.InlineKeyboardButton(text='документ(file)', callback_data='file'))
    choose.add(types.InlineKeyboardButton(text='аудио/голос', callback_data='audio/voice'))
    choose.add(types.InlineKeyboardButton(text='видеосообщение(videonote)', callback_data='videonote'))
    choose.add(types.InlineKeyboardButton(text='⏪ ⏪ ⏪', callback_data='back_to_admin'))
    bot.send_message(chat_id=message.chat.id, text=result, reply_markup=choose)


def video_to_all(message, markup, capt, video):
    num = 0
    num_error = 0
    with sqlite3.connect("data.db") as con:
        cur = con.cursor()

    cur.execute("SELECT user_id FROM users")
    con.commit()

    Lmy = cur.fetchall()
    for i in Lmy:
        try:
            if message.content_type == "video":
                bot.send_video(i[0], video, caption=capt, parse_mode='html', reply_markup=markup)
                num += 1
        except Exception as ex:
            num_error += 1
            print(ex)
    if num == 0:
        result = f"Такой ссылки нет или вы ошиблись."
    else:
        if num_error == 0:
            result = f"Сообщение успешно дошло до {str(num)} человек."
        else:
            result = f"Сообщение успешно дошло до {str(num)} человек и по какой-то причине не дошло до {str(num_error)} человек."
    choose = types.InlineKeyboardMarkup()
    choose.add(types.InlineKeyboardButton(text='фото', callback_data='photo'),
               types.InlineKeyboardButton(text='видео', callback_data='video'))
    choose.add(types.InlineKeyboardButton(text='cообщение(text)', callback_data='text'),
               types.InlineKeyboardButton(text='документ(file)', callback_data='file'))
    choose.add(types.InlineKeyboardButton(text='аудио/голос', callback_data='audio/voice'))
    choose.add(types.InlineKeyboardButton(text='видеосообщение(videonote)', callback_data='videonote'))
    choose.add(types.InlineKeyboardButton(text='⏪ ⏪ ⏪', callback_data='back_to_admin'))
    bot.send_message(chat_id=message.chat.id, text=result, reply_markup=choose)


def text_to_all(message, markup, text):
    num = 0
    num_error = 0
    with sqlite3.connect("data.db") as con:
        cur = con.cursor()

    cur.execute("SELECT user_id FROM users")
    con.commit()

    Lmy = cur.fetchall()
    for i in Lmy:
        try:
            if message.content_type == "text":
                bot.send_message(i[0], text=text, parse_mode='html', reply_markup=markup)
                num += 1
        except Exception as ex:
            num_error += 1
            print(ex)
    if num == 0:
        result = f"Такой ссылки нет или вы ошиблись."
    else:
        if num_error == 0:
            result = f"Сообщение успешно дошло до {str(num)} человек."
        else:
            result = f"Сообщение успешно дошло до {str(num)} человек и по какой-то причине не дошло до {str(num_error)} человек."
    choose = types.InlineKeyboardMarkup()
    choose.add(types.InlineKeyboardButton(text='фото', callback_data='photo'),
               types.InlineKeyboardButton(text='видео', callback_data='video'))
    choose.add(types.InlineKeyboardButton(text='cообщение(text)', callback_data='text'),
               types.InlineKeyboardButton(text='документ(file)', callback_data='file'))
    choose.add(types.InlineKeyboardButton(text='аудио/голос', callback_data='audio/voice'))
    choose.add(types.InlineKeyboardButton(text='видеосообщение(videonote)', callback_data='videonote'))
    choose.add(types.InlineKeyboardButton(text='⏪ ⏪ ⏪', callback_data='back_to_admin'))
    bot.send_message(chat_id=message.chat.id, text=result, reply_markup=choose)


def file_to_all(message, markup, capt, document):
    num = 0
    num_error = 0
    with sqlite3.connect("data.db") as con:
        cur = con.cursor()

    cur.execute("SELECT user_id FROM users")
    con.commit()

    Lmy = cur.fetchall()
    for i in Lmy:
        try:
            if message.content_type == "document":
                bot.send_document(i[0], document, caption=capt, reply_markup=markup)
                num += 1
        except Exception as ex:
            num_error += 1
            print(ex)
    if num == 0:
        result = f"Такой ссылки нет или вы ошиблись."
    else:
        if num_error == 0:
            result = f"Сообщение успешно дошло до {str(num)} человек."
        else:
            result = f"Сообщение успешно дошло до {str(num)} человек и по какой-то причине не дошло до {str(num_error)} человек."
    choose = types.InlineKeyboardMarkup()
    choose.add(types.InlineKeyboardButton(text='фото', callback_data='photo'),
               types.InlineKeyboardButton(text='видео', callback_data='video'))
    choose.add(types.InlineKeyboardButton(text='cообщение(text)', callback_data='text'),
               types.InlineKeyboardButton(text='документ(file)', callback_data='file'))
    choose.add(types.InlineKeyboardButton(text='аудио/голос', callback_data='audio/voice'))
    choose.add(types.InlineKeyboardButton(text='видеосообщение(videonote)', callback_data='videonote'))
    choose.add(types.InlineKeyboardButton(text='⏪ ⏪ ⏪', callback_data='back_to_admin'))
    bot.send_message(chat_id=message.chat.id, text=result, reply_markup=choose)


def audio_to_all(message, markup, capt, audio):
    num = 0
    num_error = 0
    with sqlite3.connect("data.db") as con:
        cur = con.cursor()

    cur.execute("SELECT user_id FROM users")
    con.commit()

    Lmy = cur.fetchall()
    for i in Lmy:
        try:
            if message.content_type == "audio":
                bot.send_audio(i[0], audio, caption=capt, parse_mode='html', reply_markup=markup)
                num += 1
            elif message.content_type == 'voice':
                bot.send_voice(i[0], audio, caption=capt, parse_mode='html', reply_markup=markup)
                num += 1
        except Exception as ex:
            num_error += 1
            print(ex)
    if num == 0:
        result = f"Такой ссылки нет или вы ошиблись."
    else:
        if num_error == 0:
            result = f"Сообщение успешно дошло до {str(num)} человек."
        else:
            result = f"Сообщение успешно дошло до {str(num)} человек и по какой-то причине не дошло до {str(num_error)} человек."
    choose = types.InlineKeyboardMarkup()
    choose.add(types.InlineKeyboardButton(text='фото', callback_data='photo'),
               types.InlineKeyboardButton(text='видео', callback_data='video'))
    choose.add(types.InlineKeyboardButton(text='cообщение(text)', callback_data='text'),
               types.InlineKeyboardButton(text='документ(file)', callback_data='file'))
    choose.add(types.InlineKeyboardButton(text='аудио/голос', callback_data='audio/voice'))
    choose.add(types.InlineKeyboardButton(text='видеосообщение(videonote)', callback_data='videonote'))
    choose.add(types.InlineKeyboardButton(text='⏪ ⏪ ⏪', callback_data='back_to_admin'))
    bot.send_message(chat_id=message.chat.id, text=result, reply_markup=choose)


def videonote_to_all(message, markup, videonote):
    num = 0
    num_error = 0
    with sqlite3.connect("data.db") as con:
        cur = con.cursor()

    cur.execute("SELECT user_id FROM users")
    con.commit()

    Lmy = cur.fetchall()
    for i in Lmy:
        try:
            if message.content_type == "video_note":
                bot.send_video_note(i[0], videonote, reply_markup=markup)
                num += 1
        except Exception as ex:
            num_error += 1
            print(ex)
    if num == 0:
        result = f"Такой ссылки нет или вы ошиблись."
    else:
        if num_error == 0:
            result = f"Сообщение успешно дошло до {str(num)} человек."
        else:
            result = f"Сообщение успешно дошло до {str(num)} человек и по какой-то причине не дошло до {str(num_error)} человек."
    choose = types.InlineKeyboardMarkup()
    choose.add(types.InlineKeyboardButton(text='фото', callback_data='photo'),
               types.InlineKeyboardButton(text='видео', callback_data='video'))
    choose.add(types.InlineKeyboardButton(text='cообщение(text)', callback_data='text'),
               types.InlineKeyboardButton(text='документ(file)', callback_data='file'))
    choose.add(types.InlineKeyboardButton(text='аудио/голос', callback_data='audio/voice'))
    choose.add(types.InlineKeyboardButton(text='видеосообщение(videonote)', callback_data='videonote'))
    choose.add(types.InlineKeyboardButton(text='⏪ ⏪ ⏪', callback_data='back_to_admin'))
    bot.send_message(chat_id=message.chat.id, text=result, reply_markup=choose)


bot.polling()
