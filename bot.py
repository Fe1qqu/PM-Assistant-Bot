import json
import os

from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, ConversationHandler, MessageHandler, filters

from message_mapper import map_message
from source_config import SourceConfig
from source_config_store import SourceConfigStore


load_dotenv()

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

config_store = SourceConfigStore()

PROJECT_ID_STATE, SOURCE_TYPE_STATE, SOURCE_ID_STATE = range(3)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Бот работает.\n\n"
        "Для настройки этого чата используйте /connect."
    )


async def connect_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text(
        "Введите project_id:"
    )

    return PROJECT_ID_STATE


async def connect_project_id(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["project_id"] = update.message.text

    await update.message.reply_text(
        "Введите source_type:\n"
        "client_chat\n"
        "team_chat"
    )

    return SOURCE_TYPE_STATE


async def connect_source_type(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["source_type"] = update.message.text

    await update.message.reply_text(
        "Введите source_id:"
    )

    return SOURCE_ID_STATE


async def connect_source_id(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["source_id"] = update.message.text

    chat_id = update.effective_chat.id

    config = SourceConfig(
        project_id=context.user_data["project_id"],
        source_id=context.user_data["source_id"],
        source_type=context.user_data["source_type"],
    )

    config_store.set(chat_id, config)

    context.user_data.clear()

    await update.message.reply_text(
        "Источник настроен."
    )

    return ConversationHandler.END


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = update.message

    if message is None or message.text is None:
        return

    chat_id = message.chat.id
    source_config = config_store.get(chat_id)

    if source_config is None:
        await message.reply_text(
            "Этот чат ещё не настроен. "
            "Используйте /connect."
        )
        return

    data = map_message(message, source_config)

    print(
        json.dumps(
            data,
            ensure_ascii=False,
            indent=2,
        )
    )


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    print(f"Exception: {context.error}")


def main() -> None:
    if not TOKEN:
        raise RuntimeError("TELEGRAM_BOT_TOKEN is not set")

    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    
    connect_handler = ConversationHandler(
        entry_points=[
            CommandHandler("connect", connect_start)
        ],
        states={
            PROJECT_ID_STATE: [
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND,
                    connect_project_id,
                )
            ],
            SOURCE_TYPE_STATE: [
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND,
                    connect_source_type,
                )
            ],
            SOURCE_ID_STATE: [
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND,
                    connect_source_id,
                )
            ],
        },
        fallbacks=[],
    )

    application.add_handler(connect_handler)

    application.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            handle_message,
        )
    )
    
    application.add_error_handler(error_handler)

    print("Bot started")

    application.run_polling()


if __name__ == "__main__":
    main()
