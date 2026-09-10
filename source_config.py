from dataclasses import dataclass


@dataclass
class SourceConfig:
    project_id: str
    source_type: str
    channel: str
