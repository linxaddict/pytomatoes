import asyncio

from gpiozero import DigitalOutputDevice


class Pump:
    ML_PER_SECOND = 18

    def __init__(self, gpio_pin: int):
        self._output_device = DigitalOutputDevice(gpio_pin)

    @staticmethod
    def _calculate_watering_time(ml, ml_per_second=ML_PER_SECOND) -> int:
        return int(ml / ml_per_second)

    async def on(self, water_in_ml: int) -> None:
        self._output_device.on()
        await asyncio.sleep(self._calculate_watering_time(water_in_ml))
        self._output_device.off()

    async def off(self) -> None:
        self._output_device.off()
