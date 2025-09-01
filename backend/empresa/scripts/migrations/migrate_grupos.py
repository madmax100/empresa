import os
import sys
import logging
from datetime import datetime
import pyodbc
import psycopg2
from psycopg2 import errorcodes
from decimal import Decimal, InvalidOperation
import re

# Importar configurações
from config import PG_CONFIG, CADASTROS_DB, ACCESS_PASSWORD

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('migration_grupos.log'),
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

def create_table_if_not_exists(cursor):
    """Cria a tabela grupos se não existir"""
    try:
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS grupos (
            id INTEGER PRIMARY KEY,
            nome VARCHAR(50) NOT NULL
        );

        CREATE INDEX IF NOT EXISTS idx_grupos_nome ON grupos (nome);
        """)
        logger.info("Estrutura da tabela grupos verificada/criada com sucesso")
    except Exception as e:
        logger.error(f"Erro ao criar tabela grupos: {str(e)}")
        raise

def clean_tables(pg_conn):
    """Limpa as tabelas no PostgreSQL"""
    try:
        cursor = pg_conn.cursor()
        logger.info("Iniciando limpeza das tabelas...")
        
        # Desabilitar verificação de chaves estrangeiras
        cursor.execute("SET session_replication_role = 'replica';")
        
        tabelas_dependentes = [
            'produtos',  # Tabelas que dependem de grupos
            'grupos'
        ]
        
        for tabela in tabelas_dependentes:
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

def migrate_grupos():
    """Função principal de migração dos grupos"""
    start_time = datetime.now()
    logger.info(f"Iniciando migração de grupos às {start_time}")
    
    access_conn = None
    pg_conn = None
    
    try:
        # Estabelecer conexões
        logger.info("Estabelecendo conexões com os bancos de dados...")
        access_conn = DatabaseConfig.get_access_conn()
        pg_conn = DatabaseConfig.get_postgres_conn()
        
        # Limpar tabelas
        clean_tables(pg_conn)
        
        # Criar estrutura da tabela se não existir
        pg_cursor = pg_conn.cursor()
        create_table_if_not_exists(pg_cursor)
        
        # Consulta dados do Access
        logger.info("Consultando dados do Access...")
        access_cursor = access_conn.cursor()
        access_cursor.execute("""
            SELECT Codigo, Descricao
            FROM Grupos
            ORDER BY Codigo
        """)
        
        # SQL de inserção
        insert_sql = """
            INSERT INTO grupos (id, nome)
            VALUES (%s, %s)
        """
        
        # Processo de migração
        contador = 0
        erros = 0
        
        logger.info("Iniciando migração dos registros...")
        
        for row in access_cursor.fetchall():
            try:
                grupo_id = int(row[0])
                nome = clean_string(row[1])
                
                if not nome:
                    logger.warning(f"Grupo {grupo_id} ignorado: nome vazio")
                    continue
                
                dados = (grupo_id, nome)
                
                pg_cursor.execute(insert_sql, dados)
                pg_conn.commit()
                contador += 1
                
                if contador % 100 == 0:
                    logger.info(f"Migrados {contador} grupos...")
                
            except Exception as e:
                erros += 1
                logger.error(f"Erro ao migrar grupo {row[0]}: {str(e)}")
                pg_conn.rollback()
                continue
        
        # Atualizar sequence
        pg_cursor.execute("""
            SELECT setval(pg_get_serial_sequence('grupos', 'id'), 
                         COALESCE((SELECT MAX(id) FROM grupos), 1), 
                         true);
        """)
        pg_conn.commit()
        
        end_time = datetime.now()
        duration = end_time - start_time
        
        logger.info(f"""
        Migração concluída em {duration}:
        - Total de grupos migrados: {contador}
        - Total de erros: {erros}
        """)
        
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
        migrate_grupos()
    except KeyboardInterrupt:
        logger.info("Migração interrompida pelo usuário")
    except Exception as e:
        logger.error(f"Erro não tratado: {str(e)}")