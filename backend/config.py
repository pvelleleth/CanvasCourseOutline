class Config:
    _instance = None
    _token = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Config, cls).__new__(cls)
        return cls._instance

    @classmethod
    def set_token(cls, token: str):
        cls._token = token

    @classmethod
    def get_token(cls) -> str:
        if cls._token is None:
            raise ValueError("Token not set")
        return cls._token 