from data.model.model import OneTimeActivationData, ScheduledActivationData, CircuitData
from data.smart_garden.model import PumpActivationData
from domain.model import ScheduledActivation, Circuit, OneTimeActivation, PumpActivation


def map_scheduled_activation_to_domain(activation: ScheduledActivationData) -> ScheduledActivation:
    return ScheduledActivation(
        time=activation.time,
        amount=activation.amount,
        active=activation.active
    )


def map_domain_to_scheduled_activation(activation: ScheduledActivation) -> ScheduledActivationData:
    return ScheduledActivationData(
        time=activation.time,
        amount=activation.amount,
        active=activation.active
    )


def map_one_time_activation_to_domain(activation: OneTimeActivationData) -> OneTimeActivation:
    return OneTimeActivation(
        timestamp=activation.timestamp,
        amount=activation.amount
    )


def map_domain_to_one_time_activation(activation: OneTimeActivation) -> OneTimeActivationData:
    return OneTimeActivationData(
        timestamp=activation.timestamp,
        amount=activation.amount
    )


def map_circuit_to_domain(circuit: CircuitData) -> Circuit:
    return Circuit(
        id=circuit.id,
        name=circuit.name,
        active=circuit.active,
        one_time_activation=map_one_time_activation_to_domain(
            circuit.one_time_activation) if circuit.one_time_activation else None,
        schedule=[map_scheduled_activation_to_domain(p) for p in circuit.schedule]
    )


def map_domain_to_circuit(circuit: Circuit) -> CircuitData:
    return CircuitData(
        id=circuit.id,
        name=circuit.name,
        active=circuit.active,
        one_time_activation=map_domain_to_one_time_activation(
            circuit.one_time_activation) if circuit.one_time_activation else None,
        schedule=[map_domain_to_scheduled_activation(p) for p in circuit.schedule]
    )


def map_pump_activation_to_domain(pump_activation: PumpActivationData) -> PumpActivation:
    return PumpActivation(
        timestamp=pump_activation.timestamp,
        amount=pump_activation.amount
    )


def map_domain_to_pump_activation(pump_activation: PumpActivation) -> PumpActivationData:
    return PumpActivationData(
        timestamp=pump_activation.timestamp,
        amount=pump_activation.amount
    )
