# Testes Avançados

Este diretório contém testes especializados que demonstram técnicas avançadas de teste de software.

## Estrutura

### 1. Testes com Mocks e Stubs ([test_mocks_stubs.py](test_mocks_stubs.py))
**9 testes** que demonstram isolamento de dependências externas.

#### Técnicas Implementadas:
- **Mock de Repositórios**: Isolamento da lógica de serviço do acesso a dados
- **Stub de Respostas**: Simulação de diferentes cenários de resposta
- **Patch de Dependências Externas**: Mock de banco de dados e APIs
- **Verificação de Chamadas**: Validação de interações com mocks
- **Simulação de Erros**: Timeout, conexão falha, falhas parciais

#### Classes de Teste:
- `TestRepositoryMocking`: Mocking básico de repositórios (2 testes)
- `TestStubbing`: Uso de stubs para respostas (4 testes)
- `TestExternalDependencyMocking`: Mock de dependências externas com @patch (1 teste)
- `TestErrorScenarioMocking`: Simulação de cenários de erro (2 testes)

### 2. Testes de Performance ([test_performance.py](test_performance.py))
**10 testes** que medem e validam performance do sistema.

#### Técnicas Implementadas:
- **Benchmark com pytest-benchmark**: Medição precisa de tempo de execução
- **Testes com Grandes Volumes**: Validação com 1000+ operações
- **Comparação de Implementações**: Análise de diferentes abordagens
- **Restrições de Tempo**: Validação de SLA de performance
- **Testes de Escalabilidade**: Comportamento com carga crescente

#### Classes de Teste:
- `TestBasicPerformance`: Performance de operações básicas (2 testes)
- `TestBulkOperationsPerformance`: Operações em lote (2 testes)
- `TestLargeDatasetPerformance`: Grande volume de dados (2 testes)
- `TestTimingConstraints`: Validação de restrições de tempo (4 testes)

#### Exemplos de Métricas:
- Validação de CPF: ~3μs por operação
- Cálculo de aluguel: ~103μs por operação
- Validação em lote (100 CPFs): ~299μs total
- Serialização (500 objetos): ~104μs por objeto

### 3. Testes de Orientação a Objetos ([test_oop.py](test_oop.py))
**12 testes** que validam conceitos de OOP.

#### Técnicas Implementadas:
- **Herança**: Hierarquias de classes em múltiplos níveis
- **Polimorfismo**: Strategy Pattern e sobrescrita de métodos
- **Encapsulamento**: Properties e atributos privados
- **Classes Abstratas**: ABC e métodos abstratos
- **Composição vs Herança**: Diferentes padrões de design

#### Hierarquia de Classes Criada:
```
BaseModel (abstract)
└── Vehicle (abstract)
    └── RentalCar
        └── PremiumCar

DiscountStrategy (abstract)
├── NoDiscount
├── StandardDiscount
└── VIPDiscount
```

#### Classes de Teste:
- `TestInheritance`: Validação de herança correta (2 testes)
- `TestPolymorphism`: Polimorfismo e sobrescrita (2 testes)
- `TestEncapsulation`: Acesso a atributos (2 testes)
- `TestAbstractClasses`: Classes abstratas e interfaces (3 testes)
- `TestComposition`: Composição vs Herança (1 teste)
- `TestOOPValidation`: Validação OOP (2 testes)

## Executar os Testes

### Todos os testes avançados:
```bash
pytest tests/advanced/ -v
```

### Apenas Mocks:
```bash
pytest tests/advanced/test_mocks_stubs.py -v
```

### Apenas Performance (com benchmark):
```bash
pytest tests/advanced/test_performance.py --benchmark-only
```

### Apenas OOP:
```bash
pytest tests/advanced/test_oop.py -v
```

## Estatísticas

- **Total de Testes Avançados**: 31 (reduzido de 60)
- **Taxa de Sucesso**: 100%
- **Tipos de Teste**: 3 (Mocks, Performance, OOP)
- **Frameworks Utilizados**: unittest.mock, pytest-benchmark, ABC
- **Redução**: ~50% mantendo os testes mais relevantes

## Pontos Fortes

1. **Isolamento Completo**: Testes não dependem de BD ou APIs externas
2. **Métricas de Performance**: Validação quantitativa de tempo de execução
3. **Conceitos OOP Avançados**: Demonstração de boas práticas
4. **Testes Essenciais**: Mantém apenas os mais representativos de cada técnica
5. **Documentação Clara**: Cada teste explica o que está validando

## Tecnologias

- **Python 3.13**
- **pytest 9.0.0**
- **pytest-benchmark 5.2.3**
- **unittest.mock** (built-in)
- **ABC - Abstract Base Classes** (built-in)

## Integração com CI/CD

Estes testes podem ser executados em pipeline CI/CD:

```yaml
# Exemplo GitHub Actions
- name: Run Advanced Tests
  run: |
    pytest tests/advanced/ -v --benchmark-skip
```

Para ambientes de performance testing:
```yaml
- name: Performance Tests
  run: |
    pytest tests/advanced/test_performance.py --benchmark-only --benchmark-json=output.json
```
