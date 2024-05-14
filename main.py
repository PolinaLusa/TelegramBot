import telebot
from telebot import types
from page_parser import *

bot = telebot.TeleBot('this_your_token')

user_states = {}
stream_mapping = {
    'stream_bel': 'Белорусская филология',
    'stream_rus': 'Русская филология',
    'stream_class': 'Классическая филология',
    'stream_slav': 'Славянская филология',
    'stream_rom': 'Романо-германская филология',
    'stream_east': 'Восточная филология'
}
@bot.callback_query_handler(func=lambda call: call.data == 'show_schedule')
def show_schedule(call):
    user_id = call.from_user.id
    try:
        url = "https://philology.bsu.by/ru/studjentu/raspisanie/1379-raspisanie-zanyatij-studentov-dnevnogo-otdeleniya"
        data = parse_and_extract(url)
        if data:
            for idx, filename in enumerate(data):
                bot.send_document(call.message.chat.id, open(filename, 'rb'))
        else:
            bot.send_message(call.message.chat.id, "Не удалось получить данные из PDF файлов.")
    except Exception as e:
        print(f"Ошибка при отправке расписания: {e}")
        bot.send_message(call.message.chat.id, "Произошла ошибка при отправке расписания.")

def schedule_options(chat_id, user_id):
    schedule_markup = types.InlineKeyboardMarkup(row_width=1)
    schedule_markup.add(
        types.InlineKeyboardButton("Сегодня", callback_data='today'),
        types.InlineKeyboardButton("Завтра", callback_data='tomorrow'),
        types.InlineKeyboardButton("Определённый день", callback_data='specific_day'),
        types.InlineKeyboardButton("Изменить курс", callback_data='change_course'),
        types.InlineKeyboardButton("Изменить поток", callback_data='change_stream'),
        types.InlineKeyboardButton("Изменить группу", callback_data='change_group'),
        types.InlineKeyboardButton("Включить ежедневные уведомления", callback_data='notifications'),
        types.InlineKeyboardButton("Показать расписание", callback_data='show_schedule')
    )
    user_info = bot.get_chat_member(chat_id, user_id)
    user_first_name = user_info.user.first_name
    user_last_name = user_info.user.last_name
    message_text = f'<b>{user_first_name} {user_last_name}</b>, выберите нужный вам день для получения расписания:'
    bot.send_message(chat_id, message_text, parse_mode='html', reply_markup=schedule_markup)
@bot.message_handler(commands=['start'])
def start(message):
    markup = types.InlineKeyboardMarkup(row_width=2)
    item1 = types.InlineKeyboardButton("Выберите курс", callback_data='course')
    markup.add(item1)
    mess = f'Привет, <b>{message.from_user.first_name} {message.from_user.last_name}</b>! Выберите курс:'
    if message.from_user.id in user_states and 'last_message_id' in user_states[message.from_user.id]:
        bot.edit_message_reply_markup(chat_id=message.chat.id,
                                      message_id=user_states[message.from_user.id]['last_message_id'],
                                      reply_markup=None)

    sent_message = bot.send_message(message.chat.id, mess, parse_mode='html', reply_markup=markup)
    user_states[message.from_user.id] = {'last_message_id': sent_message.message_id}


@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    chat_id = call.message.chat.id
    user_id = call.from_user.id

    if call.data == 'course':
        course_markup = types.InlineKeyboardMarkup(row_width=2)
        course_markup.add(
            types.InlineKeyboardButton("1к.", callback_data='course_1'),
            types.InlineKeyboardButton("2к.", callback_data='course_2'),
            types.InlineKeyboardButton("3к.", callback_data='course_3'),
            types.InlineKeyboardButton("4к.", callback_data='course_4')
        )
        sent_message = bot.send_message(chat_id, "Выберите свой курс:", reply_markup=course_markup)
        user_states[user_id] = {'last_message_id': sent_message.message_id}

    elif call.data.startswith('course_'):
        user_states[user_id]['course'] = call.data
        stream_markup = types.InlineKeyboardMarkup(row_width=1)
        stream_markup.add(
            types.InlineKeyboardButton("Белорусская филология", callback_data='stream_bel'),
            types.InlineKeyboardButton("Русская филология", callback_data='stream_rus'),
            types.InlineKeyboardButton("Классическая филология", callback_data='stream_class'),
            types.InlineKeyboardButton("Славянская филология", callback_data='stream_slav'),
            types.InlineKeyboardButton("Романо-германская филология", callback_data='stream_rom'),
            types.InlineKeyboardButton("Восточная филология", callback_data='stream_east')
        )
        if user_id in user_states and 'last_message_id' in user_states[user_id]:
            bot.edit_message_reply_markup(chat_id=chat_id,
                                          message_id=user_states[user_id]['last_message_id'],
                                          reply_markup=None)

        sent_message = bot.send_message(chat_id, f'Вы выбрали {call.data[-1]} курс. Теперь выберите свой поток.',
                                        reply_markup=stream_markup)
        user_states[user_id]['last_message_id'] = sent_message.message_id

    elif call.data.startswith('stream_'):
        user_states[user_id]['stream'] = call.data
        if call.data in ['stream_rus']:
            group_markup = types.InlineKeyboardMarkup(row_width=2)
            group_markup.add(
                types.InlineKeyboardButton("5гр.", callback_data='group_5'),
                types.InlineKeyboardButton("6гр.", callback_data='group_6')
            )
        elif call.data == 'stream_rom':
            group_markup = types.InlineKeyboardMarkup(row_width=2)
            group_markup.add(
                types.InlineKeyboardButton("8гр.", callback_data='group_8'),
                types.InlineKeyboardButton("9гр.", callback_data='group_9'),
                types.InlineKeyboardButton("10гр.", callback_data='group_10'),
                types.InlineKeyboardButton("11гр.", callback_data='group_11'),
                types.InlineKeyboardButton("12гр.", callback_data='group_12')
            )
        elif call.data == 'stream_slav':
            group_markup = types.InlineKeyboardMarkup(row_width=2)
            group_markup.add(
                types.InlineKeyboardButton("13гр.", callback_data='group_13'),
                types.InlineKeyboardButton("14гр.", callback_data='group_14')
            )
        else:
            final_message = f'<b>{call.from_user.first_name} {call.from_user.last_name}</b>, вы выбрали:\n'
            final_message += f'Курс: {user_states[user_id]["course"][-1]}\n'
            final_message += f'Поток: {stream_mapping.get(user_states[user_id]["stream"], "Unknown")}\n'
            bot.edit_message_text(final_message, chat_id, message_id=user_states[user_id]['last_message_id'],
                                  parse_mode='html')
            schedule_options(chat_id, user_id)
            return

        if user_id in user_states and 'last_message_id' in user_states[user_id]:
            bot.edit_message_reply_markup(chat_id=chat_id,
                                          message_id=user_states[user_id]['last_message_id'],
                                          reply_markup=None)

        sent_message = bot.send_message(chat_id,
                                        f'Вы выбрали поток: {stream_mapping.get(call.data, "Unknown")}. Теперь выберите свою группу.',
                                        reply_markup=group_markup)
        user_states[user_id]['last_message_id'] = sent_message.message_id

    elif call.data.startswith('group_'):
        user_states[user_id]['group'] = call.data
        final_message = f'<b>{call.from_user.first_name} {call.from_user.last_name}</b>, вы выбрали:\n'
        final_message += f'Курс: {user_states[user_id]["course"][-1]}\n'
        final_message += f'Поток: {stream_mapping.get(user_states[user_id]["stream"], "Unknown")}\n'
        final_message += f'Группу: {user_states[user_id]["group"].split("_")[-1]}'
        bot.edit_message_text(final_message, chat_id, message_id=user_states[user_id]['last_message_id'],
                              parse_mode='html')
        user_states[user_id]['group_selected'] = True
        schedule_options(chat_id, user_id)

bot.polling(none_stop=True)
