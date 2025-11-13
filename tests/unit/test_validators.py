import pytest
from src.utils import Validator, ValidationException
from datetime import datetime, timedelta

# Importar fixtures necessárias
from tests.fixtures.test_data import (
    valid_cpfs,
    invalid_cpfs,
    valid_emails,
    invalid_emails,
    valid_phones,
    invalid_phones,
    valid_license_plates,
    invalid_license_plates
)


class TestCPFValidator:
    """
    Testes unitários para validação de CPF.
    """

    def test_all_valid_cpfs(self, valid_cpfs):
        """Testa todos os CPFs válidos da fixture (inclui CPF com formatação)."""
        for cpf in valid_cpfs:
            assert Validator.validate_cpf(cpf) is True

    def test_all_invalid_cpfs(self, invalid_cpfs):
        """Testa todos os CPFs inválidos da fixture."""
        for cpf in invalid_cpfs:
            with pytest.raises(ValidationException):
                Validator.validate_cpf(cpf)


class TestEmailValidator:
    """
    Testes unitários para validação de email.
    """

    def test_all_valid_emails(self, valid_emails):
        """Testa todos os emails válidos da fixture."""
        for email in valid_emails:
            assert Validator.validate_email(email) is True

    def test_all_invalid_emails(self, invalid_emails):
        """Testa todos os emails inválidos da fixture."""
        for email in invalid_emails:
            with pytest.raises(ValidationException, match="Email inválido"):
                Validator.validate_email(email)


class TestPhoneValidator:
    """
    Testes unitários para validação de telefone.
    """

    def test_all_valid_phones(self, valid_phones):
        """Testa todos os telefones válidos da fixture."""
        for phone in valid_phones:
            assert Validator.validate_phone(phone) is True

    def test_all_invalid_phones(self, invalid_phones):
        """Testa todos os telefones inválidos da fixture."""
        for phone in invalid_phones:
            with pytest.raises(ValidationException, match="Telefone inválido"):
                Validator.validate_phone(phone)


class TestLicensePlateValidator:
    """
    Testes unitários para validação de placa.
    """

    def test_all_valid_license_plates(self, valid_license_plates):
        """Testa todas as placas válidas da fixture (formatos antigo e Mercosul)."""
        for plate in valid_license_plates:
            assert Validator.validate_license_plate(plate) is True

    def test_all_invalid_license_plates(self, invalid_license_plates):
        """Testa todas as placas inválidas da fixture."""
        for plate in invalid_license_plates:
            with pytest.raises(ValidationException, match="Placa inválida"):
                Validator.validate_license_plate(plate)


class TestDateRangeValidator:
    """
    Testes unitários para validação de intervalo de datas.
    """

    def test_valid_date_range(self):
        """Testa intervalo de datas válido."""
        start = datetime.now() + timedelta(days=1)
        end = start + timedelta(days=10)
        assert Validator.validate_date_range(start, end) is True

    def test_invalid_date_range_start_after_end(self):
        """Testa intervalo inválido onde início é depois do fim."""
        start = datetime.now() + timedelta(days=10)
        end = datetime.now() + timedelta(days=1)
        with pytest.raises(ValidationException, match="Data de início deve ser anterior"):
            Validator.validate_date_range(start, end)

    def test_invalid_date_range_start_in_past(self):
        """Testa intervalo inválido onde início está no passado."""
        start = datetime.now() - timedelta(days=1)
        end = datetime.now() + timedelta(days=10)
        with pytest.raises(ValidationException, match="não pode ser no passado"):
            Validator.validate_date_range(start, end)


class TestPositiveNumberValidator:
    """
    Testes unitários para validação de números positivos.
    """

    @pytest.mark.parametrize("value", [1, 10, 100.5, 0.01])
    def test_valid_positive_numbers(self, value):
        """Testa números positivos válidos."""
        assert Validator.validate_positive_number(value) is True

    @pytest.mark.parametrize("value", [0, -1, -100.5])
    def test_invalid_non_positive_numbers(self, value):
        """Testa números não positivos."""
        with pytest.raises(ValidationException, match="deve ser maior que zero"):
            Validator.validate_positive_number(value)


class TestYearValidator:
    """
    Testes unitários para validação de ano.
    """

    @pytest.mark.parametrize("year", [2000, 2023, 2024, 2025])
    def test_valid_years(self, year):
        """Testa anos válidos."""
        assert Validator.validate_year(year) is True

    @pytest.mark.parametrize("year", [1899, 2050, 3000])
    def test_invalid_years(self, year):
        """Testa anos inválidos."""
        with pytest.raises(ValidationException, match="Ano deve estar entre"):
            Validator.validate_year(year)
