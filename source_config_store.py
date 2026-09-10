import json
from pathlib import Path

from source_config import SourceConfig


class SourceConfigStore:
    def __init__(self, path: str = "source_configs.json") -> None:
        self._path = Path(path)
        self._configs: dict[int, SourceConfig] = {}

        self._load()

    def get(self, chat_id: int) -> SourceConfig | None:
        return self._configs.get(chat_id)

    def set(self, chat_id: int, config: SourceConfig) -> None:
        self._configs[chat_id] = config
        self._save()

    def _load(self) -> None:
        if not self._path.exists():
            return

        with self._path.open("r", encoding="utf-8") as file:
            data = json.load(file)

        self._configs = {
            int(chat_id): SourceConfig(
                project_id=config["project_id"],
                source_type=config["source_type"],
                channel=config["channel"],
            )
            for chat_id, config in data.items()
        }

    def _save(self) -> None:
        data = {
            str(chat_id): {
                "project_id": config.project_id,
                "source_type": config.source_type,
                "channel": config.channel,
            }
            for chat_id, config in self._configs.items()
        }

        with self._path.open("w", encoding="utf-8") as file:
            json.dump(
                data,
                file,
                ensure_ascii=False,
                indent=2,
            )
