from pydantic_settings import BaseSettings, SettingsConfigDict
from uvicorn import Config


class Settings(BaseSettings):
    database_url: str 
    JWT_SECRET:str
    JWT_ALGORITHM:str
    ACCESS_TOKEN_EXPIRY: int
    REFRESH_TOKEN_EXPIRY: int

    class Config:
        env_file = ".env"


settings = Settings() 

