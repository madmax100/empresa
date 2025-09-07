#!/usr/bin/env python3
"""
Script para criar tipos de movimentação de estoque básicos
Este script deve ser executado antes da migração de movimentações
"""

import os
import sys
import django
import logging

# Configurar o ambiente Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'empresa.settings')
django.setup()

from contas.models.access import TiposMovimentacaoEstoque

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('migrate_tipos_movimentacao.log'),
        logging.StreamHandler()
    ]
)

def main():
    """Cria tipos de movimentação básicos se não existirem"""
    logging.info("=== INICIANDO CRIAÇÃO DE TIPOS DE MOVIMENTAÇÃO ===")
    
    try:
        # Verificar se já existem tipos
        tipos_existentes = TiposMovimentacaoEstoque.objects.count()
        logging.info(f"Tipos de movimentação existentes: {tipos_existentes}")
        
        if tipos_existentes == 0:
            # Criar tipos básicos
            tipos = [
                {
                    'codigo': 'ENT',
                    'descricao': 'Entrada de Estoque',
                    'tipo': 'E',
                    'movimenta_custo': True,
                    'ativo': True
                },
                {
                    'codigo': 'SAI',
                    'descricao': 'Saída de Estoque',
                    'tipo': 'S',
                    'movimenta_custo': True,
                    'ativo': True
                }
            ]
            
            for tipo_data in tipos:
                tipo, created = TiposMovimentacaoEstoque.objects.get_or_create(
                    codigo=tipo_data['codigo'],
                    defaults=tipo_data
                )
                if created:
                    logging.info(f"Tipo criado: {tipo}")
                else:
                    logging.info(f"Tipo já existe: {tipo}")
        else:
            logging.info("Tipos de movimentação já existem, pulando criação")
        
        # Listar todos os tipos
        logging.info("--- TIPOS CADASTRADOS ---")
        for tipo in TiposMovimentacaoEstoque.objects.all():
            logging.info(f"• {tipo.codigo} - {tipo.descricao} (Tipo: {tipo.tipo})")
        
        logging.info("=== CRIAÇÃO DE TIPOS CONCLUÍDA COM SUCESSO ===")
        return True
        
    except Exception as e:
        logging.error(f"Erro ao criar tipos de movimentação: {e}")
        return False

if __name__ == "__main__":
    success = main()
    if success:
        print("Tipos de movimentação criados com sucesso!")
    else:
        print("Erro na criação dos tipos de movimentação!")
        sys.exit(1)
