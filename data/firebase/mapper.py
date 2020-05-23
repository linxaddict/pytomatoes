from data.firebase.model import PlanItemData, PumpActivationData, ScheduleData, OneTimeActivationData
from domain.model import PlanItem, PumpActivation, Schedule, OneTimeActivation


def map_plan_item_to_domain(plan_item: PlanItemData) -> PlanItem:
    return PlanItem(
        time=plan_item.time,
        water=plan_item.water
    )


def map_domain_to_plan_item(plan_item: PlanItem) -> PlanItemData:
    return PlanItemData(
        time=plan_item.time,
        water=plan_item.water
    )


def map_pump_activation_to_domain(pump_activation: PumpActivationData) -> PumpActivation:
    return PumpActivation(
        timestamp=pump_activation.timestamp,
        water=pump_activation.water
    )


def map_domain_to_pump_activation(pump_activation: PumpActivation) -> PumpActivationData:
    return PumpActivationData(
        timestamp=pump_activation.timestamp,
        water=pump_activation.water
    )


def map_one_time_activation_to_domain(activation: OneTimeActivationData) -> OneTimeActivation:
    return OneTimeActivation(
        date=activation.date,
        water=activation.water
    )


def map_domain_to_one_time_activation(activation: OneTimeActivation) -> OneTimeActivationData:
    return OneTimeActivationData(
        date=activation.date,
        water=activation.water
    )


def map_schedule_to_domain(schedule: ScheduleData) -> Schedule:
    return Schedule(
        plan=[map_plan_item_to_domain(p) for p in schedule.plan],
        active=schedule.active,
        one_time_activation=map_one_time_activation_to_domain(
            schedule.one_time_activation) if schedule.one_time_activation else None
    )


def map_domain_to_schedule(schedule: Schedule) -> ScheduleData:
    return ScheduleData(
        plan=[map_domain_to_plan_item(p) for p in schedule.plan],
        active=schedule.active,
        one_time_activation=map_domain_to_one_time_activation(
            schedule.one_time_activation) if schedule.one_time_activation else None
    )
