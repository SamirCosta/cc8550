"""
Configuração de Fixtures para Testes do Módulo Fixtures

Este conftest.py importa todas as fixtures definidas nos módulos
para que fiquem disponíveis aos testes em test_fixtures.py
"""
# Importa todas as fixtures dos módulos
from .database import *
from .repositories import *
from .models import *
from .test_data import *
