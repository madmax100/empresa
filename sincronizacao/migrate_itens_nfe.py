import pyodbc
import psycopg2
from datetime import datetime
from decimal import Decimal
from config import PG_CONFIG, ACCESS_PASSWORD, CADASTROS_DB # ou o DB específico

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
    pg_cursor.execute("""
        SELECT DISTINCT nota_fiscal_id, produto_id
        FROM itens_nf_entrada
    """)
    return {(row[0], row[1]) for row in pg_cursor.fetchall()}

def get_valid_entities(pg_cursor):
    pg_cursor.execute("SELECT id, numero_nota FROM notas_fiscais_entrada WHERE numero_nota IS NOT NULL")
    notas = {clean_string(row[1]): row[0] for row in pg_cursor.fetchall()}
    
    pg_cursor.execute("SELECT id FROM produtos")
    produtos = {row[0] for row in pg_cursor.fetchall()}
    
    return notas, produtos

def migrar_itens_nfe():
    try:
        db_path = r"C:\Users\Cirilo\Documents\c3mcopias\Bancos\Movimentos\Movimentos.mdb"
        conn_str = (
            r'Driver={Microsoft Access Driver (*.mdb, *.accdb)};'
            f'DBQ={db_path};'
            'PWD=010182;'
        )

        with pyodbc.connect(conn_str) as access_conn, \
             psycopg2.connect(**PG_CONFIG) as pg_conn:
            
            pg_cursor = pg_conn.cursor()
            existing_items = get_existing_items(pg_cursor)
            notas_fiscais, produtos = get_valid_entities(pg_cursor)

            access_cursor = access_conn.cursor()
            access_cursor.execute("""
                SELECT NumNFE, Data, Produtos, Qtde, Valor, Total, PercIpi,
                       Status, Aliquota, Desconto, CFOP, BaseSubstituicao,
                       ICMSSubstituicao, OutrasDespesas, frete,
                       AliquotaSubstituicao, ContNCM, Controle
                FROM [Itens da NFE] 
                ORDER BY NumNFE
            """)

            insert_sql = """
                INSERT INTO itens_nf_entrada (
                    nota_fiscal_id, data, produto_id, quantidade,
                    valor_unitario, valor_total, percentual_ipi,
                    status, aliquota, desconto, cfop,
                    base_substituicao, icms_substituicao,
                    outras_despesas, frete, aliquota_substituicao,
                    ncm, controle
                ) VALUES %s
                ON CONFLICT (nota_fiscal_id, produto_id) DO UPDATE SET
                    data = EXCLUDED.data,
                    quantidade = EXCLUDED.quantidade,
                    valor_unitario = EXCLUDED.valor_unitario,
                    valor_total = EXCLUDED.valor_total,
                    percentual_ipi = EXCLUDED.percentual_ipi,
                    status = EXCLUDED.status,
                    aliquota = EXCLUDED.aliquota,
                    desconto = EXCLUDED.desconto,
                    cfop = EXCLUDED.cfop,
                    base_substituicao = EXCLUDED.base_substituicao,
                    icms_substituicao = EXCLUDED.icms_substituicao,
                    outras_despesas = EXCLUDED.outras_despesas,
                    frete = EXCLUDED.frete,
                    aliquota_substituicao = EXCLUDED.aliquota_substituicao,
                    ncm = EXCLUDED.ncm,
                    controle = EXCLUDED.controle
            """

            insercoes = atualizacoes = erros = 0

            for row in access_cursor.fetchall():
                try:
                    num_nfe = clean_string(str(row[0]))
                    nota_fiscal_id = notas_fiscais.get(num_nfe)
                    produto_id = int(row[2]) if row[2] is not None else None

                    if not nota_fiscal_id or produto_id not in produtos:
                        continue

                    dados = (
                        (
                            nota_fiscal_id,
                            row[1],
                            produto_id,
                            clean_decimal(row[3]),
                            clean_decimal(row[4]),
                            clean_decimal(row[5]),
                            clean_decimal(row[6]),
                            clean_string(row[7]),
                            clean_decimal(row[8]),
                            clean_decimal(row[9]),
                            clean_string(row[10]),
                            clean_decimal(row[11]),
                            clean_decimal(row[12]),
                            clean_decimal(row[13]),
                            clean_decimal(row[14]),
                            clean_decimal(row[15]),
                            clean_string(row[16]),
                            clean_string(row[17])
                        ),
                    )

                    pg_cursor.execute(insert_sql, dados)
                    pg_conn.commit()

                    if (nota_fiscal_id, produto_id) in existing_items:
                        atualizacoes += 1
                    else:
                        insercoes += 1

                except Exception as e:
                    erros += 1
                    print(f"Erro ao processar item da NFE {row[0]}: {str(e)}")
                    pg_conn.rollback()

            print(f"\nItens inseridos: {insercoes}")
            print(f"Itens atualizados: {atualizacoes}")
            print(f"Erros: {erros}")

            return True

    except Exception as e:
        print(f"Erro durante a migração: {str(e)}")
        return False