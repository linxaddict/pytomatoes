import asyncio

from data.smart_garden.smart_garden_backend import SmartGardenBackend


class RunHealthCheckLoop:
    def __init__(self, backend: SmartGardenBackend, interval: int = 5) -> None:
        self._backend = backend
        self._interval = interval

    async def execute(self) -> None:
        """
        Runs an infinite loop in which health checks are sent so the user knows that his device is alive.
        """
        while True:
            await asyncio.gather(
                asyncio.sleep(self._interval),
                self._backend.send_health_check()
            )
