import pyodbc
import psycopg2
from decimal import Decimal, InvalidOperation
import logging
import sys
from datetime import datetime

# Configurar logging para exibir informações no console e salvar em um arquivo
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('sync_current_stock.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

# --- Configurações dos Bancos de Dados ---
PG_CONFIG = {
    'dbname': 'c3mcopiasdb2',
    'user': 'cirilomax',
    'password': '226cmm100',
    'host': 'localhost',
    'port': '5432'
}

ACCESS_DB_PATH = r"C:\\Users\\Cirilo\\Documents\\Bancos\\Cadastros\\Cadastros.mdb"
ACCESS_PASSWORD = '010182'

def get_access_connection():
    """Estabelece e retorna uma conexão com o MS Access."""
    try:
        conn_str = (
            r"Driver={Microsoft Access Driver (*.mdb, *.accdb)};"
            f"DBQ={ACCESS_DB_PATH};"
            f"PWD={ACCESS_PASSWORD};"
        )
        return pyodbc.connect(conn_str)
    except pyodbc.Error as e:
        logging.error(f"Erro ao conectar ao MS Access: {e}")
        raise

def get_postgres_connection():
    """Estabelece e retorna uma conexão com o PostgreSQL."""
    try:
        return psycopg2.connect(**PG_CONFIG)
    except psycopg2.Error as e:
        logging.error(f"Erro ao conectar ao PostgreSQL: {e}")
        raise

def sync_current_stock():
    """
    Sincroniza o campo 'estoque_atual' na tabela 'produtos' do PostgreSQL
    com os valores da tabela 'produtos' do MS Access.
    """
    logging.info("Iniciando a sincronização do estoque atual.")
    access_conn = None
    pg_conn = None
    
    try:
        # Estabelecer conexões
        access_conn = get_access_connection()
        pg_conn = get_postgres_connection()
        pg_cursor = pg_conn.cursor()

        # 1. Buscar dados do MS Access
        logging.info("Buscando dados de estoque do MS Access...")
        access_cursor = access_conn.cursor()
        access_cursor.execute("SELECT Codigo, Estoque FROM produtos")
        access_products = access_cursor.fetchall()
        
        # Criar um mapa para acesso rápido: {codigo: estoque}
        access_stock_map = {}
        for row in access_products:
            try:
                # Limpar e validar o código do produto
                codigo = str(row.Codigo).strip()
                # Limpar e validar o valor do estoque
                estoque = Decimal(row.Estoque or '0')
                if codigo:
                    access_stock_map[codigo] = estoque
            except (InvalidOperation, TypeError):
                logging.warning(f"Ignorando linha do Access com dados inválidos: Codigo={row.Codigo}, Estoque={row.Estoque}")
        
        logging.info(f"Encontrados {len(access_stock_map)} produtos válidos no MS Access.")

        # 2. Atualizar dados no PostgreSQL
        logging.info("Iniciando a atualização no PostgreSQL...")
        
        # Buscar todos os produtos do PostgreSQL para comparar
        pg_cursor.execute("SELECT id, codigo FROM produtos")
        pg_products = pg_cursor.fetchall()
        
        updates_to_perform = []
        for pg_id, pg_codigo in pg_products:
            pg_codigo_clean = str(pg_codigo).strip()
            if pg_codigo_clean in access_stock_map:
                access_stock = access_stock_map[pg_codigo_clean]
                updates_to_perform.append((access_stock, pg_id))

        logging.info(f"Serão atualizados {len(updates_to_perform)} produtos no PostgreSQL.")

        # 3. Executar a atualização em lote (executemany)
        if updates_to_perform:
            update_query = "UPDATE produtos SET estoque_atual = %s WHERE id = %s"
            pg_cursor.executemany(update_query, updates_to_perform)
            pg_conn.commit()
            logging.info(f"Atualização em lote concluída. {pg_cursor.rowcount} registros foram afetados.")
        else:
            logging.info("Nenhuma atualização necessária.")

    except Exception as e:
        logging.error(f"Ocorreu um erro durante a sincronização: {e}")
        if pg_conn:
            pg_conn.rollback()
    finally:
        # Fechar conexões
        if access_conn:
            access_conn.close()
        if pg_conn:
            pg_conn.close()
        logging.info("Processo de sincronização finalizado.")

if __name__ == "__main__":
    sync_current_stock()
