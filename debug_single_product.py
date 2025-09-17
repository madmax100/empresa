import os
import sys
import django
from datetime import date
from decimal import Decimal
import pyodbc
import logging

# --- CONFIGURAÇÃO ---
# Altere este ID para o produto que deseja depurar
PRODUCT_ID_TO_DEBUG = 1

# --- Configuração do Ambiente Django ---
# Adiciona o caminho do projeto Django ao sys.path
# Ajuste este caminho se a estrutura do seu projeto for diferente
project_path = r'C:\\Users\\Cirilo\\Documents\\kiro\\empresa\\backend\\empresa'
if project_path not in sys.path:
    sys.path.append(project_path)

# Define a variável de ambiente para o arquivo de settings do Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'empresa.settings')

# Inicializa o Django
try:
    django.setup()
    from contas.models.access import Produtos, MovimentacoesEstoque
    from contas.services.stock_calculation_service import StockCalculationService
    DJANGO_LOADED = True
except ImportError as e:
    logging.error(f"Erro ao carregar o Django. Verifique o caminho do projeto e as dependências: {e}")
    DJANGO_LOADED = False

# --- Configurações do Banco de Dados Access ---
ACCESS_DB_PATH = r"C:\\Users\\Cirilo\\Documents\\Bancos\\Cadastros\\Cadastros.mdb"
ACCESS_PASSWORD = '010182'

# --- Configuração do Logging ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

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
        return None

def debug_single_product(product_id: int):
    """
    Executa uma análise detalhada de um único produto, comparando Access, PG DB e o Service.
    """
    if not DJANGO_LOADED:
        logging.error("O ambiente Django não pôde ser carregado. Abortando.")
        return

    logging.info(f"--- Iniciando depuração para o Produto ID: {product_id} ---")
    
    # 1. Obter dados do Produto no PostgreSQL (usando o ORM do Django)
    try:
        pg_product = Produtos.objects.get(id=product_id)
        pg_codigo = pg_product.codigo.strip()
        pg_estoque_atual = pg_product.estoque_atual or Decimal('0')
        pg_preco_custo = pg_product.preco_custo or Decimal('0')
        logging.info(f"Produto encontrado no PG: Código='{pg_codigo}', Nome='{pg_product.nome}'")
    except Produtos.DoesNotExist:
        logging.error(f"Produto com ID {product_id} não encontrado no PostgreSQL.")
        return

    # 2. Obter dados do Produto no MS Access
    access_conn = get_access_connection()
    access_estoque = Decimal('0')
    access_custo = Decimal('0')
    if access_conn:
        try:
            cursor = access_conn.cursor()
            cursor.execute("SELECT Estoque, Custo FROM produtos WHERE Codigo = ?", pg_codigo)
            row = cursor.fetchone()
            if row:
                access_estoque = Decimal(row.Estoque or '0')
                access_custo = Decimal(row.Custo or '0')
                logging.info(f"Produto encontrado no Access: Estoque={access_estoque}, Custo={access_custo}")
            else:
                logging.warning(f"Produto com Código '{pg_codigo}' não encontrado no MS Access.")
        except Exception as e:
            logging.error(f"Erro ao buscar dados no Access: {e}")
        finally:
            access_conn.close()

    # 3. Calcular estoque usando o StockCalculationService
    today = date.today()
    service_stock = StockCalculationService.calculate_stock_at_date(product_id, today)
    logging.info(f"Estoque calculado pelo Service para {today}: {service_stock}")

    # --- Relatório Comparativo ---
    print("\\n" + "="*50)
    print(f"RELATÓRIO DE COMPARAÇÃO - PRODUTO ID: {product_id} (CÓDIGO: {pg_codigo})")
    print("="*50)
    print(f"{'Fonte':<25} | {'Estoque':>10} | {'Custo':>12} | {'Valor Total':>15}")
    print("-"*80)
    
    access_valor = access_estoque * access_custo
    pg_db_valor = pg_estoque_atual * pg_preco_custo
    service_valor = service_stock * pg_preco_custo

    print(f"{'MS Access (Tabela)':<25} | {access_estoque:>10.2f} | {access_custo:>12.2f} | {access_valor:>15.2f}")
    print(f"{'PostgreSQL (estoque_atual)':<25} | {pg_estoque_atual:>10.2f} | {pg_preco_custo:>12.2f} | {pg_db_valor:>15.2f}")
    print(f"{'Service (Calculado)':<25} | {service_stock:>10.2f} | {pg_preco_custo:>12.2f} | {service_valor:>15.2f}")
    print("="*80)

    # 4. Listar todas as movimentações do produto no PostgreSQL
    print("\\n--- Histórico de Movimentações (PostgreSQL) ---")
    movements = MovimentacoesEstoque.objects.filter(produto_id=product_id).order_by('data_movimentacao')
    if movements.exists():
        print(f"{'Data':<20} | {'Tipo':<10} | {'Quantidade':>12} | {'Documento':<15} | {'Observação'}")
        print("-"*80)
        for mov in movements:
            tipo_map = {1: 'Entrada', 2: 'Saída', 3: 'Inicial'}
            tipo_str = tipo_map.get(mov.tipo_movimentacao_id, 'Desconhecido')
            doc_ref = mov.documento_referencia or ''
            obs = mov.observacoes or ''
            
            # Destaque para resets
            if doc_ref == '000000':
                print(f"*** RESET ***")
            
            print(f"{mov.data_movimentacao.strftime('%Y-%m-%d %H:%M'):<20} | {tipo_str:<10} | {mov.quantidade:>12.2f} | {doc_ref:<15} | {obs[:30]}")
    else:
        print("Nenhuma movimentação encontrada para este produto no PostgreSQL.")
    
    print("="*80)


def find_candidate_product():
    """
    Encontra um ID de produto adequado para depuração.
    O candidato ideal tem movimentações no PG e estoque > 0 no Access.
    """
    if not DJANGO_LOADED:
        logging.error("Django não carregado, não é possível encontrar candidato.")
        return None

    logging.info("--- Procurando um produto candidato para depuração ---")
    
    # 1. Encontrar produtos com movimentações no PostgreSQL
    products_with_movements = MovimentacoesEstoque.objects.values_list('produto_id', flat=True).distinct()
    
    if not products_with_movements:
        logging.warning("Nenhum produto com movimentações encontrado no PostgreSQL.")
        return None
        
    logging.info(f"Encontrados {len(products_with_movements)} produtos com movimentações no PG.")

    # 2. Obter os códigos desses produtos
    pg_products_map = {p.id: p.codigo.strip() for p in Produtos.objects.filter(id__in=products_with_movements)}

    # 3. Verificar quais deles têm estoque no Access
    access_conn = get_access_connection()
    if not access_conn:
        return None
        
    try:
        cursor = access_conn.cursor()
        # Iterar sobre os produtos com movimentação para encontrar um com estoque no Access
        for product_id, product_code in pg_products_map.items():
            cursor.execute("SELECT Estoque FROM produtos WHERE Codigo = ? AND Estoque > 0", product_code)
            row = cursor.fetchone()
            if row:
                logging.info(f"Candidato encontrado! Produto ID: {product_id} (Código: {product_code}) tem estoque > 0 no Access.")
                return product_id # Retorna o primeiro candidato encontrado
    except Exception as e:
        logging.error(f"Erro ao procurar candidato no Access: {e}")
        return None
    finally:
        access_conn.close()

    logging.warning("Nenhum produto candidato ideal (com movimentações no PG e estoque no Access) foi encontrado.")
    return None

if __name__ == "__main__":
    if not DJANGO_LOADED:
        sys.exit(1)
    
    # Encontra um candidato para depuração
    candidate_id = find_candidate_product()
    
    if candidate_id:
        # Executa a depuração para o candidato encontrado
        debug_single_product(candidate_id)
    else:
        logging.info("Não foi possível encontrar um produto adequado para a depuração automática.")
