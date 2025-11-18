# Plano de Testes - Sistema de Aluguel de Carros

## 1. Objetivo

Este plano define a estratégia de testes para garantir a qualidade, confiabilidade e robustez do sistema de aluguel de carros, abrangendo diferentes níveis e técnicas de teste.

## 2. Escopo dos Testes

### 2.1 Módulos Testados
- Modelos de dados (Car, Customer, Rental, Payment, Maintenance)
- Repositórios (persistência e consultas)
- Serviços (regras de negócio)
- Controladores (API endpoints)
- Validadores (CPF, email, telefone, placas, datas)
- Utilitários (exportação de arquivos)

## 3. Níveis de Teste

### 3.1 Testes Unitários

#### 3.1.1 Modelos
**Objetivo:** Validar a criação, serialização e deserialização de entidades.

**Cobertura:**
- Criação de objetos com diferentes combinações de atributos
- Conversão para dicionário (to_dict)
- Criação a partir de dicionário (from_dict)
- Validação de atributos obrigatórios

**Entidades testadas:** Car, Customer, Rental, Payment, Maintenance

#### 3.1.2 Repositórios
**Objetivo:** Garantir operações CRUD e consultas especializadas funcionam corretamente.

**Cobertura:**
- Operações CREATE (criação de registros)
- Operações READ (busca por ID, listagem, filtros)
- Operações UPDATE (atualização completa e parcial)
- Operações DELETE (remoção de registros)
- Consultas especializadas (busca por placa, CPF, email, status)
- Tratamento de registros não encontrados

**Repositórios testados:** CarRepository, CustomerRepository, RentalRepository, PaymentRepository, MaintenanceRepository

#### 3.1.3 Serviços
**Objetivo:** Validar regras de negócio e lógica de aplicação.

**Cobertura CarService:**
- Criação de carros com validação de placa duplicada
- Verificação de disponibilidade (status + manutenções ativas)
- Atualização de disponibilidade

**Cobertura CustomerService:**
- Criação de clientes com validação de CPF e email únicos
- Verificação de status de pagamento
- Bloqueio de novos aluguéis para clientes inadimplentes

**Cobertura RentalService:**
- Cálculo de valor com descontos progressivos:
  - 7-14 dias: 10% desconto
  - 15-30 dias: 15% desconto
  - Mais de 30 dias: 20% desconto
- Criação de aluguéis com validações completas
- Finalização de aluguéis ativos
- Cancelamento de aluguéis
- Rejeição de operações em aluguéis finalizados

**Cobertura PaymentService:**
- Validação de métodos de pagamento (credit_card, debit_card, pix, cash)
- Processamento de pagamentos pendentes
- Atualização de status do cliente após pagamento

**Cobertura MaintenanceService:**
- Criação de manutenções com bloqueio de disponibilidade
- Conclusão de manutenções com liberação do carro

#### 3.1.4 Validadores
**Objetivo:** Garantir validação rigorosa de dados de entrada.

**Cobertura:**
- Validação de CPF (formato e dígitos verificadores)
- Validação de email (formato RFC-compliant)
- Validação de telefone (formatos brasileiro)
- Validação de placas (formato antigo e Mercosul)
- Validação de intervalos de datas (início < fim, não no passado)
- Validação de números positivos
- Validação de ano (1900 a ano atual + 1)

**Técnica:** Testes parametrizados com múltiplos casos válidos e inválidos

#### 3.1.5 Controladores
**Objetivo:** Validar mapeamento de requisições HTTP e tratamento de erros.

**Cobertura:**
- Conversão correta de dados de entrada
- Tratamento de exceções (404, 422, 500)
- Retorno de status HTTP apropriados
- Serialização de respostas

**Controladores testados:** CarController, CustomerController, RentalController, PaymentController, MaintenanceController

#### 3.1.6 Utilitários
**Objetivo:** Validar funcionalidades auxiliares.

**Cobertura FileExporter:**
- Exportação para JSON (incluindo caracteres especiais UTF-8)
- Exportação para CSV (validação de campos e encoding)
- Leitura de arquivos JSON e CSV
- Criação automática de diretórios
- Validação de dados vazios

### 3.2 Testes de Integração

**Objetivo:** Validar interação entre múltiplos componentes do sistema.

**Cenários testados:**

#### 3.2.1 Fluxo Completo de Aluguel
1. Criação de carro e cliente
2. Criação de aluguel (validações + cálculo de valor + bloqueio do carro)
3. Criação de pagamento
4. Processamento de pagamento
5. Finalização de aluguel (liberação do carro)

**Validações:** Status do carro alterado corretamente em cada etapa

#### 3.2.2 Prevenção de Dupla Reserva
- Tentativa de alugar carro já alugado deve falhar
- Validação de disponibilidade em tempo real

#### 3.2.3 Bloqueio por Inadimplência
- Cliente com pagamento pendente não pode fazer novos aluguéis
- Após pagamento, cliente é liberado

#### 3.2.4 Integração com Manutenção
- Carro com manutenção ativa não pode ser alugado
- Conclusão de manutenção libera o carro para aluguel

### 3.3 Testes Funcionais (Caixa-Preta)

**Objetivo:** Validar endpoints da API via HTTP, sem conhecimento da implementação interna.

**Cobertura por recurso:**

#### 3.3.1 Carros (/cars)
- POST: Criação com dados válidos e inválidos
- GET: Busca por ID (existente e inexistente)
- GET: Listagem completa
- GET: Busca com filtros (marca, preço máximo)
- PUT: Atualização de campos
- DELETE: Remoção e verificação de exclusão

#### 3.3.2 Clientes (/customers)
- POST: Criação com validação de CPF duplicado
- GET: Busca por ID
- GET: Listagem completa
- PUT: Atualização de dados
- DELETE: Remoção de cliente

#### 3.3.3 Aluguéis (/rentals)
- POST: Criação de aluguel válido
- GET: Busca por ID
- GET: Listagem e filtros por status/cliente
- POST: Finalização de aluguel (/complete)
- POST: Cancelamento de aluguel (/cancel)

#### 3.3.4 Pagamentos (/payments)
- POST: Criação de pagamento
- POST: Processamento de pagamento (/process)
- GET: Busca por ID
- GET: Listagem de pagamentos por aluguel

#### 3.3.5 Manutenções (/maintenances)
- POST: Criação de manutenção
- POST: Conclusão de manutenção (/complete)
- GET: Busca por ID
- GET: Listagem por carro

**Técnica:** TestClient do FastAPI com banco de dados isolado por teste

### 3.4 Testes Específicos

#### 3.4.1 Testes de Performance
**Objetivo:** Garantir que operações críticas atendem requisitos de tempo.

**Métricas monitoradas:**
- Tempo de validação de CPF (< 1ms por operação)
- Tempo de cálculo de valor de aluguel
- Throughput de validações em lote (100, 1000 operações)
- Performance de serialização de modelos (500 objetos)
- Escalabilidade com carga crescente

**Ferramenta:** pytest-benchmark

#### 3.4.2 Testes de Orientação a Objetos
**Objetivo:** Validar princípios de OOP e design patterns.

**Cobertura:**
- Herança (hierarquia Vehicle -> RentalCar -> PremiumCar)
- Polimorfismo (Strategy Pattern para cálculo de descontos)
- Encapsulamento (properties, atributos privados)
- Classes abstratas (BaseModel, DiscountStrategy)
- Composição (Rental referencia Car e Customer)
- Sobrescrita de métodos (to_dict, validate)

#### 3.4.3 Testes com Mocks e Stubs
**Objetivo:** Isolar componentes para testes focados.

**Técnicas aplicadas:**
- Mock de repositórios para testar serviços isoladamente
- Coordenação de múltiplos mocks (car_service + customer_service + repositories)
- Stubs parametrizados (diferentes métodos de pagamento)
- Patch de dependências externas (banco de dados)
- Simulação de erros (conexão BD, timeouts)
- Side effects para múltiplos comportamentos
- Verificação de chamadas e argumentos

**Ferramentas:** unittest.mock (Mock, patch, MagicMock)

#### 3.4.4 Testes de Mutação
**Objetivo:** Detectar mutações no código que não são detectadas pelos testes convencionais.

**Mutações testadas:**
- Operadores aritméticos (multiplicação -> adição)
- Operadores relacionais (> -> >=, != -> ==)
- Constantes numéricas (valores de desconto: 0.20 -> 0.19)
- Valores booleanos (True -> False em availability)
- Lógica de status (active -> completed)

**Componentes cobertos:** RentalService, RentalController, RentalRepository

**Ferramenta:** mutmut

## 4. Estratégia de Testes

### 4.1 Testes Parametrizados
Utilização de @pytest.mark.parametrize para:
- Testar múltiplos CPFs, emails, telefones, placas válidos e inválidos
- Validar diferentes períodos de aluguel e descontos
- Testar métodos de pagamento variados
- Verificar escalabilidade com diferentes cargas

### 4.2 Fixtures
Fixtures reutilizáveis para:
- Dados de teste (valid_cpfs, valid_emails, valid_phones, valid_license_plates)
- Instâncias de modelos (sample_car, sample_customer, sample_rental)
- Repositórios com banco de dados de teste
- Cliente de teste da API (TestClient)

### 4.3 Isolamento de Testes
- Banco de dados único por teste (UUID no nome do arquivo)
- Limpeza automática após cada teste (teardown)
- Mocks para evitar dependências externas
- Sem compartilhamento de estado entre testes

### 4.4 Cobertura de Código
**Meta:** Mínimo 90% de cobertura de linhas

**Áreas críticas com 100% de cobertura:**
- Validadores (segurança de dados)
- Cálculo de valores (precisão financeira)
- Regras de negócio (consistência do sistema)

## 5. Critérios de Aceitação

### 5.1 Testes Unitários
- Todos os testes devem passar
- Cobertura mínima de 80%
- Tempo de execução < 30 segundos

### 5.2 Testes de Integração
- Fluxos completos executam sem erros
- Validações de regras de negócio são respeitadas
- Transações mantêm consistência do banco

### 5.3 Testes Funcionais
- Todos os endpoints retornam códigos HTTP corretos
- Respostas JSON estão bem formatadas
- Validações de entrada funcionam adequadamente

### 5.4 Testes de Performance
- Operações críticas atendem SLAs definidos
- Escalabilidade linear comprovada
- Sem degradação com carga crescente

### 5.5 Testes de Mutação
- Score de mutação > 80%
- Mutações críticas são detectadas
- Cobertura de operadores e constantes

## 6. Ambiente de Testes

### 6.1 Ferramentas
- **Framework:** pytest
- **Cobertura:** pytest-cov
- **Performance:** pytest-benchmark
- **Mutação:** mutmut
- **Mocks:** unittest.mock
- **HTTP Client:** FastAPI TestClient

### 6.2 Banco de Dados
- SQLite em memória para testes unitários
- Arquivos temporários únicos para testes de integração/funcionais
- Limpeza automática após execução

### 6.3 Fixtures Globais
- Dados válidos pré-definidos (CPFs, emails, placas)
- Modelos de exemplo reutilizáveis
- Configuração de repositórios com banco de teste

## 7. Execução dos Testes

### 7.1 Comandos
```bash
# Todos os testes
pytest

# Com cobertura
pytest --cov=src --cov-report=html

# Apenas unitários
pytest tests/unit/

# Apenas integração
pytest tests/integration/

# Apenas funcionais
pytest tests/functional/

# Performance com benchmark
pytest tests/especific/test_performance.py --benchmark-only

# Testes de mutação
mutmut run
```