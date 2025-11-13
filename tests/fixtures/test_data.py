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
    """
    return [
        "ABC123",       # Muito curto
        "ABC12345",     # Muito longo
        "1234567",      # Apenas números
        "ABCDEFG",      # Apenas letras
        ""              # Vazio
    ]
