import os
import sys
import logging
from datetime import datetime, date
import pyodbc
import psycopg2
from psycopg2 import errorcodes
from decimal import Decimal, InvalidOperation
import re

# Importar configurações
from config import PG_CONFIG, CONTAS_DB, ACCESS_PASSWORD

# Data de corte para migração
DATA_CORTE = date(2024, 1, 1)

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('migration_contas_pagar.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

class DatabaseConfig:
    """Configurações de conexão com os bancos de dados"""
    
    @staticmethod
    def get_postgres_conn():
        """Retorna conexão com PostgreSQL"""
        try:
            return psycopg2.connect(**PG_CONFIG)
        except Exception as e:
            logger.error(f"Erro ao conectar ao PostgreSQL: {str(e)}")
            raise

    @staticmethod
    def get_access_conn():
        """Retorna conexão com MS Access"""
        try:
            conn_str = (
                r'Driver={Microsoft Access Driver (*.mdb, *.accdb)};'
                f'DBQ={CONTAS_DB};'
                f'PWD={ACCESS_PASSWORD};'
            )
            return pyodbc.connect(conn_str)
        except Exception as e:
            logger.error(f"Erro ao conectar ao Access: {str(e)}")
            raise

def clean_string(value):
    """Limpa e valida uma string"""
    if value is None:
        return None
    cleaned = str(value).strip()
    return cleaned if cleaned else None

def clean_decimal(value):
    """Limpa e valida valor decimal"""
    if value is None:
        return Decimal('0.00')
    try:
        if isinstance(value, str):
            cleaned = value.replace(',', '.')
        else:
            cleaned = str(value)
        return Decimal(cleaned).quantize(Decimal('0.01'))
    except:
        return Decimal('0.00')

def clean_date(value):
    """Limpa e valida data"""
    if not value:
        return None
    if isinstance(value, (date, datetime)):
        return value
    return None

def determinar_status(pagamento, valor_pago, valor_total):
    """Determina o status do título"""
    if pagamento:
        if valor_pago >= valor_total:
            return 'P'  # Pago
        return 'A'  # Em aberto com pagamento parcial
    return 'A'  # Em aberto

def verificar_fornecedores(pg_cursor):
    """Verifica fornecedores cadastrados"""
    try:
        pg_cursor.execute("SELECT id FROM fornecedores")
        return {row[0] for row in pg_cursor.fetchall()}
    except Exception as e:
        logger.error(f"Erro ao verificar fornecedores: {str(e)}")
        raise

def verificar_contas(pg_cursor):
    """Verifica contas bancárias cadastradas"""
    try:
        pg_cursor.execute("SELECT id FROM contas_bancarias")
        return {row[0] for row in pg_cursor.fetchall()}
    except Exception as e:
        logger.error(f"Erro ao verificar contas bancárias: {str(e)}")
        raise

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
        raise

def clean_tables(pg_conn):
    """Limpa as tabelas no PostgreSQL"""
    try:
        cursor = pg_conn.cursor()
        logger.info("Iniciando limpeza das tabelas...")
        
        cursor.execute("SET session_replication_role = 'replica';")
        
        tabelas = ['contas_pagar']
        
        for tabela in tabelas:
            try:
                if verify_table_exists(cursor, tabela):
                    logger.info(f"Limpando tabela {tabela}...")
                    cursor.execute(f"TRUNCATE TABLE {tabela} CASCADE")
                    logger.info(f"Tabela {tabela} limpa com sucesso")
            except Exception as e:
                logger.error(f"Erro ao limpar tabela {tabela}: {str(e)}")
                raise
        
        cursor.execute("SET session_replication_role = 'origin';")
        pg_conn.commit()
        logger.info("Limpeza de tabelas concluída com sucesso")
        return True
        
    except Exception as e:
        logger.error(f"Erro durante processo de limpeza: {str(e)}")
        pg_conn.rollback()
        raise

def migrate_contas_pagar():
    """Função principal de migração das contas a pagar"""
    start_time = datetime.now()
    logger.info(f"Iniciando migração de contas a pagar às {start_time}")
    
    access_conn = None
    pg_conn = None
    
    try:
        logger.info("Estabelecendo conexões com os bancos de dados...")
        access_conn = DatabaseConfig.get_access_conn()
        pg_conn = DatabaseConfig.get_postgres_conn()
        
        clean_tables(pg_conn)
        
        pg_cursor = pg_conn.cursor()
        
        # Carregar dados relacionados
        fornecedores_validos = verificar_fornecedores(pg_cursor)
        contas_validas = verificar_contas(pg_cursor)
        
        logger.info("Consultando dados do Access...")
        access_cursor = access_conn.cursor()
        
        query = """
        SELECT [CodConta a Pagar], Data, Valor, Fornecedor, 
               Vencimento, ValorTotalPago, Historico, FormaPagto,
               Condicoes, Confirmacao, Juros, Tarifas, NDuplicata,
               DataPagto, ValorPago, Local, Status, Conta
        FROM Pagar 
        WHERE Data >= #2024/01/01# OR Vencimento >= #2024/01/01#
        ORDER BY [CodConta a Pagar]
        """
        
        access_cursor.execute(query)
        
        insert_sql = """
            INSERT INTO contas_pagar (
                id, data, valor, fornecedor_id, vencimento,
                valor_total_pago, historico, forma_pagamento,
                condicoes, confirmacao, juros, tarifas,
                numero_duplicata, data_pagamento, valor_pago,
                local, status, conta_id
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, %s, %s, %s
            )
        """
        
        contador = 0
        erros = 0
        fornecedores_nao_encontrados = set()
        contas_nao_encontradas = set()
        
        logger.info("Iniciando migração dos registros...")
        
        for row in access_cursor.fetchall():
            try:
                # Validar fornecedor
                fornecedor_id = int(row[3]) if row[3] else None
                if fornecedor_id and fornecedor_id not in fornecedores_validos:
                    fornecedores_nao_encontrados.add(fornecedor_id)
                    if not row[6]:  # Se não tem histórico, pula
                        continue
                
                # Validar conta bancária
                conta_id = int(row[17]) if row[17] else None
                if conta_id and conta_id not in contas_validas:
                    contas_nao_encontradas.add(conta_id)
                    conta_id = None
                
                # Calcular valores
                valor = clean_decimal(row[2])
                valor_pago = clean_decimal(row[14])
                valor_total_pago = (
                    valor_pago +
                    clean_decimal(row[10]) +  # juros
                    clean_decimal(row[11])    # tarifas
                )
                
                # Usar status diretamente do MS Access
                status_access = clean_string(row[16])  # Status do MS Access
                status = status_access if status_access else 'A'  # Default para 'A' se vazio
                
                dados = (
                    int(row[0]),                # id
                    clean_date(row[1]),         # data
                    valor,                      # valor
                    fornecedor_id,              # fornecedor_id
                    clean_date(row[4]),         # vencimento
                    valor_total_pago,           # valor_total_pago
                    clean_string(row[6]),       # historico
                    clean_string(row[7]),       # forma_pagamento
                    clean_string(row[8]),       # condicoes
                    clean_string(row[9]),       # confirmacao
                    clean_decimal(row[10]),     # juros
                    clean_decimal(row[11]),     # tarifas
                    clean_string(row[12]),      # numero_duplicata
                    clean_date(row[13]),        # data_pagamento
                    valor_pago,                 # valor_pago
                    clean_string(row[15]),      # local
                    status,                     # status
                    conta_id                    # conta_id
                )
                
                pg_cursor.execute(insert_sql, dados)
                pg_conn.commit()
                contador += 1
                
                if contador % 100 == 0:
                    logger.info(f"Migradas {contador} contas...")
            
            except Exception as e:
                erros += 1
                logger.error(f"Erro ao migrar conta {row[0]}: {str(e)}")
                pg_conn.rollback()
                continue
        
        end_time = datetime.now()
        duration = end_time - start_time
        
        logger.info(f"""
        Migração concluída em {duration}:
        - Total de contas migradas: {contador}
        - Total de erros: {erros}
        """)
        
        if fornecedores_nao_encontrados:
            logger.warning("\nFornecedores não encontrados:")
            for f in sorted(fornecedores_nao_encontrados):
                logger.warning(f"- Fornecedor {f}")
        
        if contas_nao_encontradas:
            logger.warning("\nContas bancárias não encontradas:")
            for c in sorted(contas_nao_encontradas):
                logger.warning(f"- Conta {c}")
        
        return True
        
    except Exception as e:
        logger.error(f"Erro durante a migração: {str(e)}")
        if pg_conn:
            pg_conn.rollback()
        return False
        
    finally:
        if access_conn:
            access_conn.close()
        if pg_conn:
            pg_conn.close()

if __name__ == "__main__":
    try:
        migrate_contas_pagar()
    except KeyboardInterrupt:
        logger.info("Migração interrompida pelo usuário")
    except Exception as e:
        logger.error(f"Erro não tratado: {str(e)}")