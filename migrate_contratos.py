import pyodbc
import psycopg2
from datetime import datetime
from decimal import Decimal
import re

def clean_string(value):
    if value is None:
        return None
    return str(value).strip()

def clean_decimal(value):
    if value is None:
        return Decimal('0.00')
    try:
        clean_value = re.sub(r'[^\d.,\-]', '', str(value))
        clean_value = clean_value.replace(',', '.')
        return Decimal(clean_value).quantize(Decimal('0.01'))
    except:
        return Decimal('0.00')

def clean_date(value):
    if value is None:
        return None
    try:
        if isinstance(value, datetime):
            return value
        return None
    except:
        return None

def limpar_tabelas(pg_conn):
    try:
        cursor = pg_conn.cursor()
        
        print("\nIniciando limpeza das tabelas...")
        cursor.execute("SET session_replication_role = 'replica';")
        
        tabelas = [
            'itens_contrato_locacao',
            'contratos_locacao'
        ]
        
        for tabela in tabelas:
            try:
                print(f"\nVerificando tabela {tabela}...")
                cursor.execute(f"SELECT COUNT(*) FROM {tabela}")
                qtd_antes = cursor.fetchone()[0]
                print(f"Registros encontrados em {tabela}: {qtd_antes}")
                
                if qtd_antes > 0:
                    print(f"Limpando tabela {tabela}...")
                    cursor.execute(f"TRUNCATE TABLE {tabela} CASCADE")
                    pg_conn.commit()
                    print(f"Tabela {tabela} limpa com sucesso!")
                
            except Exception as e:
                print(f"Erro ao limpar tabela {tabela}: {str(e)}")
                pg_conn.rollback()
                raise
        
        cursor.execute("SET session_replication_role = 'origin';")
        pg_conn.commit()
        
        print("\nLimpeza concluída com sucesso!")
        return True
        
    except Exception as e:
        print(f"Erro durante a limpeza: {str(e)}")
        pg_conn.rollback()
        return False

def migrar_contratos():
    pg_config = {
        'dbname': 'c3mcopiasdb2',
        'user': 'cirilomax',
        'password': '226cmm100',
        'host': 'localhost',
        'port': '5432'
    }

    db_path = r"C:\Users\Cirilo\Documents\c3mcopias\Bancos\cadastros\Cadastros.mdb"
    
    try:
        # Conexões
        print("Conectando aos bancos de dados...")
        conn_str = (
            r'Driver={Microsoft Access Driver (*.mdb, *.accdb)};'
            f'DBQ={db_path};'
            'PWD=010182;'
        )
        access_conn = pyodbc.connect(conn_str)
        pg_conn = psycopg2.connect(**pg_config)
        
        # Limpar tabelas
        if not limpar_tabelas(pg_conn):
            raise Exception("Falha na limpeza das tabelas. Abortando importação.")

        pg_cursor = pg_conn.cursor()

        # Verificar clientes existentes
        print("\nVerificando clientes existentes...")
        pg_cursor.execute("SELECT id FROM clientes")
        clientes_existentes = {row[0] for row in pg_cursor.fetchall()}

        # Busca dados do Access
        print("\nBuscando dados do Access...")
        access_cursor = access_conn.cursor()
        access_cursor.execute("""
            SELECT Contrato, Cliente, TipoContrato, Renovado, 
                   TotalMaquinas, ValorContrato, NumeroParcelas, 
                   ValorPacela, Referencia, Data, Incio, Fim, 
                   UltimoAtendimento, NMaquinas, ClienteReal, 
                   TipoContratoReal, Obs
            FROM Contratos 
            ORDER BY Contrato
        """)

        # SQL de inserção
        insert_sql = """
            INSERT INTO contratos_locacao (
                id, contrato, cliente_id, tipocontrato, renovado,
                totalmaquinas, valorcontrato, numeroparcelas,
                valorpacela, referencia, data, incio, fim,
                ultimoatendimento, nmaquinas, clientereal,
                tipocontratoreal, obs
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, %s, %s, %s
            )
        """

        # Processo de migração
        contador = 0
        erros = 0
        
        print("\nIniciando migração dos contratos...")
        
        while True:
            rows = access_cursor.fetchmany(1000)
            if not rows:
                break
            
            for row in rows:
                try:
                    contrato_id = int(row[0].replace('C', ''))  # Remove o 'C' do número do contrato
                    cliente_id = int(row[1]) if row[1] else None

                    # Verificar se o cliente existe
                    if cliente_id and cliente_id not in clientes_existentes:
                        print(f"Cliente {cliente_id} não encontrado para o contrato {row[0]}")
                        continue

                    dados = (
                        contrato_id,               # id
                        row[0],                    # contrato (com o 'C')
                        cliente_id,                # cliente_id
                        clean_string(row[2]),      # tipocontrato
                        clean_string(row[3]),      # renovado
                        clean_string(row[4]),      # totalmaquinas
                        clean_decimal(row[5]),     # valorcontrato
                        clean_string(row[6]),      # numeroparcelas
                        clean_decimal(row[7]),     # valorpacela
                        clean_string(row[8]),      # referencia
                        clean_date(row[9]),        # data
                        clean_date(row[10]),       # incio
                        clean_date(row[11]),       # fim
                        clean_date(row[12]),       # ultimoatendimento
                        clean_string(row[13]),     # nmaquinas
                        clean_string(row[14]),     # clientereal
                        clean_string(row[15]),     # tipocontratoreal
                        clean_string(row[16])      # obs
                    )
                    
                    pg_cursor.execute(insert_sql, dados)
                    pg_conn.commit()
                    contador += 1
                    
                    if contador % 50 == 0:
                        print(f"Migrados {contador} contratos...")
                
                except Exception as e:
                    erros += 1
                    print(f"Erro ao migrar contrato {row[0]}: {str(e)}")
                    print("Dados:", row)
                    pg_conn.rollback()
                    continue

        print("\nMigração concluída!")
        print(f"Total de contratos migrados: {contador}")
        print(f"Total de erros: {erros}")
        
        # Atualizar sequence
        pg_cursor.execute("""
            SELECT setval('contratos_locacao_id_seq', 
                         (SELECT MAX(id) FROM contratos_locacao));
        """)
        pg_conn.commit()
        
    except Exception as e:
        print(f"Erro durante a migração: {str(e)}")
        if 'pg_conn' in locals():
            pg_conn.rollback()
    finally:
        if 'access_conn' in locals():
            access_conn.close()
        if 'pg_conn' in locals():
            pg_conn.close()

if __name__ == "__main__":
    print("=== MIGRAÇÃO DE CONTRATOS ===")
    print("Início:", datetime.now())
    migrar_contratos()
    print("Fim:", datetime.now())
