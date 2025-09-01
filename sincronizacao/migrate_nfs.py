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
    pg_cursor.execute("SELECT numero_nota FROM notas_fiscais_saida")
    return {row[0] for row in pg_cursor.fetchall()}

def get_valid_entities(pg_cursor):
    pg_cursor.execute("SELECT id FROM clientes")
    clientes = {row[0] for row in pg_cursor.fetchall()}

    pg_cursor.execute("SELECT id FROM funcionarios")
    funcionarios = {row[0] for row in pg_cursor.fetchall()}

    pg_cursor.execute("SELECT id FROM transportadoras")
    transportadoras = {row[0] for row in pg_cursor.fetchall()}

    return clientes, funcionarios, transportadoras

def migrar_nfs():
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
            existing_nfs = get_existing_nfs(pg_cursor)
            clientes, funcionarios, transportadoras = get_valid_entities(pg_cursor)

            access_cursor = access_conn.cursor()
            access_cursor.execute("""
                SELECT NumNFS, Data, Cliente, ValorProdutos, BaseCalculo, Desconto,
                       ValorFrete, TipoFrete, Valoricms, Valoripi, Valoricmsfonte,
                       Valortotalnota, FormaPagto, Condicoes, vendedor, Operador,
                       Transportadora, Formulario, Peso, Volume, Obs, Operacao,
                       CFOP, ImpostoFederalTotal, NSerie, Comissao, Parcelas,
                       ValRef, PercentualICMS, Detalhes, NFReferencia, Finalidade,
                       OutrasDespesas, Seguro
                FROM NFS ORDER BY NumNFS
            """)

            insert_sql = """
                INSERT INTO notas_fiscais_saida (
                    numero_nota, data, cliente_id, valor_produtos, base_calculo,
                    desconto, valor_frete, tipo_frete, valor_icms, valor_ipi,
                    valor_icms_fonte, valor_total_nota, forma_pagamento, condicoes,
                    vendedor_id, operador, transportadora_id, formulario, peso,
                    volume, obs, operacao, cfop, imposto_federal_total, n_serie,
                    comissao, parcelas, val_ref, percentual_icms, detalhes,
                    nf_referencia, finalidade, outras_despesas, seguro
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                         %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                         %s, %s, %s, %s, %s, %s)
                ON CONFLICT (numero_nota) DO UPDATE SET
                    data = EXCLUDED.data,
                    cliente_id = EXCLUDED.cliente_id,
                    valor_produtos = EXCLUDED.valor_produtos,
                    base_calculo = EXCLUDED.base_calculo,
                    desconto = EXCLUDED.desconto,
                    valor_frete = EXCLUDED.valor_frete,
                    tipo_frete = EXCLUDED.tipo_frete,
                    valor_icms = EXCLUDED.valor_icms,
                    valor_ipi = EXCLUDED.valor_ipi,
                    valor_icms_fonte = EXCLUDED.valor_icms_fonte,
                    valor_total_nota = EXCLUDED.valor_total_nota,
                    forma_pagamento = EXCLUDED.forma_pagamento,
                    condicoes = EXCLUDED.condicoes,
                    vendedor_id = EXCLUDED.vendedor_id,
                    operador = EXCLUDED.operador,
                    transportadora_id = EXCLUDED.transportadora_id,
                    formulario = EXCLUDED.formulario,
                    peso = EXCLUDED.peso,
                    volume = EXCLUDED.volume,
                    obs = EXCLUDED.obs,
                    operacao = EXCLUDED.operacao,
                    cfop = EXCLUDED.cfop,
                    imposto_federal_total = EXCLUDED.imposto_federal_total,
                    n_serie = EXCLUDED.n_serie,
                    comissao = EXCLUDED.comissao,
                    parcelas = EXCLUDED.parcelas,
                    val_ref = EXCLUDED.val_ref,
                    percentual_icms = EXCLUDED.percentual_icms,
                    detalhes = EXCLUDED.detalhes,
                    nf_referencia = EXCLUDED.nf_referencia,
                    finalidade = EXCLUDED.finalidade,
                    outras_despesas = EXCLUDED.outras_despesas,
                    seguro = EXCLUDED.seguro
            """

            insercoes = atualizacoes = erros = 0

            for row in access_cursor.fetchall():
                try:
                    nf_numero = clean_string(row[0])
                    cliente_id = int(row[2]) if row[2] else None
                    vendedor_id = int(row[14]) if row[14] else None
                    transportadora_id = int(row[16]) if row[16] and row[16] != '-' else None

                    if cliente_id and cliente_id not in clientes:
                        continue
                    if vendedor_id and vendedor_id not in funcionarios:
                        vendedor_id = None
                    if transportadora_id and transportadora_id not in transportadoras:
                        transportadora_id = None

                    dados = (
                        nf_numero,
                        row[1],
                        cliente_id,
                        clean_decimal(row[3]),
                        clean_decimal(row[4]),
                        clean_decimal(row[5]),
                        clean_decimal(row[6]),
                        clean_string(row[7]),
                        clean_decimal(row[8]),
                        clean_decimal(row[9]),
                        clean_decimal(row[10]),
                        clean_decimal(row[11]),
                        clean_string(row[12]),
                        clean_string(row[13]),
                        vendedor_id,
                        clean_string(row[15]),
                        transportadora_id,
                        clean_string(row[17]),
                        clean_decimal(row[18]),
                        clean_decimal(row[19]),
                        clean_string(row[20]),
                        clean_string(row[21]),
                        clean_string(row[22]),
                        clean_decimal(row[23]),
                        clean_string(row[24]),
                        clean_decimal(row[25]),
                        clean_string(row[26]),
                        clean_string(row[27]),
                        clean_decimal(row[28]),
                        clean_string(row[29]),
                        clean_string(row[30]),
                        clean_string(row[31]),
                        clean_decimal(row[32]),
                        clean_decimal(row[33])
                    )

                    pg_cursor.execute(insert_sql, dados)
                    pg_conn.commit()

                    if nf_numero in existing_nfs:
                        atualizacoes += 1
                    else:
                        insercoes += 1

                except Exception as e:
                    erros += 1
                    print(f"Erro ao processar NF {row[0]}: {str(e)}")
                    pg_conn.rollback()

            print(f"\nNotas fiscais inseridas: {insercoes}")
            print(f"Notas fiscais atualizadas: {atualizacoes}")
            print(f"Erros: {erros}")

            return True

    except Exception as e:
        print(f"Erro durante a migração: {str(e)}")
        return False