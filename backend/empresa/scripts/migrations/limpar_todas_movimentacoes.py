#!/usr/bin/env python
"""
Script para limpar TODAS as movimentações importadas com data incorreta
"""

import os
import sys
import django

# Configurar o ambiente Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'empresa.settings')
django.setup()

from contas.models.access import MovimentacoesEstoque
from django.db import transaction

def limpar_todas_movimentacoes():
    """Remove TODAS as movimentações que foram importadas incorretamente"""
    
    total_antes = MovimentacoesEstoque.objects.count()
    print(f"Total de registros antes da limpeza: {total_antes}")
    
    # Remover TODOS os registros (pois todos têm data incorreta)
    with transaction.atomic():
        MovimentacoesEstoque.objects.all().delete()
    
    total_depois = MovimentacoesEstoque.objects.count()
    print(f"Total de registros após limpeza: {total_depois}")
    print(f"Registros removidos: {total_antes - total_depois}")
    
    return True

if __name__ == "__main__":
    print("=== LIMPEZA COMPLETA DE MOVIMENTAÇÕES ===")
    limpar_todas_movimentacoes()
    print("Limpeza concluída!")
