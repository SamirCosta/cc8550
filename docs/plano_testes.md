# Plano de Teste
## Sistema de Aluguel de Carros - API REST

## 1. Introdução

### 1.1 Definição

Documento estratégico que define a abordagem geral de testes para a API REST de aluguel de carros. Este plano estabelece a visão macro do projeto de testes, diferenciando-se do Ciclo de Vida de Testes (STLC) por ser estático e estratégico, enquanto o STLC é dinâmico e executivo.

---

## 2. Escopo e Objetivos

### 2.1 Objetivo Principal

Garantir que o sistema de aluguel de carros funcione corretamente, seja seguro, confiável e atenda aos requisitos de negócio antes da implantação em produção.

### 2.2 Objetivos Específicos

#### Funcionalidade
- 95% dos casos de teste funcionais aprovados
- 100% das features principais testadas
- Validação completa das regras de negócio

#### Performance
- Tempo de resposta < 200ms para 90% das requisições
- Suporte a 100 requisições simultâneas
- Taxa de sucesso > 99.5%

#### Segurança
- Zero vulnerabilidades críticas
- Validação de entrada em todos os endpoints
- Tratamento adequado de erros

#### Cobertura
- Cobertura de código ≥ 80%
- Cobertura de branches ≥ 75%
- Testes de mutação com score ≥ 70%

---

## 3. Componentes do Plano

### 3.1 Escopo e Objetivos

**Funcionalidades:**
- Gerenciamento de carros (CRUD)
- Gerenciamento de clientes (CRUD)
- Sistema de aluguéis com cálculo de descontos
- Controle de pagamentos
- Gestão de manutenções
- Validação de regras de negócio
- Tratamento de exceções

**Tipos de Teste:**
- Testes unitários
- Testes de integração
- Testes funcionais (API)
- Testes de mutação
- Testes de cobertura

### 3.2 Estratégias de Teste

#### Abordagem Geral

Abordagem em pirâmide de testes:
1. Base: Testes unitários
2. Meio: Testes de integração
3. Topo: Testes funcionais

#### Testes Unitários
- **Técnica:** Testes isolados de cada componente
- **Cobertura:** Repositories, Services, Models
- **Ferramenta:** Pytest

#### Testes de Integração
- **Técnica:** Testes de interação entre componentes
- **Foco:** Repository + Service, Service + Controller
- **Ferramenta:** Pytest com fixtures

#### Testes Funcionais (API)
- **Técnica:** Testes de endpoints completos
- **Método:** HTTP requests via TestClient
- **Ferramenta:** Pytest + FastAPI TestClient

#### Testes de Mutação
- **Técnica:** Mutação de código para validar qualidade dos testes
- **Ferramenta:** mutmut
- **Meta:** Score ≥ 70%

### 3.3 Critérios de Entrada e Saída

#### Critérios de Entrada

Para iniciar uma fase de testes:
- Código desenvolvido e revisado
- Ambiente de testes configurado
- Banco de dados de testes disponível
- Dependências instaladas
- Documentação técnica atualizada

#### Critérios de Saída

Para concluir uma fase de testes:
- 100% dos testes executados
- Taxa de aprovação ≥ 95%
- Zero defeitos críticos
- Zero defeitos de alta prioridade
- Cobertura de código ≥ 80%
- Documentação de testes completa

### 3.5 Recursos

#### Equipe

| Função | Quantidade | Dedicação |
|--------|------------|-----------|
| Test Manager | 1 | 50% |
| QA Analysts | 2 | 100% |
| Developers (suporte) | 3 | 20% |

#### Ferramentas

| Categoria | Ferramenta | Custo |
|-----------|------------|-------|
| **Framework de Teste** | Pytest | Gratuito |
| **Cobertura** | pytest-cov | Gratuito |
| **Mutação** | mutmut | Gratuito |
| **API Testing** | httpx | Gratuito |
| **Mock** | pytest-mock | Gratuito |

#### Infraestrutura

| Recurso | Especificação |
|---------|---------------|
| **Ambiente de Testes** | Local + GitHub Actions |
| **Banco de Dados** | SQLite em memória |
| **Servidor** | Uvicorn (local) |

### 3.6 Ambiente de Testes

#### Configuração de Desenvolvimento

```
- Sistema Operacional: Windows/Linux/macOS
- Python: 3.10+
- Banco de Dados: SQLite (in-memory para testes)
- Framework Web: FastAPI 0.121.1
- Servidor: Uvicorn
```

#### Configuração de CI/CD

```
- Plataforma: GitHub Actions
- Python: 3.10
- Execução automática: A cada push
- Relatórios: Coverage reports automáticos
```

### 3.7 Métricas de Qualidade

#### Cobertura de Testes

| Métrica | Meta |
|---------|------|
| **Cobertura de Linhas** | ≥ 80% |
| **Cobertura de Branches** | ≥ 75% |
| **Testes Unitários** | > 100 |
| **Testes Integração** | > 30 |
| **Testes Funcionais** | > 50 |

#### Taxa de Mutação

| Métrica | Meta |
|---------|------|
| **Mutation Score** | ≥ 70% |
| **Mutantes Mortos** | ≥ 14 |
| **Mutantes Sobreviventes** | < 30% |

---

## 4. Estratégia de Teste por Componente

### 4.1 Models

**Objetivo:** Validar estrutura, validações e regras de negócio

**Abordagem:**
- Testes de validação de campos obrigatórios
- Testes de validação de tipos
- Testes de validação de formatos (email, telefone, CPF)
- Testes de valores padrão

**Prioridade:** Alta

### 4.2 Repositories

**Objetivo:** Validar operações CRUD e consultas ao banco

**Abordagem:**
- Testes de criação de registros
- Testes de leitura (busca por ID, listagem, filtros)
- Testes de atualização
- Testes de exclusão
- Testes de consultas complexas

**Prioridade:** Alta

### 4.3 Services

**Objetivo:** Validar regras de negócio e processamento

**Abordagem:**
- Testes de cálculo de desconto (1-7, 8-14, 15-30, >30 dias)
- Testes de validação de disponibilidade
- Testes de validação de inadimplência
- Testes de regras de manutenção
- Testes de exceções de negócio

**Prioridade:** Muito Alta

### 4.4 Controllers

**Objetivo:** Validar interface HTTP e integração completa

**Abordagem:**
- Testes de status HTTP corretos
- Testes de payload de resposta
- Testes de validação de entrada
- Testes de tratamento de erros
- Testes de autenticação (se aplicável)

**Prioridade:** Alta

---

## 5. Cenários de Teste Principais

### 5.1 Fluxo de Aluguel Completo

```
1. Criar cliente
2. Criar carro
3. Verificar disponibilidade
4. Criar aluguel
5. Validar cálculo de valor
6. Processar pagamento
7. Finalizar aluguel
```

### 5.2 Validação de Regras de Desconto

```
Cenário 1: Aluguel de 5 dias → Sem desconto
Cenário 2: Aluguel de 10 dias → 10% desconto
Cenário 3: Aluguel de 20 dias → 15% desconto
Cenário 4: Aluguel de 35 dias → 20% desconto
```

### 5.3 Validação de Disponibilidade

```
Cenário 1: Carro disponível → Aluguel permitido
Cenário 2: Carro indisponível → Aluguel bloqueado
Cenário 3: Carro em manutenção → Aluguel bloqueado
Cenário 4: Carro com manutenção agendada → Aluguel bloqueado
```

### 5.4 Validação de Inadimplência

```
Cenário 1: Cliente sem pendências → Aluguel permitido
Cenário 2: Cliente com pagamento pendente → Aluguel bloqueado
Cenário 3: Cliente com pagamento processado → Aluguel permitido
```