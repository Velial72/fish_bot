import os
from pathlib import Path
from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message, FSInputFile
from aiogram_dialog import DialogManager, StartMode, setup_dialogs
from time import sleep
import requests.exceptions
import logging

from help_functions.dialog import FishSG, start_dialog
from help_functions.settings import SetEnv


logger = logging.getLogger('Logger')


def main():
    setting = SetEnv()
    bot_token = setting.tg_token
    bot = Bot(token=bot_token)
    dp = Dispatcher()

    logger.setLevel(logging.WARNING)
    logger.warning("TG_bot запущен")

    @dp.message(Command(commands=["start"]))
    async def process_start_command(message: Message, dialog_manager: DialogManager):
        await message.answer('Привет!\nРыбки захотел?')
        # await bot.send_photo(chat_id=message.chat.id, photo=photo)
        await dialog_manager.start(state=FishSG.start, mode=StartMode.RESET_STACK)

    @dp.message(Command(commands=['help']))
    async def process_help_command(message: Message):
        await message.answer(
            'Я создан, чтобы барыжить рыбой...'
        )

    while True:
        try:
            dp.include_router(start_dialog)
            setup_dialogs(dp)
            dp.run_polling(bot)
        except requests.exceptions.ReadTimeout:
            pass
        except requests.exceptions.ConnectionError:
            logging.exception("TG_bot упал с ошибкой")
            sleep(120)


if __name__ == '__main__':
    main()