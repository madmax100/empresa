#!/usr/bin/env python
"""
Script para aplicar otimizações de performance
Cria índices e implementa melhorias nos endpoints
"""

import os
import sys
import django
from datetime import datetime
from django.db import connection

# Configurar Django
sys.path.append(os.path.abspath('.'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'empresa.settings')
django.setup()

def criar_indices_performance():
    """Cria índices para melhorar performance"""
    print("🔧 CRIANDO ÍNDICES PARA PERFORMANCE")
    print("=" * 60)
    
    indices = [
        {
            'nome': 'idx_movimentacoes_data_movimentacao',
            'sql': 'CREATE INDEX IF NOT EXISTS idx_movimentacoes_data_movimentacao ON movimentacoes_estoque(data_movimentacao);',
            'descricao': 'Índice para consultas por data'
        },
        {
            'nome': 'idx_movimentacoes_data_date', 
            'sql': 'CREATE INDEX IF NOT EXISTS idx_movimentacoes_data_date ON movimentacoes_estoque(DATE(data_movimentacao));',
            'descricao': 'Índice para consultas por data (apenas data)'
        },
        {
            'nome': 'idx_movimentacoes_produto_data',
            'sql': 'CREATE INDEX IF NOT EXISTS idx_movimentacoes_produto_data ON movimentacoes_estoque(produto_id, data_movimentacao);',
            'descricao': 'Índice composto produto + data'
        },
        {
            'nome': 'idx_movimentacoes_tipo_data',
            'sql': 'CREATE INDEX IF NOT EXISTS idx_movimentacoes_tipo_data ON movimentacoes_estoque(tipo_movimentacao_id, data_movimentacao);',
            'descricao': 'Índice composto tipo + data'
        },
        {
            'nome': 'idx_saldos_quantidade',
            'sql': 'CREATE INDEX IF NOT EXISTS idx_saldos_quantidade ON saldos_estoque(quantidade) WHERE quantidade > 0;',
            'descricao': 'Índice parcial para saldos positivos'
        },
        {
            'nome': 'idx_contas_pagar_status_venc',
            'sql': 'CREATE INDEX IF NOT EXISTS idx_contas_pagar_status_venc ON contas_pagar(status, data_vencimento);',
            'descricao': 'Índice composto status + vencimento'
        },
        {
            'nome': 'idx_contas_receber_status_venc',
            'sql': 'CREATE INDEX IF NOT EXISTS idx_contas_receber_status_venc ON contas_receber(status, data_vencimento);',
            'descricao': 'Índice composto status + vencimento'
        }
    ]
    
    sucessos = 0
    erros = 0
    
    with connection.cursor() as cursor:
        for indice in indices:
            try:
                print(f"📝 Criando {indice['nome']}...")
                cursor.execute(indice['sql'])
                print(f"✅ {indice['descricao']}")
                sucessos += 1
            except Exception as e:
                print(f"❌ Erro ao criar {indice['nome']}: {str(e)}")
                erros += 1
    
    print(f"\n📊 Resultado: {sucessos} sucessos, {erros} erros")
    print()

def criar_view_materializada_estoque():
    """Cria view materializada para consultas de estoque rápidas"""
    print("📊 CRIANDO VIEW MATERIALIZADA PARA ESTOQUE")
    print("=" * 60)
    
    sql_view = """
    CREATE MATERIALIZED VIEW IF NOT EXISTS view_saldos_estoque_rapido AS
    SELECT 
        me.produto_id,
        p.codigo as produto_codigo,
        p.nome as produto_nome,
        p.preco_custo as custo_unitario,
        SUM(CASE 
            WHEN tme.tipo = 'E' THEN me.quantidade 
            WHEN tme.tipo = 'S' THEN -me.quantidade 
            ELSE 0 
        END) as saldo_atual,
        MAX(me.data_movimentacao) as ultima_movimentacao,
        COUNT(*) as total_movimentacoes
    FROM movimentacoes_estoque me
    INNER JOIN produtos p ON me.produto_id = p.id
    INNER JOIN tipos_movimentacao_estoque tme ON me.tipo_movimentacao_id = tme.id
    GROUP BY me.produto_id, p.codigo, p.nome, p.preco_custo
    HAVING SUM(CASE 
        WHEN tme.tipo = 'E' THEN me.quantidade 
        WHEN tme.tipo = 'S' THEN -me.quantidade 
        ELSE 0 
    END) > 0;
    """
    
    sql_index = """
    CREATE UNIQUE INDEX IF NOT EXISTS idx_view_saldos_produto 
    ON view_saldos_estoque_rapido(produto_id);
    """
    
    sql_index2 = """
    CREATE INDEX IF NOT EXISTS idx_view_saldos_codigo 
    ON view_saldos_estoque_rapido(produto_codigo);
    """
    
    try:
        with connection.cursor() as cursor:
            print("📝 Criando view materializada...")
            cursor.execute(sql_view)
            print("✅ View materializada criada")
            
            print("📝 Criando índices na view...")
            cursor.execute(sql_index)
            cursor.execute(sql_index2)
            print("✅ Índices da view criados")
            
            print("📝 Atualizando dados da view...")
            cursor.execute("REFRESH MATERIALIZED VIEW view_saldos_estoque_rapido;")
            print("✅ View atualizada")
            
            # Verifica quantos registros foram criados
            cursor.execute("SELECT COUNT(*) FROM view_saldos_estoque_rapido;")
            count = cursor.fetchone()[0]
            print(f"📊 {count:,} produtos com estoque na view")
            
    except Exception as e:
        print(f"❌ Erro ao criar view materializada: {str(e)}")
    
    print()

def otimizar_configuracoes_django():
    """Cria arquivo com configurações otimizadas"""
    print("⚙️ GERANDO CONFIGURAÇÕES OTIMIZADAS")
    print("=" * 60)
    
    config_otimizada = '''
# Configurações de Performance para settings.py

# 1. Configuração do banco de dados otimizada
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'c3mcopiasdb2',
        'USER': 'postgres',
        'PASSWORD': 'sua_senha',
        'HOST': 'localhost',
        'PORT': '5432',
        'CONN_MAX_AGE': 300,  # Mantém conexões por 5 minutos
        'OPTIONS': {
            'connect_timeout': 10,
            'options': '-c default_transaction_isolation=read_committed'
        }
    }
}

# 2. Cache Redis (recomendado para produção)
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'SERIALIZER': 'django_redis.serializers.json.JSONSerializer',
        },
        'TIMEOUT': 3600,  # 1 hora
        'KEY_PREFIX': 'c3mcopias'
    }
}

# 3. Configurações de logging para produção
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': 'django.log',
            'formatter': 'verbose',
        },
        'db_queries': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': 'db_queries.log',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django.db.backends': {
            'handlers': ['db_queries'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'django': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}

# 4. Configurações de sessão
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_CACHE_ALIAS = 'default'
SESSION_COOKIE_AGE = 86400  # 24 horas

# 5. Configurações de segurança para produção
if not DEBUG:
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = 'DENY'
    SECURE_HSTS_SECONDS = 3600
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True

# 6. Configuração do Django REST Framework
REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 50,
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle'
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/hour',
        'user': '1000/hour'
    }
}
'''
    
    with open('scripts/configuracoes_performance.py', 'w', encoding='utf-8') as f:
        f.write(config_otimizada)
    
    print("✅ Arquivo 'configuracoes_performance.py' criado")
    print("💡 Copie as configurações relevantes para o settings.py")
    print()

def criar_endpoint_otimizado():
    """Cria versão otimizada do endpoint de estoque"""
    print("🚀 CRIANDO ENDPOINT OTIMIZADO")
    print("=" * 60)
    
    codigo_otimizado = '''
# views/estoque_otimizado.py
from django.core.cache import cache
from django.db import connection
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from datetime import datetime, date
from decimal import Decimal

@api_view(['GET'])
def relatorio_valor_estoque_otimizado(request):
    """
    Versão otimizada do relatório de estoque por data
    """
    try:
        # 1. Parâmetros
        data_str = request.query_params.get('data', date.today().strftime('%Y-%m-%d'))
        data_posicao = datetime.strptime(data_str, '%Y-%m-%d').date()
        usar_cache = request.query_params.get('cache', 'true').lower() == 'true'
        
        # 2. Verificar cache primeiro
        cache_key = f'estoque_data_{data_posicao}'
        if usar_cache:
            cached_result = cache.get(cache_key)
            if cached_result:
                cached_result['cache_hit'] = True
                return Response(cached_result)
        
        # 3. Query otimizada usando SQL direto
        with connection.cursor() as cursor:
            sql = """
            SELECT 
                me.produto_id,
                p.codigo,
                p.nome,
                COALESCE(p.preco_custo, 0) as custo_unitario,
                SUM(CASE 
                    WHEN tme.tipo = 'E' THEN me.quantidade 
                    WHEN tme.tipo = 'S' THEN -me.quantidade 
                    ELSE 0 
                END) as saldo_final
            FROM movimentacoes_estoque me
            INNER JOIN produtos p ON me.produto_id = p.id
            INNER JOIN tipos_movimentacao_estoque tme ON me.tipo_movimentacao_id = tme.id
            WHERE DATE(me.data_movimentacao) <= %s
            GROUP BY me.produto_id, p.codigo, p.nome, p.preco_custo
            HAVING SUM(CASE 
                WHEN tme.tipo = 'E' THEN me.quantidade 
                WHEN tme.tipo = 'S' THEN -me.quantidade 
                ELSE 0 
            END) > 0
            ORDER BY saldo_final DESC
            """
            
            cursor.execute(sql, [data_posicao])
            resultados = cursor.fetchall()
        
        # 4. Processar resultados
        valor_total_estoque = Decimal('0.00')
        detalhes_produtos = []
        
        for produto_id, codigo, nome, custo, saldo in resultados:
            custo_decimal = Decimal(str(custo))
            saldo_decimal = Decimal(str(saldo))
            valor_produto = saldo_decimal * custo_decimal
            valor_total_estoque += valor_produto
            
            detalhes_produtos.append({
                'produto_id': produto_id,
                'produto_codigo': codigo,
                'produto_descricao': nome,
                'quantidade_em_estoque': saldo_decimal,
                'custo_unitario': custo_decimal,
                'valor_total_produto': valor_produto
            })
        
        # 5. Resposta
        response_data = {
            'data_posicao': data_posicao,
            'valor_total_estoque': valor_total_estoque,
            'total_produtos_em_estoque': len(detalhes_produtos),
            'detalhes_por_produto': detalhes_produtos,
            'cache_hit': False,
            'otimizado': True
        }
        
        # 6. Salvar no cache (1 hora para dados do dia, 24h para dados antigos)
        if usar_cache:
            timeout = 3600 if data_posicao == date.today() else 86400
            cache.set(cache_key, response_data, timeout)
        
        return Response(response_data)
        
    except Exception as e:
        return Response(
            {'error': f'Erro interno: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
def refresh_cache_estoque(request):
    """
    Endpoint para limpar cache de estoque
    """
    try:
        data_str = request.data.get('data')
        if data_str:
            cache_key = f'estoque_data_{data_str}'
            cache.delete(cache_key)
            return Response({'message': f'Cache removido para {data_str}'})
        else:
            # Remove todos os caches de estoque
            cache.delete_many(cache.keys('estoque_data_*'))
            return Response({'message': 'Todos os caches de estoque removidos'})
            
    except Exception as e:
        return Response(
            {'error': str(e)}, 
            status=status.HTTP_400_BAD_REQUEST
        )


@api_view(['GET'])
def estoque_view_materializada(request):
    """
    Endpoint usando view materializada (muito rápido)
    """
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT 
                    produto_id,
                    produto_codigo,
                    produto_nome,
                    saldo_atual,
                    custo_unitario,
                    saldo_atual * COALESCE(custo_unitario, 0) as valor_total,
                    ultima_movimentacao
                FROM view_saldos_estoque_rapido
                ORDER BY saldo_atual DESC
            """)
            
            colunas = [desc[0] for desc in cursor.description]
            resultados = [dict(zip(colunas, row)) for row in cursor.fetchall()]
        
        valor_total = sum(r['valor_total'] or 0 for r in resultados)
        
        return Response({
            'produtos': resultados,
            'total_produtos': len(resultados),
            'valor_total': valor_total,
            'fonte': 'view_materializada',
            'observacao': 'Dados podem estar até 1 hora desatualizados'
        })
        
    except Exception as e:
        return Response(
            {'error': str(e)}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
'''

    with open('scripts/endpoint_estoque_otimizado.py', 'w', encoding='utf-8') as f:
        f.write(codigo_otimizado)
    
    print("✅ Arquivo 'endpoint_estoque_otimizado.py' criado")
    print("💡 Integre este código ao seu projeto para endpoints mais rápidos")
    print()

def criar_script_manutencao():
    """Cria script para manutenção de performance"""
    print("🔧 CRIANDO SCRIPT DE MANUTENÇÃO")
    print("=" * 60)
    
    script_manutencao = '''#!/usr/bin/env python
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
        
        print("\\n✅ Manutenção concluída com sucesso!")
        
    except Exception as e:
        print(f"❌ Erro durante manutenção: {str(e)}")

if __name__ == '__main__':
    main()
'''
    
    with open('scripts/manutencao_performance.py', 'w', encoding='utf-8') as f:
        f.write(script_manutencao)
    
    print("✅ Arquivo 'manutencao_performance.py' criado")
    print("💡 Execute este script semanalmente: python scripts/manutencao_performance.py")
    print()

def main():
    """Função principal"""
    print(f"APLICANDO OTIMIZAÇÕES DE PERFORMANCE - {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print("=" * 80)
    
    try:
        criar_indices_performance()
        criar_view_materializada_estoque()
        otimizar_configuracoes_django()
        criar_endpoint_otimizado()
        criar_script_manutencao()
        
        print("=" * 80)
        print("✅ OTIMIZAÇÕES APLICADAS COM SUCESSO!")
        print("=" * 80)
        
        print("🎯 PRÓXIMOS PASSOS:")
        print("1. ✅ Índices criados no banco de dados")
        print("2. ✅ View materializada criada") 
        print("3. 📄 Arquivo de configurações gerado (configuracoes_performance.py)")
        print("4. 🚀 Endpoint otimizado criado (endpoint_estoque_otimizado.py)")
        print("5. 🔧 Script de manutenção criado (manutencao_performance.py)")
        
        print("\n💡 RECOMENDAÇÕES:")
        print("• Integre o endpoint otimizado ao seu projeto")
        print("• Configure Redis para cache em produção")
        print("• Execute manutenção semanalmente")
        print("• Monitore logs de performance")
        print("\n🚀 Os endpoints devem estar significativamente mais rápidos agora!")
        
    except Exception as e:
        print(f"❌ Erro durante aplicação das otimizações: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
