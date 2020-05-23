import asyncio

from data.firebase.firebase_backend import FirebaseBackend


class RunHealthcheckLoop:
    def __init__(self, firebase: FirebaseBackend, interval: int = 5) -> None:
        self._firebase = firebase
        self._interval = interval

    async def execute(self) -> None:
        """
        Runs an infinite loop in which health checks are sent so the user knows that his device is alive.
        """
        while True:
            await asyncio.gather(
                asyncio.sleep(self._interval),
                self._firebase.send_health_check()
            )
