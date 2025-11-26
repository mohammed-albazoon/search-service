from pydantic import BaseSettings, AnyHttpUrl

class Settings(BaseSettings):
    # Remote data source (Swagger-provided)
    MESSAGES_API_BASE: AnyHttpUrl = "https://november7-730026606190.europe-west1.run.app"
    # Path to GET messages route based on swagger: /messages? (we'll call GET /messages)
    MESSAGES_ENDPOINT: str = "/messages/"
    SQLITE_DB_PATH: str = "data/messages.db"
    REINDEX_ON_START: bool = True
    # page limits
    DEFAULT_PAGE_SIZE: int = 20
    MAX_PAGE_SIZE: int = 200

settings = Settings()
