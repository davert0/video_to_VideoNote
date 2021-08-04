import logging
import tempfile
import os


from aiogram import Bot, Dispatcher, executor, types
import crop_video
from config import TOKEN

# Инициализация
bot = Bot(TOKEN)
logging.basicConfig(level=logging.INFO)
dp = Dispatcher(bot)

# Переменная, которая отражает готовность принять видео
READY_FLAG = False

# Кнопки и клавиатуры
video_input_button = types.InlineKeyboardButton('Принять видео', callback_data='video_input')
send_videonote_button = types.InlineKeyboardButton('Сделать VideoNote', callback_data='make_videonote')

inline_kb_for_request = types.InlineKeyboardMarkup().add(video_input_button)
inline_kb_for_making_videonote = types.InlineKeyboardMarkup().add(send_videonote_button)


# Обработчики колбэков
@dp.callback_query_handler(lambda c: c.data == 'video_input')
async def process_callback_video_input_button(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(callback_query.from_user.id, 'Готов принять видеофайл!')
    global READY_FLAG
    READY_FLAG = True


@dp.callback_query_handler(lambda c: c.data == 'make_videonote')
async def process_callback_video_input_button(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)

    response = await bot.send_message(callback_query.from_user.id, 'Идёт обработка видео!')

    with tempfile.NamedTemporaryFile(suffix='.mp4', dir=os.getcwd()) as out_video:
        crop_video.video_crop('video_note.mp4', out_video.name)

        video_note = await bot.send_video_note(
            callback_query.from_user.id,
            video_note=out_video.read()
        )
        if not video_note:
            await response.edit_text("Не удалось конвертировать файл!")
        else:
            await response.delete()
        global READY_FLAG
        READY_FLAG = False


# Обработчики сообщений
@dp.message_handler(commands=['start', 'help'])
async def send_welcome(message: types.Message):
    await message.reply("Данный бот позволяет преобразовать видеофайл в VideoNote!", reply_markup=inline_kb_for_request)


@dp.message_handler(content_types=["video"])
async def convert(message: types.Message):
    if READY_FLAG:
        response = await message.answer("Загружаю видео!")

        video = await bot.download_file_by_id(message.video.file_id, 'video_note.mp4')

        if not video:
            await response.edit_text('Не удалось загрузить видео!')
        else:
            await response.edit_text('Видео загружено!', reply_markup=inline_kb_for_making_videonote)
    else:
        await message.answer("Бот не готов загрузить видео!")


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
