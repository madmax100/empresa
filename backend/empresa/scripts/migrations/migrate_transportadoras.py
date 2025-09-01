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
        logging.FileHandler('migration_transportadoras.log'),
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

def clean_cpf_cnpj(value):
    """Limpa e valida CPF/CNPJ"""
    if value is None:
        return None
    cleaned = re.sub(r'[^\d]', '', str(value))
    return cleaned if cleaned else None

def clean_phone(value):
    """Limpa e valida número de telefone"""
    if value is None:
        return None
    cleaned = re.sub(r'[^\d]', '', str(value))
    return cleaned if cleaned else None

def clean_cep(value):
    """Limpa e valida CEP"""
    if value is None:
        return None
    cleaned = re.sub(r'[^\d]', '', str(value))
    return cleaned if cleaned else None

def clean_decimal(value):
    """Limpa e valida valor decimal"""
    if value is None:
        return Decimal('0.00')
    try:
        cleaned = str(value).replace(',', '.')
        return Decimal(cleaned)
    except:
        return Decimal('0.00')

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
    """Cria a tabela transportadoras se não existir"""
    try:
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS transportadoras (
            id INTEGER PRIMARY KEY,
            razao_social VARCHAR(100) NOT NULL,
            nome VARCHAR(100),
            cnpj VARCHAR(20),
            ie VARCHAR(20),
            endereco VARCHAR(100),
            numero VARCHAR(10),
            complemento VARCHAR(50),
            bairro VARCHAR(50),
            cidade VARCHAR(50),
            estado CHAR(2),
            cep VARCHAR(15),
            fone VARCHAR(20),
            celular VARCHAR(20),
            email VARCHAR(100),
            contato_principal VARCHAR(100),
            site_rastreamento VARCHAR(200),
            formato_codigo_rastreio VARCHAR(50),
            prazo_medio_entrega INTEGER,
            valor_minimo_frete DECIMAL(10,2),
            percentual_seguro DECIMAL(5,2),
            observacoes TEXT,
            data_cadastro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            ativo BOOLEAN DEFAULT true,
            contato VARCHAR(50)
        );

        CREATE INDEX IF NOT EXISTS idx_transportadoras_razao_social ON transportadoras (razao_social);
        CREATE INDEX IF NOT EXISTS idx_transportadoras_cnpj ON transportadoras (cnpj);
        CREATE INDEX IF NOT EXISTS idx_transportadoras_cidade ON transportadoras (cidade);
        """)
        logger.info("Estrutura da tabela transportadoras verificada/criada com sucesso")
    except Exception as e:
        logger.error(f"Erro ao criar tabela transportadoras: {str(e)}")
        raise

def clean_tables(pg_conn):
    """Limpa as tabelas no PostgreSQL"""
    try:
        cursor = pg_conn.cursor()
        logger.info("Iniciando limpeza das tabelas...")
        
        cursor.execute("SET session_replication_role = 'replica';")
        
        tabelas_dependentes = [
            'notas_fiscais_entrada',
            'notas_fiscais_saida',
            'fretes',
            'transportadoras'
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

def migrate_transportadoras():
    """Função principal de migração das transportadoras"""
    start_time = datetime.now()
    logger.info(f"Iniciando migração de transportadoras às {start_time}")
    
    access_conn = None
    pg_conn = None
    
    try:
        logger.info("Estabelecendo conexões com os bancos de dados...")
        access_conn = DatabaseConfig.get_access_conn()
        pg_conn = DatabaseConfig.get_postgres_conn()
        
        clean_tables(pg_conn)
        
        pg_cursor = pg_conn.cursor()
        create_table_if_not_exists(pg_cursor)
        
        logger.info("Consultando dados do Access...")
        access_cursor = access_conn.cursor()
        access_cursor.execute("""
            SELECT codigo, nome, endereco, bairro, cidade, 
                   cep, fone, celular, Contato, Região, 
                   CNPJ, UF, IE, EMAIL, datacadastro
            FROM Transportadoras 
            ORDER BY codigo
        """)
        
        insert_sql = """
            INSERT INTO transportadoras (
                id, razao_social, nome, cnpj, ie,
                endereco, bairro, cidade, estado, cep,
                fone, celular, email, contato_principal,
                data_cadastro, ativo,
                prazo_medio_entrega, valor_minimo_frete, percentual_seguro
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, %s, %s, %s, %s
            )
        """
        
        contador = 0
        erros = 0
        
        logger.info("Iniciando migração dos registros...")
        
        for row in access_cursor.fetchall():
            try:
                transportadora_id = int(row[0])
                razao_social = clean_string(row[1])
                
                if not razao_social:
                    logger.warning(f"Transportadora {transportadora_id} ignorada: razão social vazia")
                    continue
                
                dados = (
                    transportadora_id,          # id
                    razao_social,              # razao_social
                    razao_social,              # nome (mesmo que razao_social)
                    clean_cpf_cnpj(row[10]),   # cnpj
                    clean_string(row[12]),     # ie
                    clean_string(row[2]),      # endereco
                    clean_string(row[3]),      # bairro
                    clean_string(row[4]),      # cidade
                    clean_string(row[11]),     # estado (UF)
                    clean_cep(row[5]),         # cep
                    clean_phone(row[6]),       # fone
                    clean_phone(row[7]),       # celular
                    clean_string(row[13]),     # email
                    clean_string(row[8]),      # contato_principal (Contato)
                    row[14] or datetime.now(), # data_cadastro
                    True,                      # ativo
                    5,                         # prazo_medio_entrega (default)
                    Decimal('0.00'),           # valor_minimo_frete (default)
                    Decimal('0.00')            # percentual_seguro (default)
                )
                
                pg_cursor.execute(insert_sql, dados)
                pg_conn.commit()
                contador += 1
                
                if contador % 100 == 0:
                    logger.info(f"Migradas {contador} transportadoras...")
                
            except Exception as e:
                erros += 1
                logger.error(f"Erro ao migrar transportadora {row[0]}: {str(e)}")
                pg_conn.rollback()
                continue
        
        # Atualizar sequence
        pg_cursor.execute("""
            SELECT setval(pg_get_serial_sequence('transportadoras', 'id'), 
                         COALESCE((SELECT MAX(id) FROM transportadoras), 1), 
                         true);
        """)
        pg_conn.commit()
        
        end_time = datetime.now()
        duration = end_time - start_time
        
        logger.info(f"""
        Migração concluída em {duration}:
        - Total de transportadoras migradas: {contador}
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
        migrate_transportadoras()
    except KeyboardInterrupt:
        logger.info("Migração interrompida pelo usuário")
    except Exception as e:
        logger.error(f"Erro não tratado: {str(e)}")