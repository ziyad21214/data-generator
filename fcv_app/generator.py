import csv
import logging
from typing import List, Any
from faker import Faker
from .models import GenerationConfig

logger = logging.getLogger(__name__)


class CSVGeneratorEngine:


    def __init__(self, config: GenerationConfig):
        self.config = config
        self.faker = Faker(config.locale)

    def generate(self, progress_callback=None) -> int:
        columns = self.config.columns
        if not columns:
            raise ValueError("No columns specified for generation.")

        header = [col.name for col in columns]
        total_rows = self.config.row_count
        written_rows = 0

        try:
            with open(self.config.file_path, mode="w", newline="", encoding="utf-8") as csv_file:
                writer = csv.writer(csv_file)
                writer.writerow(header)

                for i in range(1, total_rows + 1):
                    row_data = []
                    for col in columns:
                        value = self._fetch_faker_value(col.faker_provider)
                        row_data.append(value)
                    
                    writer.writerow(row_data)
                    written_rows += 1

                    if progress_callback and (i % 100 == 0 or i == total_rows):
                        progress_callback(i, total_rows)

            logger.info("Successfully generated %d rows into %s", written_rows, self.config.file_path)
            return written_rows

        except Exception as e:
            logger.error("Error during CSV generation: %s", str(e))
            raise

    def _fetch_faker_value(self, provider_path: str) -> Any:
        try:
            parts = provider_path.split(".")
            attr = self.faker
            for part in parts:
                attr = getattr(attr, part)
            
            if callable(attr):
                return attr()
            return attr
        except AttributeError:
            logger.warning("Faker provider '%s' not found. Falling back to dummy text.", provider_path)
            return f"INVALID_PROVIDER_{provider_path}"