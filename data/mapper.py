from data.db.model import ScheduleEntity, PlanItemEntity, PumpActivationEntity
from data.model import Schedule, PlanItem, PumpActivation


def map_plan_item_to_entity(plan_item: PlanItem) -> PlanItemEntity:
    return PlanItemEntity(time=plan_item.time, water=plan_item.water)


def map_schedule_to_entity(schedule: Schedule) -> ScheduleEntity:
    return ScheduleEntity(plan_items=[map_plan_item_to_entity(item) for item in schedule.plan])


def map_pump_activation_to_entity(pump_activation: PumpActivation) -> PumpActivationEntity:
    return PumpActivationEntity(timestamp=pump_activation.timestamp, water=pump_activation.water)


def map_plan_item_entity_to_domain(plan_item: PlanItemEntity) -> PlanItem:
    return PlanItem(time=plan_item.time, water=plan_item.water)


def map_schedule_entity_to_domain(schedule: ScheduleEntity) -> Schedule:
    return Schedule(plan=[map_plan_item_entity_to_domain(item) for item in schedule.plan_items])


def map_pump_activation_entity_to_domain(pump_activation: PumpActivationEntity) -> PumpActivation:
    return PumpActivation(timestamp=pump_activation.timestamp, water=pump_activation.water)
