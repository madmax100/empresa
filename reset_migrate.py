# reset_and_migrate_fixed.py
import pyodbc
import psycopg2
from datetime import datetime
from decimal import Decimal

def reset_financial_data():
    """Apaga todos os dados da tabela de movimentos financeiros"""
    pg_config = {
        'dbname': 'nova_empresa',
        'user': 'cirilomax',
        'password': '226cmm100',
        'host': 'localhost',
        'port': '5432'
    }

    try:
        print("Conectando ao PostgreSQL...")
        conn = psycopg2.connect(**pg_config)
        cur = conn.cursor()

        print("\nApagando todos os registros...")
        cur.execute("TRUNCATE TABLE movimentos_financeiros")
        conn.commit()

        print("Limpeza concluída com sucesso!")

    except Exception as e:
        print(f"Erro durante a limpeza: {str(e)}")
        if 'conn' in locals():
            conn.rollback()
        raise
    finally:
        if 'cur' in locals():
            cur.close()
        if 'conn' in locals():
            conn.close()

def migrate_movimentos():
    """Migra os dados do Access para PostgreSQL"""
    pg_config = {
        'dbname': 'nova_empresa',
        'user': 'cirilomax',
        'password': '226cmm100',
        'host': 'localhost',
        'port': '5432'
    }

    access_path = r"C:\Users\Cirilo\Documents\empresa\Bancos\Caixa\Caixa.mdb"
    
    try:
        print("\nConectando aos bancos de dados...")
        conn_str = (
            r'Driver={Microsoft Access Driver (*.mdb, *.accdb)};'
            f'DBQ={access_path};'
            'PWD=010182;'
        )
        access_conn = pyodbc.connect(conn_str)
        access_cursor = access_conn.cursor()
        
        pg_conn = psycopg2.connect(**pg_config)
        pg_cursor = pg_conn.cursor()

        # Carrega todos os registros de uma vez
        print("\nCarregando dados do Access...")
        access_cursor.execute("""
            SELECT 
                Data, Horario, Local, Conta, 
                Credito, Debito, Historico, Operador
            FROM Movimento
            ORDER BY Data, Horario
        """)
        
        # Processa os registros
        registros_processados = 0
        lote = []
        lote_size = 1000

        print("\nIniciando migração...")
        while True:
            row = access_cursor.fetchone()
            if not row:
                # Processa último lote
                if lote:
                    try:
                        pg_cursor.executemany("""
                            INSERT INTO movimentos_financeiros (
                                data, hora, tipo, conta, credito,
                                debito, historico, operador
                            )
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                        """, lote)
                        pg_conn.commit()
                        registros_processados += len(lote)
                    except Exception as e:
                        print(f"Erro ao processar lote: {str(e)}")
                break

            try:
                data, hora, local, conta, credito, debito, historico, operador = row
                
                # Processa o registro
                registro_processado = (
                    data,
                    hora,
                    local.strip() if local else None,
                    conta.strip() if conta else None,
                    float(credito) if credito else 0.00,
                    float(debito) if debito else 0.00,
                    historico.strip() if historico else None,
                    operador.strip() if operador else None
                )
                
                lote.append(registro_processado)
                
                if len(lote) >= lote_size:
                    try:
                        pg_cursor.executemany("""
                            INSERT INTO movimentos_financeiros (
                                data, hora, tipo, conta, credito,
                                debito, historico, operador
                            )
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                        """, lote)
                        pg_conn.commit()
                        registros_processados += len(lote)
                        print(f"Processados {registros_processados} registros...")
                        lote = []
                    except Exception as e:
                        print(f"Erro ao processar lote: {str(e)}")
                        lote = []
                        continue
                
            except Exception as e:
                print(f"Erro ao processar registro: {str(e)}")
                print(f"Data: {data}, Histórico: {historico}")
                continue

        print("\nMigração concluída!")
        
        # Verifica quantidade final
        pg_cursor.execute("SELECT COUNT(*) FROM movimentos_financeiros")
        total_final = pg_cursor.fetchone()[0]
        print(f"\nTotal de registros migrados: {total_final}")
        
        # Verifica totais
        pg_cursor.execute("""
            SELECT 
                COUNT(*) as total,
                SUM(credito) as total_creditos,
                SUM(debito) as total_debitos
            FROM movimentos_financeiros
        """)
        
        totais = pg_cursor.fetchone()
        print(f"\nResumo:")
        print(f"Total de registros: {totais[0]}")
        print(f"Total de créditos: R$ {totais[1]:,.2f}")
        print(f"Total de débitos: R$ {totais[2]:,.2f}")
        print(f"Saldo: R$ {(totais[1] - totais[2]):,.2f}")
        
    except Exception as e:
        print(f"Erro durante a migração: {str(e)}")
        if 'pg_conn' in locals():
            pg_conn.rollback()
        raise
    finally:
        if 'access_cursor' in locals():
            access_cursor.close()
        if 'access_conn' in locals():
            access_conn.close()
        if 'pg_cursor' in locals():
            pg_cursor.close()
        if 'pg_conn' in locals():
            pg_conn.close()

if __name__ == "__main__":
    print("Iniciando processo de reset e migração...")
    print("Data e hora início:", datetime.now())
    
    # Primeiro apaga todos os dados
    reset_financial_data()
    
    # Depois faz a nova migração
    migrate_movimentos()
    
    print("\nData e hora fim:", datetime.now())