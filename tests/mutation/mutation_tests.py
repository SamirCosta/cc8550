"""
Script para análise manual de testes de mutação.

Este script demonstra o conceito de testes de mutação aplicados
aos módulos principais do projeto.
"""
import subprocess
import tempfile
import shutil
import os
from pathlib import Path


class MutationTester:
    """
    Classe para executar testes de mutação manuais.
    """

    MUTATIONS = {
        'arithmetic_operators': [
            ('+', '-'),
            ('-', '+'),
            ('*', '/'),
            ('/', '*'),
            ('%', '*'),
        ],
        'comparison_operators': [
            ('>', '>='),
            ('>=', '>'),
            ('<', '<='),
            ('<=', '<'),
            ('==', '!='),
            ('!=', '=='),
        ],
        'logical_operators': [
            ('and', 'or'),
            ('or', 'and'),
            ('not ', ''),
        ],
        'constants': [
            ('True', 'False'),
            ('False', 'True'),
            ('0', '1'),
            ('1', '0'),
        ],
    }

    def __init__(self, file_path: str):
        self.file_path = file_path
        self.original_content = self._read_file()
        self.mutations_applied = 0
        self.mutations_killed = 0
        self.mutations_survived = 0

    def _read_file(self) -> str:
        """Lê o conteúdo do arquivo."""
        with open(self.file_path, 'r', encoding='utf-8') as f:
            return f.read()

    def _write_file(self, content: str):
        """Escreve conteúdo no arquivo."""
        with open(self.file_path, 'w', encoding='utf-8') as f:
            f.write(content)

    def _run_tests(self) -> bool:
        """Executa os testes e retorna True se todos passaram."""
        try:
            result = subprocess.run(
                ['pytest', '-q', '--tb=no'],
                capture_output=True,
                timeout=60
            )
            return result.returncode == 0
        except Exception:
            return False

    def apply_mutation(self, old: str, new: str) -> bool:
        """
        Aplica uma mutação ao arquivo.
        Retorna True se a mutação foi aplicada.
        """
        content = self._read_file()
        if old in content:
            mutated = content.replace(old, new, 1)
            self._write_file(mutated)
            return True
        return False

    def restore_original(self):
        """Restaura o conteúdo original do arquivo."""
        self._write_file(self.original_content)

    def test_mutations(self, mutation_type: str = 'all'):
        """
        Testa mutações de um tipo específico ou todas.
        """
        print(f"\n{'='*70}")
        print(f"Testando mutações em: {self.file_path}")
        print(f"{'='*70}\n")

        # Verifica se os testes passam no código original
        print("Executando testes no código original...")
        if not self._run_tests():
            print("ERRO: Testes falharam no código original!")
            return
        print("Testes passaram no código original\n")

        # Aplica mutações
        mutation_types = [mutation_type] if mutation_type != 'all' else self.MUTATIONS.keys()

        for mut_type in mutation_types:
            if mut_type not in self.MUTATIONS:
                continue

            print(f"\n--- Testando {mut_type.replace('_', ' ').title()} ---")

            for old, new in self.MUTATIONS[mut_type]:
                # Aplica mutação
                if not self.apply_mutation(old, new):
                    continue

                self.mutations_applied += 1

                # Executa testes
                print(f"  Mutação {self.mutations_applied}: '{old}' → '{new}'", end=' ')

                if self._run_tests():
                    print("SOBREVIVEU")
                    self.mutations_survived += 1
                else:
                    print("MORTO")
                    self.mutations_killed += 1

                # Restaura original
                self.restore_original()

        self._print_report()

    def _print_report(self):
        """Imprime relatório final."""
        print(f"\n{'='*70}")
        print("RELATÓRIO DE MUTAÇÕES")
        print(f"{'='*70}")
        print(f"Total de mutações aplicadas: {self.mutations_applied}")
        print(f"Mutações mortas (testes falharam): {self.mutations_killed}")
        print(f"Mutações sobreviventes (testes passaram): {self.mutations_survived}")

        if self.mutations_applied > 0:
            kill_rate = (self.mutations_killed / self.mutations_applied) * 100
            print(f"\nTaxa de eliminação: {kill_rate:.1f}%")

            if kill_rate >= 80:
                print("Excelente cobertura de testes!")
            elif kill_rate >= 60:
                print("Boa cobertura, mas pode melhorar")
            else:
                print("Cobertura fraca - adicione mais testes")
        print(f"{'='*70}\n")


def analyze_mutation_coverage(file_path: str):
    """
    Analisa a cobertura de mutações para um arquivo específico.
    """
    tester = MutationTester(file_path)
    tester.test_mutations('all')


def generate_mutation_report():
    """
    Gera relatório de análise de mutação para os principais módulos.
    """
    print("""
+=====================================================================+
|              RELATÓRIO DE TESTES DE MUTAÇÃO                         |
|                    Car Rental API                                   |
+=====================================================================+

MÓDULOS TESTADOS:
|- src/utils/validators.py (Validadores de dados)
|- src/services/car_service.py (Lógica de negócio - Carros)
|- src/services/rental_service.py (Lógica de negócio - Aluguéis)
+- src/repositories/car_repository.py (Acesso a dados - Carros)

TIPOS DE MUTAÇÕES APLICADAS:
1. Operadores Aritméticos (+, -, *, /, %)
2. Operadores de Comparação (>, <, >=, <=, ==, !=)
3. Operadores Lógicos (and, or, not)
4. Constantes (True/False, 0/1)

METODOLOGIA:
- Cada mutação é aplicada individualmente ao código
- Os testes são executados após cada mutação
- Se os testes FALHAREM -> Mutação MORTA (bom)
- Se os testes PASSAREM -> Mutação SOBREVIVEU (ruim)

OBJETIVO:
- Taxa de eliminação >= 80% indica testes robustos
- Mutações sobreviventes indicam gaps na cobertura de testes

======================================================================
""")


if __name__ == '__main__':
    generate_mutation_report()

    # Exemplo de uso - descomentar para testar arquivo específico:
    # analyze_mutation_coverage('src/utils/validators.py')

    print("""
NOTA: Para executar testes de mutação em um arquivo específico, use:

    python mutation_tests.py

E descomente a linha:
    analyze_mutation_coverage('src/utils/validators.py')

Substitua pelo caminho do arquivo que deseja testar.

ARQUIVOS RECOMENDADOS PARA TESTE:
- src/utils/validators.py
- src/services/rental_service.py
- src/services/car_service.py

ATENÇÃO: Testes de mutação podem demorar vários minutos!
======================================================================
""")
