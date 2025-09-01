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
        logging.FileHandler('migration_clientes.log'),
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
        if isinstance(value, str):
            cleaned = value.replace(',', '.')
        else:
            cleaned = str(value)
        return Decimal(cleaned).quantize(Decimal('0.01'))
    except:
        return Decimal('0.00')

def determinar_tipo_pessoa(cpf_cnpj):
    """Determina o tipo de pessoa baseado no documento"""
    if not cpf_cnpj:
        return None
    cleaned = clean_cpf_cnpj(cpf_cnpj)
    if not cleaned:
        return None
    return 'F' if len(cleaned) <= 11 else 'J'

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
    """Cria a tabela clientes se não existir"""
    try:
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS clientes (
            id INTEGER PRIMARY KEY,
            tipo_pessoa CHAR(1),
            nome VARCHAR(100) NOT NULL,
            cpf_cnpj VARCHAR(20),
            rg_ie VARCHAR(20),
            data_nascimento DATE,
            endereco VARCHAR(100),
            numero VARCHAR(10),
            complemento VARCHAR(50),
            bairro VARCHAR(50),
            cidade VARCHAR(50),
            estado CHAR(2),
            cep VARCHAR(25),
            telefone VARCHAR(20),
            email VARCHAR(100),
            limite_credito DECIMAL(10,2),
            data_cadastro TIMESTAMP,
            ativo BOOLEAN DEFAULT true,
            contato VARCHAR(50)
        );

        CREATE INDEX IF NOT EXISTS idx_clientes_nome ON clientes (nome);
        CREATE INDEX IF NOT EXISTS idx_clientes_cpf_cnpj ON clientes (cpf_cnpj);
        CREATE INDEX IF NOT EXISTS idx_clientes_cidade ON clientes (cidade);
        """)
        logger.info("Estrutura da tabela clientes verificada/criada com sucesso")
    except Exception as e:
        logger.error(f"Erro ao criar tabela clientes: {str(e)}")
        raise

def clean_tables(pg_conn):
    """Limpa as tabelas no PostgreSQL"""
    try:
        cursor = pg_conn.cursor()
        logger.info("Iniciando limpeza das tabelas...")
        
        cursor.execute("SET session_replication_role = 'replica';")
        
        tabelas_dependentes = [
            'contas_receber',
            'notas_fiscais_saida',
            'notas_fiscais_servico',
            'contratos_locacao',
            'clientes'
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

def migrate_clientes():
    """Função principal de migração dos clientes"""
    start_time = datetime.now()
    logger.info(f"Iniciando migração de clientes às {start_time}")
    
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
            SELECT CODCLIENTE, NOME, ENDERECO, BAIRRO, CIDADE, UF, CEP, 
                   FONE, [CPF/CGC] as CPF_CGC, DATACADASTRO, CONTATO, 
                   [RG/IE] as RG_IE, EMAIL, LIMITE
            FROM Clientes 
            ORDER BY CODCLIENTE
        """)
        
        insert_sql = """
            INSERT INTO clientes (
                id, tipo_pessoa, nome, cpf_cnpj, rg_ie,
                endereco, bairro, cidade, estado, cep,
                telefone, email, contato, limite_credito,
                data_cadastro, ativo
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, %s
            )
        """
        
        contador = 0
        erros = 0
        
        logger.info("Iniciando migração dos registros...")
        
        for row in access_cursor.fetchall():
            try:
                cliente_id = int(row[0])
                nome = clean_string(row[1])
                
                if not nome:
                    logger.warning(f"Cliente {cliente_id} ignorado: nome vazio")
                    continue
                
                # CPF/CNPJ e tipo de pessoa
                cpf_cnpj = clean_cpf_cnpj(row[8])
                tipo_pessoa = determinar_tipo_pessoa(cpf_cnpj)
                
                # Limite de crédito
                limite_credito = clean_decimal(row[13])
                
                # Data de cadastro
                data_cadastro = row[9] if row[9] else datetime.now()
                
                dados = (
                    cliente_id,                 # id
                    tipo_pessoa,                # tipo_pessoa
                    nome,                       # nome
                    cpf_cnpj,                   # cpf_cnpj
                    clean_string(row[11]),      # rg_ie
                    clean_string(row[2]),       # endereco
                    clean_string(row[3]),       # bairro
                    clean_string(row[4]),       # cidade
                    clean_string(row[5]),       # estado
                    clean_cep(row[6]),          # cep
                    clean_phone(row[7]),        # telefone
                    clean_string(row[12]),      # email
                    clean_string(row[10]),      # contato
                    limite_credito,             # limite_credito
                    data_cadastro,              # data_cadastro
                    True                        # ativo
                )
                
                pg_cursor.execute(insert_sql, dados)
                pg_conn.commit()
                contador += 1
                
                if contador % 100 == 0:
                    logger.info(f"Migrados {contador} clientes...")
                
            except Exception as e:
                erros += 1
                logger.error(f"Erro ao migrar cliente {row[0]}: {str(e)}")
                pg_conn.rollback()
                continue
        
        # Atualizar sequence
        pg_cursor.execute("""
            SELECT setval(pg_get_serial_sequence('clientes', 'id'), 
                         COALESCE((SELECT MAX(id) FROM clientes), 1), 
                         true);
        """)
        pg_conn.commit()
        
        end_time = datetime.now()
        duration = end_time - start_time
        
        logger.info(f"""
        Migração concluída em {duration}:
        - Total de clientes migrados: {contador}
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
        migrate_clientes()
    except KeyboardInterrupt:
        logger.info("Migração interrompida pelo usuário")
    except Exception as e:
        logger.error(f"Erro não tratado: {str(e)}")