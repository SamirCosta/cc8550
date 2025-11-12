import pytest
import os
import json
import csv
from pathlib import Path
from src.utils import FileExporter


class TestFileExporter:
    """
    Testes unitários para FileExporter.
    """

    def teardown_method(self):
        """
        Limpa arquivos de teste após cada teste.
        """
        if os.path.exists("exports"):
            for file in os.listdir("exports"):
                os.remove(os.path.join("exports", file))
            os.rmdir("exports")

    def test_export_to_json_success(self):
        """Testa exportação para JSON com sucesso."""
        data = [
            {"id": 1, "name": "João", "age": 30},
            {"id": 2, "name": "Maria", "age": 25}
        ]

        filepath = FileExporter.export_to_json(data, "test_users")

        assert os.path.exists(filepath)
        assert filepath.startswith("exports/test_users_")
        assert filepath.endswith(".json")

        with open(filepath, 'r', encoding='utf-8') as f:
            loaded_data = json.load(f)

        assert len(loaded_data) == 2
        assert loaded_data[0]["name"] == "João"

    def test_export_to_json_empty_list(self):
        """Testa exportação de lista vazia para JSON."""
        data = []

        filepath = FileExporter.export_to_json(data, "empty")

        assert os.path.exists(filepath)

        with open(filepath, 'r', encoding='utf-8') as f:
            loaded_data = json.load(f)

        assert loaded_data == []

    def test_export_to_json_with_special_characters(self):
        """Testa exportação para JSON com caracteres especiais."""
        data = [
            {"name": "José", "city": "São Paulo"},
            {"name": "François", "city": "Münich"}
        ]

        filepath = FileExporter.export_to_json(data, "special_chars")

        assert os.path.exists(filepath)

        with open(filepath, 'r', encoding='utf-8') as f:
            loaded_data = json.load(f)

        assert loaded_data[0]["name"] == "José"
        assert loaded_data[0]["city"] == "São Paulo"

    def test_export_to_csv_success(self):
        """Testa exportação para CSV com sucesso."""
        data = [
            {"id": "1", "name": "João", "email": "joao@example.com"},
            {"id": "2", "name": "Maria", "email": "maria@example.com"}
        ]

        filepath = FileExporter.export_to_csv(data, "test_users")

        assert os.path.exists(filepath)
        assert filepath.startswith("exports/test_users_")
        assert filepath.endswith(".csv")

        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)

        assert len(rows) == 2
        assert rows[0]["name"] == "João"
        assert rows[1]["email"] == "maria@example.com"

    def test_export_to_csv_empty_data_raises_error(self):
        """Testa que exportar lista vazia para CSV gera erro."""
        data = []

        with pytest.raises(ValueError, match="Nenhum dado para exportar"):
            FileExporter.export_to_csv(data, "empty")

    def test_export_to_csv_with_special_characters(self):
        """Testa exportação para CSV com caracteres especiais."""
        data = [
            {"name": "José", "city": "São Paulo"},
            {"name": "François", "city": "Münich"}
        ]

        filepath = FileExporter.export_to_csv(data, "special_csv")

        assert os.path.exists(filepath)

        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)

        assert rows[0]["name"] == "José"

    def test_read_json_success(self):
        """Testa leitura de arquivo JSON."""
        data = [
            {"id": 1, "name": "Test User"},
            {"id": 2, "name": "Another User"}
        ]

        filepath = FileExporter.export_to_json(data, "read_test")
        loaded_data = FileExporter.read_json(filepath)

        assert len(loaded_data) == 2
        assert loaded_data[0]["name"] == "Test User"
        assert loaded_data[1]["id"] == 2

    def test_read_csv_success(self):
        """Testa leitura de arquivo CSV."""
        data = [
            {"id": "1", "name": "Test User", "active": "true"},
            {"id": "2", "name": "Another User", "active": "false"}
        ]

        filepath = FileExporter.export_to_csv(data, "read_csv_test")
        loaded_data = FileExporter.read_csv(filepath)

        assert len(loaded_data) == 2
        assert loaded_data[0]["name"] == "Test User"
        assert loaded_data[1]["active"] == "false"

    def test_export_creates_directory_if_not_exists(self):
        """Testa que o diretório exports é criado automaticamente."""
        if os.path.exists("exports"):
            os.rmdir("exports")

        assert not os.path.exists("exports")

        data = [{"test": "data"}]
        FileExporter.export_to_json(data, "test")

        assert os.path.exists("exports")
