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
        logging.FileHandler('migration_contratos.log'),
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
    if isinstance(value, datetime):
        return value.date()  # Converte datetime para date
    if isinstance(value, date):
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

def create_tables_if_not_exist(cursor):
    """Cria as tabelas de contratos se não existirem"""
    try:
        # Tabela de contratos
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS contratos_locacao (
            id INTEGER PRIMARY KEY,
            cliente_id INTEGER REFERENCES clientes(id),
            contrato VARCHAR(100),
            tipocontrato VARCHAR(20),
            renovado VARCHAR(100),
            totalmaquinas VARCHAR(100),
            valorcontrato DECIMAL(10,2),
            numeroparcelas VARCHAR(100),
            valorpacela DECIMAL(10,2),
            referencia VARCHAR(100),
            data DATE,
            inicio DATE,
            fim DATE,
            ultimoatendimento DATE,
            nmaquinas VARCHAR(100),
            clientereal VARCHAR(100),
            tipocontratoreal VARCHAR(100),
            obs VARCHAR(255)
        );

        -- Tabela de itens do contrato
        CREATE TABLE IF NOT EXISTS itens_contrato_locacao (
            id INTEGER PRIMARY KEY,
            contrato_id INTEGER REFERENCES contratos_locacao(id),
            numeroserie VARCHAR(30),
            modelo VARCHAR(50),
            categoria_id INTEGER REFERENCES categorias_produtos(id),
            inicio DATE,
            fim DATE
        );

        -- Índices
        CREATE INDEX IF NOT EXISTS idx_contratos_cliente ON contratos_locacao (cliente_id);
        CREATE INDEX IF NOT EXISTS idx_contratos_data ON contratos_locacao (data);
        CREATE INDEX IF NOT EXISTS idx_contratos_inicio ON contratos_locacao (inicio);
        CREATE INDEX IF NOT EXISTS idx_contratos_fim ON contratos_locacao (fim);
        CREATE INDEX IF NOT EXISTS idx_itens_contrato ON itens_contrato_locacao (contrato_id);
        """)
        
        logger.info("Estrutura das tabelas verificada/criada com sucesso")
    except Exception as e:
        logger.error(f"Erro ao criar tabelas: {str(e)}")
        raise

def clean_tables(pg_conn):
    """Limpa as tabelas no PostgreSQL"""
    try:
        cursor = pg_conn.cursor()
        logger.info("Iniciando limpeza das tabelas...")
        
        cursor.execute("SET session_replication_role = 'replica';")
        
        tabelas = [
            'itens_contrato_locacao',
            'contratos_locacao'
        ]
        
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

def verificar_clientes(pg_cursor):
    """Verifica clientes existentes"""
    try:
        pg_cursor.execute("SELECT id FROM clientes")
        return {row[0] for row in pg_cursor.fetchall()}
    except Exception as e:
        logger.error(f"Erro ao verificar clientes: {str(e)}")
        raise

def migrate_contratos():
    """Função principal de migração dos contratos"""
    start_time = datetime.now()
    logger.info(f"Iniciando migração de contratos às {start_time}")
    
    access_conn = None
    pg_conn = None
    
    try:
        logger.info("Estabelecendo conexões com os bancos de dados...")
        access_conn = DatabaseConfig.get_access_conn()
        pg_conn = DatabaseConfig.get_postgres_conn()
        
        clean_tables(pg_conn)
        
        pg_cursor = pg_conn.cursor()
        create_tables_if_not_exist(pg_cursor)
        
        # Verificar clientes existentes
        clientes_validos = verificar_clientes(pg_cursor)
        
        logger.info("Consultando dados do Access...")
        access_cursor = access_conn.cursor()
        access_cursor.execute("""
            SELECT Contrato, Cliente, TipoContrato, Renovado, 
                   TotalMaquinas, ValorContrato, NumeroParcelas, 
                   ValorPacela, Referencia, Data, Incio, Fim, 
                   UltimoAtendimento, NMaquinas, ClienteReal, 
                   TipoContratoReal, Obs
            FROM Contratos 
            WHERE Incio >= #2024/01/01# OR Fim >= #2024/01/01#
            ORDER BY Contrato
        """)
        
        insert_sql = """
            INSERT INTO contratos_locacao (
                id, contrato, cliente_id, tipocontrato, renovado,
                totalmaquinas, valorcontrato, numeroparcelas, valorpacela,
                referencia, data, inicio, fim, ultimoatendimento,
                nmaquinas, clientereal, tipocontratoreal, obs
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s
            )
        """
        
        contador = 0
        erros = 0
        clientes_nao_encontrados = set()
        
        logger.info("Iniciando migração dos registros...")
        
        for row in access_cursor.fetchall():
            try:
                contrato_numero = clean_string(row[0])
                if not contrato_numero:
                    continue
                
                contrato_id = int(contrato_numero.replace('C', ''))
                cliente_id = int(row[1]) if row[1] else None
                
                # Validar cliente
                if cliente_id and cliente_id not in clientes_validos:
                    clientes_nao_encontrados.add(cliente_id)
                    continue
                
                # Validar datas
                data_inicio = clean_date(row[10])  # Incio
                data_fim = clean_date(row[11])    # Fim
                
                # Ignorar contratos antigos
                if data_inicio and data_inicio < DATA_CORTE and (not data_fim or data_fim < DATA_CORTE):
                    continue
                
                dados = (
                    contrato_id,                # id
                    contrato_numero,            # contrato
                    cliente_id,                 # cliente_id
                    clean_string(row[2]),       # tipocontrato
                    clean_string(row[3]),       # renovado
                    clean_string(row[4]),       # totalmaquinas
                    clean_decimal(row[5]),      # valorcontrato
                    clean_string(row[6]),       # numeroparcelas
                    clean_decimal(row[7]),      # valorpacela
                    clean_string(row[8]),       # referencia
                    clean_date(row[9]),         # data
                    data_inicio,                # incio
                    data_fim,                   # fim
                    clean_date(row[12]),        # ultimoatendimento
                    clean_string(row[13]),      # nmaquinas
                    clean_string(row[14]),      # clientereal
                    clean_string(row[15]),      # tipocontratoreal
                    clean_string(row[16])       # obs
                )
                
                pg_cursor.execute(insert_sql, dados)
                pg_conn.commit()
                contador += 1
                
                if contador % 100 == 0:
                    logger.info(f"Migrados {contador} contratos...")
                
            except Exception as e:
                erros += 1
                logger.error(f"Erro ao migrar contrato {row[0]}: {str(e)}")
                pg_conn.rollback()
                continue
        
        # Atualizar sequence
        pg_cursor.execute("""
            SELECT setval('contratos_locacao_id_seq', 
                         COALESCE((SELECT MAX(id) FROM contratos_locacao), 1), 
                         true);
        """)
        pg_conn.commit()
        
        end_time = datetime.now()
        duration = end_time - start_time
        
        logger.info(f"""
        Migração concluída em {duration}:
        - Total de contratos migrados: {contador}
        - Total de erros: {erros}
        """)
        
        if clientes_nao_encontrados:
            logger.warning("Clientes não encontrados:")
            for cliente in sorted(clientes_nao_encontrados):
                logger.warning(f"- Cliente {cliente}")
        
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
        migrate_contratos()
    except KeyboardInterrupt:
        logger.info("Migração interrompida pelo usuário")
    except Exception as e:
        logger.error(f"Erro não tratado: {str(e)}")