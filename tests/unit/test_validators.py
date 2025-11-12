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

    def test_valid_cpf(self, valid_cpfs):
        """Testa CPF válido usando fixture."""
        assert Validator.validate_cpf(valid_cpfs[0]) is True

    def test_all_valid_cpfs(self, valid_cpfs):
        """Testa todos os CPFs válidos da fixture."""
        for cpf in valid_cpfs:
            assert Validator.validate_cpf(cpf) is True

    @pytest.mark.parametrize("cpf", [
        "52998224725",
        "84434916041",
        "111.444.777-35"
    ])
    def test_multiple_valid_cpfs(self, cpf):
        """Testa múltiplos CPFs válidos usando parametrização."""
        assert Validator.validate_cpf(cpf) is True

    def test_invalid_cpf_all_same_digits(self):
        """Testa CPF inválido com todos os dígitos iguais."""
        with pytest.raises(ValidationException, match="CPF inválido"):
            Validator.validate_cpf("11111111111")

    def test_all_invalid_cpfs(self, invalid_cpfs):
        """Testa todos os CPFs inválidos da fixture."""
        for cpf in invalid_cpfs:
            with pytest.raises(ValidationException):
                Validator.validate_cpf(cpf)

    @pytest.mark.parametrize("cpf", [
        "00000000000",
        "12345678901",
        "123",
        ""
    ])
    def test_multiple_invalid_cpfs(self, cpf):
        """Testa múltiplos CPFs inválidos."""
        with pytest.raises(ValidationException):
            Validator.validate_cpf(cpf)

    def test_cpf_with_formatting(self):
        """Testa CPF válido com formatação."""
        assert Validator.validate_cpf("111.444.777-35") is True


class TestEmailValidator:
    """
    Testes unitários para validação de email.
    """

    def test_valid_email(self, valid_emails):
        """Testa email válido usando fixture."""
        assert Validator.validate_email(valid_emails[0]) is True

    def test_all_valid_emails(self, valid_emails):
        """Testa todos os emails válidos da fixture."""
        for email in valid_emails:
            assert Validator.validate_email(email) is True

    @pytest.mark.parametrize("email", [
        "test@domain.com",
        "user.name@site.com.br",
        "admin+tag@example.org"
    ])
    def test_multiple_valid_emails(self, email):
        """Testa múltiplos emails válidos."""
        assert Validator.validate_email(email) is True

    def test_all_invalid_emails(self, invalid_emails):
        """Testa todos os emails inválidos da fixture."""
        for email in invalid_emails:
            with pytest.raises(ValidationException, match="Email inválido"):
                Validator.validate_email(email)

    @pytest.mark.parametrize("email", [
        "invalid",
        "@example.com",
        "user@",
        "user @example.com",
        ""
    ])
    def test_invalid_emails(self, email):
        """Testa emails inválidos."""
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

    @pytest.mark.parametrize("phone", [
        "11987654321",
        "1133334444",
        "(11) 98765-4321",
        "(11) 3333-4444"
    ])
    def test_valid_phones(self, phone):
        """Testa telefones válidos."""
        assert Validator.validate_phone(phone) is True

    def test_all_invalid_phones(self, invalid_phones):
        """Testa todos os telefones inválidos da fixture."""
        for phone in invalid_phones:
            with pytest.raises(ValidationException, match="Telefone inválido"):
                Validator.validate_phone(phone)

    @pytest.mark.parametrize("phone", [
        "123",
        "123456789012",
        "abc",
        ""
    ])
    def test_invalid_phones(self, phone):
        """Testa telefones inválidos."""
        with pytest.raises(ValidationException, match="Telefone inválido"):
            Validator.validate_phone(phone)


class TestLicensePlateValidator:
    """
    Testes unitários para validação de placa.
    """

    def test_all_valid_license_plates(self, valid_license_plates):
        """Testa todas as placas válidas da fixture."""
        for plate in valid_license_plates:
            assert Validator.validate_license_plate(plate) is True

    @pytest.mark.parametrize("plate", [
        "ABC1234",
        "ABC1D23",
        "abc1234",
        "ABC-1234"
    ])
    def test_valid_plates(self, plate):
        """Testa placas válidas (formato antigo e Mercosul)."""
        assert Validator.validate_license_plate(plate) is True

    def test_all_invalid_license_plates(self, invalid_license_plates):
        """Testa todas as placas inválidas da fixture."""
        for plate in invalid_license_plates:
            with pytest.raises(ValidationException, match="Placa inválida"):
                Validator.validate_license_plate(plate)

    @pytest.mark.parametrize("plate", [
        "AB1234",
        "ABCD123",
        "1234567",
        ""
    ])
    def test_invalid_plates(self, plate):
        """Testa placas inválidas."""
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
