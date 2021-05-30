import os


class Settings:
    """
    Contains the configuration settings.
    """

    def __init__(self, email: str = None, password: str = None, local_db_name: str = None, pin_number: int = None,
                 ml_per_second: int = None):
        from dotenv import load_dotenv
        load_dotenv()

        self._email = email or os.getenv('EMAIL')
        self._password = password or os.getenv('PASSWORD')
        self._local_db_name = local_db_name or os.getenv('DB_NAME')
        self._ml_per_second = int(ml_per_second or os.getenv('ML_PER_SECOND'))
        self._pin_number = pin_number or os.getenv('PIN')

    @property
    def email(self) -> str:
        return self._email

    @property
    def password(self) -> str:
        return self._password

    @property
    def local_db_name(self) -> str:
        return self._local_db_name

    @property
    def pin_number(self) -> int:
        return self._pin_number

    @property
    def ml_per_seconds(self) -> int:
        return self._ml_per_second
