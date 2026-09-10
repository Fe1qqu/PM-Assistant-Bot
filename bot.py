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

SET_INFO_PROJECT_ID, SET_INFO_SOURCE_TYPE, SET_INFO_CHANNEL = range(3)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat = update.effective_chat
    message = update.message

    if chat is None or message is None:
        return

    chat_id = chat.id
    config = config_store.get(chat_id)

    if config is None:
        config = SourceConfig(
            project_id=str(chat_id),
            source_type="",
            channel="",
        )

        config_store.set(chat_id, config)

        await message.reply_text(
            "Бот подключён к чату.\n\n"
            f"Project ID: {config.project_id}\n"
            "Source type: не задан\n"
            "Channel: не задан\n\n"
            "Для настройки используйте /set_info."
        )

        return

    await message.reply_text(
        "Бот уже подключён к этому чату.\n\n"
        f"Project ID: {config.project_id}\n"
        f"Source type: {config.source_type or 'не задан'}\n"
        f"Channel: {config.channel or 'не задан'}"
    )


async def start_set_info(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    chat = update.effective_chat
    message = update.message

    if chat is None or message is None:
        return ConversationHandler.END

    config = config_store.get(chat.id)

    if config is None:
        await message.reply_text(
            "Сначала подключите бота с помощью /start."
        )
        return ConversationHandler.END

    context.user_data.clear()

    await message.reply_text(
        "Введите project_id.\n"
        f"Текущее значение: "
        f"{config.project_id or 'не задано'}\n\n"
        "Чтобы оставить текущее значение, используйте /skip."
    )

    return SET_INFO_PROJECT_ID


async def handle_set_info_project_id(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    chat = update.effective_chat
    message = update.message

    if chat is None or message is None or message.text is None:
        return ConversationHandler.END

    config = config_store.get(chat.id)

    if config is None:
        return ConversationHandler.END

    context.user_data["project_id"] = message.text

    await message.reply_text(
        "Введите source_type.\n"
        f"Текущее значение: "
        f"{config.source_type or 'не задано'}\n\n"
        "Чтобы оставить текущее значение, используйте /skip."
    )

    return SET_INFO_SOURCE_TYPE


async def skip_set_info_project_id(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    chat = update.effective_chat
    message = update.message

    if chat is None or message is None:
        return ConversationHandler.END

    config = config_store.get(chat.id)

    if config is None:
        return ConversationHandler.END

    context.user_data["project_id"] = config.project_id

    await message.reply_text(
        "Project ID оставлен без изменений.\n\n"
        "Введите source_type.\n"
        f"Текущее значение: "
        f"{config.source_type or 'не задано'}\n\n"
        "Чтобы оставить текущее значение, используйте /skip."
    )

    return SET_INFO_SOURCE_TYPE



async def handle_set_info_source_type(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    chat = update.effective_chat
    message = update.message

    if chat is None or message is None or message.text is None:
        return ConversationHandler.END

    config = config_store.get(chat.id)

    if config is None:
        return ConversationHandler.END

    context.user_data["source_type"] = message.text

    await message.reply_text(
        "Введите channel.\n"
        f"Текущее значение: "
        f"{config.channel or 'не задано'}\n\n"
        "Чтобы оставить текущее значение, используйте /skip."
    )

    return SET_INFO_CHANNEL


async def skip_set_info_source_type(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    chat = update.effective_chat
    message = update.message

    if chat is None or message is None:
        return ConversationHandler.END

    config = config_store.get(chat.id)

    if config is None:
        return ConversationHandler.END

    context.user_data["source_type"] = config.source_type

    await message.reply_text(
        "Source type оставлен без изменений.\n\n"
        "Введите channel.\n"
        f"Текущее значение: "
        f"{config.channel or 'не задано'}\n\n"
        "Чтобы оставить текущее значение, используйте /skip."
    )

    return SET_INFO_CHANNEL


async def handle_set_info_channel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    chat = update.effective_chat
    message = update.message

    if chat is None or message is None or message.text is None:
        return ConversationHandler.END

    config = config_store.get(chat.id)

    if config is None:
        return ConversationHandler.END

    config.project_id = context.user_data["project_id"]
    config.source_type = context.user_data["source_type"]
    config.channel = message.text

    config_store.set(chat.id, config)

    context.user_data.clear()

    await message.reply_text(
        "Настройки сохранены.\n\n"
        f"Project ID: {config.project_id}\n"
        f"Source type: {config.source_type or 'не задан'}\n"
        f"Channel: {config.channel or 'не задан'}"
    )

    return ConversationHandler.END


async def skip_set_info_channel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    chat = update.effective_chat
    message = update.message

    if chat is None or message is None:
        return ConversationHandler.END

    config = config_store.get(chat.id)

    if config is None:
        return ConversationHandler.END

    config.project_id = context.user_data["project_id"]
    config.source_type = context.user_data["source_type"]

    config_store.set(chat.id, config)

    context.user_data.clear()

    await message.reply_text(
        "Channel оставлен без изменений.\n\n"
        "Настройки сохранены.\n\n"
        f"Project ID: {config.project_id}\n"
        f"Source type: {config.source_type or 'не задан'}\n"
        f"Channel: {config.channel or 'не задан'}"
    )

    return ConversationHandler.END


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = update.message

    if message is None or message.text is None:
        return

    chat_id = message.chat.id
    config = config_store.get(chat_id)

    if config is None:
        return

    data = map_message(message, config)

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

    application.add_handler(
        CommandHandler("start", start)
    )

    set_info_handler = ConversationHandler(
        entry_points=[
            CommandHandler("set_info", start_set_info)
        ],
        states={
            SET_INFO_PROJECT_ID: [
                CommandHandler("skip", skip_set_info_project_id),
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND,
                    handle_set_info_project_id,
                ),
            ],
            SET_INFO_SOURCE_TYPE: [
                CommandHandler("skip", skip_set_info_source_type),
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND,
                    handle_set_info_source_type,
                ),
            ],
            SET_INFO_CHANNEL: [
                CommandHandler("skip", skip_set_info_channel),
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND,
                    handle_set_info_channel,
                ),
            ],
        },
        fallbacks=[],
        per_chat=True,
        per_user=True,
    )

    application.add_handler(set_info_handler)

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
