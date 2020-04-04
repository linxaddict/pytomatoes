import asyncio
import os
from datetime import datetime, date

from firebase_backend import FirebaseBackend, FirebaseConfig
from model import PlanItem
from pump import Pump
from schedule_repository import ScheduleRepository

INTERVAL = 5

processed_time_slots = set()


def extract_slot_ts(item: PlanItem) -> str:
    time = datetime.strptime(item.time, '%H:%M').time()
    slot = datetime.combine(date.today(), time)

    return slot.strftime('%Y-%m-%dT%H:%M')


def should_start_pump(item: PlanItem) -> bool:
    time = datetime.strptime(item.time, '%H:%M').time()
    now = datetime.now().time()

    slot = datetime.combine(date.today(), time)

    slot_str = slot.strftime('%Y-%m-%dT%H:%M')
    delta = datetime.combine(date.today(), now) - slot

    return now > time and delta.seconds >= INTERVAL and slot_str not in processed_time_slots


async def main():
    from dotenv import load_dotenv
    load_dotenv()

    config = {
        'apiKey': os.getenv('API_KEY'),
        'authDomain': os.getenv('AUTH_DOMAIN'),
        'databaseURL': os.getenv('DATABASE_URL'),
        'storageBucket': os.getenv('STORAGE_BUCKET'),
        'email': os.getenv('EMAIL'),
        'password': os.getenv('PASSWORD')
    }

    firebase_backend = FirebaseBackend(FirebaseConfig(**config))
    repository = ScheduleRepository(firebase_backend)
    pump = Pump(gpio_pin=21)

    while True:
        schedule = await repository.fetch()

        try:
            for item in schedule.plan:
                print('item: ', item)

                if should_start_pump(item):
                    slot_ts = extract_slot_ts(item)
                    processed_time_slots.add(slot_ts)
                    await pump.on(item.water)
        except Exception as e:
            print('could not parse data: ', e)

        await asyncio.sleep(INTERVAL)


if __name__ == "__main__":
    asyncio.run(main())
