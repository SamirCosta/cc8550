from typing import List, Optional, Dict, Any
from src.models import Car
from src.config import Database
from src.utils import DatabaseException, NotFoundException


class CarRepository:
    """
    Repositório para operações de banco de dados relacionadas a carros.

    Implementa o padrão Repository para abstrair o acesso a dados
    e fornecer operações CRUD para a entidade Car.
    """

    def __init__(self, database: Optional[Database] = None) -> None:
        self.db = database or Database()

    def create(self, car: Car) -> Car:
        """
        Cria um novo carro no banco de dados.

        Args:
            car: Objeto Car a ser criado

        Returns:
            Car: Objeto Car com o ID atualizado

        Raises:
            DatabaseException: Se houver erro ao criar o carro
        """
        try:
            query = """
                INSERT INTO cars (brand, model, year, license_plate, daily_rate, is_available)
                VALUES (?, ?, ?, ?, ?, ?)
            """
            car_id = self.db.execute_update(
                query,
                (car.brand, car.model, car.year, car.license_plate, car.daily_rate, int(car.is_available))
            )
            car.id = car_id
            return car
        except Exception as e:
            raise DatabaseException(f"Erro ao criar carro: {str(e)}")

    def find_by_id(self, car_id: int) -> Car:
        """
        Busca um carro pelo ID.

        Args:
            car_id: ID do carro

        Returns:
            Car: Objeto Car encontrado

        Raises:
            NotFoundException: Se o carro não for encontrado
        """
        query = "SELECT * FROM cars WHERE id = ?"
        results = self.db.execute_query(query, (car_id,))

        if not results:
            raise NotFoundException(f"Carro com ID {car_id} não encontrado")

        return Car.from_dict(results[0])

    def find_all(self) -> List[Car]:
        """
        Busca todos os carros.

        Returns:
            List[Car]: Lista de carros
        """
        query = "SELECT * FROM cars ORDER BY id DESC"
        results = self.db.execute_query(query)
        return [Car.from_dict(row) for row in results]

    def find_available(self, filters: Optional[Dict[str, Any]] = None) -> List[Car]:
        """
        Busca carros disponíveis com filtros opcionais.

        Args:
            filters: Dicionário com filtros (brand, model, max_price, min_year, max_year)

        Returns:
            List[Car]: Lista de carros disponíveis
        """
        query = "SELECT * FROM cars WHERE is_available = 1"
        params = []

        if filters:
            if filters.get("brand"):
                query += " AND LOWER(brand) LIKE ?"
                params.append(f"%{filters['brand'].lower()}%")

            if filters.get("model"):
                query += " AND LOWER(model) LIKE ?"
                params.append(f"%{filters['model'].lower()}%")

            if filters.get("max_price"):
                query += " AND daily_rate <= ?"
                params.append(filters["max_price"])

            if filters.get("min_year"):
                query += " AND year >= ?"
                params.append(filters["min_year"])

            if filters.get("max_year"):
                query += " AND year <= ?"
                params.append(filters["max_year"])

        query += " ORDER BY daily_rate ASC"
        results = self.db.execute_query(query, tuple(params))
        return [Car.from_dict(row) for row in results]

    def update(self, car: Car) -> Car:
        """
        Atualiza um carro existente.

        Args:
            car: Objeto Car com os dados atualizados

        Returns:
            Car: Objeto Car atualizado

        Raises:
            NotFoundException: Se o carro não for encontrado
            DatabaseException: Se houver erro ao atualizar
        """
        self.find_by_id(car.id)

        try:
            query = """
                UPDATE cars
                SET brand = ?, model = ?, year = ?, license_plate = ?,
                    daily_rate = ?, is_available = ?
                WHERE id = ?
            """
            self.db.execute_update(
                query,
                (car.brand, car.model, car.year, car.license_plate,
                 car.daily_rate, int(car.is_available), car.id)
            )
            return car
        except Exception as e:
            raise DatabaseException(f"Erro ao atualizar carro: {str(e)}")

    def delete(self, car_id: int) -> bool:
        """
        Remove um carro do banco de dados.

        Args:
            car_id: ID do carro a ser removido

        Returns:
            bool: True se o carro foi removido

        Raises:
            NotFoundException: Se o carro não for encontrado
        """
        self.find_by_id(car_id)

        query = "DELETE FROM cars WHERE id = ?"
        self.db.execute_update(query, (car_id,))
        return True

    def find_by_license_plate(self, license_plate: str) -> Optional[Car]:
        """
        Busca um carro pela placa.

        Args:
            license_plate: Placa do carro

        Returns:
            Optional[Car]: Objeto Car se encontrado, None caso contrário
        """
        query = "SELECT * FROM cars WHERE license_plate = ?"
        results = self.db.execute_query(query, (license_plate,))

        if not results:
            return None

        return Car.from_dict(results[0])

    def update_availability(self, car_id: int, is_available: bool) -> bool:
        """
        Atualiza a disponibilidade de um carro.

        Args:
            car_id: ID do carro
            is_available: Disponibilidade do carro

        Returns:
            bool: True se atualizado com sucesso

        Raises:
            NotFoundException: Se o carro não for encontrado
        """
        self.find_by_id(car_id)

        query = "UPDATE cars SET is_available = ? WHERE id = ?"
        self.db.execute_update(query, (int(is_available), car_id))
        return True
