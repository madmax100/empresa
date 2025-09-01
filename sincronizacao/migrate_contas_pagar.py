import pyodbc
import psycopg2
from datetime import datetime, date
from decimal import Decimal
import re
from config import PG_CONFIG, ACCESS_PASSWORD, CADASTROS_DB # ou o DB específico

def clean_string(value):
    return str(value).strip() if value else None

def clean_decimal(value):
    if not value:
        return Decimal('0.00')
    try:
        clean_value = re.sub(r'[^\d.,\-]', '', str(value))
        clean_value = clean_value.replace(',', '.')
        return Decimal(clean_value).quantize(Decimal('0.01'))
    except:
        return Decimal('0.00')

def clean_date(value):
    if not value:
        return None
    if isinstance(value, (datetime, date)):
        return value
    try:
        clean_value = str(value).strip()
        return datetime.strptime(clean_value, '%Y-%m-%d %H:%M:%S').date() if clean_value else None
    except:
        try:
            return datetime.strptime(clean_value, '%d/%m/%Y').date()
        except:
            return None

def determinar_status(row):
    if row[16] and str(row[16]).strip().upper() in ['A', 'P', 'C']:
        return str(row[16]).strip().upper()
    if row[13]:
        return 'P'
    valor_pago = clean_decimal(row[14])
    if valor_pago >= clean_decimal(row[2]):
        return 'P'
    return 'A'

def get_existing_contas(pg_cursor):
    pg_cursor.execute("SELECT id FROM contas_pagar")
    return {row[0] for row in pg_cursor.fetchall()}

def get_valid_entities(pg_cursor):
    pg_cursor.execute("SELECT id FROM fornecedores")
    fornecedores = {row[0] for row in pg_cursor.fetchall()}
    
    pg_cursor.execute("SELECT id FROM contas_bancarias")
    contas = {row[0] for row in pg_cursor.fetchall()}
    
    return fornecedores, contas

def migrar_contas_pagar():
    try:
        db_path = r"C:\Users\Cirilo\Documents\empresa\Bancos\Contas\Contas.mdb"
        conn_str = (
            r'Driver={Microsoft Access Driver (*.mdb, *.accdb)};'
            f'DBQ={db_path};'
            'PWD=010182;'
        )

        with pyodbc.connect(conn_str) as access_conn, \
             psycopg2.connect(**PG_CONFIG) as pg_conn:
            
            pg_cursor = pg_conn.cursor()
            existing_contas = get_existing_contas(pg_cursor)
            fornecedores, contas = get_valid_entities(pg_cursor)

            access_cursor = access_conn.cursor()
            access_cursor.execute("""
                SELECT [CodConta a Pagar], Data, Valor, Fornecedor, Vencimento,
                       ValorTotalPago, Historico, FormaPagto, Condicoes,
                       Confirmacao, Juros, Tarifas, NDuplicata, DataPagto,
                       ValorPago, Local, Status, Conta
                FROM Pagar
                ORDER BY [CodConta a Pagar]
            """)

            insert_sql = """
                INSERT INTO contas_pagar (
                    id, data, valor, fornecedor_id, vencimento,
                    valor_total_pago, historico, forma_pagamento,
                    condicoes, confirmacao, juros, tarifas,
                    numero_duplicata, data_pagamento, valor_pago,
                    local, status, conta_id
                ) VALUES %s
                ON CONFLICT (id) DO UPDATE SET
                    data = EXCLUDED.data,
                    valor = EXCLUDED.valor,
                    fornecedor_id = EXCLUDED.fornecedor_id,
                    vencimento = EXCLUDED.vencimento,
                    valor_total_pago = EXCLUDED.valor_total_pago,
                    historico = EXCLUDED.historico,
                    forma_pagamento = EXCLUDED.forma_pagamento,
                    condicoes = EXCLUDED.condicoes,
                    confirmacao = EXCLUDED.confirmacao,
                    juros = EXCLUDED.juros,
                    tarifas = EXCLUDED.tarifas,
                    numero_duplicata = EXCLUDED.numero_duplicata,
                    data_pagamento = EXCLUDED.data_pagamento,
                    valor_pago = EXCLUDED.valor_pago,
                    local = EXCLUDED.local,
                    status = EXCLUDED.status,
                    conta_id = EXCLUDED.conta_id
            """

            insercoes = atualizacoes = erros = 0
            zerados = 0

            for row in access_cursor.fetchall():
                try:
                    conta_id = int(row[0])

                    if clean_decimal(row[2]) == Decimal('0.00'):
                        zerados += 1
                        continue

                    fornecedor_id = int(row[3]) if row[3] and str(row[3]).strip() != '0' else None
                    if fornecedor_id not in fornecedores:
                        if not row[6]:
                            continue
                        fornecedor_id = None

                    conta_bancaria_id = None
                    if row[17] and str(row[17]).strip() != '0':
                        try:
                            temp_conta_id = int(row[17])
                            if temp_conta_id in contas:
                                conta_bancaria_id = temp_conta_id
                        except (ValueError, TypeError):
                            pass

                    dados = (
                        (
                            conta_id,
                            clean_date(row[1]),
                            clean_decimal(row[2]),
                            fornecedor_id,
                            clean_date(row[4]),
                            clean_decimal(row[5]),
                            clean_string(row[6]),
                            clean_string(row[7]),
                            clean_string(row[8]),
                            clean_string(row[9]),
                            clean_decimal(row[10]),
                            clean_decimal(row[11]),
                            clean_string(row[12]),
                            clean_date(row[13]),
                            clean_decimal(row[14]),
                            clean_string(row[15]),
                            determinar_status(row),
                            conta_bancaria_id
                        ),
                    )

                    pg_cursor.execute(insert_sql, dados)
                    pg_conn.commit()

                    if conta_id in existing_contas:
                        atualizacoes += 1
                    else:
                        insercoes += 1

                except Exception as e:
                    erros += 1
                    print(f"Erro ao processar conta a pagar {row[0]}: {str(e)}")
                    pg_conn.rollback()

            print(f"\nContas a pagar inseridas: {insercoes}")
            print(f"Contas a pagar atualizadas: {atualizacoes}")
            print(f"Contas com valor zero: {zerados}")
            print(f"Erros: {erros}")

            return True

    except Exception as e:
        print(f"Erro durante a migração: {str(e)}")
        return False