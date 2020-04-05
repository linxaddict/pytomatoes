import asyncio
import os
from datetime import datetime, date

from data.db.db_common import Session
from data.db.plan_item_dao import PlanItemDao
from data.db.pump_activation_dao import PumpActivationDao
from data.db.schedule_dao import ScheduleDao
from data.firebase_backend import FirebaseBackend, FirebaseConfig
from data.model import PlanItem, PumpActivation
from data.pump_activation_repository import PumpActivationRepository
from data.schedule_repository import ScheduleRepository
from pump.pump import Pump

INTERVAL = 5


def extract_slot_ts(item: PlanItem) -> str:
    time = datetime.strptime(item.time, '%H:%M').time()
    slot = datetime.combine(date.today(), time)

    return slot.strftime('%Y-%m-%dT%H:%M')


async def should_start_pump(item: PlanItem, activation_repository: PumpActivationRepository) -> bool:
    time = datetime.strptime(item.time, '%H:%M').time()
    now = datetime.now().time()

    slot = datetime.combine(date.today(), time)

    slot_str = slot.strftime('%Y-%m-%dT%H:%M')
    delta = datetime.combine(date.today(), now) - slot

    return now > time and delta.seconds >= INTERVAL and not await activation_repository.exists(slot_str)


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
    session = Session()

    plan_item_dao = PlanItemDao(session=session)
    schedule_dao = ScheduleDao(session=session)
    pump_activation_dao = PumpActivationDao(session=session)

    schedule_repository = ScheduleRepository(firebase_backend, plan_item_dao, schedule_dao)
    pump_activation_repository = PumpActivationRepository(pump_activation_dao)

    pump = Pump(gpio_pin=21)

    while True:
        schedule = await schedule_repository.fetch()
        if schedule:
            try:
                for item in schedule.plan:
                    print('item: ', item)

                    if await should_start_pump(item, pump_activation_repository):
                        slot_ts = extract_slot_ts(item)

                        await asyncio.gather(
                            pump_activation_repository.store(PumpActivation(timestamp=slot_ts, water=item.water)),
                            pump.on(item.water)
                        )
                    else:
                        print('slot_ts in db: ', extract_slot_ts(item))
            except Exception as e:
                print('an exception occurred: ', e)

        await asyncio.sleep(INTERVAL)


if __name__ == "__main__":
    asyncio.run(main())
