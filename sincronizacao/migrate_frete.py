import pyodbc
import psycopg2
from datetime import datetime
from decimal import Decimal
from config import PG_CONFIG, ACCESS_PASSWORD, CADASTROS_DB, OUTROS_MOVIMENTOS_DB # ou o DB específico

def clean_string(value):
    return str(value).strip() if value else None

def clean_decimal(value):
    if not value:
        return Decimal('0.00')
    try:
        return Decimal(str(value)).quantize(Decimal('0.01'))
    except:
        return Decimal('0.00')

def get_existing_fretes(pg_cursor):
    pg_cursor.execute("SELECT id FROM fretes")
    return {row[0] for row in pg_cursor.fetchall()}

def get_valid_transportadoras(pg_cursor):
    pg_cursor.execute("SELECT id FROM transportadoras")
    return {row[0] for row in pg_cursor.fetchall()}

def migrar_fretes():
    try:
        db_path = OUTROS_MOVIMENTOS_DB
        conn_str = (
            r'Driver={Microsoft Access Driver (*.mdb, *.accdb)};'
            f'DBQ={db_path};'
            'PWD=010182;'
        )

        with pyodbc.connect(conn_str) as access_conn, \
             psycopg2.connect(**PG_CONFIG) as pg_conn:
            
            pg_cursor = pg_conn.cursor()
            existing_fretes = get_existing_fretes(pg_cursor)
            transportadoras = get_valid_transportadoras(pg_cursor)

            access_cursor = access_conn.cursor()
            access_cursor.execute("""
                SELECT Codigo, Numero, DataEmissão, DataEntrada, Frete, 
                       Transportadora, CFOP, ValorTotal, BaseCalculo, Aliquota,
                       ICMS, UFColeta, MunicipioColeta, CodIbge, Tipo, 
                       Chave, Fatura, Formulario
                FROM Fretes 
                ORDER BY Codigo
            """)

            insert_sql = """
                INSERT INTO fretes (
                    id, numero, data_emissao, data_entrada, transportadora_id,
                    cfop, valor_total, base_calculo, aliquota, icms,
                    ufcoleta, municipiocoleta, ibge, tipo_cte, tipo_fob_cif,
                    chave, fatura, formulario
                ) VALUES %s
                ON CONFLICT (id) DO UPDATE SET
                    numero = EXCLUDED.numero,
                    data_emissao = EXCLUDED.data_emissao,
                    data_entrada = EXCLUDED.data_entrada,
                    transportadora_id = EXCLUDED.transportadora_id,
                    cfop = EXCLUDED.cfop,
                    valor_total = EXCLUDED.valor_total,
                    base_calculo = EXCLUDED.base_calculo,
                    aliquota = EXCLUDED.aliquota,
                    icms = EXCLUDED.icms,
                    ufcoleta = EXCLUDED.ufcoleta,
                    municipiocoleta = EXCLUDED.municipiocoleta,
                    ibge = EXCLUDED.ibge,
                    tipo_cte = EXCLUDED.tipo_cte,
                    tipo_fob_cif = EXCLUDED.tipo_fob_cif,
                    chave = EXCLUDED.chave,
                    fatura = EXCLUDED.fatura,
                    formulario = EXCLUDED.formulario
            """

            insercoes = atualizacoes = erros = 0

            for row in access_cursor.fetchall():
                try:
                    frete_id = int(row[0])
                    transportadora_id = int(row[5]) if row[5] and str(row[5]) != '-' else None

                    if transportadora_id and transportadora_id not in transportadoras:
                        transportadora_id = None

                    dados = (
                        (
                            frete_id,
                            clean_string(row[1]),
                            row[2],
                            row[3],
                            transportadora_id,
                            clean_string(row[6]),
                            clean_decimal(row[7]),
                            clean_decimal(row[8]),
                            clean_decimal(row[9]),
                            clean_decimal(row[10]),
                            clean_string(row[11]),
                            clean_string(row[12]),
                            clean_string(row[13]),
                            clean_string(row[14]),
                            clean_string(row[4]),
                            clean_string(row[15]),
                            clean_string(row[16]),
                            clean_string(row[17])
                        ),
                    )

                    pg_cursor.execute(insert_sql, dados)
                    pg_conn.commit()

                    if frete_id in existing_fretes:
                        atualizacoes += 1
                    else:
                        insercoes += 1

                except Exception as e:
                    erros += 1
                    print(f"Erro ao processar frete {row[0]}: {str(e)}")
                    pg_conn.rollback()

            pg_cursor.execute("SELECT setval('fretes_id_seq', (SELECT MAX(id) FROM fretes));")
            pg_conn.commit()

            print(f"\nFretes inseridos: {insercoes}")
            print(f"Fretes atualizados: {atualizacoes}")
            print(f"Erros: {erros}")

            return True

    except Exception as e:
        print(f"Erro durante a migração: {str(e)}")
        return False