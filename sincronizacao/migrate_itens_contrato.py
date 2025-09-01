import pyodbc
import psycopg2
from datetime import datetime
from decimal import Decimal
from config import PG_CONFIG, ACCESS_PASSWORD, CADASTROS_DB

def clean_string(value):
    return str(value).strip() if value else None

def get_existing_items(pg_cursor):
    pg_cursor.execute("SELECT id FROM itens_contrato_locacao")
    return {row[0] for row in pg_cursor.fetchall()}

def get_valid_entities(pg_cursor):
    pg_cursor.execute("SELECT id, contrato FROM contratos_locacao")
    contratos = {row[1]: row[0] for row in pg_cursor.fetchall()}
    
    pg_cursor.execute("SELECT id, id FROM categorias_produtos")
    categorias = {str(row[0]): row[1] for row in pg_cursor.fetchall()}
    
    return contratos, categorias

def migrar_itens_contrato():
    try:
        conn_str = (
            r'Driver={Microsoft Access Driver (*.mdb, *.accdb)};'
            f'DBQ={CADASTROS_DB};'
            f'PWD={ACCESS_PASSWORD};'
        )

        with pyodbc.connect(conn_str) as access_conn, \
             psycopg2.connect(**PG_CONFIG) as pg_conn:
            
            pg_cursor = pg_conn.cursor()
            existing_items = get_existing_items(pg_cursor)
            contratos, categorias = get_valid_entities(pg_cursor)

            access_cursor = access_conn.cursor()
            access_cursor.execute("""
                SELECT Codigo, Contrato, Serie, Categoria, 
                       Modelo, Inicio, Fim
                FROM [Itens dos Contratos]
                ORDER BY Codigo
            """)

            insert_sql = """
                INSERT INTO itens_contrato_locacao (
                    id, contrato_id, numeroserie, categoria_id, modelo,
                    inicio, fim
                ) VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (id) DO UPDATE SET
                    contrato_id = EXCLUDED.contrato_id,
                    numeroserie = EXCLUDED.numeroserie,
                    categoria_id = EXCLUDED.categoria_id,
                    modelo = EXCLUDED.modelo,
                    inicio = EXCLUDED.inicio,
                    fim = EXCLUDED.fim
            """

            insercoes = atualizacoes = erros = 0

            for row in access_cursor.fetchall():
                try:
                    item_id = int(row[0])
                    contrato_numero = row[1]
                    contrato_id = contratos.get(contrato_numero)
                    categoria_codigo = str(row[3]) if row[3] is not None else None
                    categoria_id = categorias.get(categoria_codigo)

                    if not contrato_id:
                        print(f"Contrato não encontrado: {contrato_numero}")
                        continue

                    dados = (
                        item_id,
                        contrato_id,
                        clean_string(row[2]),
                        categoria_id,
                        clean_string(row[4]),
                        row[5],
                        row[6]
                    )

                    pg_cursor.execute(insert_sql, dados)
                    pg_conn.commit()

                    if item_id in existing_items:
                        atualizacoes += 1
                    else:
                        insercoes += 1

                except Exception as e:
                    erros += 1
                    print(f"Erro ao processar item {row[0]}: {str(e)}")
                    pg_conn.rollback()

            pg_cursor.execute("SELECT setval('itens_contrato_locacao_id_seq', (SELECT MAX(id) FROM itens_contrato_locacao));")
            pg_conn.commit()

            print(f"\nItens inseridos: {insercoes}")
            print(f"Itens atualizados: {atualizacoes}")
            print(f"Erros: {erros}")

            return True

    except Exception as e:
        print(f"Erro durante a migração: {str(e)}")
        return False