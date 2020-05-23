from dataclasses import dataclass
from typing import List, Optional


@dataclass
class PlanItem:
    time: str
    water: int
    active: bool


@dataclass
class OneTimeActivation:
    date: str
    water: int


@dataclass
class Schedule:
    plan: List[PlanItem]
    active: bool
    one_time_activation: Optional[OneTimeActivation]


@dataclass
class PumpActivation:
    timestamp: str
    water: int
