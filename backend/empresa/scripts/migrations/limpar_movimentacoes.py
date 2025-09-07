#!/usr/bin/env python
"""
Script para corrigir as datas das movimentações já migradas e limpar registros com data incorreta
"""

import os
import sys
import django
from datetime import datetime
import logging
from django.utils import timezone

# Configurar o ambiente Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'empresa.settings')
django.setup()

from contas.models.access import MovimentacoesEstoque
from django.db import transaction

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def limpar_movimentacoes_incorretas():
    """Remove todas as movimentações que foram importadas com data incorreta (data atual)"""
    
    # Data de hoje (as movimentações incorretas terão data de hoje)
    data_hoje = datetime.now().date()
    
    # Contar registros com data de hoje
    registros_hoje = MovimentacoesEstoque.objects.filter(
        data_movimentacao__date=data_hoje
    ).count()
    
    logging.info(f"Encontrados {registros_hoje} registros com data de hoje que serão removidos")
    
    if registros_hoje > 0:
        with transaction.atomic():
            # Remover registros com data de hoje (foram importados incorretamente)
            MovimentacoesEstoque.objects.filter(
                data_movimentacao__date=data_hoje
            ).delete()
            
        logging.info(f"Removidos {registros_hoje} registros com data incorreta")
    
    # Verificar total restante
    total_restante = MovimentacoesEstoque.objects.count()
    logging.info(f"Total de registros restantes: {total_restante}")
    
    return True

def main():
    try:
        logging.info("=== LIMPEZA DE MOVIMENTAÇÕES COM DATA INCORRETA ===")
        success = limpar_movimentacoes_incorretas()
        
        if success:
            print("Limpeza concluída com sucesso!")
        else:
            print("Falha na limpeza.")
            
    except Exception as e:
        logging.error(f"Erro na limpeza: {e}")
        print(f"Erro na limpeza: {e}")

if __name__ == "__main__":
    main()
