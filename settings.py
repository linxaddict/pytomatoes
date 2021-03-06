import os


class Settings:
    """
    Contains the configuration settings.
    """

    def __init__(self, api_key: str = None, auth_domain: str = None, database_url: str = None, node: str = None,
                 storage_bucket: str = None, firebase_email: str = None, firebase_password: str = None,
                 local_db_name: str = None, pin_number: int = None, ml_per_second: int = None):
        from dotenv import load_dotenv
        load_dotenv()

        self._api_key = api_key or os.getenv('API_KEY')
        self._auth_domain = auth_domain or os.getenv('AUTH_DOMAIN')
        self._database_url = database_url or os.getenv('DATABASE_URL')
        self._node = node or os.getenv('NODE')
        self._storage_bucket = storage_bucket or os.getenv('STORAGE_BUCKET')
        self._firebase_email = firebase_email or os.getenv('EMAIL')
        self._firebase_password = firebase_password or os.getenv('PASSWORD')
        self._local_db_name = local_db_name or 'db.sqlite3'
        self._ml_per_second = int(ml_per_second or os.getenv('ML_PER_SECOND'))
        self._pin_number = pin_number or os.getenv('PIN')

    @property
    def api_key(self) -> str:
        return self._api_key

    @property
    def auth_domain(self) -> str:
        return self._auth_domain

    @property
    def database_url(self) -> str:
        return self._database_url

    @property
    def node(self) -> str:
        return self._node

    @property
    def storage_bucket(self) -> str:
        return self._storage_bucket

    @property
    def firebase_email(self) -> str:
        return self._firebase_email

    @property
    def firebase_password(self) -> str:
        return self._firebase_password

    @property
    def local_db_name(self) -> str:
        return self._local_db_name

    @property
    def pin_number(self) -> int:
        return self._pin_number

    @property
    def ml_per_seconds(self) -> int:
        return self._ml_per_second
