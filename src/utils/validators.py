import re
from datetime import datetime
from typing import Optional
from .exceptions import ValidationException


class Validator:
    """
    Classe utilitária para validação de dados de entrada.

    Fornece métodos estáticos para validação de CPF, email,
    datas e outros dados utilizados no sistema.
    """

    @staticmethod
    def validate_cpf(cpf: str) -> bool:
        """
        Valida um CPF brasileiro.

        Args:
            cpf: String contendo o CPF (com ou sem pontuação)

        Returns:
            bool: True se o CPF é válido

        Raises:
            ValidationException: Se o CPF for inválido
        """
        cpf = re.sub(r'[^0-9]', '', cpf)

        if len(cpf) != 11 or cpf == cpf[0] * 11:
            raise ValidationException("CPF inválido")

        def calculate_digit(cpf_partial: str, multiplier: int) -> str:
            total = sum(int(digit) * (multiplier - idx) for idx, digit in enumerate(cpf_partial))
            remainder = total % 11
            return '0' if remainder < 2 else str(11 - remainder)

        if cpf[9] != calculate_digit(cpf[:9], 10):
            raise ValidationException("CPF inválido")

        if cpf[10] != calculate_digit(cpf[:10], 11):
            raise ValidationException("CPF inválido")

        return True

    @staticmethod
    def validate_email(email: str) -> bool:
        """
        Valida um endereço de email.

        Args:
            email: String contendo o email

        Returns:
            bool: True se o email é válido

        Raises:
            ValidationException: Se o email for inválido
        """
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(pattern, email):
            raise ValidationException("Email inválido")
        return True

    @staticmethod
    def validate_phone(phone: str) -> bool:
        """
        Valida um número de telefone brasileiro.

        Args:
            phone: String contendo o telefone

        Returns:
            bool: True se o telefone é válido

        Raises:
            ValidationException: Se o telefone for inválido
        """
        phone = re.sub(r'[^0-9]', '', phone)
        if len(phone) < 10 or len(phone) > 11:
            raise ValidationException("Telefone inválido")
        return True

    @staticmethod
    def validate_license_plate(license_plate: str) -> bool:
        """
        Valida uma placa de veículo (formato antigo e Mercosul).

        Args:
            license_plate: String contendo a placa

        Returns:
            bool: True se a placa é válida

        Raises:
            ValidationException: Se a placa for inválida
        """
        pattern_old = r'^[A-Z]{3}[0-9]{4}$'
        pattern_mercosul = r'^[A-Z]{3}[0-9][A-Z][0-9]{2}$'

        plate = license_plate.upper().replace('-', '')

        if not (re.match(pattern_old, plate) or re.match(pattern_mercosul, plate)):
            raise ValidationException("Placa inválida")
        return True

    @staticmethod
    def validate_date_range(start_date: datetime, end_date: datetime) -> bool:
        """
        Valida um intervalo de datas.

        Args:
            start_date: Data de início
            end_date: Data de término

        Returns:
            bool: True se o intervalo é válido

        Raises:
            ValidationException: Se o intervalo for inválido
        """
        if start_date >= end_date:
            raise ValidationException("Data de início deve ser anterior à data de término")

        if start_date < datetime.now().replace(hour=0, minute=0, second=0, microsecond=0):
            raise ValidationException("Data de início não pode ser no passado")

        return True

    @staticmethod
    def validate_positive_number(value: float, field_name: str = "Valor") -> bool:
        """
        Valida se um número é positivo.

        Args:
            value: Valor numérico a ser validado
            field_name: Nome do campo para mensagem de erro

        Returns:
            bool: True se o valor é positivo

        Raises:
            ValidationException: Se o valor for negativo ou zero
        """
        if value <= 0:
            raise ValidationException(f"{field_name} deve ser maior que zero")
        return True

    @staticmethod
    def validate_year(year: int) -> bool:
        """
        Valida um ano de fabricação de veículo.

        Args:
            year: Ano a ser validado

        Returns:
            bool: True se o ano é válido

        Raises:
            ValidationException: Se o ano for inválido
        """
        current_year = datetime.now().year
        if year < 1900 or year > current_year + 1:
            raise ValidationException(f"Ano deve estar entre 1900 e {current_year + 1}")
        return True
