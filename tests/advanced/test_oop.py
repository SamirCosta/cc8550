"""
Testes de Orientação a Objetos

Demonstra testes de conceitos OOP:
- Herança e hierarquia de classes
- Polimorfismo e sobrescrita de métodos
- Encapsulamento e acesso a atributos
- Classes abstratas e interfaces
- Composição vs Herança
"""
import pytest
from abc import ABC, abstractmethod
from datetime import datetime
from src.models import Rental
from src.utils import ValidationException


# ============================================================================
# Classes base para demonstrar OOP
# ============================================================================

class BaseModel(ABC):
    """Classe abstrata base para todos os modelos."""

    def __init__(self, id=None):
        self._id = id
        self._created_at = datetime.now()

    @property
    def id(self):
        """Encapsulamento: getter para id."""
        return self._id

    @abstractmethod
    def to_dict(self):
        """Método abstrato que deve ser implementado por subclasses."""
        pass

    @abstractmethod
    def validate(self):
        """Validação específica de cada modelo."""
        pass


class Vehicle(BaseModel):
    """Classe base para veículos (demonstra herança)."""

    def __init__(self, id=None, brand=None, model=None, year=None, license_plate=None):
        super().__init__(id)
        self._brand = brand
        self._model = model
        self._year = year
        self._license_plate = license_plate

    @property
    def brand(self):
        return self._brand

    @property
    def model(self):
        return self._model

    def to_dict(self):
        """Implementação base de to_dict."""
        return {
            "id": self.id,
            "brand": self.brand,
            "model": self.model,
            "year": self._year,
            "license_plate": self._license_plate
        }

    def validate(self):
        """Validação base de veículo."""
        if not self.brand or not self.model:
            raise ValidationException("Brand e model são obrigatórios")
        if self._year < 1900 or self._year > datetime.now().year + 1:
            raise ValidationException("Ano inválido")


class RentalCar(Vehicle):
    """Carro de aluguel (demonstra herança específica)."""

    def __init__(self, id=None, brand=None, model=None, year=None,
                 license_plate=None, daily_rate=None, is_available=True):
        super().__init__(id, brand, model, year, license_plate)
        self._daily_rate = daily_rate
        self._is_available = is_available

    @property
    def daily_rate(self):
        return self._daily_rate

    def to_dict(self):
        """Sobrescreve to_dict adicionando campos específicos."""
        data = super().to_dict()
        data.update({
            "daily_rate": self.daily_rate,
            "is_available": self._is_available
        })
        return data

    def validate(self):
        """Estende validação da classe base."""
        super().validate()
        if self.daily_rate is None or self.daily_rate <= 0:
            raise ValidationException("Daily rate deve ser positivo")


class PremiumCar(RentalCar):
    """Carro premium com funcionalidades extras (herança em múltiplos níveis)."""

    def __init__(self, id=None, brand=None, model=None, year=None,
                 license_plate=None, daily_rate=None, is_available=True,
                 premium_features=None):
        super().__init__(id, brand, model, year, license_plate, daily_rate, is_available)
        self._premium_features = premium_features or []

    @property
    def premium_features(self):
        return self._premium_features

    def to_dict(self):
        """Adiciona features premium ao dicionário."""
        data = super().to_dict()
        data["premium_features"] = self.premium_features
        return data


# ============================================================================
# Interface para cálculo de descontos (demonstra polimorfismo)
# ============================================================================

class DiscountStrategy(ABC):
    """Interface para estratégias de desconto."""

    @abstractmethod
    def calculate_discount(self, days: int, base_value: float) -> float:
        """Calcula o desconto baseado nos dias."""
        pass


class StandardDiscount(DiscountStrategy):
    """Desconto padrão por período."""

    def calculate_discount(self, days: int, base_value: float) -> float:
        if days > 30:
            return base_value * 0.20
        elif days > 14:
            return base_value * 0.15
        elif days > 7:
            return base_value * 0.10
        return 0.0


class VIPDiscount(DiscountStrategy):
    """Desconto VIP (maior que o padrão)."""

    def calculate_discount(self, days: int, base_value: float) -> float:
        if days > 30:
            return base_value * 0.30
        elif days > 14:
            return base_value * 0.25
        elif days > 7:
            return base_value * 0.15
        return base_value * 0.05


# ============================================================================
# Testes de Herança
# ============================================================================

class TestInheritance:
    """Testes que verificam herança correta."""

    def test_vehicle_inheritance(self):
        """
        Testa que RentalCar herda de Vehicle.
        Demonstra: Verificação de hierarquia de herança, acesso a propriedades herdadas.
        """
        car = RentalCar(
            id=1,
            brand="Toyota",
            model="Corolla",
            year=2023,
            license_plate="ABC1234",
            daily_rate=100.0
        )

        # Verifica herança
        assert isinstance(car, RentalCar)
        assert isinstance(car, Vehicle)
        assert isinstance(car, BaseModel)

        # Verifica acesso a propriedades herdadas
        assert car.brand == "Toyota"
        assert car.model == "Corolla"

    def test_premium_car_multi_level_inheritance(self):
        """
        Testa herança em múltiplos níveis.
        Demonstra: Herança em 3 níveis, acesso a propriedades de todos os níveis.
        """
        premium = PremiumCar(
            id=1,
            brand="BMW",
            model="X5",
            year=2024,
            license_plate="XYZ9999",
            daily_rate=300.0,
            premium_features=["GPS", "Leather Seats", "Sunroof"]
        )

        # Verifica toda a hierarquia
        assert isinstance(premium, PremiumCar)
        assert isinstance(premium, RentalCar)
        assert isinstance(premium, Vehicle)
        assert isinstance(premium, BaseModel)

        # Verifica propriedades de todos os níveis
        assert premium.brand == "BMW"  # Vehicle
        assert premium.daily_rate == 300.0  # RentalCar
        assert len(premium.premium_features) == 3  # PremiumCar


# ============================================================================
# Testes de Polimorfismo
# ============================================================================

class TestPolymorphism:
    """Testes que verificam polimorfismo."""

    def test_discount_strategy_polymorphism(self):
        """
        Testa polimorfismo com estratégias de desconto.
        Demonstra: Strategy Pattern, comportamento polimórfico.
        """
        base_value = 1000.0
        days = 15

        strategies = [
            StandardDiscount(),
            VIPDiscount()
        ]

        results = []
        for strategy in strategies:
            discount = strategy.calculate_discount(days, base_value)
            results.append(discount)

        # Diferentes estratégias produzem diferentes resultados
        assert results[0] == 150.0  # StandardDiscount (15%)
        assert results[1] == 250.0  # VIPDiscount (25%)

    def test_method_overriding(self):
        """
        Testa sobrescrita de métodos.
        Demonstra: Override de métodos, comportamento específico de subclasse.
        """
        base_car = RentalCar(
            id=1,
            brand="Toyota",
            model="Corolla",
            year=2023,
            license_plate="ABC1234",
            daily_rate=100.0
        )

        premium_car = PremiumCar(
            id=2,
            brand="BMW",
            model="X5",
            year=2024,
            license_plate="XYZ9999",
            daily_rate=300.0,
            premium_features=["GPS", "Leather"]
        )

        # to_dict é sobrescrito em cada nível
        base_dict = base_car.to_dict()
        premium_dict = premium_car.to_dict()

        assert "premium_features" not in base_dict
        assert "premium_features" in premium_dict
        assert len(premium_dict["premium_features"]) == 2


# ============================================================================
# Testes de Encapsulamento
# ============================================================================

class TestEncapsulation:
    """Testes que verificam encapsulamento correto."""

    def test_property_encapsulation(self):
        """
        Testa que atributos são acessados via properties.
        Demonstra: Properties, atributos privados.
        """
        car = RentalCar(
            id=1,
            brand="Toyota",
            model="Corolla",
            year=2023,
            license_plate="ABC1234",
            daily_rate=100.0
        )

        # Acesso via property
        assert car.brand == "Toyota"
        assert car.daily_rate == 100.0

        # Atributos privados não devem ser acessados diretamente
        assert hasattr(car, '_brand')
        assert hasattr(car, '_daily_rate')

    def test_property_read_only(self):
        """
        Testa que properties são read-only quando apropriado.
        Demonstra: Properties read-only, proteção de atributos.
        """
        car = RentalCar(
            id=1,
            brand="Honda",
            model="Civic",
            year=2023,
            license_plate="DEF5678",
            daily_rate=120.0
        )

        # Tentar modificar deve falhar (não tem setter)
        with pytest.raises(AttributeError):
            car.brand = "Toyota"

        with pytest.raises(AttributeError):
            car.id = 999


# ============================================================================
# Testes de Classes Abstratas
# ============================================================================

class TestAbstractClasses:
    """Testes que verificam uso correto de classes abstratas."""

    def test_cannot_instantiate_abstract_class(self):
        """
        Testa que classe abstrata não pode ser instanciada.
        Demonstra: ABC, impossibilidade de instanciar classes abstratas.
        """
        with pytest.raises(TypeError):
            BaseModel(id=1)

    def test_abstract_methods_must_be_implemented(self):
        """
        Testa que métodos abstratos devem ser implementados.
        Demonstra: Forçar implementação de métodos abstratos.
        """
        # Criar classe que não implementa métodos abstratos
        class IncompleteModel(BaseModel):
            pass

        # Não pode instanciar
        with pytest.raises(TypeError):
            IncompleteModel(id=1)

    def test_concrete_implementation_of_abstract_methods(self):
        """
        Testa implementação concreta de métodos abstratos.
        Demonstra: Implementação correta de métodos abstratos.
        """
        car = RentalCar(
            id=1,
            brand="Honda",
            model="Civic",
            year=2023,
            license_plate="MNO7890",
            daily_rate=120.0
        )

        # Métodos abstratos foram implementados
        assert callable(car.to_dict)
        assert callable(car.validate)

        # Executar métodos
        data = car.to_dict()
        assert isinstance(data, dict)

        car.validate()  # Não deve lançar exceção


# ============================================================================
# Testes de Composição
# ============================================================================

class TestComposition:
    """Testes que demonstram composição como alternativa à herança."""

    def test_model_with_composition(self):
        """
        Testa modelo usando composição.
        Demonstra: Composição vs herança, referências em vez de herança.
        """
        # Rental usa composição com Car e Customer
        rental = Rental(
            id=1,
            customer_id=1,
            car_id=1,
            start_date=datetime.now(),
            end_date=datetime.now(),
            total_value=500.0,
            status="active"
        )

        # Rental tem referências, não herança
        assert hasattr(rental, 'customer_id')
        assert hasattr(rental, 'car_id')


# ============================================================================
# Testes de Validação OOP
# ============================================================================

class TestOOPValidation:
    """Testes de validação específicos de OOP."""

    def test_validation_inheritance(self):
        """
        Testa que validação é herdada e estendida.
        Demonstra: Herança de métodos de validação, super().
        """
        # Validação base (Vehicle)
        car = RentalCar(
            id=1,
            brand="",  # Inválido
            model="Civic",
            year=2023,
            license_plate="PQR1234",
            daily_rate=120.0
        )

        with pytest.raises(ValidationException, match="Brand e model são obrigatórios"):
            car.validate()

    def test_extended_validation(self):
        """
        Testa validação estendida em subclasse.
        Demonstra: Extensão de validação em subclasse.
        """
        # Validação específica de RentalCar
        car = RentalCar(
            id=1,
            brand="Honda",
            model="Civic",
            year=2023,
            license_plate="STU5678",
            daily_rate=-50.0  # Inválido
        )

        with pytest.raises(ValidationException, match="Daily rate deve ser positivo"):
            car.validate()
