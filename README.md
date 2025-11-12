# Car Rental API

API REST para sistema de aluguel de carros desenvolvida com FastAPI e SQLite.

## Estrutura do Projeto

```
projeto/
|-- src/
|   |-- config/          # Configurações e banco de dados
|   |-- models/          # Modelos de dados
|   |-- repositories/    # Camada de acesso a dados
|   |-- services/        # Lógica de negócio
|   |-- controllers/     # Controladores da API
|   +-- utils/           # Utilitários e validadores
|-- tests/               # Testes automatizados
|-- main.py              # Aplicação principal
|-- requirements.txt     # Dependências
+-- .env.example         # Exemplo de variáveis de ambiente
```

## Funcionalidades

### Entidades
- **Carros**: Gerenciamento de veículos disponíveis para aluguel
- **Clientes**: Cadastro e gerenciamento de clientes
- **Aluguéis**: Controle de aluguéis com cálculo automático de valores
- **Pagamentos**: Gestão de pagamentos e inadimplências
- **Manutenções**: Controle de manutenções dos veículos

### Regras de Negócio
1. **Cálculo de Valor**: Descontos progressivos baseados no período de aluguel
   - 1-7 dias: valor integral
   - 8-14 dias: 10% de desconto
   - 15-30 dias: 15% de desconto
   - Acima de 30 dias: 20% de desconto

2. **Disponibilidade**: Carros não podem ser alugados se:
   - Estiverem marcados como indisponíveis
   - Possuírem manutenção ativa ou agendada

3. **Inadimplência**: Clientes com pagamentos pendentes não podem realizar novos aluguéis

## Instalação

```bash
# Crie um ambiente virtual
python -m venv venv

# Ative o ambiente virtual
source venv/Scripts/activate

# Instale as dependências
pip install -r requirements.txt

# Configure as variáveis de ambiente
cp .env.example .env
```

## Execução

```bash
# Iniciar o servidor
python main.py

# A API estará disponível em http://localhost:8000
# Documentação interativa: http://localhost:8000/docs
```

## Endpoints

### Carros
- POST /cars/ - Criar carro
- GET /cars/{id} - Buscar carro
- GET /cars/ - Listar carros
- GET /cars/available/search - Buscar carros disponíveis (com filtros)
- PUT /cars/{id} - Atualizar carro
- DELETE /cars/{id} - Remover carro

### Clientes
- POST /customers/ - Criar cliente
- GET /customers/{id} - Buscar cliente
- GET /customers/ - Listar clientes
- PUT /customers/{id} - Atualizar cliente
- DELETE /customers/{id} - Remover cliente

### Aluguéis
- POST /rentals/ - Criar aluguel
- GET /rentals/{id} - Buscar aluguel
- GET /rentals/ - Listar aluguéis
- GET /rentals/search/filter - Buscar aluguéis (com filtros)
- PUT /rentals/{id} - Atualizar aluguel
- POST /rentals/{id}/complete - Finalizar aluguel
- POST /rentals/{id}/cancel - Cancelar aluguel
- DELETE /rentals/{id} - Remover aluguel

### Pagamentos
- POST /payments/ - Criar pagamento
- GET /payments/{id} - Buscar pagamento
- GET /payments/ - Listar pagamentos
- GET /payments/rental/{rental_id} - Buscar pagamentos de um aluguel
- PUT /payments/{id} - Atualizar pagamento
- POST /payments/{id}/process - Processar pagamento
- DELETE /payments/{id} - Remover pagamento

### Manutenções
- POST /maintenances/ - Criar manutenção
- GET /maintenances/{id} - Buscar manutenção
- GET /maintenances/ - Listar manutenções
- GET /maintenances/car/{car_id} - Buscar manutenções de um carro
- PUT /maintenances/{id} - Atualizar manutenção
- POST /maintenances/{id}/complete - Finalizar manutenção
- DELETE /maintenances/{id} - Remover manutenção

## Tecnologias

- **FastAPI**: Framework web para construção da API
- **SQLite**: Banco de dados
- **Pydantic**: Validação de dados
- **Uvicorn**: Servidor ASGI
- **Pytest**: Framework de testes

## Desenvolvimento

O projeto foi desenvolvido seguindo os princípios de:
- Clean Architecture
- Repository Pattern
- Dependency Injection
- Type Hints
- Docstrings (Google Style)
