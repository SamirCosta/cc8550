# Guia de Testes - Car Rental API

Este documento descreve como executar os diferentes tipos de testes implementados no projeto.

## Estrutura de Testes

```
tests/
|-- conftest.py              # Fixtures compartilhadas (legado)
|-- fixtures/                # Fixtures organizadas por categoria 
|   |-- __init__.py         # Exporta todas as fixtures
|   |-- conftest.py         # Configura fixtures para pytest
|   |-- database.py         # Fixtures de banco de dados
|   |-- repositories.py     # Fixtures de repositórios
|   |-- models.py           # Fixtures de modelos (sample + created)
|   |-- test_data.py        # Fixtures de dados para parametrização
|   |-- test_fixtures.py    # Testes das fixtures (28 testes)
|   +-- README.md           # Documentação completa
|-- unit/                    # Testes unitários (101+ testes)
|   |-- test_models.py
|   |-- test_validators.py
|   |-- test_repositories.py
|   |-- test_services.py
|   +-- test_file_export.py
|-- integration/             # Testes de integração (10+ testes)
|   +-- test_rental_flow.py
|-- functional/              # Testes funcionais/API (30+ testes)
|   +-- test_api_endpoints.py
+-- mutation/                # Testes de mutação (21 testes) 
    |-- test_mutation_killers.py
    |-- mutation_tests.py
    |-- MUTATION_TESTING_REPORT.md
    |-- MUTATION_TESTING_SUMMARY.md
    +-- README.md
```

## Pré-requisitos

```bash
pip install -r requirements.txt
```

##  Fixtures

O projeto possui um sistema organizado de fixtures para reutilização em testes. As fixtures estão categorizadas em módulos para melhor manutenção:

### Categorias de Fixtures

1. **Database** - Banco de dados limpo para cada teste
2. **Repositories** - Repositórios já configurados com banco de teste
3. **Models** - Objetos de exemplo (sample_*) e objetos criados no banco (create_test_*)
4. **Test Data** - Listas de dados para testes parametrizados

### Uso de Fixtures

```python
def test_car_creation(car_repository, sample_car):
    """As fixtures são injetadas automaticamente pelo pytest."""
    created_car = car_repository.create(sample_car)
    assert created_car.id is not None
```

### Executar Testes das Fixtures

```bash
# Testar todas as fixtures
pytest tests/fixtures/test_fixtures.py -v

# Total: 28 testes validando fixtures
```

**Para mais detalhes:** [tests/fixtures/README.md](fixtures/README.md)

## Executando os Testes

### 1. Testes Unitários

Testa funções e métodos isoladamente com mocks:

```bash
pytest tests/unit/ -v
```

**Cobertura:** Validators, Models, Repositories, Services
**Total:** 30+ casos de teste

### 2. Testes de Integração

Testa interações entre módulos e banco de dados:

```bash
pytest tests/integration/ -v
```

**Cobertura:** Fluxos completos de aluguel, manutenção, pagamento
**Total:** 10+ casos de teste

### 3. Testes Funcionais (Caixa-Preta)

Testa a API sem conhecer a implementação:

```bash
pytest tests/functional/ -v
```

**Cobertura:** Todos os endpoints da API REST
**Total:** 8+ cenários funcionais

### 4. Executar Todos os Testes

```bash
pytest -v
```

## Cobertura de Código

### Executar com Cobertura

```bash
pytest --cov=src --cov-report=html --cov-report=term-missing
```

### Visualizar Relatório HTML

```bash
# O relatório será gerado em htmlcov/index.html
# Abra no navegador para ver detalhes
```

### Meta de Cobertura

- **Objetivo:** Mínimo 80% de cobertura
- **Branches:** Incluído na análise
- **Arquivos Principais:** Services, Repositories, Utils

## Testes de Mutação 

Os testes de mutação avaliam a qualidade dos testes automatizados introduzindo pequenas alterações (mutações) no código.

### Executar Testes de Mutação

```bash
# Executar mutation killers (21 testes específicos)
pytest tests/mutation/test_mutation_killers.py -v

# Executar com cobertura
pytest tests/mutation/test_mutation_killers.py --cov=src --cov-report=html

# Executar análise manual (Windows-compatible)
python tests/mutation/mutation_tests.py
```

### Documentação Completa

```bash
# Relatório detalhado (14 páginas)
start tests/mutation/MUTATION_TESTING_REPORT.md

# Sumário executivo (4 páginas)
start tests/mutation/MUTATION_TESTING_SUMMARY.md

# Guia específico de mutation testing
start tests/mutation/README.md
```

### Resultados

- **Taxa de Eliminação:** 89.4% (meta: ≥80%) 
- **Cobertura Total:** 80.64%
- **Mutações Analisadas:** 104 em 4 módulos críticos
- **Qualidade:**  Excelente

### Módulos Testados com Mutação

- `src/services/` - Lógica de negócio
- `src/repositories/` - Acesso a dados
- `src/utils/validators.py` - Validações

## Tipos de Testes Implementados

###  Testes Unitários (25%)
- Testes de Models
- Testes de Validators (parametrizados)
- Testes de Repositories
- Testes de Services (com mocks)
- Uso de fixtures
- Parametrização com pytest.mark.parametrize

###  Testes de Integração (20%)
- Fluxo completo de aluguel
- Prevenção de double booking
- Validação de pagamento pendente
- Manutenção bloqueando aluguel
- Cálculo de descontos progressivos

###  Testes Funcionais (15%)
- CRUD de Carros via API
- CRUD de Clientes via API
- Criação e finalização de Aluguéis
- Processamento de Pagamentos
- Gerenciamento de Manutenções
- Validação de regras de negócio

###  Testes Estruturais (15%)
- Configuração de cobertura
- Relatório HTML
- Meta de 80% de cobertura
- Cobertura de branches

###  Testes de Mutação (10%)
- Configuração do mutmut
- Aplicação em 3+ módulos
- Análise de mutantes

###  Testes Específicos (15%)
- Testes de API/REST
- Testes de Exceções
- Testes com Mocks e Stubs

## Comandos Úteis

```bash
# Executar apenas testes de uma classe
pytest tests/unit/test_validators.py::TestCPFValidator -v

# Executar testes por marcador
pytest -m unit -v

# Executar com saída detalhada
pytest -vv

# Executar e parar no primeiro erro
pytest -x

# Executar testes que falharam na última execução
pytest --lf

# Ver duração dos testes mais lentos
pytest --durations=10

# Executar com relatório de cobertura simples
pytest --cov=src --cov-report=term
```

## Fixtures Disponíveis

### Banco de Dados
- `test_db` - Banco SQLite limpo para cada teste
- `car_repository`, `customer_repository`, etc. - Repositórios configurados

### Dados de Exemplo
- `sample_car` - Carro de exemplo
- `sample_customer` - Cliente de exemplo
- `sample_rental` - Aluguel de exemplo
- `sample_payment` - Pagamento de exemplo
- `sample_maintenance` - Manutenção de exemplo

### Dados Criados
- `create_test_car` - Carro criado no banco
- `create_test_customer` - Cliente criado no banco
- `create_test_rental` - Aluguel criado no banco

### Parametrização
- `valid_cpfs` - Lista de CPFs válidos
- `invalid_cpfs` - Lista de CPFs inválidos
- `valid_emails` - Lista de emails válidos
- `invalid_emails` - Lista de emails inválidos

## Regras de Negócio Testadas

1. **Cálculo de Desconto:**
   - 1-7 dias: 0%
   - 8-14 dias: 10%
   - 15-30 dias: 15%
   - 30+ dias: 20%

2. **Disponibilidade de Carro:**
   - Não pode estar alugado
   - Não pode ter manutenção ativa

3. **Validação de Cliente:**
   - CPF único
   - Email único
   - Sem pagamentos pendentes para alugar

4. **Validações de Dados:**
   - CPF com dígitos verificadores
   - Email no formato correto
   - Placas válidas (antigo e Mercosul)
   - Datas válidas

## Resultados Esperados

Ao executar `pytest --cov=src --cov-report=term-missing`, você deve ver:

```
=================== test session starts ===================
collected 60+ items

tests/unit/test_models.py ............          [ 20%]
tests/unit/test_validators.py .................  [ 50%]
tests/unit/test_repositories.py ...............  [ 75%]
tests/unit/test_services.py ................... [ 90%]
tests/integration/test_rental_flow.py ......... [ 95%]
tests/functional/test_api_endpoints.py ........ [100%]

---------- coverage: platform win32, python 3.x -----------
Name                              Stmts   Miss  Cover   Missing
---------------------------------------------------------------
src/models/car.py                    25      0   100%
src/models/customer.py               25      0   100%
src/utils/validators.py              45      2    96%   45-46
src/services/rental_service.py       89      7    92%
src/services/car_service.py          67      5    93%
...
---------------------------------------------------------------
TOTAL                              1247     89    93%
```

## Troubleshooting

### Erro: "No module named 'src'"
```bash
# Certifique-se de estar no diretório raiz do projeto
cd cc8550
pytest
```

### Erro: "database is locked"
```bash
# Limpe arquivos de teste antigos
rm test_rental.db
pytest
```

### Baixa cobertura em um módulo
```bash
# Execute com relatório detalhado
pytest --cov=src --cov-report=html
# Abra htmlcov/index.html e veja as linhas não cobertas
```
