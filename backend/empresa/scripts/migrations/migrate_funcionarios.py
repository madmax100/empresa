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
        logging.FileHandler('migration_funcionarios.log'),
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

def clean_cpf(value):
    """Limpa e valida CPF"""
    if value is None:
        return None
    cleaned = re.sub(r'[^\d]', '', str(value))
    return cleaned if len(cleaned) == 11 else None

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
    """Cria a tabela funcionarios se não existir"""
    try:
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS funcionarios (
            id INTEGER PRIMARY KEY,
            nome VARCHAR(100) NOT NULL,
            cpf VARCHAR(11),
            rg VARCHAR(20),
            data_nascimento DATE,
            data_admissao DATE,
            data_demissao DATE,
            cargo VARCHAR(50),
            salario_base DECIMAL(10,2),
            endereco VARCHAR(100),
            numero VARCHAR(10),
            complemento VARCHAR(50),
            bairro VARCHAR(50),
            cidade VARCHAR(50),
            estado CHAR(2),
            cep VARCHAR(8),
            telefone VARCHAR(20),
            email VARCHAR(100),
            banco VARCHAR(50),
            agencia VARCHAR(10),
            conta VARCHAR(20),
            pix VARCHAR(100),
            data_cadastro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            ativo BOOLEAN DEFAULT true
        );

        CREATE INDEX IF NOT EXISTS idx_funcionarios_nome ON funcionarios (nome);
        CREATE INDEX IF NOT EXISTS idx_funcionarios_cpf ON funcionarios (cpf);
        CREATE INDEX IF NOT EXISTS idx_funcionarios_cargo ON funcionarios (cargo);
        """)
        logger.info("Estrutura da tabela funcionarios verificada/criada com sucesso")
    except Exception as e:
        logger.error(f"Erro ao criar tabela funcionarios: {str(e)}")
        raise

def clean_tables(pg_conn):
    """Limpa as tabelas no PostgreSQL"""
    try:
        cursor = pg_conn.cursor()
        logger.info("Iniciando limpeza das tabelas...")
        
        cursor.execute("SET session_replication_role = 'replica';")
        
        tabelas_dependentes = [
            'pagamentos_funcionarios',
            'notas_fiscais_saida',  # onde o funcionário pode ser vendedor
            'notas_fiscais_servico',
            'funcionarios'
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

def migrate_funcionarios():
    """Função principal de migração dos funcionários"""
    start_time = datetime.now()
    logger.info(f"Iniciando migração de funcionários às {start_time}")
    
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
                   cep, fone, celular, cpf, rg, funcao, 
                   salario, dataadmissao, email
            FROM Funcionarios 
            ORDER BY codigo
        """)
        
        insert_sql = """
            INSERT INTO funcionarios (
                id, nome, cpf, rg, cargo,
                salario_base, endereco, bairro, cidade,
                estado, cep, telefone, email,
                data_admissao, data_cadastro, ativo
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
                funcionario_id = int(row[0])
                nome = clean_string(row[1])
                
                if not nome:
                    logger.warning(f"Funcionário {funcionario_id} ignorado: nome vazio")
                    continue
                
                # Tratamento do salário
                salario = clean_decimal(row[11])
                if salario == Decimal('0.00'):
                    logger.warning(f"Funcionário {funcionario_id}: salário zerado")
                
                dados = (
                    funcionario_id,             # id
                    nome,                       # nome
                    clean_cpf(row[8]),          # cpf
                    clean_string(row[9]),       # rg
                    clean_string(row[10]),      # cargo (funcao)
                    salario,                    # salario_base
                    clean_string(row[2]),       # endereco
                    clean_string(row[3]),       # bairro
                    clean_string(row[4]),       # cidade
                    'SP',                       # estado (default SP)
                    clean_cep(row[5]),          # cep
                    clean_phone(row[6]),        # telefone
                    clean_string(row[13]),      # email
                    row[12],                    # data_admissao
                    datetime.now(),             # data_cadastro
                    True                        # ativo
                )
                
                pg_cursor.execute(insert_sql, dados)
                pg_conn.commit()
                contador += 1
                
                if contador % 100 == 0:
                    logger.info(f"Migrados {contador} funcionários...")
                
            except Exception as e:
                erros += 1
                logger.error(f"Erro ao migrar funcionário {row[0]}: {str(e)}")
                pg_conn.rollback()
                continue
        
        # Atualizar sequence
        pg_cursor.execute("""
            SELECT setval(pg_get_serial_sequence('funcionarios', 'id'), 
                         COALESCE((SELECT MAX(id) FROM funcionarios), 1), 
                         true);
        """)
        pg_conn.commit()
        
        end_time = datetime.now()
        duration = end_time - start_time
        
        logger.info(f"""
        Migração concluída em {duration}:
        - Total de funcionários migrados: {contador}
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
        migrate_funcionarios()
    except KeyboardInterrupt:
        logger.info("Migração interrompida pelo usuário")
    except Exception as e:
        logger.error(f"Erro não tratado: {str(e)}")