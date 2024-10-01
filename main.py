import logging
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram import F
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.utils.exceptions import ChatNotFound

logging.basicConfig(level=logging.INFO)

API_TOKEN = 'ВАШ_ТОКЕН'  # Замените на ваш токен
CHANNELS = {'@blackrussia': 'Black Russia'}  # Словарь каналов: тэг канала -> название канала

bot = Bot(token=API_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# Функция для создания inline-клавиатуры с кнопкой на канал и проверкой подписки
def get_subscription_keyboard():
    keyboard = InlineKeyboardMarkup(row_width=1)
    # Добавляем кнопку с ссылкой на канал
    for channel, name in CHANNELS.items():
        keyboard.add(InlineKeyboardButton(text=name, url=f"https://t.me/{channel.lstrip('@')}"))
    # Кнопка для проверки подписки
    keyboard.add(InlineKeyboardButton(text="✅ Проверить", callback_data="check_subscription"))
    return keyboard

# Функция для проверки подписки пользователя на каналы
async def check_subscriptions(user_id):
    not_subscribed_channels = []
    for channel, name in CHANNELS.items():
        try:
            chat_member = await bot.get_chat_member(chat_id=channel, user_id=user_id)
            if chat_member.status not in ['member', 'administrator', 'creator']:
                not_subscribed_channels.append(name)
        except ChatNotFound:
            logging.error(f"Канал {channel} не найден. Проверьте, правильный ли ID канала.")
            not_subscribed_channels.append(name)
        except Exception as e:
            logging.error(f"Ошибка при проверке подписки на {channel}: {e}")
            not_subscribed_channels.append(name)
    return not_subscribed_channels

# Обработчик команды /start
@dp.message(F.text == "/start")
async def send_welcome(message: types.Message):
    user_id = message.from_user.id
    not_subscribed_channels = await check_subscriptions(user_id)
    if not not_subscribed_channels:
        await message.answer("Добро пожаловать! Вы подписаны на все необходимые каналы.")
    else:
        channels_list = '\n'.join(not_subscribed_channels)
        await message.answer(
            f"⛔️ Вы не подписаны на следующие каналы:\n{channels_list}",
            reply_markup=get_subscription_keyboard()
        )

# Обработчик нажатий на inline-кнопки
@dp.callback_query(lambda c: c.data == "check_subscription")
async def process_callback_check_subscription(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    not_subscribed_channels = await check_subscriptions(user_id)
    if not not_subscribed_channels:
        await callback_query.message.edit_text("✅ Спасибо за подписку!")
    else:
        channels_list = '\n'.join(not_subscribed_channels)
        await callback_query.answer(f"Вы не подписаны на следующие каналы:\n{channels_list}", show_alert=True)

# Основная функция для запуска бота
async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == '__main__':
    import asyncio
    print("Бот запущен!")
    asyncio.run(main())
