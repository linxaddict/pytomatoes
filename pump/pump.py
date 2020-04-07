from time import sleep

from gpiozero import DigitalOutputDevice


class Pump:
    ML_PER_SECOND = 18

    def __init__(self, gpio_pin: int, ml_per_second=ML_PER_SECOND):
        self._output_device = DigitalOutputDevice(gpio_pin)
        self._ml_per_second = ml_per_second

    def _calculate_watering_time(self, ml: int) -> int:
        return int(ml / self._ml_per_second)

    def on(self, water_in_ml: int) -> None:
        self._output_device.on()
        sleep(self._calculate_watering_time(water_in_ml))
        self._output_device.off()

    def off(self) -> None:
        self._output_device.off()
