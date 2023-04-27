from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

TOKEN = "ss"
bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
keyboard.add(KeyboardButton('Подписка'), KeyboardButton('Пополнение кошелька'))

@dp.message_handler(commands=['start'])
async def send_welcome(msg: types.Message):
    await bot.send_message(chat_id=msg.chat.id, text='Здравствуйте, чем я могу вам помочь?.', reply_markup=keyboard)

@dp.message_handler(lambda message: message.text == 'Подписка')
async def handle_button1_click(msg: types.Message):
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(KeyboardButton('Статус подписки'), KeyboardButton('Купить подписку'), KeyboardButton('Продлить подписку'), KeyboardButton('Отмена'))
    await bot.delete_message(chat_id=msg.chat.id, message_id=msg.message_id)
    await bot.send_message(chat_id=msg.chat.id, text='Выберите действие:', reply_markup=keyboard)

@dp.message_handler(lambda message: message.text == 'Отмена')
async def handle_button1_click(msg: types.Message):
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(KeyboardButton('Подписка'), KeyboardButton('Пополнение кошелька'))
    await bot.delete_message(chat_id=msg.chat.id, message_id=msg.message_id)
    await bot.send_message(chat_id=msg.chat.id, text='Действие отменено. Выберите категорию:', reply_markup=keyboard)

@dp.message_handler(content_types=['text'])
async def get_text_messages(msg: types.Message):
   if msg.text.lower() == 'привет':
       await bot.send_message(chat_id=msg.chat.id, text='Привет!')
   else:
       await bot.send_message(chat_id=msg.chat.id, text='Воспользуйтесь командой /start')

@dp.message_handler(lambda message: message.text == 'Пополнение кошелька')
async def handle_button1_click(msg: types.Message):
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(KeyboardButton('Пополнить баланс кошелька'), KeyboardButton('Выбрать криптовалюту'), KeyboardButton('Отмена'))
    await bot.delete_message(chat_id=msg.chat.id, message_id=msg.message_id)
    await bot.send_message(chat_id=msg.chat.id, text='Выберите действие:', reply_markup=keyboard)


if __name__ == '__main__':
   executor.start_polling(dp)
