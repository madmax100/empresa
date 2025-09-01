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
from config import PG_CONFIG, CADASTROS_DB, ACCESS_PASSWORD

# Data de corte para migração
DATA_CORTE = date(2024, 1, 1)

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('migration_itens_contrato.log'),
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
                f'DBQ={CADASTROS_DB};'
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

def clean_date(value):
    """Limpa e valida data"""
    if not value:
        return None
    if isinstance(value, (date, datetime)):
        return value
    return None

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

def verificar_contratos_validos(pg_cursor):
    """Carrega contratos válidos (a partir de 2024)"""
    try:
        pg_cursor.execute("""
            SELECT id, contrato 
            FROM contratos_locacao 
            WHERE inicio >= %s OR fim >= %s
        """, (DATA_CORTE, DATA_CORTE))
        return {row[1]: row[0] for row in pg_cursor.fetchall()}
    except Exception as e:
        logger.error(f"Erro ao verificar contratos válidos: {str(e)}")
        raise

def verificar_categorias(pg_cursor):
    """Verifica categorias cadastradas"""
    try:
        pg_cursor.execute("SELECT id FROM categorias_produtos")
        return {row[0] for row in pg_cursor.fetchall()}
    except Exception as e:
        logger.error(f"Erro ao verificar categorias: {str(e)}")
        raise

def clean_tables(pg_conn):
    """Limpa as tabelas no PostgreSQL"""
    try:
        cursor = pg_conn.cursor()
        logger.info("Iniciando limpeza das tabelas...")
        
        cursor.execute("SET session_replication_role = 'replica';")
        
        tabelas = ['itens_contrato_locacao']
        
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

def migrate_itens_contrato():
    """Função principal de migração dos itens de contratos"""
    start_time = datetime.now()
    logger.info(f"Iniciando migração de itens de contratos às {start_time}")
    
    access_conn = None
    pg_conn = None
    
    try:
        logger.info("Estabelecendo conexões com os bancos de dados...")
        access_conn = DatabaseConfig.get_access_conn()
        pg_conn = DatabaseConfig.get_postgres_conn()
        
        clean_tables(pg_conn)
        
        pg_cursor = pg_conn.cursor()
        
        # Carregar dados relacionados
        contratos_validos = verificar_contratos_validos(pg_cursor)
        categorias_validas = verificar_categorias(pg_cursor)
        
        logger.info("Consultando dados do Access...")
        access_cursor = access_conn.cursor()
        
        # Query para buscar itens dos contratos válidos
        query = """
        SELECT i.Codigo, i.Contrato, i.Serie, i.Categoria,
               i.Modelo, i.Inicio, i.Fim
        FROM [Itens dos Contratos] i
        INNER JOIN Contratos c ON i.Contrato = c.Contrato
        WHERE c.Incio >= #2024/01/01# OR c.Fim >= #2024/01/01#
        ORDER BY i.Codigo
        """
        
        access_cursor.execute(query)
        
        insert_sql = """
            INSERT INTO itens_contrato_locacao (
                id, contrato_id, numeroserie, categoria_id,
                modelo, inicio, fim
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s
            )
        """
        
        contador = 0
        erros = 0
        contratos_nao_encontrados = set()
        categorias_nao_encontradas = set()
        
        logger.info("Iniciando migração dos itens...")
        
        for row in access_cursor.fetchall():
            try:
                # Validar contrato
                contrato_numero = clean_string(row[1])
                contrato_id = contratos_validos.get(contrato_numero)
                
                if not contrato_id:
                    contratos_nao_encontrados.add(contrato_numero)
                    continue
                
                # Validar categoria
                categoria_id = int(row[3]) if row[3] else None
                if categoria_id and categoria_id not in categorias_validas:
                    categorias_nao_encontradas.add(categoria_id)
                    categoria_id = None
                
                dados = (
                    int(row[0]),                # id
                    contrato_id,                # contrato_id
                    clean_string(row[2]),       # numeroserie
                    categoria_id,               # categoria_id
                    clean_string(row[4]),       # modelo
                    clean_date(row[5]),         # inicio
                    clean_date(row[6])          # fim
                )
                
                pg_cursor.execute(insert_sql, dados)
                pg_conn.commit()
                contador += 1
                
                if contador % 100 == 0:
                    logger.info(f"Migrados {contador} itens...")
            
            except Exception as e:
                erros += 1
                logger.error(f"Erro ao migrar item {row[0]}: {str(e)}")
                pg_conn.rollback()
                continue
        
        end_time = datetime.now()
        duration = end_time - start_time
        
        logger.info(f"""
        Migração concluída em {duration}:
        - Total de itens migrados: {contador}
        - Total de erros: {erros}
        """)
        
        if contratos_nao_encontrados:
            logger.warning("\nContratos não encontrados:")
            for c in sorted(contratos_nao_encontrados):
                logger.warning(f"- Contrato {c}")
        
        if categorias_nao_encontradas:
            logger.warning("\nCategorias não encontradas:")
            for c in sorted(categorias_nao_encontradas):
                logger.warning(f"- Categoria {c}")
        
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
        migrate_itens_contrato()
    except KeyboardInterrupt:
        logger.info("Migração interrompida pelo usuário")
    except Exception as e:
        logger.error(f"Erro não tratado: {str(e)}")