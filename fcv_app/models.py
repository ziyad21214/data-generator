"""
Data models and configuration classes for the Faker CSV Generator.
"""

from dataclasses import dataclass, field
from typing import List, Dict


@dataclass
class ColumnDefinition:
    name: str
    faker_provider: str


@dataclass
class GenerationConfig:
    row_count: int
    file_path: str
    locale: str = "en_US"
    columns: List[ColumnDefinition] = field(default_factory=list)

    def to_dict(self) -> Dict:
        return {
            "row_count": self.row_count,
            "file_path": self.file_path,
            "locale": self.locale,
            "columns": [{"name": c.name, "provider": c.faker_provider} for c in self.columns]
        }