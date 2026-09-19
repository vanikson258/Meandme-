"""
Бот «Я с собой» — открывает Mini App с протоколом саморегуляции.

Запуск:
    export BOT_TOKEN="токен от @BotFather"
    export WEBAPP_URL="https://имя.github.io/ya-s-soboy/"
    python bot.py
"""

import asyncio
import logging
import os

from aiogram import Bot, Dispatcher, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import Command, CommandStart
from aiogram.types import (
    BotCommand,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    MenuButtonWebApp,
    Message,
    WebAppInfo,
)

BOT_TOKEN = os.environ.get("BOT_TOKEN")
WEBAPP_URL = os.environ.get("WEBAPP_URL")

if not BOT_TOKEN or not WEBAPP_URL:
    raise SystemExit(
        "Нужны переменные окружения BOT_TOKEN и WEBAPP_URL.\n"
        '  export BOT_TOKEN="123456:AA..."\n'
        '  export WEBAPP_URL="https://имя.github.io/ya-s-soboy/"'
    )

if not WEBAPP_URL.startswith("https://"):
    raise SystemExit("WEBAPP_URL должен начинаться с https:// — Telegram не откроет http.")

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()


def open_kb(text: str = "Открыть приложение") -> InlineKeyboardMarkup:
    """Кнопка, открывающая Mini App. Работает только в личных чатах."""
    return InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text=text, web_app=WebAppInfo(url=WEBAPP_URL))]]
    )


WELCOME = (
    "<b>Я с собой</b>\n\n"
    "Протокол саморегуляции для выхода из компульсивных защитных реакций "
    "при ране покинутости и отвержения.\n\n"
    "Внутри: дневник триггерных ситуаций, пошаговый разбор по трём блокам, "
    "таблица чувств, дыхание, заземление и работа с импульсом.\n\n"
    "Записи хранятся в твоём аккаунте Telegram и подтянутся на любом устройстве, "
    "где ты в него вошёл."
)

HELP = (
    "<b>Как этим пользоваться</b>\n\n"
    "• <b>Когда накрыло</b> — открой приложение и нажми «Пройти протокол». "
    "Он проведёт от автоматической реакции к новому действию.\n"
    "• <b>Когда нет сил на весь протокол</b> — /pause или вкладка «Практики»: "
    "дыхание, заземление, серфинг импульса.\n"
    "• <b>Потом</b> — вкладка «Прогресс» покажет, что запускает чаще всего "
    "и как часто пауза срабатывает.\n\n"
    "Приложение — поддержка, а не замена терапии."
)

PAUSE = (
    "<b>Стоп. Это старая рана. Сейчас я в безопасности. Я взрослая. Я с собой.</b>\n\n"
    "1. Поставь обе стопы на пол. Найди пол пятками и пальцами. "
    "Почувствуй, как таз опирается на стул.\n"
    "2. Вдох на 4 — выдох на 8. Десять раз. Выдох должен быть длиннее вдоха.\n"
    "3. Ничего не решай и не пиши ближайшие двадцать минут. "
    "Импульс дойдёт до пика примерно за десять минут и начнёт спадать сам.\n\n"
    "Когда станет чуть тише — открой приложение и разбери ситуацию."
)


@dp.message(CommandStart())
async def cmd_start(message: Message) -> None:
    await message.answer(WELCOME, reply_markup=open_kb("Открыть приложение"))


@dp.message(Command("help"))
async def cmd_help(message: Message) -> None:
    await message.answer(HELP, reply_markup=open_kb())


@dp.message(Command("pause"))
async def cmd_pause(message: Message) -> None:
    await message.answer(PAUSE, reply_markup=open_kb("Разобрать ситуацию"))


@dp.message(F.web_app_data)
async def on_webapp_data(message: Message) -> None:
    """Сюда приходят данные, если приложение вызовет Telegram.WebApp.sendData().
    Сейчас не используется — всё хранится на стороне приложения."""
    logging.info("web_app_data: %s", message.web_app_data.data)


@dp.message()
async def fallback(message: Message) -> None:
    await message.answer(
        "Всё, что нужно, — внутри приложения. Команды: /pause и /help.",
        reply_markup=open_kb(),
    )


async def main() -> None:
    await bot.set_my_commands(
        [
            BotCommand(command="start", description="Открыть приложение"),
            BotCommand(command="pause", description="Быстрая пауза, когда накрыло"),
            BotCommand(command="help", description="Как этим пользоваться"),
        ]
    )
    # Постоянная кнопка рядом с полем ввода во всех личных чатах с ботом
    await bot.set_chat_menu_button(
        menu_button=MenuButtonWebApp(text="Я с собой", web_app=WebAppInfo(url=WEBAPP_URL))
    )
    logging.info("Бот запущен. Mini App: %s", WEBAPP_URL)
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.info("Остановлен")
