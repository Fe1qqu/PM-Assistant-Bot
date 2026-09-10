from telegram import Message

from source_config import SourceConfig


def map_message(message: Message, source_config: SourceConfig) -> dict:
    return {
        "project_id": source_config.project_id,
        "source_id": source_config.source_id,
        "source_type": source_config.source_type,
        "message_id": f"tg-{message.message_id}",
        "speaker": message.from_user.full_name,
        "text": message.text,
        "occurred_at": message.date.isoformat(),
        "channel": "Telegram · клиент",
    }
