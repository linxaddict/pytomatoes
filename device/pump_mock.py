from time import sleep


class Pump:
    """
    Represents a DC water pump that can be controlled by simple turning it on for some time and turning it off.
    The amount of water that flows through the pump has to be measured for each device and supplied when constructing
    an instance of this class.
    """

    ML_PER_SECOND = 18.0

    def __init__(self, ml_per_second=ML_PER_SECOND):
        """
        :param ml_per_second:   specifies how much water flows through the pump in a second
        """
        self._ml_per_second = ml_per_second

    def _calculate_watering_time(self, ml: float) -> float:
        """
        Calculates for how long the pump has to be turned on for given amount of water.
        :param ml: amount of water in ml
        :return: time in seconds
        """
        return ml / self._ml_per_second

    def on(self, water_in_ml: int) -> None:
        """
        Turns on the pump.
        :param water_in_ml: specifies how much water should flow through the pump
        """
        # self._output_device.on()
        print('pump on')
        sleep(self._calculate_watering_time(float(water_in_ml)))
        # self._output_device.off()
        print('pump off')

    def on_async(self, water_in_ml: int) -> None:
        """
        Turns on the pump on a dedicated GPIO thread.
        :param water_in_ml: specifies how much water should flow through the pump
        """
        # self._output_device.blink(on_time=self._calculate_watering_time(water_in_ml), n=1, background=True)
        print('pump blink')

    def off(self) -> None:
        """
        Turns off the pump.
        """
        # self._output_device.off()
        print('pump off')
