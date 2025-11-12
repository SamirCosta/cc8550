class RentalException(Exception):
    """
    Exceção base para todas as exceções do sistema de aluguel.

    Attributes:
        message: Mensagem de erro descritiva
        code: Código de erro HTTP associado
    """

    def __init__(self, message: str, code: int = 500) -> None:
        self.message = message
        self.code = code
        super().__init__(self.message)


class NotFoundException(RentalException):
    """
    Exceção lançada quando um recurso não é encontrado.

    Utilizada quando uma entidade (car, customer, rental, etc)
    não é encontrada no banco de dados.
    """

    def __init__(self, message: str = "Resource not found") -> None:
        super().__init__(message, code=404)


class ValidationException(RentalException):
    """
    Exceção lançada quando há erro de validação de dados.

    Utilizada para validações de entrada como CPF inválido,
    email malformado, datas inconsistentes, etc.
    """

    def __init__(self, message: str = "Validation error") -> None:
        super().__init__(message, code=400)


class BusinessRuleException(RentalException):
    """
    Exceção lançada quando uma regra de negócio é violada.

    Utilizada para situações como tentativa de alugar carro
    indisponível, cliente com pagamento pendente, etc.
    """

    def __init__(self, message: str = "Business rule violation") -> None:
        super().__init__(message, code=422)


class DatabaseException(RentalException):
    """
    Exceção lançada quando há erro de banco de dados.

    Utilizada para erros de conexão, constraint violations,
    e outros problemas relacionados ao banco de dados.
    """

    def __init__(self, message: str = "Database error") -> None:
        super().__init__(message, code=500)
