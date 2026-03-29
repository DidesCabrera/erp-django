#Que necesita el picker para funcionar"
from dataclasses import dataclass
from typing import Optional, List


@dataclass
class DpmFoodPickerContextPayload:
    meal: dict
    dailyplan: dict
    mode: str
    editing: dict | None

    def as_dict(self):
        return {
            "meal": self.meal,
            "dailyplan": self.dailyplan,
            "mode": self.mode,
            "editing": self.editing,
        }