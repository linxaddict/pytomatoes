from time import sleep

from gpiozero import DigitalOutputDevice


class Pump:
    """
    Represents a DC water pump that can be controlled by simple turning it on for some time and turning it off.
    The amount of water that flows through the pump has to be measured for each device and supplied when constructing
    an instance of this class.
    """

    ML_PER_SECOND = 18

    def __init__(self, gpio_pin: int, ml_per_second=ML_PER_SECOND):
        """
        :param gpio_pin: gpio pin that is used to control the pump
        :param ml_per_second:   specifies how much water flows through the pump in a second
        """
        self._output_device = DigitalOutputDevice(gpio_pin)
        self._ml_per_second = ml_per_second

    def _calculate_watering_time(self, ml: int) -> int:
        """
        Calculates for how long the pump has to be turned on for given amount of water.
        :param ml: amount of water in ml
        :return: time in seconds
        """
        return int(ml / self._ml_per_second)

    def on(self, water_in_ml: int) -> None:
        """
        TUrns on the pump.
        :param water_in_ml: specifies how much water should flow through the pump
        """
        self._output_device.on()
        sleep(self._calculate_watering_time(water_in_ml))
        self._output_device.off()

    def off(self) -> None:
        """
        TUrns off the pump.
        """
        self._output_device.off()
