import json
import csv
from typing import List, Dict, Any
from pathlib import Path
from datetime import datetime


class FileExporter:
    """
    Classe utilitária para exportação de dados para arquivos.

    Implementa funcionalidades de leitura e escrita de arquivos
    em diferentes formatos (JSON, CSV).
    """

    @staticmethod
    def export_to_json(data: List[Dict[str, Any]], filename: str) -> str:
        """
        Exporta dados para um arquivo JSON.

        Args:
            data: Lista de dicionários com os dados
            filename: Nome do arquivo (sem extensão)

        Returns:
            str: Caminho do arquivo criado
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filepath = f"exports/{filename}_{timestamp}.json"

        Path("exports").mkdir(exist_ok=True)

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2, default=str)

        return filepath

    @staticmethod
    def export_to_csv(data: List[Dict[str, Any]], filename: str) -> str:
        """
        Exporta dados para um arquivo CSV.

        Args:
            data: Lista de dicionários com os dados
            filename: Nome do arquivo (sem extensão)

        Returns:
            str: Caminho do arquivo criado
        """
        if not data:
            raise ValueError("Nenhum dado para exportar")

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filepath = f"exports/{filename}_{timestamp}.csv"

        Path("exports").mkdir(exist_ok=True)

        keys = data[0].keys()

        with open(filepath, 'w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=keys)
            writer.writeheader()
            writer.writerows(data)

        return filepath

    @staticmethod
    def read_json(filepath: str) -> List[Dict[str, Any]]:
        """
        Lê dados de um arquivo JSON.

        Args:
            filepath: Caminho do arquivo

        Returns:
            List[Dict[str, Any]]: Dados lidos do arquivo
        """
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)

    @staticmethod
    def read_csv(filepath: str) -> List[Dict[str, Any]]:
        """
        Lê dados de um arquivo CSV.

        Args:
            filepath: Caminho do arquivo

        Returns:
            List[Dict[str, Any]]: Dados lidos do arquivo
        """
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            return list(reader)
