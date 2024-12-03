import psycopg2

# Dados de conexão com o banco de dados
host = "seu_host"
database = "seu_banco_de_dados"
user = "seu_usuario"
password = "sua_senha"

# Conectar ao banco de dados
try:
    pg_config = {
        'dbname': 'nova_empresa',
        'user': 'cirilomax',
        'password': '226cmm100',
        'host': 'localhost',
        'port': '5432'
    }
    conn = psycopg2.connect(**pg_config)

    print("Conexão estabelecida com sucesso!")
except (Exception, psycopg2.Error) as error:
    print("Erro ao conectar ao banco de dados:", error)
    exit()

# Criar um cursor
cur = conn.cursor()

# Obter informações sobre o banco de dados
cur.execute("SELECT version();")
db_version = cur.fetchone()[0]
print("Versão do banco de dados:", db_version)

cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';")
tables = [row[0] for row in cur.fetchall()]
print("Tabelas no banco de dados:", tables)

for table_name in tables:
    cur.execute(f"SELECT * FROM {table_name} LIMIT 1;")
    columns = [col[0] for col in cur.description]
    print(f"Colunas da tabela '{table_name}':")
    for column in columns:
        cur.execute(f"SELECT data_type FROM information_schema.columns WHERE table_name = '{table_name}' AND column_name = '{column}';")
        data_type = cur.fetchone()[0]
        print(f"- {column} ({data_type})")
        
    # Obter informações sobre chaves estrangeiras
    cur.execute(f"""
        SELECT 
            tc.constraint_name, 
            tc.table_name, 
            kcu.column_name, 
            ccu.table_name AS foreign_table_name,
            ccu.column_name AS foreign_column_name
        FROM 
            information_schema.table_constraints tc
        JOIN 
            information_schema.key_column_usage kcu
            ON tc.constraint_name = kcu.constraint_name
        JOIN 
            information_schema.constraint_column_usage ccu
            ON ccu.constraint_name = tc.constraint_name
        WHERE 
            tc.constraint_type = 'FOREIGN KEY' AND tc.table_name = '{table_name}'
    """)
    foreign_keys = cur.fetchall()
    if foreign_keys:
        print("Chaves estrangeiras:")
        for foreign_key in foreign_keys:
            print(f"- Constraint: {foreign_key[0]}")
            print(f"  Tabela: {foreign_key[1]}, Coluna: {foreign_key[2]}")
            print(f"  Tabela externa: {foreign_key[3]}, Coluna externa: {foreign_key[4]}")
    print()

# Fechar a conexão
cur.close()
conn.close()