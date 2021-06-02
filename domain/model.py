from dataclasses import dataclass
from typing import List, Optional


@dataclass
class ScheduledActivation:
    time: str
    amount: int
    active: bool


@dataclass
class OneTimeActivation:
    timestamp: str
    amount: int


@dataclass
class Circuit:
    id: int
    name: str
    active: bool
    one_time_activation: Optional[OneTimeActivation]
    schedule: List[ScheduledActivation]


@dataclass
class PumpActivation:
    timestamp: str
    amount: int
