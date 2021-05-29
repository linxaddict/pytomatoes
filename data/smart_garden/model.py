from dataclasses import dataclass


@dataclass
class SmartGardenAuthPayload:
    email: str
    password: str


@dataclass
class SmartGardenAuthRefreshPayload:
    refresh: str


@dataclass
class SmartGardenAuthData:
    access: str
    refresh: str


@dataclass
class SmartGardenAuthRefreshData:
    access: str
