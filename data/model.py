from dataclasses import dataclass
from typing import List


@dataclass
class PlanItem:
    time: str
    water: int


@dataclass
class Schedule:
    plan: List[PlanItem]
