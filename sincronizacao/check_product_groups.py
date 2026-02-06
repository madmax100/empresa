
import psycopg2
from config import PG_CONFIG

def check_product_groups():
    try:
        conn = psycopg2.connect(**PG_CONFIG)
        cursor = conn.cursor()

        # Count total products
        cursor.execute("SELECT COUNT(*) FROM produtos")
        total_products = cursor.fetchone()[0]

        # Count products with group
        cursor.execute("SELECT COUNT(*) FROM produtos WHERE grupo_id IS NOT NULL")
        products_with_group = cursor.fetchone()[0]

        # Get examples
        cursor.execute("""
            SELECT p.nome, g.nome 
            FROM produtos p 
            JOIN grupos g ON p.grupo_id = g.id 
            LIMIT 5
        """)
        examples = cursor.fetchall()

        print(f"Total de Produtos: {total_products}")
        print(f"Produtos com Grupo: {products_with_group}")
        print("\nExemplos de Associação:")
        for prod, group in examples:
            print(f"- {prod} -> {group}")

        conn.close()

    except Exception as e:
        print(f"Erro: {e}")

if __name__ == "__main__":
    check_product_groups()
