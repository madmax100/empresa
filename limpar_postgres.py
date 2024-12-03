import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

def conectar_postgresql():
    try:
        pg_config = {
            'dbname': 'c3mcopiasdb',
            'user': 'cirilomax',
            'password': '226cmm100',
            'host': 'localhost',
            'port': '5432'
        }
        return psycopg2.connect(**pg_config)
    except Exception as e:
        print(f"Erro ao conectar ao PostgreSQL: {str(e)}")
        return None

def limpar_todas_tabelas():
    conn = conectar_postgresql()
    if not conn:
        return False
    
    try:
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        # Buscar todas as tabelas do schema public
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_type = 'BASE TABLE'
            ORDER BY table_name;
        """)
        
        tabelas = cursor.fetchall()
        
        print("\nTabelas encontradas:")
        for tabela in tabelas:
            print(f"- {tabela[0]}")
            
        confirmacao = input("\nISSO IRÁ APAGAR TODOS OS DADOS! Tem certeza? (digite 'SIM' para confirmar): ")
        if confirmacao != 'SIM':
            print("Operação cancelada.")
            return False
            
        print("\nIniciando limpeza das tabelas...")
        
        # Desabilitar verificação de chaves estrangeiras
        cursor.execute("SET session_replication_role = 'replica';")
        
        # Limpar todas as tabelas
        for tabela in tabelas:
            nome_tabela = tabela[0]
            print(f"\nLimpando tabela {nome_tabela}...")
            
            # Verificar quantidade de registros antes
            cursor.execute(f"SELECT COUNT(*) FROM {nome_tabela};")
            qtd_antes = cursor.fetchone()[0]
            
            # Limpar a tabela
            cursor.execute(f"TRUNCATE TABLE {nome_tabela} CASCADE;")
            
            # Verificar quantidade de registros depois
            cursor.execute(f"SELECT COUNT(*) FROM {nome_tabela};")
            qtd_depois = cursor.fetchone()[0]
            
            print(f"  Registros removidos: {qtd_antes}")
            print(f"  Registros restantes: {qtd_depois}")
        
        # Reabilitar verificação de chaves estrangeiras
        cursor.execute("SET session_replication_role = 'origin';")
        
        print("\nOperação concluída com sucesso!")
        print("\nTodas as tabelas foram limpas e estão prontas para nova importação.")
        
        return True
        
    except Exception as e:
        print(f"Erro durante a limpeza: {str(e)}")
        return False
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    print("=== LIMPEZA DO BANCO DE DADOS ===")
    limpar_todas_tabelas()
