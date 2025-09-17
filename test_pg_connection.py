import psycopg2
import sys

# Configurações do banco de dados PostgreSQL
PG_CONFIG = {
    'dbname': 'c3mcopiasdb2',
    'user': 'cirilomax',
    'password': '226cmm100',
    'host': 'localhost',
    'port': '5432'
}

def test_connection():
    """
    Tenta conectar ao PostgreSQL com diferentes configurações de codificação.
    """
    encodings_to_try = ['utf-8', 'latin1', None] # None usará o padrão do psycopg2

    for encoding in encodings_to_try:
        conn = None
        try:
            print(f"--- Tentando conectar com a codificação: {encoding or 'padrão'} ---")
            
            # Constrói os argumentos de conexão
            conn_args = PG_CONFIG.copy()
            if encoding:
                conn_args['client_encoding'] = encoding

            # Tenta conectar
            conn = psycopg2.connect(**conn_args)
            cursor = conn.cursor()
            
            # Executa uma consulta simples para confirmar a conexão
            cursor.execute("SELECT version();")
            version = cursor.fetchone()
            print(f"Conexão bem-sucedida! Versão do PostgreSQL: {version[0]}")
            
            # Se a conexão foi bem-sucedida, podemos parar
            return True

        except UnicodeDecodeError as e:
            print(f"Falha na conexão com '{encoding}': {e}")
            # Imprime mais detalhes do erro
            print(f"  - Erro na classe: {e.__class__.__name__}")
            print(f"  - Argumentos do erro: {e.args}")
            print("-" * 20)

        except psycopg2.Error as e:
            print(f"Falha na conexão com '{encoding}' (Erro do Psycopg2): {e}")
            print("-" * 20)

        finally:
            if conn:
                conn.close()
    
    print("\\nNão foi possível conectar ao banco de dados com nenhuma das codificações testadas.")
    return False

if __name__ == "__main__":
    test_connection()
