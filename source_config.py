from dataclasses import dataclass


@dataclass
class SourceConfig:
    project_id: str
    source_id: str
    source_type: str


_configs: dict[int, SourceConfig] = {}


def set_config(chat_id: int, config: SourceConfig) -> None:
    _configs[chat_id] = config


def get_config(chat_id: int) -> SourceConfig | None:
    return _configs.get(chat_id)
