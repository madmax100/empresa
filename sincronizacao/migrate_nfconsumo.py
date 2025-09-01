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

def get_existing_nfs(pg_cursor):
    pg_cursor.execute("SELECT id FROM notas_fiscais_consumo")
    return {row[0] for row in pg_cursor.fetchall()}

def get_valid_fornecedores(pg_cursor):
    pg_cursor.execute("SELECT id FROM fornecedores")
    return {row[0] for row in pg_cursor.fetchall()}

def migrar_nf_consumo():
    try:
        db_path = r"C:\Users\Cirilo\Documents\c3mcopias\Bancos\Movimentos\Outrosmovimentos.mdb"
        conn_str = (
            r'Driver={Microsoft Access Driver (*.mdb, *.accdb)};'
            f'DBQ={db_path};'
            'PWD=010182;'
        )

        with pyodbc.connect(conn_str) as access_conn, \
             psycopg2.connect(**PG_CONFIG) as pg_conn:
            
            pg_cursor = pg_conn.cursor()
            existing_nfs = get_existing_nfs(pg_cursor)
            fornecedores = get_valid_fornecedores(pg_cursor)

            access_cursor = access_conn.cursor()
            access_cursor.execute("""
                SELECT CodNFConsumo, NumNFConsumo, Data, Fornecedor,
                       ValorProdutos, BaseCalculo, Desconto, ValorFrete,
                       TipoFrete, Valoricms, Valoripi, Valoricmsfonte,
                       Valortotalnota, FormaPagto, Condicoes, CFOP,
                       Formulario, DataConhec, DataSelo, DataEntrada,
                       Tipo, Chave, Serie
                FROM NFConsumo 
                ORDER BY CodNFConsumo
            """)

            insert_sql = """
                INSERT INTO notas_fiscais_consumo (
                    id, numero_nota, data_emissao, fornecedor_id,
                    valor_produtos, base_calculo_icms, valor_desconto,
                    valor_frete, modalidade_frete, valor_icms, valor_ipi,
                    valor_icms_st, valor_total, forma_pagamento,
                    condicoes_pagamento, cfop, formulario, data_conhecimento,
                    data_selo, data_entrada, tipo_nota, chave_nfe, serie_nota
                ) VALUES %s
                ON CONFLICT (id) DO UPDATE SET
                    numero_nota = EXCLUDED.numero_nota,
                    data_emissao = EXCLUDED.data_emissao,
                    fornecedor_id = EXCLUDED.fornecedor_id,
                    valor_produtos = EXCLUDED.valor_produtos,
                    base_calculo_icms = EXCLUDED.base_calculo_icms,
                    valor_desconto = EXCLUDED.valor_desconto,
                    valor_frete = EXCLUDED.valor_frete,
                    modalidade_frete = EXCLUDED.modalidade_frete,
                    valor_icms = EXCLUDED.valor_icms,
                    valor_ipi = EXCLUDED.valor_ipi,
                    valor_icms_st = EXCLUDED.valor_icms_st,
                    valor_total = EXCLUDED.valor_total,
                    forma_pagamento = EXCLUDED.forma_pagamento,
                    condicoes_pagamento = EXCLUDED.condicoes_pagamento,
                    cfop = EXCLUDED.cfop,
                    formulario = EXCLUDED.formulario,
                    data_conhecimento = EXCLUDED.data_conhecimento,
                    data_selo = EXCLUDED.data_selo,
                    data_entrada = EXCLUDED.data_entrada,
                    tipo_nota = EXCLUDED.tipo_nota,
                    chave_nfe = EXCLUDED.chave_nfe,
                    serie_nota = EXCLUDED.serie_nota
            """

            insercoes = atualizacoes = erros = 0

            for row in access_cursor.fetchall():
                try:
                    nf_id = int(row[0])
                    fornecedor_id = int(row[3]) if row[3] else None

                    if fornecedor_id not in fornecedores:
                        continue

                    dados = (
                        (
                            nf_id,
                            clean_string(row[1]),
                            row[2],
                            fornecedor_id,
                            clean_decimal(row[4]),
                            clean_decimal(row[5]),
                            clean_decimal(row[6]),
                            clean_decimal(row[7]),
                            clean_string(row[8]),
                            clean_decimal(row[9]),
                            clean_decimal(row[10]),
                            clean_decimal(row[11]),
                            clean_decimal(row[12]),
                            clean_string(row[13]),
                            clean_string(row[14]),
                            clean_string(row[15]),
                            clean_string(row[16]),
                            row[17],
                            row[18],
                            row[19],
                            clean_string(row[20]),
                            clean_string(row[21]),
                            clean_string(row[22])
                        ),
                    )

                    pg_cursor.execute(insert_sql, dados)
                    pg_conn.commit()

                    if nf_id in existing_nfs:
                        atualizacoes += 1
                    else:
                        insercoes += 1

                except Exception as e:
                    erros += 1
                    print(f"Erro ao processar NF consumo {row[1]}: {str(e)}")
                    pg_conn.rollback()

            pg_cursor.execute("""
                SELECT setval('notas_fiscais_consumo_id_seq', 
                            COALESCE((SELECT MAX(id) FROM notas_fiscais_consumo), 1),
                            true);
            """)
            pg_conn.commit()

            print(f"\nNotas fiscais de consumo inseridas: {insercoes}")
            print(f"Notas fiscais de consumo atualizadas: {atualizacoes}")
            print(f"Erros: {erros}")

            return True

    except Exception as e:
        print(f"Erro durante a migração: {str(e)}")
        return False