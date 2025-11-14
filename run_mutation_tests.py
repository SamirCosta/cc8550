#!/usr/bin/env python
"""
Script para executar testes de mutação.

Oferece várias opções para rodar os testes de mutação do projeto.
"""

import sys
import subprocess
import argparse
from pathlib import Path


def run_manual_tests(verbose: bool = False, coverage: bool = False):
    """Executa os testes de mutação manuais."""
    print("[TESTE] Executando testes de mutacao manuais...")
    print("=" * 60)

    cmd = ["pytest", "tests/mutation/"]

    if verbose:
        cmd.append("-v")

    if coverage:
        cmd.extend([
            "--cov=src",
            "--cov-report=html",
            "--cov-report=term-missing"
        ])

    result = subprocess.run(cmd)
    return result.returncode


def run_specific_test(test_file: str, verbose: bool = False):
    """Executa testes de um arquivo específico."""
    print(f"[TESTE] Executando testes de {test_file}...")
    print("=" * 60)

    cmd = ["pytest", f"tests/mutation/{test_file}"]

    if verbose:
        cmd.append("-v")

    result = subprocess.run(cmd)
    return result.returncode


def check_mutmut_available():
    """Verifica se mutmut está disponível."""
    try:
        result = subprocess.run(
            ["mutmut", "--version"],
            capture_output=True,
            text=True
        )
        return result.returncode == 0
    except FileNotFoundError:
        return False


def run_mutmut():
    """Tenta executar mutmut."""
    print("[MUTMUT] Executando mutmut...")
    print("=" * 60)

    if not check_mutmut_available():
        print("[ERRO] Mutmut nao esta instalado ou nao esta disponivel no Windows.")
        print("\nOpcoes:")
        print("1. Usar WSL: wsl -e mutmut run")
        print("2. Instalar Cosmic Ray: pip install cosmic-ray")
        print("3. Usar os testes manuais (ja disponiveis)")
        return 1

    print("[AVISO] Nota: mutmut pode nao funcionar corretamente no Windows")
    print("Tentando executar...")

    try:
        result = subprocess.run(["mutmut", "run"])
        return result.returncode
    except Exception as e:
        print(f"[ERRO] Erro ao executar mutmut: {e}")
        return 1


def show_summary():
    """Mostra resumo dos testes disponíveis."""
    print("\n[RESUMO] Testes de Mutacao Disponiveis")
    print("=" * 60)
    print("[OK] test_rental_service_mutations.py    - 6 testes")
    print("[OK] test_rental_controller_mutations.py - 7 testes")
    print("[OK] test_rental_repository_mutations.py - 7 testes")
    print("-" * 60)
    print("Total: 20 testes de mutacao (essenciais)")
    print("\n[INFO] Arquivos cobertos:")
    print("  - src/services/rental_service.py (62% cobertura)")
    print("  - src/controllers/rental_controller.py (51.89% cobertura)")
    print("  - src/repositories/rental_repository.py (59.09% cobertura)")


def main():
    parser = argparse.ArgumentParser(
        description="Executar testes de mutação do projeto"
    )

    parser.add_argument(
        "command",
        nargs="?",
        choices=["manual", "mutmut", "service", "controller", "repository", "summary"],
        default="manual",
        help="Comando a executar (padrão: manual)"
    )

    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Saída verbosa"
    )

    parser.add_argument(
        "-c", "--coverage",
        action="store_true",
        help="Gerar relatório de cobertura"
    )

    args = parser.parse_args()

    if args.command == "manual":
        return run_manual_tests(args.verbose, args.coverage)

    elif args.command == "mutmut":
        return run_mutmut()

    elif args.command == "service":
        return run_specific_test("test_rental_service_mutations.py", args.verbose)

    elif args.command == "controller":
        return run_specific_test("test_rental_controller_mutations.py", args.verbose)

    elif args.command == "repository":
        return run_specific_test("test_rental_repository_mutations.py", args.verbose)

    elif args.command == "summary":
        show_summary()
        return 0

    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\n[AVISO] Execucao interrompida pelo usuario")
        sys.exit(130)
