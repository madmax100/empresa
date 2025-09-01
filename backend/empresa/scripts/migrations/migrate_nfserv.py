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
        logging.FileHandler('migration_nfserv.log'),
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
        
        tabelas_dependentes = [
            'itens_nf_servico',
            'notas_fiscais_servico'
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

def carregar_dependencias(pg_cursor):
    """Carrega dados das tabelas relacionadas"""
    try:
        # Carregar clientes
        pg_cursor.execute("SELECT id FROM clientes")
        clientes = {row[0] for row in pg_cursor.fetchall()}
        
        # Carregar vendedores (funcionários)
        pg_cursor.execute("SELECT id FROM funcionarios")
        vendedores = {row[0] for row in pg_cursor.fetchall()}
        
        # Carregar transportadoras
        pg_cursor.execute("SELECT id FROM transportadoras")
        transportadoras = {row[0] for row in pg_cursor.fetchall()}
        
        return clientes, vendedores, transportadoras
        
    except Exception as e:
        logger.error(f"Erro ao carregar dependências: {str(e)}")
        raise

def migrate_nfserv():
    """Função principal de migração das notas fiscais de serviço"""
    start_time = datetime.now()
    logger.info(f"Iniciando migração de notas fiscais de serviço às {start_time}")
    
    access_conn = None
    pg_conn = None
    
    try:
        logger.info("Estabelecendo conexões com os bancos de dados...")
        access_conn = DatabaseConfig.get_access_conn()
        pg_conn = DatabaseConfig.get_postgres_conn()
        
        clean_tables(pg_conn)
        
        pg_cursor = pg_conn.cursor()
        
        # Carregar dependências
        clientes_validos, vendedores_validos, transportadoras_validas = carregar_dependencias(pg_cursor)
        
        logger.info("Consultando dados do Access...")
        access_cursor = access_conn.cursor()
        
        query = """
        SELECT NumNFSERV, MesAno, Data, Cliente, ValorProdutos,
               ISS, BaseCalculo, Desconto, Valortotalnota,
               FormaPagto, Condicoes, vendedor, Operador,
               Transportadora, Formulario, Obs, Operacao,
               CFOP, NSerie, Parcelas, Comissao, Tipo
        FROM NFSERV 
        WHERE Data >= #2024/01/01#
        ORDER BY NumNFSERV
        """
        
        access_cursor.execute(query)
        
        insert_sql = """
            INSERT INTO notas_fiscais_servico (
                numero_nota, mes_ano, data, cliente_id,
                valor_produtos, iss, base_calculo, desconto,
                valor_total, forma_pagamento, condicoes,
                vendedor_id, operador, transportadora_id,
                formulario, obs, operacao, cfop, n_serie,
                parcelas, comissao, tipo
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                %s, %s
            )
        """
        
        contador = 0
        erros = 0
        clientes_nao_encontrados = set()
        vendedores_nao_encontrados = set()
        transportadoras_nao_encontradas = set()
        
        logger.info("Iniciando migração dos registros...")
        
        for row in access_cursor.fetchall():
            try:
                # Validar cliente
                cliente_id = int(row[3]) if row[3] else None
                if cliente_id and cliente_id not in clientes_validos:
                    clientes_nao_encontrados.add(cliente_id)
                    continue
                
                # Validar vendedor
                vendedor_id = int(row[11]) if row[11] else None
                if vendedor_id and vendedor_id not in vendedores_validos:
                    vendedores_nao_encontrados.add(vendedor_id)
                    vendedor_id = None
                
                # Validar transportadora
                transportadora_id = int(row[13]) if row[13] else None
                if transportadora_id and transportadora_id not in transportadoras_validas:
                    transportadoras_nao_encontradas.add(transportadora_id)
                    transportadora_id = None
                
                # Calcular valor total
                valor_total = (
                    clean_decimal(row[4]) -    # valor_produtos
                    clean_decimal(row[7])      # desconto
                )
                
                dados = (
                    clean_string(row[0]),       # numero_nota
                    clean_string(row[1]),       # mes_ano
                    clean_date(row[2]),         # data
                    cliente_id,                 # cliente_id
                    clean_decimal(row[4]),      # valor_produtos
                    clean_decimal(row[5]),      # iss
                    clean_decimal(row[6]),      # base_calculo
                    clean_decimal(row[7]),      # desconto
                    valor_total,                # valor_total
                    clean_string(row[9]),       # forma_pagamento
                    clean_string(row[10]),      # condicoes
                    vendedor_id,                # vendedor_id
                    clean_string(row[12]),      # operador
                    transportadora_id,          # transportadora_id
                    clean_string(row[14]),      # formulario
                    clean_string(row[15]),      # obs
                    clean_string(row[16]),      # operacao
                    clean_string(row[17]),      # cfop
                    clean_string(row[18]),      # n_serie
                    clean_string(row[19]),      # parcelas
                    clean_decimal(row[20]),     # comissao
                    clean_string(row[21])       # tipo
                )
                
                pg_cursor.execute(insert_sql, dados)
                pg_conn.commit()
                contador += 1
                
                if contador % 100 == 0:
                    logger.info(f"Migradas {contador} notas fiscais de serviço...")
            
            except Exception as e:
                erros += 1
                logger.error(f"Erro ao migrar nota fiscal de serviço {row[0]}: {str(e)}")
                pg_conn.rollback()
                continue
        
        end_time = datetime.now()
        duration = end_time - start_time
        
        logger.info(f"""
        Migração concluída em {duration}:
        - Total de notas fiscais de serviço migradas: {contador}
        - Total de erros: {erros}
        """)
        
        if clientes_nao_encontrados:
            logger.warning("\nClientes não encontrados:")
            for c in sorted(clientes_nao_encontrados):
                logger.warning(f"- Cliente {c}")
        
        if vendedores_nao_encontrados:
            logger.warning("\nVendedores não encontrados:")
            for v in sorted(vendedores_nao_encontrados):
                logger.warning(f"- Vendedor {v}")
        
        if transportadoras_nao_encontradas:
            logger.warning("\nTransportadoras não encontradas:")
            for t in sorted(transportadoras_nao_encontradas):
                logger.warning(f"- Transportadora {t}")
        
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
        migrate_nfserv()
    except KeyboardInterrupt:
        logger.info("Migração interrompida pelo usuário")
    except Exception as e:
        logger.error(f"Erro não tratado: {str(e)}")