# Documentação do Projeto
## Sistema de Aluguel de Carros - API REST

## 1. Visão Geral do Projeto

### 1.1 Descrição

Sistema de gerenciamento de aluguel de carros desenvolvido como API REST utilizando FastAPI e SQLite. O sistema implementa regras de negócio para cálculo de descontos progressivos, controle de disponibilidade de veículos, gestão de inadimplência e manutenções.

### 1.2 Objetivos

**Objetivo Principal:**
Desenvolver uma API REST robusta, testável e bem documentada para gerenciamento de aluguel de carros.

**Objetivos Específicos:**
- Implementar CRUD completo para todas as entidades
- Aplicar regras de negócio complexas (descontos, disponibilidade)
- Garantir qualidade através de testes automatizados
- Atingir alta cobertura de código (>80%)
- Demonstrar aplicação prática de conceitos de teste de software

---

## 2. Arquitetura

### 2.1 Padrões Arquiteturais

O projeto segue os princípios de **Clean Architecture** e utiliza o **Repository Pattern**:

```
┌─────────────────────────────────────────┐
│          Controllers (API)              │
│  Endpoints HTTP / Validação Request     │
└────────────────┬────────────────────────┘
                 │
┌────────────────▼────────────────────────┐
│            Services                     │
│   Lógica de Negócio / Regras            │
└────────────────┬────────────────────────┘
                 │
┌────────────────▼────────────────────────┐
│         Repositories                    │
│   Acesso a Dados / Persistência         │
└────────────────┬────────────────────────┘
                 │
┌────────────────▼────────────────────────┐
│        Database (SQLite)                │
│      Persistência de Dados              │
└─────────────────────────────────────────┘
```

---

## 3. Entidades e Modelos de Dados

### 3.1 Car (Carro)

| Campo | Tipo | Descrição |
|-------|------|-----------|
| id | int | Identificador único |
| license_plate | str | Placa do veículo (único) |
| brand | str | Marca |
| model | str | Modelo |
| year | int | Ano de fabricação |
| category | str | Categoria (sedan, suv, etc.) |
| daily_rate | float | Valor da diária (R$) |
| available | bool | Disponibilidade |

### 3.2 Customer (Cliente)

| Campo | Tipo | Descrição |
|-------|------|-----------|
| id | int | Identificador único |
| name | str | Nome completo |
| cpf | str | CPF (único, validado) |
| email | str | Email (único, validado) |
| phone | str | Telefone |
| address | str | Endereço |
| has_pending_payment | bool | Indicador de inadimplência |

### 3.3 Rental (Aluguel)

| Campo | Tipo | Descrição |
|-------|------|-----------|
| id | int | Identificador único |
| car_id | int | ID do carro |
| customer_id | int | ID do cliente |
| start_date | date | Data de início |
| end_date | date | Data de término |
| total_days | int | Total de dias |
| daily_rate | float | Valor da diária |
| discount_percentage | float | Percentual de desconto |
| total_value | float | Valor total |
| status | str | Status (active, completed, cancelled) |

### 3.4 Payment (Pagamento)

| Campo | Tipo | Descrição |
|-------|------|-----------|
| id | int | Identificador único |
| rental_id | int | ID do aluguel |
| amount | float | Valor |
| payment_date | date | Data do pagamento |
| payment_method | str | Método (credit, debit, cash) |
| status | str | Status (pending, processed, cancelled) |

### 3.5 Maintenance (Manutenção)

| Campo | Tipo | Descrição |
|-------|------|-----------|
| id | int | Identificador único |
| car_id | int | ID do carro |
| description | str | Descrição da manutenção |
| scheduled_date | date | Data agendada |
| completion_date | date | Data de conclusão |
| cost | float | Custo |
| status | str | Status (scheduled, in_progress, completed) |

---

## 4. Regras de Negócio

### 4.1 Cálculo de Descontos

Sistema de descontos progressivos baseado no período de aluguel:

| Período (dias) | Desconto | Cálculo |
|----------------|----------|---------|
| 1 - 7 | 0% | total_days × daily_rate |
| 8 - 14 | 10% | total_days × daily_rate × 0.90 |
| 15 - 30 | 15% | total_days × daily_rate × 0.85 |
| > 30 | 20% | total_days × daily_rate × 0.80 |

**Exemplo:**
- Carro: R$ 100/dia
- Período: 10 dias
- Cálculo: 10 × 100 × 0.90 = R$ 900,00

### 4.2 Disponibilidade de Carros

Um carro NÃO pode ser alugado se:

1. **Status indisponível:** `car.available = False`
2. **Manutenção ativa:** Existe manutenção com status "in_progress"
3. **Manutenção agendada:** Existe manutenção com status "scheduled" para o período

### 4.3 Inadimplência

Cliente com pagamento pendente NÃO pode realizar novo aluguel.

### 4.4 Finalização de Aluguel

Ao finalizar aluguel:
1. Status do aluguel → "completed"
2. Carro volta a ficar disponível (available = True)
3. Cliente pode fazer novo aluguel (se pagamento OK)

---

## 5. Stack Tecnológico

### 5.1 Backend

| Tecnologia | Versão | Finalidade |
|------------|--------|------------|
| **Python** | 3.10+ | Linguagem de programação |
| **FastAPI** | 0.121.1 | Framework web/API |
| **Uvicorn** | 0.38.0 | Servidor ASGI |
| **Pydantic** | 2.12.4 | Validação de dados |
| **SQLite** | 3.x | Banco de dados |

### 5.2 Testes

| Tecnologia | Versão | Finalidade |
|------------|--------|------------|
| **pytest** | 9.0.0 | Framework de testes |
| **pytest-cov** | 7.0.0 | Cobertura de código |
| **pytest-mock** | 3.15.1 | Mocking e stubbing |
| **httpx** | 0.28.1 | Client HTTP para testes de API |
| **mutmut** | 3.3.1 | Testes de mutação |

---

## 6. Qualidade e Testes

### 6.1 Estratégia de Testes

Abordagem em **Pirâmide de Testes**:

```
            /\
           /  \  29 Testes Funcionais (API)
          /____\
         /      \
        / 9 IT  \ 9 Testes de Integração
       /__________\
      /            \
     /  154 UNIT   \ 154 Testes Unitários
    /________________\
```

### 6.2 Métricas de Qualidade Alcançadas

| Métrica | Meta | Alcançado | Status |
|---------|------|-----------|--------|
| **Testes Totais** | 210 | 213 | ✓ |
| **Taxa de Aprovação** | 95% | 100% | ✓ |
| **Cobertura de Linhas** | 80% | 81.45% | ✓ |
| **Cobertura de Branches** | 75% | 78.62% | ✓ |
| **Defeitos Críticos** | 0 | 0 | ✓ |
| **Tempo de Execução** | <10min | 6.04s | ✓ |

---

## 7. API Endpoints

### 7.1 Documentação Interativa

**Swagger UI:** `http://localhost:8000/docs`
**ReDoc:** `http://localhost:8000/redoc`

### 7.2 Resumo de Endpoints

| Recurso | Total | POST | GET | PUT | DELETE |
|---------|-------|------|-----|-----|--------|
| **/cars** | 6 | 1 | 4 | 1 | 1 |
| **/customers** | 5 | 1 | 2 | 1 | 1 |
| **/rentals** | 7 | 2 | 3 | 1 | 1 |
| **/payments** | 6 | 2 | 3 | 1 | 1 |
| **/maintenances** | 6 | 2 | 3 | 1 | 1 |
| **TOTAL** | **30** | - | - | - | - |

---

## 8. Instalação e Execução

### 8.1 Requisitos

- Python 3.10 ou superior
- pip (gerenciador de pacotes)
- Git

### 8.2 Instalação

```bash
# Clonar repositório
git clone https://github.com/usuario/cc8550.git
cd cc8550

# Criar ambiente virtual
python -m venv venv

# Ativar ambiente (Windows)
venv\Scripts\activate

# Ativar ambiente (Linux/Mac)
source venv/bin/activate

# Instalar dependências
pip install -r requirements.txt
```

### 8.3 Execução

**Iniciar API:**
```bash
python main.py
```

**Acessar documentação:**
- Swagger: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

**Executar testes:**
```bash
# Todos os testes
pytest

# Com cobertura
pytest --cov=src --cov-report=html

# Apenas unitários
pytest tests/unit/
```