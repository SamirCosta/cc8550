import sqlite3
from typing import Optional, List, Dict, Any
from contextlib import contextmanager
from .config import settings


class Database:
    """
    Classe responsável pelo gerenciamento da conexão com o banco de dados SQLite.

    Implementa o padrão Singleton para garantir uma única instância
    e fornece métodos para execução de queries e gerenciamento de transações.
    """

    _instance: Optional['Database'] = None

    def __new__(cls) -> 'Database':
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        if not hasattr(self, 'initialized'):
            self.db_path = settings.database_path
            self.initialized = True

    def get_connection(self) -> sqlite3.Connection:
        """
        Cria e retorna uma nova conexão com o banco de dados.

        Returns:
            sqlite3.Connection: Objeto de conexão com o banco
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    @contextmanager
    def get_cursor(self):
        """
        Context manager para obter um cursor de banco de dados.

        Yields:
            sqlite3.Cursor: Cursor para execução de queries
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            yield cursor
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            cursor.close()
            conn.close()

    def execute_query(self, query: str, params: tuple = ()) -> List[Dict[str, Any]]:
        """
        Executa uma query SELECT e retorna os resultados.

        Args:
            query: String SQL da query a ser executada
            params: Tupla com os parâmetros da query

        Returns:
            List[Dict[str, Any]]: Lista de dicionários com os resultados
        """
        with self.get_cursor() as cursor:
            cursor.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]

    def execute_update(self, query: str, params: tuple = ()) -> int:
        """
        Executa uma query de UPDATE, INSERT ou DELETE.

        Args:
            query: String SQL da query a ser executada
            params: Tupla com os parâmetros da query

        Returns:
            int: ID da última linha inserida ou número de linhas afetadas
        """
        with self.get_cursor() as cursor:
            cursor.execute(query, params)
            return cursor.lastrowid if cursor.lastrowid else cursor.rowcount

    def initialize_schema(self) -> None:
        """
        Inicializa o schema do banco de dados criando todas as tabelas necessárias.
        """
        schema = """
        CREATE TABLE IF NOT EXISTS cars (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            brand TEXT NOT NULL,
            model TEXT NOT NULL,
            year INTEGER NOT NULL,
            license_plate TEXT UNIQUE NOT NULL,
            daily_rate REAL NOT NULL,
            is_available INTEGER DEFAULT 1,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS customers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            cpf TEXT UNIQUE NOT NULL,
            phone TEXT NOT NULL,
            email TEXT NOT NULL,
            has_pending_payment INTEGER DEFAULT 0,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS rentals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id INTEGER NOT NULL,
            car_id INTEGER NOT NULL,
            start_date TEXT NOT NULL,
            end_date TEXT NOT NULL,
            total_value REAL NOT NULL,
            status TEXT DEFAULT 'active',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (customer_id) REFERENCES customers (id),
            FOREIGN KEY (car_id) REFERENCES cars (id)
        );

        CREATE TABLE IF NOT EXISTS payments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            rental_id INTEGER NOT NULL,
            amount REAL NOT NULL,
            payment_method TEXT NOT NULL,
            payment_date TEXT NOT NULL,
            status TEXT DEFAULT 'pending',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (rental_id) REFERENCES rentals (id)
        );

        CREATE TABLE IF NOT EXISTS maintenances (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            car_id INTEGER NOT NULL,
            description TEXT NOT NULL,
            maintenance_date TEXT NOT NULL,
            cost REAL NOT NULL,
            status TEXT DEFAULT 'scheduled',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (car_id) REFERENCES cars (id)
        );

        CREATE INDEX IF NOT EXISTS idx_cars_available ON cars(is_available);
        CREATE INDEX IF NOT EXISTS idx_customers_cpf ON customers(cpf);
        CREATE INDEX IF NOT EXISTS idx_rentals_status ON rentals(status);
        CREATE INDEX IF NOT EXISTS idx_rentals_dates ON rentals(start_date, end_date);
        """

        with self.get_cursor() as cursor:
            cursor.executescript(schema)
