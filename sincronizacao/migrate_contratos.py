import pyodbc
import psycopg2
from datetime import datetime
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
    try:
        return value if isinstance(value, datetime) else None
    except:
        return None

def get_existing_contratos(pg_cursor):
    pg_cursor.execute("SELECT id FROM contratos_locacao")
    return {row[0] for row in pg_cursor.fetchall()}

def get_valid_clientes(pg_cursor):
    pg_cursor.execute("SELECT id FROM clientes")
    return {row[0] for row in pg_cursor.fetchall()}

def migrar_contratos():
    try:
        db_path = CADASTROS_DB
        conn_str = (
            r'Driver={Microsoft Access Driver (*.mdb, *.accdb)};'
            f'DBQ={db_path};'
            'PWD=010182;'
        )

        with pyodbc.connect(conn_str) as access_conn, \
             psycopg2.connect(**PG_CONFIG) as pg_conn:
            
            pg_cursor = pg_conn.cursor()
            existing_contratos = get_existing_contratos(pg_cursor)
            valid_clientes = get_valid_clientes(pg_cursor)

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

            insert_sql = """
                INSERT INTO contratos_locacao (
                    id, contrato, cliente_id, tipocontrato, renovado,
                    totalmaquinas, valorcontrato, numeroparcelas,
                    valorpacela, referencia, data, inicio, fim,
                    ultimoatendimento, nmaquinas, clientereal,
                    tipocontratoreal, obs
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s, %s, %s, %s
                )
                ON CONFLICT (id) DO UPDATE SET
                    contrato = EXCLUDED.contrato,
                    cliente_id = EXCLUDED.cliente_id,
                    tipocontrato = EXCLUDED.tipocontrato,
                    renovado = EXCLUDED.renovado,
                    totalmaquinas = EXCLUDED.totalmaquinas,
                    valorcontrato = EXCLUDED.valorcontrato,
                    numeroparcelas = EXCLUDED.numeroparcelas,
                    valorpacela = EXCLUDED.valorpacela,
                    referencia = EXCLUDED.referencia,
                    data = EXCLUDED.data,
                    inicio = EXCLUDED.inicio,
                    fim = EXCLUDED.fim,
                    ultimoatendimento = EXCLUDED.ultimoatendimento,
                    nmaquinas = EXCLUDED.nmaquinas,
                    clientereal = EXCLUDED.clientereal,
                    tipocontratoreal = EXCLUDED.tipocontratoreal,
                    obs = EXCLUDED.obs
            """

            insercoes = atualizacoes = erros = 0

            for row in access_cursor.fetchall():
                try:
                    contrato_id = int(row[0].replace('C', ''))
                    cliente_id = int(row[1]) if row[1] else None

                    if cliente_id and cliente_id not in valid_clientes:
                        print(f"Cliente {cliente_id} não encontrado para o contrato {row[0]}")
                        continue

                    dados = (
                        contrato_id,
                        row[0],
                        cliente_id,
                        clean_string(row[2]),
                        clean_string(row[3]),
                        clean_string(row[4]),
                        clean_decimal(row[5]),
                        clean_string(row[6]),
                        clean_decimal(row[7]),
                        clean_string(row[8]),
                        clean_date(row[9]),
                        clean_date(row[10]),
                        clean_date(row[11]),
                        clean_date(row[12]),
                        clean_string(row[13]),
                        clean_string(row[14]),
                        clean_string(row[15]),
                        clean_string(row[16])
                    )

                    pg_cursor.execute(insert_sql, dados)
                    pg_conn.commit()

                    if contrato_id in existing_contratos:
                        atualizacoes += 1
                    else:
                        insercoes += 1

                except Exception as e:
                    erros += 1
                    print(f"Erro ao processar contrato {row[0]}: {str(e)}")
                    pg_conn.rollback()

            pg_cursor.execute("SELECT setval('contratos_locacao_id_seq', (SELECT MAX(id) FROM contratos_locacao));")
            pg_conn.commit()

            print(f"\nContratos inseridos: {insercoes}")
            print(f"Contratos atualizados: {atualizacoes}")
            print(f"Erros: {erros}")

            return True

    except Exception as e:
        print(f"Erro durante a migração: {str(e)}")
        return False


if __name__ == '__main__':
    migrar_contratos()