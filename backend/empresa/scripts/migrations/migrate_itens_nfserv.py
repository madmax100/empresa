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
from config import PG_CONFIG, MOVIMENTOS_DB, ACCESS_PASSWORD

# Data de corte para migração
DATA_CORTE = date(2024, 1, 1)

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('migration_itens_nfserv.log'),
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
                f'DBQ={MOVIMENTOS_DB};'
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

def verificar_notas_validas(pg_cursor):
    """Carrega notas fiscais de serviço válidas (a partir de 2024)"""
    try:
        pg_cursor.execute("""
            SELECT id, numero_nota 
            FROM notas_fiscais_servico 
            WHERE data >= %s
        """, (DATA_CORTE,))
        return {row[1]: row[0] for row in pg_cursor.fetchall()}
    except Exception as e:
        logger.error(f"Erro ao verificar notas válidas: {str(e)}")
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
        
        tabelas = ['itens_nf_servico']
        
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

def migrate_itens_nfserv():
    """Função principal de migração dos itens de notas fiscais de serviço"""
    start_time = datetime.now()
    logger.info(f"Iniciando migração de itens de NFSERV às {start_time}")
    
    access_conn = None
    pg_conn = None
    
    try:
        logger.info("Estabelecendo conexões com os bancos de dados...")
        access_conn = DatabaseConfig.get_access_conn()
        pg_conn = DatabaseConfig.get_postgres_conn()
        
        clean_tables(pg_conn)
        
        pg_cursor = pg_conn.cursor()
        
        # Carregar notas válidas
        notas_validas = verificar_notas_validas(pg_cursor)
        
        logger.info("Consultando dados do Access...")
        access_cursor = access_conn.cursor()
        
        # Query para buscar itens de notas a partir de 2024
        query = """
        SELECT i.NumNFSERV, i.Data, i.Serviços,
               i.Qtde, i.Valor, i.Total
        FROM [Itens da NFSERV] i
        INNER JOIN NFSERV n ON i.NumNFSERV = n.NumNFSERV
        WHERE n.Data >= #2024/01/01#
        ORDER BY i.NumNFSERV
        """
        
        access_cursor.execute(query)
        
        insert_sql = """
            INSERT INTO itens_nf_servico (
                nota_fiscal_id, data, servico,
                quantidade, valor_unitario, valor_total
            ) VALUES (
                %s, %s, %s, %s, %s, %s
            )
        """
        
        contador = 0
        erros = 0
        notas_nao_encontradas = set()
        
        logger.info("Iniciando migração dos itens...")
        
        for row in access_cursor.fetchall():
            try:
                num_nfserv = clean_string(row[0])
                nota_fiscal_id = notas_validas.get(num_nfserv)
                
                if not nota_fiscal_id:
                    notas_nao_encontradas.add(num_nfserv)
                    continue
                
                # Calcular valor total
                quantidade = clean_decimal(row[3])
                valor_unitario = clean_decimal(row[4])
                valor_total = quantidade * valor_unitario
                
                dados = (
                    nota_fiscal_id,             # nota_fiscal_id
                    clean_date(row[1]),         # data
                    clean_string(row[2]),       # servico
                    quantidade,                 # quantidade
                    valor_unitario,            # valor_unitario
                    valor_total                # valor_total
                )
                
                pg_cursor.execute(insert_sql, dados)
                pg_conn.commit()
                contador += 1
                
                if contador % 100 == 0:
                    logger.info(f"Migrados {contador} itens...")
            
            except Exception as e:
                erros += 1
                logger.error(f"Erro ao migrar item da NFS {row[0]}: {str(e)}")
                pg_conn.rollback()
                continue
        
        end_time = datetime.now()
        duration = end_time - start_time
        
        logger.info(f"""
        Migração concluída em {duration}:
        - Total de itens migrados: {contador}
        - Total de erros: {erros}
        """)
        
        if notas_nao_encontradas:
            logger.warning("\nNotas fiscais não encontradas:")
            for nf in sorted(notas_nao_encontradas):
                logger.warning(f"- NF {nf}")
        
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
        migrate_itens_nfserv()
    except KeyboardInterrupt:
        logger.info("Migração interrompida pelo usuário")
    except Exception as e:
        logger.error(f"Erro não tratado: {str(e)}")