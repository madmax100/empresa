import pyodbc
import psycopg2
from datetime import datetime
from decimal import Decimal
from config import PG_CONFIG, ACCESS_PASSWORD, CADASTROS_DB, MOVIMENTOS_DB # ou o DB específico

def clean_string(value):
    return str(value).strip() if value else None

def clean_decimal(value):
    if not value:
        return Decimal('0.00')
    try:
        return Decimal(str(value)).quantize(Decimal('0.01'))
    except:
        return Decimal('0.00')

def get_existing_items(pg_cursor):
    pg_cursor.execute("SELECT id FROM itens_nf_saida")
    return set(row[0] for row in pg_cursor.fetchall())

def get_valid_nfs(pg_cursor):
    pg_cursor.execute("SELECT id, numero_nota FROM notas_fiscais_saida")
    return {clean_string(row[1]): row[0] for row in pg_cursor.fetchall()}

def get_valid_produtos(pg_cursor):
    pg_cursor.execute("SELECT id FROM produtos")
    return {row[0] for row in pg_cursor.fetchall()}

def migrar_itens_nfs():
    try:
        db_path = MOVIMENTOS_DB
        conn_str = (
            r'Driver={Microsoft Access Driver (*.mdb, *.accdb)};'
            f'DBQ={db_path};'
            'PWD=010182;'
        )

        with pyodbc.connect(conn_str) as access_conn, \
             psycopg2.connect(**PG_CONFIG) as pg_conn:
            
            pg_cursor = pg_conn.cursor()
            existing_items = get_existing_items(pg_cursor)
            notas_fiscais = get_valid_nfs(pg_cursor)
            produtos = get_valid_produtos(pg_cursor)

            access_cursor = access_conn.cursor()
            access_cursor.execute("""
                SELECT CodItemNFS, NumNFS, Data, Produtos, Qtde, Valor, Total,
                       PercIpi, Status, Aliquota, Reducao, Desconto, CSTA, CSTB,
                       Controle, Frete, OutrasDespesas, Seguro
                FROM [Itens da NFS] 
                ORDER BY NumNFS
            """)

            insercoes = atualizacoes = erros = 0

            for row in access_cursor.fetchall():
                try:
                    num_nfs = clean_string(str(row[1]))
                    nota_fiscal_id = notas_fiscais.get(num_nfs)
                    produto_id = int(row[3]) if row[3] is not None else None

                    if not nota_fiscal_id:
                        continue
                    if produto_id not in produtos:
                        continue

                    dados = (
                        nota_fiscal_id,
                        row[2],
                        produto_id,
                        clean_decimal(row[4]),
                        clean_decimal(row[5]),
                        clean_decimal(row[6]),
                        clean_decimal(row[7]),
                        clean_string(row[8]),
                        clean_decimal(row[9]),
                        clean_decimal(row[10]),
                        clean_decimal(row[11]),
                        clean_string(row[12]),
                        clean_string(row[13]),
                        clean_string(row[14]),
                        clean_decimal(row[15]),
                        clean_decimal(row[16]),
                        clean_decimal(row[17])
                    )

                    pg_cursor.execute("""
                        INSERT INTO itens_nf_saida (
                            nota_fiscal_id, data, produto_id, quantidade, valor_unitario,
                            valor_total, percentual_ipi, status, aliquota, reducao,
                            desconto, cst_a, cst_b, controle, frete, outras_despesas, seguro
                        ) VALUES %s
                    """, (dados,))
                    
                    pg_conn.commit()

                    if (nota_fiscal_id, produto_id) in existing_items:
                        atualizacoes += 1
                    else:
                        insercoes += 1

                except Exception as e:
                    erros += 1
                    print(f"Erro ao processar item da NF {row[1]}: {str(e)}")
                    pg_conn.rollback()

            print(f"\nItens inseridos: {insercoes}")
            print(f"Itens atualizados: {atualizacoes}")
            print(f"Erros: {erros}")

            return True

    except Exception as e:
        print(f"Erro durante a migração: {str(e)}")
        return False