"""
Fixtures de Dados de Teste

Fixtures que fornecem dados de teste para parametrização,
incluindo CPFs válidos/inválidos, emails válidos/inválidos, etc.
"""
import pytest


@pytest.fixture
def valid_cpfs():
    """
    Fixture que retorna uma lista de CPFs válidos para testes parametrizados.

    Returns:
        list[str]: Lista de CPFs válidos

    Examples:
        >>> @pytest.mark.parametrize("cpf", valid_cpfs())
        ... def test_cpf_validation(cpf):
        ...     assert Validator.validate_cpf(cpf) is True
    """
    return [
        "11144477735",
        "52998224725",
        "84434916041"
    ]


@pytest.fixture
def invalid_cpfs():
    """
    Fixture que retorna uma lista de CPFs inválidos para testes parametrizados.

    Returns:
        list[str]: Lista de CPFs inválidos

    Examples:
        >>> @pytest.mark.parametrize("cpf", invalid_cpfs())
        ... def test_invalid_cpf(cpf):
        ...     with pytest.raises(ValidationException):
        ...         Validator.validate_cpf(cpf)
    """
    return [
        "00000000000",  # Todos zeros
        "11111111111",  # Todos iguais
        "12345678901",  # Sequência inválida
        "123",          # Muito curto
        "abc12345678",  # Contém letras
        ""              # Vazio
    ]


@pytest.fixture
def valid_emails():
    """
    Fixture que retorna uma lista de emails válidos para testes parametrizados.

    Returns:
        list[str]: Lista de emails válidos

    Examples:
        >>> @pytest.mark.parametrize("email", valid_emails())
        ... def test_email_validation(email):
        ...     assert Validator.validate_email(email) is True
    """
    return [
        "joao@example.com",
        "maria.silva@empresa.com.br",
        "user+tag@domain.co",
        "test_user@subdomain.example.org"
    ]


@pytest.fixture
def invalid_emails():
    """
    Fixture que retorna uma lista de emails inválidos para testes parametrizados.

    Returns:
        list[str]: Lista de emails inválidos

    Examples:
        >>> @pytest.mark.parametrize("email", invalid_emails())
        ... def test_invalid_email(email):
        ...     with pytest.raises(ValidationException):
        ...         Validator.validate_email(email)
    """
    return [
        "invalid",           # Sem @
        "@example.com",      # Sem usuário
        "user@",             # Sem domínio
        "user @example.com", # Espaço inválido
        "",                  # Vazio
        "user@domain"        # Sem TLD
    ]


@pytest.fixture
def valid_phones():
    """
    Fixture que retorna uma lista de telefones válidos para testes parametrizados.

    Returns:
        list[str]: Lista de telefones válidos

    Examples:
        >>> @pytest.mark.parametrize("phone", valid_phones())
        ... def test_phone_validation(phone):
        ...     assert Validator.validate_phone(phone) is True
    """
    return [
        "11987654321",
        "21912345678",
        "85988776655"
    ]


@pytest.fixture
def invalid_phones():
    """
    Fixture que retorna uma lista de telefones inválidos para testes parametrizados.

    Returns:
        list[str]: Lista de telefones inválidos

    Examples:
        >>> @pytest.mark.parametrize("phone", invalid_phones())
        ... def test_invalid_phone(phone):
        ...     with pytest.raises(ValidationException):
        ...         Validator.validate_phone(phone)
    """
    return [
        "123",              # Muito curto
        "abc12345678",      # Contém letras
        ""                  # Vazio
    ]


@pytest.fixture
def valid_license_plates():
    """
    Fixture que retorna uma lista de placas válidas para testes parametrizados.

    Returns:
        list[str]: Lista de placas válidas

    Examples:
        >>> @pytest.mark.parametrize("plate", valid_license_plates())
        ... def test_plate_validation(plate):
        ...     assert Validator.validate_license_plate(plate) is True
    """
    return [
        "ABC1234",
        "XYZ9876",
        "DEF5678"
    ]


@pytest.fixture
def invalid_license_plates():
    """
    Fixture que retorna uma lista de placas inválidas para testes parametrizados.

    Returns:
        list[str]: Lista de placas inválidas

    Examples:
        >>> @pytest.mark.parametrize("plate", invalid_license_plates())
        ... def test_invalid_plate(plate):
        ...     with pytest.raises(ValidationException):
        ...         Validator.validate_license_plate(plate)
    """
    return [
        "ABC123",       # Muito curto
        "ABC12345",     # Muito longo
        "1234567",      # Apenas números
        "ABCDEFG",      # Apenas letras
        ""              # Vazio
    ]
