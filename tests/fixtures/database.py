"""
Fixtures de Banco de Dados

Fixtures relacionadas à configuração e gerenciamento do banco de dados de teste.
"""
import pytest
import os
import gc
import uuid
from src.config import Database


@pytest.fixture(scope="function")
def test_db():
    """
    Fixture que cria um banco de dados de teste limpo para cada teste.

    O banco é criado antes do teste e removido após a execução,
    garantindo isolamento entre os testes. Cada teste usa um arquivo
    de banco único para evitar conflitos no Windows.

    Yields:
        Database: Instância do banco de dados de teste
    """
    test_db_path = f"test_rental_{uuid.uuid4().hex[:8]}.db"

    db = Database()
    db.db_path = test_db_path
    db._conn = None
    db.initialize_schema()

    yield db

    if hasattr(db, '_conn') and db._conn:
        db._conn.close()
        db._conn = None

    gc.collect()

    if os.path.exists(test_db_path):
        try:
            os.remove(test_db_path)
        except PermissionError:
            pass
