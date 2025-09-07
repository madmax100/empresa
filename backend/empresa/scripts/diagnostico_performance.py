#!/usr/bin/env python
"""
Script para diagnosticar performance dos endpoints
Identifica possíveis gargalos e problemas de performance
"""

import os
import sys
import django
import time
from datetime import datetime, date, timedelta
from decimal import Decimal
from django.db import connection
from django.conf import settings

# Configurar Django
sys.path.append(os.path.abspath('.'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'empresa.settings')
django.setup()

from contas.models import (
    MovimentacoesEstoque, 
    SaldosEstoque, 
    Produtos,
    ContasPagar,
    ContasReceber,
    NotasFiscaisEntrada,
    NotasFiscaisSaida
)

def verificar_configuracao_database():
    """Verifica configurações do banco de dados"""
    print("🔍 VERIFICANDO CONFIGURAÇÃO DO BANCO DE DADOS")
    print("=" * 60)
    
    db_config = settings.DATABASES['default']
    print(f"Engine: {db_config.get('ENGINE', 'N/D')}")
    print(f"Host: {db_config.get('HOST', 'localhost')}")
    print(f"Port: {db_config.get('PORT', 'N/D')}")
    print(f"Database: {db_config.get('NAME', 'N/D')}")
    
    # Verificar configurações de performance
    performance_configs = {
        'CONN_MAX_AGE': db_config.get('CONN_MAX_AGE', 0),
        'OPTIONS': db_config.get('OPTIONS', {})
    }
    
    print(f"\nConfigurações de Performance:")
    for key, value in performance_configs.items():
        print(f"  {key}: {value}")
    
    # Teste de conexão
    start_time = time.time()
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
        connection_time = time.time() - start_time
        print(f"\n✅ Conexão OK: {connection_time:.3f}s")
    except Exception as e:
        print(f"\n❌ Erro de conexão: {str(e)}")
    
    print()

def contar_registros_tabelas():
    """Conta registros nas principais tabelas"""
    print("📊 CONTAGEM DE REGISTROS POR TABELA")
    print("=" * 60)
    
    tabelas = {
        'Produtos': Produtos,
        'MovimentacoesEstoque': MovimentacoesEstoque,
        'SaldosEstoque': SaldosEstoque,
        'ContasPagar': ContasPagar,
        'ContasReceber': ContasReceber,
        'NotasFiscaisEntrada': NotasFiscaisEntrada,
        'NotasFiscaisSaida': NotasFiscaisSaida,
    }
    
    total_registros = 0
    
    for nome, modelo in tabelas.items():
        start_time = time.time()
        try:
            count = modelo.objects.count()
            query_time = time.time() - start_time
            total_registros += count
            
            status = "⚠️" if query_time > 1.0 else "✅"
            print(f"{status} {nome:<25} {count:>10,} registros ({query_time:.3f}s)")
            
        except Exception as e:
            print(f"❌ {nome:<25} ERRO: {str(e)}")
    
    print(f"\n📈 Total geral: {total_registros:,} registros")
    print()

def testar_consultas_criticas():
    """Testa consultas que são críticas para performance"""
    print("🚀 TESTANDO CONSULTAS CRÍTICAS")
    print("=" * 60)
    
    testes = [
        {
            'nome': 'Produtos com estoque positivo',
            'query': lambda: SaldosEstoque.objects.filter(quantidade__gt=0).count()
        },
        {
            'nome': 'Movimentações último mês',
            'query': lambda: MovimentacoesEstoque.objects.filter(
                data_movimentacao__gte=date.today() - timedelta(days=30)
            ).count()
        },
        {
            'nome': 'Contas a pagar em aberto',
            'query': lambda: ContasPagar.objects.filter(
                status='aberto'
            ).count()
        },
        {
            'nome': 'Contas a receber em aberto', 
            'query': lambda: ContasReceber.objects.filter(
                status='aberto'
            ).count()
        },
        {
            'nome': 'Movimentações com JOIN produto',
            'query': lambda: MovimentacoesEstoque.objects.select_related(
                'produto', 'tipo_movimentacao'
            )[:100].count()
        }
    ]
    
    for teste in testes:
        start_time = time.time()
        try:
            resultado = teste['query']()
            query_time = time.time() - start_time
            
            status = "❌" if query_time > 5.0 else "⚠️" if query_time > 2.0 else "✅"
            print(f"{status} {teste['nome']:<35} {resultado:>8,} ({query_time:.3f}s)")
            
        except Exception as e:
            print(f"❌ {teste['nome']:<35} ERRO: {str(e)}")
    
    print()

def verificar_indices_database():
    """Verifica se existem índices nas colunas críticas"""
    print("🔗 VERIFICANDO ÍNDICES DO BANCO DE DADOS")
    print("=" * 60)
    
    with connection.cursor() as cursor:
        try:
            # Query para PostgreSQL
            cursor.execute("""
                SELECT 
                    schemaname,
                    tablename,
                    indexname,
                    indexdef
                FROM pg_indexes 
                WHERE schemaname = 'public'
                AND (tablename LIKE '%estoque%' 
                     OR tablename LIKE '%conta%' 
                     OR tablename = 'produtos')
                ORDER BY tablename, indexname
            """)
            
            indices = cursor.fetchall()
            
            if indices:
                print(f"{'Tabela':<25} {'Índice':<30} {'Definição'}")
                print("-" * 80)
                
                for schema, tabela, indice, definicao in indices:
                    print(f"{tabela:<25} {indice:<30} {definicao[:50]}...")
            else:
                print("❌ Nenhum índice encontrado ou erro na consulta")
                
        except Exception as e:
            print(f"❌ Erro ao verificar índices: {str(e)}")
            print("💡 Tentando método alternativo...")
            
            # Método alternativo - verificar models
            tabelas_criticas = [
                'movimentacoes_estoque',
                'saldos_estoque', 
                'contas_pagar',
                'contas_receber',
                'produtos'
            ]
            
            for tabela in tabelas_criticas:
                cursor.execute(f"""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name = '{tabela}'
                    AND table_schema = 'public'
                    ORDER BY ordinal_position
                """)
                
                colunas = [row[0] for row in cursor.fetchall()]
                print(f"📋 {tabela}: {len(colunas)} colunas")
    
    print()

def simular_endpoint_estoque():
    """Simula a execução do endpoint de estoque para medir performance"""
    print("⏱️ SIMULANDO ENDPOINT DE ESTOQUE")
    print("=" * 60)
    
    data_teste = date.today() - timedelta(days=1)
    
    print(f"📅 Testando estoque para data: {data_teste}")
    
    # Teste 1: Query simples de contagem
    start_time = time.time()
    total_movimentacoes = MovimentacoesEstoque.objects.filter(
        data_movimentacao__date__lte=data_teste
    ).count()
    tempo_contagem = time.time() - start_time
    
    print(f"1️⃣ Contagem movimentações: {total_movimentacoes:,} ({tempo_contagem:.3f}s)")
    
    # Teste 2: Query com agregação (similar ao endpoint real)
    start_time = time.time()
    try:
        from django.db.models import Sum, Case, When, F, DecimalField
        
        # Simula a query do endpoint relatorio_valor_estoque
        saldos = MovimentacoesEstoque.objects.filter(
            data_movimentacao__date__lte=data_teste
        ).values(
            'produto_id', 
            'produto__nome'
        ).annotate(
            saldo_final=Sum(
                Case(
                    When(tipo_movimentacao__tipo='E', then=F('quantidade')),
                    When(tipo_movimentacao__tipo='S', then=-F('quantidade')),
                    default=0,
                    output_field=DecimalField()
                )
            )
        )[:10]  # Limita para teste
        
        # Executa a query
        resultado = list(saldos)
        tempo_agregacao = time.time() - start_time
        
        print(f"2️⃣ Agregação (10 produtos): {len(resultado)} resultados ({tempo_agregacao:.3f}s)")
        
    except Exception as e:
        print(f"❌ Erro na agregação: {str(e)}")
    
    # Teste 3: Query completa (sem limite)
    if tempo_agregacao < 5.0:  # Só testa se a anterior foi rápida
        start_time = time.time()
        try:
            saldos_completos = MovimentacoesEstoque.objects.filter(
                data_movimentacao__date__lte=data_teste
            ).values(
                'produto_id'
            ).annotate(
                saldo_final=Sum(
                    Case(
                        When(tipo_movimentacao__tipo='E', then=F('quantidade')),
                        When(tipo_movimentacao__tipo='S', then=-F('quantidade')),
                        default=0,
                        output_field=DecimalField()
                    )
                )
            ).filter(saldo_final__gt=0)
            
            count_completo = saldos_completos.count()
            tempo_completo = time.time() - start_time
            
            print(f"3️⃣ Query completa: {count_completo:,} produtos com estoque ({tempo_completo:.3f}s)")
            
        except Exception as e:
            print(f"❌ Erro na query completa: {str(e)}")
    else:
        print("3️⃣ ⚠️ Pulando teste completo (agregação muito lenta)")
    
    print()

def verificar_configuracoes_django():
    """Verifica configurações do Django que afetam performance"""
    print("⚙️ VERIFICANDO CONFIGURAÇÕES DO DJANGO")
    print("=" * 60)
    
    configs = {
        'DEBUG': getattr(settings, 'DEBUG', None),
        'ALLOWED_HOSTS': getattr(settings, 'ALLOWED_HOSTS', None),
        'USE_TZ': getattr(settings, 'USE_TZ', None),
        'TIME_ZONE': getattr(settings, 'TIME_ZONE', None),
    }
    
    # Verificar middleware
    middleware = getattr(settings, 'MIDDLEWARE', [])
    
    print("Configurações principais:")
    for key, value in configs.items():
        status = "⚠️" if key == 'DEBUG' and value else "✅"
        print(f"  {status} {key}: {value}")
    
    print(f"\nMiddleware ({len(middleware)} itens):")
    for mw in middleware:
        print(f"  - {mw.split('.')[-1]}")
    
    # Verificar configurações de cache
    caches = getattr(settings, 'CACHES', {})
    print(f"\nCache configurado: {'✅' if caches else '❌'}")
    if caches:
        for cache_name, cache_config in caches.items():
            print(f"  {cache_name}: {cache_config.get('BACKEND', 'N/D')}")
    
    print()

def analisar_queries_sql():
    """Analisa as queries SQL que estão sendo executadas"""
    print("🔍 ANALISANDO QUERIES SQL")
    print("=" * 60)
    
    # Habilita logging de queries
    from django.conf import settings
    from django.db import connection
    
    # Reset queries
    connection.queries_log.clear()
    
    # Executa uma operação simples
    start_time = time.time()
    produtos_count = Produtos.objects.count()
    query_time = time.time() - start_time
    
    print(f"Teste simples: {produtos_count:,} produtos ({query_time:.3f}s)")
    print(f"Queries executadas: {len(connection.queries)}")
    
    if connection.queries:
        print("\nÚltimas queries:")
        for i, query in enumerate(connection.queries[-3:], 1):
            print(f"  {i}. Tempo: {query['time']}s")
            print(f"     SQL: {query['sql'][:100]}...")
    
    print()

def gerar_recomendacoes():
    """Gera recomendações para melhorar performance"""
    print("💡 RECOMENDAÇÕES PARA MELHORAR PERFORMANCE")
    print("=" * 60)
    
    recomendacoes = [
        {
            'titulo': '1. ÍNDICES NO BANCO DE DADOS',
            'descricao': 'Criar índices nas colunas mais consultadas',
            'sql': [
                "CREATE INDEX IF NOT EXISTS idx_movimentacoes_data ON movimentacoes_estoque(data_movimentacao);",
                "CREATE INDEX IF NOT EXISTS idx_movimentacoes_produto ON movimentacoes_estoque(produto_id);",
                "CREATE INDEX IF NOT EXISTS idx_movimentacoes_tipo ON movimentacoes_estoque(tipo_movimentacao_id);",
                "CREATE INDEX IF NOT EXISTS idx_saldos_produto ON saldos_estoque(produto_id_id);",
                "CREATE INDEX IF NOT EXISTS idx_contas_pagar_status ON contas_pagar(status);",
                "CREATE INDEX IF NOT EXISTS idx_contas_receber_status ON contas_receber(status);"
            ]
        },
        {
            'titulo': '2. OTIMIZAÇÃO DE QUERIES',
            'descricao': 'Usar select_related e prefetch_related',
            'codigo': [
                "# Em vez de:",
                "MovimentacoesEstoque.objects.all()",
                "",
                "# Use:",
                "MovimentacoesEstoque.objects.select_related('produto', 'tipo_movimentacao')"
            ]
        },
        {
            'titulo': '3. CACHE DE RESULTADOS',
            'descricao': 'Implementar cache para consultas frequentes',
            'codigo': [
                "from django.core.cache import cache",
                "",
                "def get_estoque_cached(data):",
                "    cache_key = f'estoque_{data}'",
                "    result = cache.get(cache_key)",
                "    if not result:",
                "        result = calcular_estoque(data)",
                "        cache.set(cache_key, result, 3600)  # 1 hora",
                "    return result"
            ]
        },
        {
            'titulo': '4. PAGINAÇÃO',
            'descricao': 'Implementar paginação em endpoints com muitos dados',
            'codigo': [
                "from rest_framework.pagination import PageNumberPagination",
                "",
                "class EstoquePagination(PageNumberPagination):",
                "    page_size = 50",
                "    max_page_size = 200"
            ]
        },
        {
            'titulo': '5. CONFIGURAÇÃO DO BANCO',
            'descricao': 'Ajustar configurações do PostgreSQL',
            'config': [
                "# postgresql.conf",
                "shared_buffers = 256MB",
                "effective_cache_size = 1GB", 
                "work_mem = 4MB",
                "maintenance_work_mem = 64MB"
            ]
        }
    ]
    
    for rec in recomendacoes:
        print(f"\n{rec['titulo']}")
        print("-" * 50)
        print(rec['descricao'])
        
        if 'sql' in rec:
            print("\nSQL para executar:")
            for sql in rec['sql']:
                print(f"  {sql}")
        
        if 'codigo' in rec:
            print("\nCódigo exemplo:")
            for linha in rec['codigo']:
                print(f"  {linha}")
        
        if 'config' in rec:
            print("\nConfiguração:")
            for config in rec['config']:
                print(f"  {config}")

def main():
    """Função principal"""
    print(f"DIAGNÓSTICO DE PERFORMANCE - {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print("=" * 80)
    
    try:
        verificar_configuracao_database()
        contar_registros_tabelas()
        testar_consultas_criticas()
        verificar_indices_database()
        simular_endpoint_estoque()
        verificar_configuracoes_django()
        analisar_queries_sql()
        gerar_recomendacoes()
        
        print("=" * 80)
        print("✅ DIAGNÓSTICO CONCLUÍDO")
        print("=" * 80)
        print("🎯 Principais causas de lentidão:")
        print("   1. Falta de índices no banco de dados")
        print("   2. Consultas com agregações pesadas")
        print("   3. Ausência de cache")
        print("   4. Queries sem otimização (select_related)")
        print("\n💡 Consulte as recomendações acima para melhorar a performance!")
        
    except Exception as e:
        print(f"❌ Erro durante o diagnóstico: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
