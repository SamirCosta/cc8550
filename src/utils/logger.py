import logging
import sys
from pathlib import Path
from typing import Optional
from src.config import settings


def setup_logger(name: str = "rental_api", log_file: Optional[str] = None) -> logging.Logger:
    """
    Configura e retorna um logger para a aplicação.

    Args:
        name: Nome do logger
        log_file: Caminho do arquivo de log (opcional)

    Returns:
        logging.Logger: Logger configurado
    """
    logger = logging.getLogger(name)

    if logger.handlers:
        return logger

    log_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)
    logger.setLevel(log_level)

    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    if log_file is None:
        log_file = settings.LOG_FILE

    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)

        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(log_level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger
