#!/usr/bin/env python
"""
Script de manutenção para performance do sistema
Execute periodicamente para manter a performance
"""

import os
import sys
import django
from django.db import connection
from django.core.cache import cache

# Configurar Django
sys.path.append(os.path.abspath('.'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'empresa.settings')
django.setup()

def atualizar_estatisticas_db():
    """Atualiza estatísticas do banco PostgreSQL"""
    print("📊 Atualizando estatísticas do banco...")
    
    with connection.cursor() as cursor:
        # Atualiza estatísticas das tabelas principais
        tabelas = [
            'movimentacoes_estoque',
            'saldos_estoque', 
            'produtos',
            'contas_pagar',
            'contas_receber'
        ]
        
        for tabela in tabelas:
            cursor.execute(f"ANALYZE {tabela};")
            print(f"  ✅ {tabela}")

def refresh_view_materializada():
    """Atualiza view materializada de estoque"""
    print("🔄 Atualizando view materializada...")
    
    with connection.cursor() as cursor:
        cursor.execute("REFRESH MATERIALIZED VIEW view_saldos_estoque_rapido;")
        print("  ✅ View atualizada")

def limpar_cache_antigo():
    """Remove caches antigos"""
    print("🧹 Limpando cache antigo...")
    
    # Remove caches de estoque mais antigos que 24h
    cache.delete_many(cache.keys('estoque_data_*'))
    print("  ✅ Cache de estoque limpo")

def verificar_indices():
    """Verifica se os índices estão sendo usados"""
    print("🔍 Verificando uso de índices...")
    
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT 
                schemaname,
                tablename,
                indexname,
                idx_scan,
                idx_tup_read,
                idx_tup_fetch
            FROM pg_stat_user_indexes 
            WHERE idx_scan = 0
            AND schemaname = 'public'
        """)
        
        indices_nao_usados = cursor.fetchall()
        
        if indices_nao_usados:
            print("  ⚠️ Índices não utilizados encontrados:")
            for row in indices_nao_usados:
                print(f"    - {row[2]} na tabela {row[1]}")
        else:
            print("  ✅ Todos os índices estão sendo utilizados")

def main():
    """Função principal de manutenção"""
    print("🔧 EXECUTANDO MANUTENÇÃO DE PERFORMANCE")
    print("=" * 50)
    
    try:
        atualizar_estatisticas_db()
        refresh_view_materializada() 
        limpar_cache_antigo()
        verificar_indices()
        
        print("\n✅ Manutenção concluída com sucesso!")
        
    except Exception as e:
        print(f"❌ Erro durante manutenção: {str(e)}")

if __name__ == '__main__':
    main()
