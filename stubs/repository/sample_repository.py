from __future__ import annotations
import json
from model.sample import Sample


class SampleRepository:
    def __init__(self, path: str) -> None:
        self._path = path

    def find_all(self) -> list[Sample]:
        try:
            with open(self._path, encoding="utf-8") as f:
                rows = json.load(f)
        except FileNotFoundError:
            return []
        return [Sample(**r) for r in rows]
