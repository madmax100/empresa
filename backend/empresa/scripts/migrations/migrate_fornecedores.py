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
        logging.FileHandler('migration_fornecedores.log'),
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

def determinar_tipo_pessoa(cnpj):
    """Determina o tipo de pessoa baseado no CNPJ/CPF"""
    if not cnpj:
        return 'J'  # Default para pessoa jurídica
    cleaned = clean_cpf_cnpj(cnpj)
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
    """Cria a tabela fornecedores se não existir"""
    try:
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS fornecedores (
            id INTEGER PRIMARY KEY,
            tipo_pessoa CHAR(1),
            nome VARCHAR(100) NOT NULL,
            cpf_cnpj VARCHAR(14),
            rg_ie VARCHAR(20),
            endereco VARCHAR(100),
            numero VARCHAR(10),
            complemento VARCHAR(50),
            bairro VARCHAR(50),
            cidade VARCHAR(50),
            estado CHAR(2),
            cep VARCHAR(11),
            telefone VARCHAR(20),
            email VARCHAR(100),
            contato_nome VARCHAR(100),
            contato_telefone VARCHAR(20),
            tipo VARCHAR(50),
            data_cadastro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            ativo BOOLEAN DEFAULT true
        );

        CREATE INDEX IF NOT EXISTS idx_fornecedores_nome ON fornecedores (nome);
        CREATE INDEX IF NOT EXISTS idx_fornecedores_cpf_cnpj ON fornecedores (cpf_cnpj);
        CREATE INDEX IF NOT EXISTS idx_fornecedores_cidade ON fornecedores (cidade);
        CREATE INDEX IF NOT EXISTS idx_fornecedores_tipo ON fornecedores (tipo);
        """)
        logger.info("Estrutura da tabela fornecedores verificada/criada com sucesso")
    except Exception as e:
        logger.error(f"Erro ao criar tabela fornecedores: {str(e)}")
        raise

def clean_tables(pg_conn):
    """Limpa as tabelas no PostgreSQL"""
    try:
        cursor = pg_conn.cursor()
        logger.info("Iniciando limpeza das tabelas...")
        
        # Desabilitar verificação de chaves estrangeiras
        cursor.execute("SET session_replication_role = 'replica';")
        
        tabelas_dependentes = [
            'notas_fiscais_entrada',
            'lotes',
            'fornecedores'
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

def migrate_fornecedores():
    """Função principal de migração dos fornecedores"""
    start_time = datetime.now()
    logger.info(f"Iniciando migração de fornecedores às {start_time}")
    
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
        
        # Primeiro, vamos verificar as colunas disponíveis
        access_cursor.execute("SELECT * FROM Fornecedores WHERE 1=0")
        colunas_disponiveis = [desc[0] for desc in access_cursor.description]
        logger.info(f"Colunas disponíveis na tabela Fornecedores: {colunas_disponiveis}")
        
        # Consulta com as colunas na ordem correta
        access_cursor.execute("""
            SELECT codigo, nome, endereco, bairro, cidade, 
                   uf, cep, fone, fax, cgc, 
                   cgf, contato, datacadastro, celular, email,
                   especificacao, tipo, IBGE
            FROM Fornecedores 
            ORDER BY codigo
        """)
        
        # SQL de inserção
        insert_sql = """
            INSERT INTO fornecedores (
                id, tipo_pessoa, nome, cpf_cnpj, rg_ie,
                endereco, bairro, cidade, estado, cep,
                telefone, email, contato_nome, contato_telefone,
                tipo, data_cadastro, ativo
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, %s, %s
            )
        """
        
        # Processo de migração
        contador = 0
        erros = 0
        
        logger.info("Iniciando migração dos registros...")
        
        for row in access_cursor.fetchall():
            try:
                fornecedor_id = int(row[0])
                nome = clean_string(row[1])
                
                if not nome:
                    logger.warning(f"Fornecedor {fornecedor_id} ignorado: nome vazio")
                    continue
                
                cpf_cnpj = clean_cpf_cnpj(row[9])  # cgc
                tipo_pessoa = determinar_tipo_pessoa(cpf_cnpj)
                
                # Data de cadastro
                data_cadastro = row[12] if row[12] else datetime.now()
                
                # Tipo do fornecedor (posição 16)
                tipo_fornecedor = clean_string(row[16]) if len(row) > 16 and row[16] else None
                
                dados = (
                    fornecedor_id,               # id
                    tipo_pessoa,                 # tipo_pessoa
                    nome,                        # nome
                    cpf_cnpj,                    # cpf_cnpj
                    clean_string(row[10]),       # rg_ie (cgf)
                    clean_string(row[2]),        # endereco
                    clean_string(row[3]),        # bairro
                    clean_string(row[4]),        # cidade
                    clean_string(row[5]),        # estado (uf)
                    clean_cep(row[6]),           # cep
                    clean_phone(row[7]),         # telefone (fone)
                    clean_string(row[14]),       # email
                    clean_string(row[11]),       # contato_nome (contato)
                    clean_phone(row[13]),        # contato_telefone (celular)
                    tipo_fornecedor,             # tipo
                    data_cadastro,               # data_cadastro
                    True                         # ativo
                )
                
                pg_cursor.execute(insert_sql, dados)
                pg_conn.commit()
                contador += 1
                
                if contador % 100 == 0:
                    logger.info(f"Migrados {contador} fornecedores...")
                
            except Exception as e:
                erros += 1
                logger.error(f"Erro ao migrar fornecedor {row[0]}: {str(e)}")
                pg_conn.rollback()
                continue
        
        # Atualizar sequence
        pg_cursor.execute("""
            SELECT setval(pg_get_serial_sequence('fornecedores', 'id'), 
                         COALESCE((SELECT MAX(id) FROM fornecedores), 1), 
                         true);
        """)
        pg_conn.commit()
        
        end_time = datetime.now()
        duration = end_time - start_time
        
        logger.info(f"""
        Migração concluída em {duration}:
        - Total de fornecedores migrados: {contador}
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
        migrate_fornecedores()
    except KeyboardInterrupt:
        logger.info("Migração interrompida pelo usuário")
    except Exception as e:
        logger.error(f"Erro não tratado: {str(e)}")