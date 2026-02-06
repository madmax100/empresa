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

def get_existing_nfs(pg_cursor):
    pg_cursor.execute("SELECT numero_nota FROM notas_fiscais_servico")
    return {row[0] for row in pg_cursor.fetchall()}

def get_valid_entities(pg_cursor):
    pg_cursor.execute("SELECT id FROM clientes")
    clientes = {row[0] for row in pg_cursor.fetchall()}
    
    pg_cursor.execute("SELECT id FROM funcionarios WHERE id > 0")
    funcionarios = {row[0] for row in pg_cursor.fetchall()}
    
    pg_cursor.execute("SELECT id FROM transportadoras")
    transportadoras = {row[0] for row in pg_cursor.fetchall()}
    
    return clientes, funcionarios, transportadoras

def migrar_nf_servico():
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
            existing_nfs = get_existing_nfs(pg_cursor)
            clientes, funcionarios, transportadoras = get_valid_entities(pg_cursor)

            access_cursor = access_conn.cursor()
            access_cursor.execute("""
                SELECT NumNFSERV, MesAno, Data, Cliente, ValorProdutos, ISS,
                       BaseCalculo, Desconto, Valortotalnota, FormaPagto,
                       Condicoes, vendedor, Operador, Transportadora,
                       Formulario, Obs, Operacao, CFOP, NSerie, Parcelas,
                       Comissao, Tipo
                FROM NFSERV 
                ORDER BY NumNFSERV
            """)

            insert_sql = """
                INSERT INTO notas_fiscais_servico (
                    numero_nota, mes_ano, data, cliente_id, valor_produtos,
                    iss, base_calculo, desconto, valor_total, forma_pagamento,
                    condicoes, vendedor_id, operador, transportadora_id,
                    formulario, obs, operacao, cfop, n_serie, parcelas,
                    comissao, tipo
                ) VALUES %s
                ON CONFLICT (id) DO UPDATE SET
                    mes_ano = EXCLUDED.mes_ano,
                    data = EXCLUDED.data,
                    cliente_id = EXCLUDED.cliente_id,
                    valor_produtos = EXCLUDED.valor_produtos,
                    iss = EXCLUDED.iss,
                    base_calculo = EXCLUDED.base_calculo,
                    desconto = EXCLUDED.desconto,
                    valor_total = EXCLUDED.valor_total,
                    forma_pagamento = EXCLUDED.forma_pagamento,
                    condicoes = EXCLUDED.condicoes,
                    vendedor_id = EXCLUDED.vendedor_id,
                    operador = EXCLUDED.operador,
                    transportadora_id = EXCLUDED.transportadora_id,
                    formulario = EXCLUDED.formulario,
                    obs = EXCLUDED.obs,
                    operacao = EXCLUDED.operacao,
                    cfop = EXCLUDED.cfop,
                    n_serie = EXCLUDED.n_serie,
                    parcelas = EXCLUDED.parcelas,
                    comissao = EXCLUDED.comissao,
                    tipo = EXCLUDED.tipo
            """

            insercoes = atualizacoes = erros = 0

            for row in access_cursor.fetchall():
                try:
                    nf_numero = clean_string(row[0])
                    cliente_id = int(row[3]) if row[3] is not None else None
                    vendedor_id = int(row[11]) if row[11] is not None else None
                    transportadora_id = int(row[13]) if row[13] and row[13] != '-' else None

                    if cliente_id and cliente_id not in clientes:
                        continue
                    if vendedor_id and vendedor_id not in funcionarios:
                        vendedor_id = None
                    if transportadora_id and transportadora_id not in transportadoras:
                        transportadora_id = None

                    dados = (
                        (
                            nf_numero,
                            clean_string(row[1]),
                            row[2],
                            cliente_id,
                            clean_decimal(row[4]),
                            clean_decimal(row[5]),
                            clean_decimal(row[6]),
                            clean_decimal(row[7]),
                            clean_decimal(row[8]),
                            clean_string(row[9]),
                            clean_string(row[10]),
                            vendedor_id,
                            clean_string(row[12]),
                            transportadora_id,
                            clean_string(row[14]),
                            clean_string(row[15]),
                            clean_string(row[16]),
                            clean_string(row[17]),
                            clean_string(row[18]),
                            clean_string(row[19]),
                            clean_decimal(row[20]),
                            clean_string(row[21])
                        ),
                    )

                    pg_cursor.execute(insert_sql, dados)
                    pg_conn.commit()

                    if nf_numero in existing_nfs:
                        atualizacoes += 1
                    else:
                        insercoes += 1

                except Exception as e:
                    erros += 1
                    print(f"Erro ao processar NFS {row[0]}: {str(e)}")
                    pg_conn.rollback()

            print(f"\nNotas fiscais de serviço inseridas: {insercoes}")
            print(f"Notas fiscais de serviço atualizadas: {atualizacoes}")
            print(f"Erros: {erros}")

            return True

    except Exception as e:
        print(f"Erro durante a migração: {str(e)}")
        return False