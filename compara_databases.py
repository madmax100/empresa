import os
import pyodbc
import psycopg2

def analyze_access_database(db_path):
    conn_str = (
        r'Driver={Microsoft Access Driver (*.mdb, *.accdb)};'
        f'DBQ={db_path};'
        'PWD=010182;'
    )
    conn = pyodbc.connect(conn_str)
    cursor = conn.cursor()

    # Obter lista de tabelas
    tables = [row.table_name for row in cursor.tables(tableType='TABLE')]

    # Analisar estrutura das tabelas
    report = ""
    for table in tables:
        try:
            cursor.execute(f"SELECT * FROM [{table}]")
            columns = [column[0] for column in cursor.description]
            report += f"Tabela: {table}\n"
            report += f"Colunas: {', '.join(columns)}\n\n"
        except pyodbc.Error as e:
            print(f"Erro ao acessar a tabela {table}: {str(e)}")

    cursor.close()
    conn.close()

    return report

def analyze_postgresql_database(dbname, user, password, host, port):
    pg_config = {
        'dbname': 'nova_empresa',
        'user': 'cirilomax',
        'password': '226cmm100',
        'host': 'localhost',
        'port': '5432'
    }
    conn = psycopg2.connect(**pg_config)
    cursor = conn.cursor()

    # Obter lista de tabelas
    cursor.execute(
        "SELECT table_name FROM information_schema.tables "
        "WHERE table_schema = 'public'"
    )
    tables = [row[0] for row in cursor.fetchall()]

    # Analisar estrutura das tabelas
    report = ""
    for table in tables:
        try:
            cursor.execute(f"SELECT * FROM {table} LIMIT 0")
            columns = [desc[0] for desc in cursor.description]
            report += f"Tabela: {table}\n"
            report += f"Colunas: {', '.join(columns)}\n\n"
        except psycopg2.errors.UndefinedTable as e:
            print(f"Erro ao acessar a tabela {table}: {str(e)}")
            conn.rollback()  # Rollback the transaction
        except psycopg2.errors.InFailedSqlTransaction:
            conn.rollback()  # Rollback the transaction

    cursor.close()
    conn.close()

    return report

def find_access_files(directory):
    access_files = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(".mdb") :
                access_files.append(os.path.join(root, file))
    return access_files

# Configurações dos bancos de dados
access_directory = r"C:\Users\Cirilo\Documents\empresa\Bancos"
postgresql_config = {
    'dbname': 'nova_empresa',
    'user': 'cirilomax',
    'password': '226cmm100',
    'host': 'localhost',
    'port': '5432'
}

# Encontrar arquivos do Access
access_files = find_access_files(access_directory)

# Gerar relatórios dos bancos de dados do Access
access_reports = []
for db_path in access_files:
    print(db_path)
    report = analyze_access_database(db_path)
    access_reports.append(report)

# Gerar relatório do banco de dados PostgreSQL
postgresql_report = analyze_postgresql_database(**postgresql_config)

# Exibir relatórios
print("Relatório dos Bancos de Dados do Access:")
for i, report in enumerate(access_reports):
    print(f"\nBanco de Dados {i+1}:")
    print(report)
    
with open("access_reports.txt", "w") as file:
    print("Relatório dos Bancos de Dados do Access:", file=file)
    for i, report in enumerate(access_reports):
        print(f"\nBanco de Dados {i+1}:", file=file)
        print(report, file=file)

print("\nRelatório do Banco de Dados PostgreSQL:")
print(postgresql_report)