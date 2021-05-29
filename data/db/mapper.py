from data.db.model import PumpActivationEntity, ScheduledActivationEntity, CircuitEntity
from domain.model import Circuit, ScheduledActivation, PumpActivation


def map_scheduled_activation_to_entity(activation: ScheduledActivation) -> ScheduledActivationEntity:
    """
    Maps domain model of plan item to its entity representation.
    :param activation: domain model
    :return: database model
    """
    return ScheduledActivationEntity(time=activation.time, amount=activation.amount, active=activation.active)


def map_circuit_to_entity(circuit: Circuit) -> CircuitEntity:
    """
    Maps domain model of schedule to its entity representation.
    :param circuit: domain model
    :return: database model
    """
    return CircuitEntity(name=circuit.name,
                         plan_items=[map_scheduled_activation_to_entity(item) for item in circuit.schedule],
                         active=circuit.active)


def map_pump_activation_to_entity(pump_activation: PumpActivation) -> PumpActivationEntity:
    """
    Maps domain model of pump activation to its entity representation.
    :param pump_activation: domain model
    :return: database model
    """
    return PumpActivationEntity(timestamp=pump_activation.timestamp, amount=pump_activation.amount)


def map_plan_item_entity_to_domain(activation: ScheduledActivationEntity) -> ScheduledActivation:
    """
    Maps entity representation of scheduled activation to a domain model.
    :param activation: database model
    :return: domain model
    """
    return ScheduledActivation(time=activation.time, amount=activation.amount, active=activation.active)


def map_circuit_entity_to_domain(circuit: CircuitEntity) -> Circuit:
    """
    Maps entity representation of circuit to a domain model.
    :param circuit: database model
    :return: domain model
    """
    return Circuit(id=circuit.id, name=circuit.name,
                   schedule=[map_scheduled_activation_to_entity(item) for item in circuit.schedule],
                   active=circuit.active, one_time_activation=None)


def map_pump_activation_entity_to_domain(pump_activation: PumpActivationEntity) -> PumpActivation:
    """
    Maps entity representation of pump activation to a domain model.
    :param pump_activation: database model
    :return: domain model
    """
    return PumpActivation(timestamp=pump_activation.timestamp, amount=pump_activation.amount)
