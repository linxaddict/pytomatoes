from data.db.model import ScheduleEntity, PlanItemEntity, PumpActivationEntity
from data.model import Schedule, PlanItem, PumpActivation


def map_plan_item_to_entity(plan_item: PlanItem) -> PlanItemEntity:
    """
    Maps domain model of plan item to its entity representation.
    :param plan_item: domain model
    :return: database model
    """
    return PlanItemEntity(time=plan_item.time, water=plan_item.water)


def map_schedule_to_entity(schedule: Schedule) -> ScheduleEntity:
    """
    Maps domain model of schedule to its entity representation.
    :param schedule: domain model
    :return: database model
    """
    return ScheduleEntity(plan_items=[map_plan_item_to_entity(item) for item in schedule.plan], active=schedule.active)


def map_pump_activation_to_entity(pump_activation: PumpActivation) -> PumpActivationEntity:
    """
    Maps domain model of pump activation to its entity representation.
    :param pump_activation: domain model
    :return: database model
    """
    return PumpActivationEntity(timestamp=pump_activation.timestamp, water=pump_activation.water)


def map_plan_item_entity_to_domain(plan_item: PlanItemEntity) -> PlanItem:
    """
    Maps entity representation of plan item to a domain model.
    :param plan_item: database model
    :return: domain model
    """
    return PlanItem(time=plan_item.time, water=plan_item.water)


def map_schedule_entity_to_domain(schedule: ScheduleEntity) -> Schedule:
    """
    Maps entity representation of schedule to a domain model.
    :param schedule: database model
    :return: domain model
    """
    return Schedule(plan=[map_plan_item_entity_to_domain(item) for item in schedule.plan_items], active=schedule.active)


def map_pump_activation_entity_to_domain(pump_activation: PumpActivationEntity) -> PumpActivation:
    """
    Maps entity representation of pump activation to a domain model.
    :param pump_activation: database model
    :return: domain model
    """
    return PumpActivation(timestamp=pump_activation.timestamp, water=pump_activation.water)
