# migrate_movimentos.py
import pyodbc
import psycopg2
import pandas as pd
from datetime import datetime
from decimal import Decimal

def clean_string(value):
    if pd.isna(value) or value is None:
        return None
    return str(value).strip()

def clean_decimal(value):
    if pd.isna(value) or value is None:
        return Decimal('0.00')
    try:
        clean_value = str(value).replace(',', '.')
        return Decimal(clean_value)
    except:
        return Decimal('0.00')

def clean_time(value):
    if pd.isna(value) or value is None:
        return None
    try:
        # Tenta diferentes formatos de hora
        formats = ['%H:%M:%S', '%H:%M', '%H.%M.%S', '%H.%M']
        for fmt in formats:
            try:
                return datetime.strptime(str(value).strip(), fmt).time()
            except:
                continue
        return None
    except:
        return None

def get_existing_records(cursor):
    """Obtém registros existentes usando uma combinação de campos"""
    cursor.execute("""
        SELECT data, hora, credito, debito, historico 
        FROM movimentos_financeiros
    """)
    return {(row[0], row[1], row[2], row[3], row[4]) for row in cursor.fetchall()}

def migrate_movimentos():
    # Configurações
    pg_config = {
        'dbname': 'nova_empresa',
        'user': 'cirilomax',
        'password': '226cmm100',  # Altere para sua senha
        'host': 'localhost',
        'port': '5432'
    }

    # Caminho do banco Access
    access_path = r"C:\Users\Cirilo\Documents\empresa\Bancos\Caixa\Caixa.mdb"
    
    try:
        # Conexões
        print("Conectando aos bancos de dados...")
        conn_str =  (
            r'Driver={Microsoft Access Driver (*.mdb, *.accdb)};'
            f'DBQ={access_path};'
            'PWD=010182;'
        )   
        access_conn = pyodbc.connect(conn_str)
        pg_conn = psycopg2.connect(**pg_config)
        pg_cursor = pg_conn.cursor()

        # Obtém registros existentes
        print("Verificando registros existentes...")
        existing_records = get_existing_records(pg_cursor)
        print(f"Registros existentes: {len(existing_records)}")

        # Confirma continuação
        confirm = input("\nDeseja continuar com a migração? (S/N): ")
        if confirm.upper() != 'S':
            print("Migração cancelada pelo usuário.")
            return

        # Lê dados dos movimentos
        print("\nLendo dados do Access...")
        df_movimentos = pd.read_sql("SELECT * FROM Movimento", access_conn)
        
        total = len(df_movimentos)
        print(f"Total de movimentos encontrados: {total}")
        
        # Contadores
        novos = 0
        ignorados = 0
        erros = 0
        
        # Processa cada movimento
        for idx, row in df_movimentos.iterrows():
            try:
                if idx % 1000 == 0:  # Mostra progresso a cada 1000 registros
                    print(f"Processando movimento {idx} de {total}")
                
                data = pd.to_datetime(row['Data']).date() if not pd.isna(row['Data']) else None
                hora = clean_time(row['Horario'])
                credito = clean_decimal(row['Credito'])
                debito = clean_decimal(row['Debito'])
                historico = clean_string(row['Historico'])
                
                # Verifica se o registro já existe
                if (data, hora, credito, debito, historico) in existing_records:
                    ignorados += 1
                    continue
                
                # Insere novo movimento
                pg_cursor.execute("""
                    INSERT INTO movimentos_financeiros (
                        data, hora, tipo, conta, credito,
                        debito, historico, operador
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    data,
                    hora,
                    clean_string(row['Local']),
                    clean_string(row['Conta']),
                    credito,
                    debito,
                    historico,
                    clean_string(row['Operador'])
                ))
                
                pg_conn.commit()
                novos += 1
                
            except Exception as e:
                print(f"Erro ao processar movimento {idx}: {str(e)}")
                pg_conn.rollback()
                erros += 1
                continue

        # Relatório final
        print("\n=== Relatório da Migração ===")
        print(f"Total de registros processados: {total}")
        print(f"Novos registros inseridos: {novos}")
        print(f"Registros ignorados (já existentes): {ignorados}")
        print(f"Registros com erro: {erros}")
        
        # Verifica total final
        pg_cursor.execute("SELECT COUNT(*) FROM movimentos_financeiros")
        total_final = pg_cursor.fetchone()[0]
        print(f"\nTotal de registros na tabela: {total_final}")
        
    except Exception as e:
        print(f"Erro durante a migração: {str(e)}")
        if 'pg_conn' in locals():
            pg_conn.rollback()
        raise
    finally:
        if 'access_conn' in locals():
            access_conn.close()
        if 'pg_cursor' in locals():
            pg_cursor.close()
        if 'pg_conn' in locals():
            pg_conn.close()

if __name__ == "__main__":
    print("Iniciando migração dos movimentos financeiros...")
    print("Data e hora início:", datetime.now())
    migrate_movimentos()
    print("Data e hora fim:", datetime.now())