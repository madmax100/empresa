"""
Script para limpar todas as tabelas do PostgreSQL antes da importação
"""
import os
import sys
import logging
import psycopg2
from config import PG_CONFIG

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('clean_all_tables.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

# Lista completa de todas as tabelas na ordem correta para limpeza
# (das dependentes para as principais)
ALL_TABLES = [
    # Fluxo de Caixa
    'fluxo_caixa_lancamentos',
    'saldos_diarios', 
    'configuracoes_fluxo_caixa',
    
    # Tabelas dependentes de relacionamentos
    'itens_contrato_locacao',
    'itens_nf_entrada',
    'itens_nf_saida',
    'itens_nf_servico',
    'contas_receber',
    'contas_pagar',
    'contratos_locacao',
    'notas_fiscais_entrada',
    'notas_fiscais_saida',
    'notas_fiscais_servico',
    'movimentacoes_estoque',
    'contagens_inventario',
    'posicoes_estoque',
    'saldos_estoque',
    'pagamentos_funcionarios',
    'custos_adicionais_frete',
    'ocorrencias_frete',
    'despesas',
    
    # Tabelas de cadastros básicos
    'produtos',
    'clientes',
    'fornecedores',
    'funcionarios',
    'transportadoras',
    'empresas',
    'categorias_produtos',
    'categorias',
    'grupos',
    'marcas',
    'inventarios',
    'lotes',
    'locais_estoque',
    'regioes_entrega',
    'tabelas_frete',
    'tipos_movimentacao_estoque',
    'historico_rastreamento',
    'fretes',
    'contas_bancarias'
]

def verify_table_exists(cursor, table_name):
    """Verifica se uma tabela existe no PostgreSQL"""
    try:
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = %s
            );
        """, (table_name,))
        return cursor.fetchone()[0]
    except Exception as e:
        logger.error(f"Erro ao verificar existência da tabela {table_name}: {str(e)}")
        return False

def clean_all_tables():
    """Limpa todas as tabelas do PostgreSQL"""
    pg_conn = None
    
    try:
        logger.info("=== INICIANDO LIMPEZA COMPLETA DO BANCO DE DADOS ===")
        
        # Conectar ao PostgreSQL
        logger.info("Conectando ao PostgreSQL...")
        pg_conn = psycopg2.connect(**PG_CONFIG)
        cursor = pg_conn.cursor()
        
        # Desabilitar verificações de chave estrangeira temporariamente
        logger.info("Desabilitando verificações de chave estrangeira...")
        cursor.execute("SET session_replication_role = 'replica';")
        
        tables_cleaned = 0
        tables_not_found = 0
        
        # Limpar cada tabela
        for table_name in ALL_TABLES:
            try:
                if verify_table_exists(cursor, table_name):
                    logger.info(f"Limpando tabela: {table_name}")
                    cursor.execute(f"TRUNCATE TABLE {table_name} CASCADE")
                    tables_cleaned += 1
                    logger.info(f"[OK] Tabela {table_name} limpa com sucesso")
                else:
                    logger.warning(f"[AVISO] Tabela {table_name} não encontrada (pulando)")
                    tables_not_found += 1
                    
            except Exception as e:
                logger.error(f"[ERRO] Erro ao limpar tabela {table_name}: {str(e)}")
                # Continuar mesmo se uma tabela falhar
                continue
        
        # Reabilitar verificações de chave estrangeira
        logger.info("Reabilitando verificações de chave estrangeira...")
        cursor.execute("SET session_replication_role = 'origin';")
        
        # Resetar sequências de ID
        logger.info("Resetando sequências de ID...")
        cursor.execute("""
            SELECT 'SELECT SETVAL(' || quote_literal(quote_ident(sequence_namespace.nspname) || '.' || quote_ident(class_sequence.relname)) || ', 1, false);'
            FROM pg_class AS class_sequence
            JOIN pg_namespace AS sequence_namespace ON class_sequence.relnamespace = sequence_namespace.oid
            WHERE class_sequence.relkind = 'S'
            AND sequence_namespace.nspname = 'public';
        """)
        
        reset_commands = cursor.fetchall()
        for (command,) in reset_commands:
            cursor.execute(command)
        
        # Commit das mudanças
        pg_conn.commit()
        
        logger.info("=== LIMPEZA COMPLETA FINALIZADA ===")
        logger.info(f"Tabelas limpas: {tables_cleaned}")
        logger.info(f"Tabelas não encontradas: {tables_not_found}")
        logger.info(f"Total de tabelas processadas: {len(ALL_TABLES)}")
        
        return True
        
    except Exception as e:
        logger.error(f"Erro durante a limpeza completa: {str(e)}")
        if pg_conn:
            pg_conn.rollback()
        return False
        
    finally:
        if pg_conn:
            pg_conn.close()
            logger.info("Conexão com PostgreSQL encerrada")

def main():
    """Função principal"""
    logger.info("Iniciando script de limpeza completa de tabelas...")
    
    if clean_all_tables():
        logger.info("Limpeza completa executada com sucesso!")
        return True
    else:
        logger.error("Limpeza completa falhou!")
        return False

if __name__ == "__main__":
    try:
        if main():
            sys.exit(0)
        else:
            sys.exit(1)
    except KeyboardInterrupt:
        logger.error("Limpeza interrompida pelo usuário!")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Erro não tratado: {str(e)}")
        sys.exit(1)
