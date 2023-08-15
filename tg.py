import asyncio
import telebot
from telebot import types

import requests
from telebot.async_telebot import AsyncTeleBot

# Ваш токен, полученный от @BotFather
BOT_TOKEN = '6371845124:AAEScCRDBxxMIcsz2C0fbY_hBr1vlcIDeM8'

bot = AsyncTeleBot(BOT_TOKEN)
user_state = {}
photo_to_send = []
@bot.message_handler(commands=['send_photos'])
async def send_photos(message):
    user_id = message.from_user.id
    if not photo_to_send:
        await bot.reply_to(message, "Список фотографий пуст. Сначала добавьте фотографии с помощью команды /photo.")
        return
    from telebot.types import InputMediaPhoto
    media_list = []
    for photo in photo_to_send:
        media_list.append(types.InputMediaPhoto(photo.file_id))

    await bot.send_media_group(message.chat.id, media=media_list)

    await bot.send_message(message.chat.id, "Все фотографии отправлены.")
@bot.message_handler(commands=['photo'])
async def request_photos(message):
    user_id = message.from_user.id
    user_state[user_id] = "waiting_for_photos"
    await bot.reply_to(message, "Отправьте мне фотографии для сохранения:")

@bot.message_handler(content_types=['photo'], func=lambda message: user_state.get(message.from_user.id) == "waiting_for_photos")
async def save_photos(message):
    user_id = message.from_user.id
    user_state[user_id] = None
    
    photo_to_send.append(message.photo[-1])

    await bot.reply_to(message, f"Сохранено 1 фотография. Всего в списке: {len(photo_to_send)}")

# Определение канала для отправки
def get_admin_channels():
    admin_channels = []
    response = requests.get(f'https://api.telegram.org/bot{BOT_TOKEN}/getMe')
    bot_info = response.json()
    bot_id = bot_info['result']['id']

    response = requests.get(f'https://api.telegram.org/bot{BOT_TOKEN}/getChatAdministrators?chat_id=@ffffffffffffffffar')
    chat_administrators = response.json()

    for admin in chat_administrators['result']:
        if admin['user']['id'] == bot_id:
            response = requests.get(f'https://api.telegram.org/bot6371845124:AAEScCRDBxxMIcsz2C0fbY_hBr1vlcIDeM8/getChat?chat_id=@ffffffffffffffffar')
            resp = response.json()
            admin_channels.append(resp['result']['id'])

    return admin_channels
@bot.message_handler(commands=['text'])
async def record_message(message):
    user_id = message.from_user.id
    user_state[user_id] = "waiting_for_text"  # Устанавливаем состояние ожидания текста от пользователя
    await bot.reply_to(message, "Введите сообщение для записи:")
@bot.message_handler(commands=['btext'])
async def record_message(message):
    user_id = message.from_user.id
    user_state[user_id] = "waiting_for_b_text"  # Устанавливаем состояние ожидания текста от пользователя
    await bot.reply_to(message, "Введите сообщение для записи:")

@bot.message_handler(func=lambda message: user_state.get(message.from_user.id) == "waiting_for_b_text")
async def save_message(message):
    user_id = message.from_user.id
    user_state[user_id] = None  # Сбрасываем состояние
    global to_b_sand
    to_b_sand=message.text

    await bot.reply_to(message, "Сообщение записано.")
@bot.message_handler(func=lambda message: user_state.get(message.from_user.id) == "waiting_for_text")
async def save_message(message):
    print(message)
    user_id = message.from_user.id
    user_state[user_id] = None  # Сбрасываем состояние
    global to_sand
    to_sand=message.text
    

    await bot.reply_to(message, "Сообщение записано.")

@bot.message_handler(commands=['help', 'start'])
async def send_welcome(message):
    await bot.reply_to(message, """\
Hi there, I am EchoBot.
I am here to echo your kind words back to you. Just say anything nice and I'll say the exact same thing to you!\
""")


@bot.message_handler(commands=['send', 'sand'])
async def echo_message(message):
    print(to_sand)
    user = await bot.get_me()
    admin_channels = get_admin_channels()

    if not admin_channels:
        await bot.reply_to(message, "К сожалению, у меня нет доступа к каким-либо каналам как администратору.")
        return

    user_id = message.from_user.id
    markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    for channel in admin_channels:
        markup.add(types.KeyboardButton(channel))

    user_state[user_id] = "choose_channel"
    await bot.send_message(message.chat.id, "Выберите канал для публикации:", reply_markup=markup)

@bot.message_handler(func=lambda message: user_state.get(message.from_user.id) == "choose_channel")
async def process_selected_channel(message):
    selected_channel = message.text
    admin_channels = get_admin_channels()

    if selected_channel == selected_channel:
        if photo_to_send:
            # Get the last photo from the list
            last_photo = photo_to_send[-1]
            
            # Create an InlineKeyboardMarkup
            keyboard = types.InlineKeyboardMarkup()
            callback_button = types.InlineKeyboardButton(text="Скачать", callback_data=to_b_sand)
            keyboard.add(callback_button)
            
            # Send the last photo with caption and reply markup
            await bot.send_photo(
                chat_id=selected_channel,
                photo=last_photo.file_id,
                caption=to_sand,
                reply_markup=keyboard,
                parse_mode="MarkdownV2"
            )
            await bot.send_message(message.chat.id, "Сообщение отправлено в выбранный канал.")
        else:
            await bot.send_message(message.chat.id, "Список фотографий пуст.")
    else:
        await bot.send_message(message.chat.id, "Выбранный канал не найден.")


@bot.callback_query_handler(func=lambda call: call.data)
async def download_callback(call):
    chat= get_admin_channels()
    print(call.message.chat.id)
    user_id = call.from_user.id
    print(call.id)
    response = await bot.get_chat_member(call.message.chat.id, user_id)
    if response.status in ("member", "administrator", "creator"):
          
        # Открываем ссылку канала
        channel_link = call.data
        await bot.answer_callback_query(call.id, f"{call.data}",True)
        return

    await bot.answer_callback_query(call.id, show_alert=True, text="Вы не подписаны на канал.")

async def main():
    await bot.polling()

if __name__ == "__main__":
    asyncio.run(main())
