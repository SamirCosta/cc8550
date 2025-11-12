import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

load_dotenv()


class Settings:
    """
    Classe de configuração da aplicação.

    Gerencia todas as variáveis de ambiente e configurações
    necessárias para o funcionamento da aplicação.
    """

    def __init__(self) -> None:
        self.DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./rental_cars.db")
        self.LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
        self.LOG_FILE: str = os.getenv("LOG_FILE", "app.log")
        self.API_HOST: str = os.getenv("API_HOST", "0.0.0.0")
        self.API_PORT: int = int(os.getenv("API_PORT", "8000"))
        self.API_RELOAD: bool = os.getenv("API_RELOAD", "True").lower() == "true"

    @property
    def database_path(self) -> str:
        """
        Retorna o caminho do arquivo do banco de dados SQLite.

        Returns:
            str: Caminho completo do banco de dados
        """
        if self.DATABASE_URL.startswith("sqlite:///"):
            return self.DATABASE_URL.replace("sqlite:///", "")
        return self.DATABASE_URL


settings = Settings()
