import pyodbc
import psycopg2
from datetime import datetime
from decimal import Decimal
import re
from config import PG_CONFIG, ACCESS_PASSWORD, CADASTROS_DB, CONTAS_DB # ou o DB específico

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

def clean_boolean(value):
    return bool(value) if value else False

def determinar_status(row):
    if row[19] and str(row[19]).strip().upper() in ['A', 'P', 'C']:
        return str(row[19]).strip().upper()
    if row[15]:
        return 'P'
    valor_recebido = clean_decimal(row[14])
    if valor_recebido >= clean_decimal(row[2]):
        return 'P'
    return 'A'

def get_existing_contas(pg_cursor):
    pg_cursor.execute("SELECT id FROM contas_receber")
    return {row[0] for row in pg_cursor.fetchall()}

def get_valid_entities(pg_cursor):
    pg_cursor.execute("SELECT id FROM clientes")
    clientes = {row[0] for row in pg_cursor.fetchall()}
    
    pg_cursor.execute("SELECT id FROM contas_bancarias")
    contas = {row[0] for row in pg_cursor.fetchall()}
    
    return clientes, contas

def migrar_contas_receber():
    try:
        db_path = CONTAS_DB
        conn_str = (
            r'Driver={Microsoft Access Driver (*.mdb, *.accdb)};'
            f'DBQ={db_path};'
            'PWD=010182;'
        )

        with pyodbc.connect(conn_str) as access_conn, \
             psycopg2.connect(**PG_CONFIG) as pg_conn:
            
            pg_cursor = pg_conn.cursor()
            existing_contas = get_existing_contas(pg_cursor)
            clientes, contas = get_valid_entities(pg_cursor)

            access_cursor = access_conn.cursor()
            access_cursor.execute("""
                SELECT [CodConta a Receber], Documento, Data, Valor, Cliente,
                       Vencimento, ValorTotalPago, Historico, FormaPagto,
                       Condicoes, Confirmacao, Juros, Tarifas, NN, Recebido,
                       DataPagto, Local, Conta, Impresso, Status, Comanda,
                       RepassadoFactory, Factory, ValorFactory, StatusFactory,
                       ValorPagoFactory, Cartorio, Protesto, Desconto,
                       DataPagtoFactory
                FROM Receber
                ORDER BY [CodConta a Receber]
            """)

            insert_sql = """
                INSERT INTO contas_receber (
                    id, documento, data, valor, cliente_id, vencimento,
                    valor_total_pago, historico, forma_pagamento, condicoes,
                    confirmacao, juros, tarifas, nosso_numero, recebido,
                    data_pagamento, local, conta_id, impresso, status,
                    comanda, repassado_factory, factory, valor_factory,
                    status_factory, valor_pago_factory, cartorio, protesto,
                    desconto, data_pagto_factory
                ) VALUES %s
                ON CONFLICT (id) DO UPDATE SET
                    documento = EXCLUDED.documento,
                    data = EXCLUDED.data,
                    valor = EXCLUDED.valor,
                    cliente_id = EXCLUDED.cliente_id,
                    vencimento = EXCLUDED.vencimento,
                    valor_total_pago = EXCLUDED.valor_total_pago,
                    historico = EXCLUDED.historico,
                    forma_pagamento = EXCLUDED.forma_pagamento,
                    condicoes = EXCLUDED.condicoes,
                    confirmacao = EXCLUDED.confirmacao,
                    juros = EXCLUDED.juros,
                    tarifas = EXCLUDED.tarifas,
                    nosso_numero = EXCLUDED.nosso_numero,
                    recebido = EXCLUDED.recebido,
                    data_pagamento = EXCLUDED.data_pagamento,
                    local = EXCLUDED.local,
                    conta_id = EXCLUDED.conta_id,
                    impresso = EXCLUDED.impresso,
                    status = EXCLUDED.status,
                    comanda = EXCLUDED.comanda,
                    repassado_factory = EXCLUDED.repassado_factory,
                    factory = EXCLUDED.factory,
                    valor_factory = EXCLUDED.valor_factory,
                    status_factory = EXCLUDED.status_factory,
                    valor_pago_factory = EXCLUDED.valor_pago_factory,
                    cartorio = EXCLUDED.cartorio,
                    protesto = EXCLUDED.protesto,
                    desconto = EXCLUDED.desconto,
                    data_pagto_factory = EXCLUDED.data_pagto_factory
            """

            insercoes = atualizacoes = erros = 0
            zerados = 0

            for row in access_cursor.fetchall():
                try:
                    conta_id = int(row[0])
                    
                    if clean_decimal(row[3]) == Decimal('0.00'):
                        zerados += 1
                        continue

                    cliente_id = None
                    if row[4] and str(row[4]).strip() != '0':
                        try:
                            temp_cliente_id = int(row[4])
                            if temp_cliente_id in clientes:
                                cliente_id = temp_cliente_id
                            elif not row[7]:
                                continue
                        except (ValueError, TypeError):
                            pass

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
                            clean_string(row[1]),
                            row[2],
                            clean_decimal(row[3]),
                            cliente_id,
                            row[5],
                            clean_decimal(row[6]),
                            clean_string(row[7]),
                            clean_string(row[8]),
                            clean_string(row[9]),
                            clean_string(row[10]),
                            clean_decimal(row[11]),
                            clean_decimal(row[12]),
                            clean_string(row[13]),
                            clean_decimal(row[14]),
                            row[15],
                            clean_string(row[16]),
                            conta_bancaria_id,
                            clean_boolean(row[18]),
                            determinar_status(row),
                            clean_string(row[20]),
                            clean_boolean(row[21]),
                            clean_string(row[22]),
                            clean_decimal(row[23]),
                            clean_string(row[24]),
                            clean_decimal(row[25]),
                            clean_boolean(row[26]),
                            clean_boolean(row[27]),
                            clean_decimal(row[28]),
                            row[29]
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
                    print(f"Erro ao processar conta a receber {row[0]}: {str(e)}")
                    pg_conn.rollback()

            print(f"\nContas a receber inseridas: {insercoes}")
            print(f"Contas a receber atualizadas: {atualizacoes}")
            print(f"Contas com valor zero: {zerados}")
            print(f"Erros: {erros}")

            return True

    except Exception as e:
        print(f"Erro durante a migração: {str(e)}")
        return False