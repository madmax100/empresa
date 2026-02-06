
import pyodbc
import psycopg2
from config import PG_CONFIG, MOVIMENTOS_DB
from migrate_nfe import clean_string, clean_decimal, clean_frete, get_existing_nfe, get_valid_entities

def debug_nfe():
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
            existing_nfe = get_existing_nfe(pg_cursor)
            fornecedores, fretes = get_valid_entities(pg_cursor)

            access_cursor = access_conn.cursor()
            access_cursor.execute("""
                SELECT CodNFE, NumNFE, Data, Fornecedor, ValorProdutos,
                       BaseCalculo, Desconto, ValorFrete, TipoFrete, Valoricms,
                       Valoripi, Valoricmsfonte, Valortotalnota, FormaPagto,
                       Condicoes, Comprador, Operador, Formulario, Observação,
                       OutrosEncargos, Parcelas, Operacao, CFOP, DataEntrada,
                       Chave, Serie, Protocolo, Natureza, BaseSubstituicao,
                       ICMSSubstituicao, OutrasDespesas
                FROM NFE ORDER BY CodNFE
            """)

            insert_sql = """
                INSERT INTO notas_fiscais_entrada (
                    id, numero_nota, data_emissao, fornecedor_id, valor_produtos,
                    base_calculo_icms, valor_desconto, valor_frete, tipo_frete,
                    valor_icms, valor_ipi, valor_icms_st, valor_total, forma_pagamento,
                    condicoes_pagamento, comprador, operador, frete_id, observacao,
                    outros_encargos, parcelas, operacao, cfop, data_entrada,
                    chave_nfe, serie_nota, protocolo, natureza_operacao,
                    base_calculo_st, outras_despesas
                ) VALUES %s
                ON CONFLICT (id) DO UPDATE SET
                    numero_nota = EXCLUDED.numero_nota,
                    data_emissao = EXCLUDED.data_emissao,
                    fornecedor_id = EXCLUDED.fornecedor_id,
                    valor_produtos = EXCLUDED.valor_produtos,
                    base_calculo_icms = EXCLUDED.base_calculo_icms,
                    valor_desconto = EXCLUDED.valor_desconto,
                    valor_frete = EXCLUDED.valor_frete,
                    tipo_frete = EXCLUDED.tipo_frete,
                    valor_icms = EXCLUDED.valor_icms,
                    valor_ipi = EXCLUDED.valor_ipi,
                    valor_icms_st = EXCLUDED.valor_icms_st,
                    valor_total = EXCLUDED.valor_total,
                    forma_pagamento = EXCLUDED.forma_pagamento,
                    condicoes_pagamento = EXCLUDED.condicoes_pagamento,
                    comprador = EXCLUDED.comprador,
                    operador = EXCLUDED.operador,
                    frete_id = EXCLUDED.frete_id,
                    observacao = EXCLUDED.observacao,
                    outros_encargos = EXCLUDED.outros_encargos,
                    parcelas = EXCLUDED.parcelas,
                    operacao = EXCLUDED.operacao,
                    cfop = EXCLUDED.cfop,
                    data_entrada = EXCLUDED.data_entrada,
                    chave_nfe = EXCLUDED.chave_nfe,
                    serie_nota = EXCLUDED.serie_nota,
                    protocolo = EXCLUDED.protocolo,
                    natureza_operacao = EXCLUDED.natureza_operacao,
                    base_calculo_st = EXCLUDED.base_calculo_st,
                    outras_despesas = EXCLUDED.outras_despesas
            """

            row = access_cursor.fetchone() # Get just one row
            if row:
                print("DEBUG: Processing one row...")
                nfe_id = int(row[0])
                nfe_numero = clean_string(row[1])
                fornecedor_id = int(row[3]) if row[3] else None
                
                formulario = clean_frete(row[17])
                frete_id = fretes.get(formulario) if formulario else None
                
                valor_total = (
                    clean_decimal(row[4]) +     # valor_produtos
                    clean_decimal(row[7]) +     # valor_frete
                    clean_decimal(row[10]) +    # valor_ipi
                    clean_decimal(row[11]) +    # valor_icms_st
                    clean_decimal(row[29]) +    # outras_despesas
                    clean_decimal(row[19]) -    # outros_encargos
                    clean_decimal(row[6])       # valor_desconto
                )

                dados = (
                    (
                        nfe_id,
                        nfe_numero,
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
                        valor_total,
                        clean_string(row[13]),
                        clean_string(row[14]),
                        clean_string(row[15]),
                        clean_string(row[16]),
                        frete_id,
                        clean_string(row[18]),
                        clean_decimal(row[19]),
                        clean_string(row[20]),
                        clean_string(row[21]),
                        clean_string(row[22]),
                        row[23],
                        clean_string(row[24]),
                        clean_string(row[25]),
                        clean_string(row[26]),
                        clean_string(row[27]),
                        clean_decimal(row[28]),
                        clean_decimal(row[29])
                    ),
                )

                print(f"DEBUG: SQL Length: {len(insert_sql)}")
                print(f"DEBUG: SQL: {insert_sql!r}")
                print(f"DEBUG: Data: {dados!r}")
                
                pg_cursor.execute(insert_sql, dados)
                pg_conn.commit()
                print("DEBUG: Executed successfully!")

    except Exception as e:
        print(f"DEBUG ERROR: {e}")

if __name__ == "__main__":
    debug_nfe()
