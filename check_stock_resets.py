import psycopg2
from psycopg2 import sql

# Configurações do banco de dados PostgreSQL
PG_CONFIG = {
    'dbname': 'c3mcopiasdb2',
    'user': 'cirilomax',
    'password': '226cmm100',
    'host': 'localhost',
    'port': '5432'
}

def check_stock_resets():
    """
    Verifica a existência de 'resets' de estoque para os produtos no PostgreSQL.
    """
    conn = None
    try:
        # Conectar ao PostgreSQL especificando a codificação
        conn = psycopg2.connect(**PG_CONFIG, client_encoding='latin1')
        cursor = conn.cursor()
        print("Conectado ao PostgreSQL com sucesso.")

        # 1. Obter todos os IDs de produtos ativos
        cursor.execute("SELECT id FROM produtos WHERE ativo = TRUE;")
        active_products = {row[0] for row in cursor.fetchall()}
        total_active_products = len(active_products)
        print(f"Total de produtos ativos encontrados: {total_active_products}")

        if total_active_products == 0:
            print("Nenhum produto ativo encontrado. Encerrando a verificação.")
            return

        # 2. Obter os IDs dos produtos que têm pelo menos um reset de estoque
        cursor.execute("""
            SELECT DISTINCT produto_id
            FROM movimentacoes_estoque
            WHERE documento_referencia = '000000';
        """)
        products_with_reset = {row[0] for row in cursor.fetchall()}
        total_products_with_reset = len(products_with_reset)
        print(f"Total de produtos com 'reset' de estoque: {total_products_with_reset}")

        # 3. Identificar produtos ativos que não têm um reset
        # Interseção para garantir que estamos contando apenas produtos ativos que têm resets
        active_products_with_reset = active_products.intersection(products_with_reset)
        
        products_without_reset = active_products - products_with_reset
        total_products_without_reset = len(products_without_reset)

        print("\\n--- Análise dos Resets de Estoque ---")
        print(f"Produtos ativos com pelo menos um 'reset': {len(active_products_with_reset)}")
        print(f"Produtos ativos SEM 'reset' (usam cálculo retroativo): {total_products_without_reset}")

        if total_products_without_reset > 0:
            print("\\nIsso indica que uma parte significativa dos produtos depende do cálculo de estoque retroativo, que pode ser uma fonte de imprecisão.")
            # Opcional: Listar alguns produtos sem reset para análise
            # print("Exemplos de produtos sem reset:", list(products_without_reset)[:10])
        else:
            print("\\nTudo indica que a maioria dos produtos utiliza o cálculo progressivo a partir de um 'reset', que é o método preferencial.")

    except psycopg2.Error as e:
        print(f"Erro de banco de dados: {e}")
    finally:
        if conn:
            conn.close()
            print("\\nConexão com o PostgreSQL fechada.")

if __name__ == "__main__":
    check_stock_resets()
