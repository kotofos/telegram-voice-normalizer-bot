import asyncio
import os
import logging

from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.types import ContentType
from aiogram.utils import executor

default_logging_format = (
    '%(asctime)s %(levelname)-5.5s %(name)s %(module)s:%(funcName)s:%(lineno)d %(message)s'
)

logging.basicConfig(
    level=logging.INFO,
    format=default_logging_format,
)

try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    logging.info('Skipping .env loading')
    pass

bot = Bot(token=os.environ.get('TOKEN'))
dp = Dispatcher(bot)

TMP_DIR = '/tmp'


@dp.message_handler(commands=['start'])
async def process_start_command(msg: types.Message):
    await msg.reply("Привет!\nЗапиши мне что нибудь!")
    logging.info(f'Bot started for {msg.from_user.username}')


@dp.message_handler(commands=['help'])
async def process_help_command(msg: types.Message):
    await msg.reply("Запиши мне войс или видео и я нормализую его громкость")


@dp.message_handler(content_types=[ContentType.VOICE, ContentType.VIDEO_NOTE])
async def voice_message_handler(msg: types.Message):
    await bot.send_message(
        msg.from_user.id,
        reply_to_message_id=msg.message_id,
        text='Ожидайте результата...',
    )

    msg_content = getattr(msg, msg.content_type)
    bot_send_content = getattr(bot, f'send_{msg.content_type}')
    container_fmt = {
        'voice': 'ogg',
        'video_note': 'mp4',
    }[msg.content_type]

    logging.info(
        f'Processing {msg.content_type} file size {msg_content.file_size} '
        f'for {msg.from_user.username}'
    )

    in_name = f'{TMP_DIR}/{msg_content.file_id}'
    out_name = f'{TMP_DIR}/{msg_content.file_id}-normalized.{container_fmt}'

    await bot.download_file_by_id(msg_content.file_id, in_name)

    # todo processing pool / queue to limit simultaneous processing
    # todo pipe to avoid files

    proc = await asyncio.create_subprocess_exec(
        'ffmpeg-normalize', '-v', in_name, '-c:a', 'libopus',
        '-o', out_name, '-ofmt', container_fmt,
    )
    await proc.wait()

    normalized = types.InputFile(out_name)
    await bot_send_content(msg.from_user.id, normalized)
    os.unlink(in_name)
    os.unlink(out_name)
    logging.info(f'Handled {msg.content_type} message for {msg.from_user.username}')


if __name__ == '__main__':
    executor.start_polling(dp)
