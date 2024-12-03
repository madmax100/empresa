import pyodbc
import psycopg2
from datetime import datetime
from decimal import Decimal
import re

def clean_string(value):
    if value is None:
        return None
    return str(value).strip()

def clean_decimal(value):
    if value is None:
        return Decimal('0.00')
    try:
        clean_value = re.sub(r'[^\d.,\-]', '', str(value))
        clean_value = clean_value.replace(',', '.')
        return Decimal(clean_value).quantize(Decimal('0.01'))
    except:
        return Decimal('0.00')

def limpar_tabelas(pg_conn):
    try:
        cursor = pg_conn.cursor()
        
        print("\nIniciando limpeza das tabelas...")
        cursor.execute("SET session_replication_role = 'replica';")
        
        tabelas = [
            'notas_fiscais_saida'
        ]
        
        for tabela in tabelas:
            try:
                print(f"\nVerificando tabela {tabela}...")
                cursor.execute(f"SELECT COUNT(*) FROM {tabela}")
                qtd_antes = cursor.fetchone()[0]
                print(f"Registros encontrados em {tabela}: {qtd_antes}")
                
                if qtd_antes > 0:
                    print(f"Limpando tabela {tabela}...")
                    cursor.execute(f"TRUNCATE TABLE {tabela} CASCADE")
                    pg_conn.commit()
                    print(f"Tabela {tabela} limpa com sucesso!")
                
            except Exception as e:
                print(f"Erro ao limpar tabela {tabela}: {str(e)}")
                pg_conn.rollback()
                raise
        
        cursor.execute("SET session_replication_role = 'origin';")
        pg_conn.commit()
        
        print("\nLimpeza concluída com sucesso!")
        return True
        
    except Exception as e:
        print(f"Erro durante a limpeza: {str(e)}")
        pg_conn.rollback()
        return False

def carregar_clientes(pg_cursor):
    """Carrega o mapeamento de clientes"""
    pg_cursor.execute("SELECT id FROM clientes")
    ids = {row[0] for row in pg_cursor.fetchall()}
    print(f"Clientes encontrados: {len(ids)}")
    return ids

def carregar_funcionarios(pg_cursor):
    """Carrega o mapeamento de funcionários"""
    pg_cursor.execute("SELECT id FROM funcionarios")
    ids = {row[0] for row in pg_cursor.fetchall()}
    print(f"Funcionários encontrados: {len(ids)}")
    return ids

def carregar_transportadoras(pg_cursor):
    """Carrega o mapeamento de transportadoras"""
    pg_cursor.execute("SELECT id FROM transportadoras")
    ids = {row[0] for row in pg_cursor.fetchall()}
    print(f"Transportadoras encontradas: {len(ids)}")
    return ids

def migrar_nfs():
    pg_config = {
        'dbname': 'c3mcopiasdb2',
        'user': 'cirilomax',
        'password': '226cmm100',
        'host': 'localhost',
        'port': '5432'
    }

    db_path = r"C:\Users\Cirilo\Documents\c3mcopias\Bancos\Movimentos\Movimentos.mdb"
    
    try:
        # Conexões
        print("Conectando aos bancos de dados...")
        conn_str = (
            r'Driver={Microsoft Access Driver (*.mdb, *.accdb)};'
            f'DBQ={db_path};'
            'PWD=010182;'
        )
        access_conn = pyodbc.connect(conn_str)
        pg_conn = psycopg2.connect(**pg_config)
        
        if not limpar_tabelas(pg_conn):
            raise Exception("Falha na limpeza das tabelas. Abortando importação.")

        pg_cursor = pg_conn.cursor()
        
        # Carregar mapeamentos
        clientes = carregar_clientes(pg_cursor)
        funcionarios = carregar_funcionarios(pg_cursor)
        transportadoras = carregar_transportadoras(pg_cursor)
        
        # Query para buscar dados do Access
        query = """
        SELECT NumNFS,
               Data,
               Cliente,
               ValorProdutos,
               BaseCalculo,
               Desconto,
               ValorFrete,
               TipoFrete,
               Valoricms,
               Valoripi,
               Valoricmsfonte,
               Valortotalnota,
               FormaPagto,
               Condicoes,
               vendedor,
               Operador,
               Transportadora,
               Formulario,
               Peso,
               Volume,
               Obs,
               Operacao,
               CFOP,
               ImpostoFederalTotal,
               NSerie,
               Comissao,
               Parcelas,
               ValRef,
               PercentualICMS,
               Detalhes,
               NFReferencia,
               Finalidade,
               OutrasDespesas,
               Seguro
        FROM NFS
        ORDER BY NumNFS
        """
        
        print("\nBuscando dados do Access...")
        access_cursor = access_conn.cursor()
        access_cursor.execute(query)

        # SQL de inserção
        insert_sql = """
            INSERT INTO notas_fiscais_saida (
                numero_nota,
                data,
                cliente_id,
                valor_produtos,
                base_calculo,
                desconto,
                valor_frete,
                tipo_frete,
                valor_icms,
                valor_ipi,
                valor_icms_fonte,
                valor_total_nota,
                forma_pagamento,
                condicoes,
                vendedor_id,
                operador,
                transportadora_id,
                formulario,
                peso,
                volume,
                obs,
                operacao,
                cfop,
                imposto_federal_total,
                n_serie,
                comissao,
                parcelas,
                val_ref,
                percentual_icms,
                detalhes,
                nf_referencia,
                finalidade,
                outras_despesas,
                seguro
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s
            )
        """

        # Processo de migração
        contador = 0
        erros = 0
        clientes_nao_encontrados = set()
        funcionarios_nao_encontrados = set()
        transportadoras_nao_encontradas = set()
        
        print("\nIniciando migração das notas fiscais de saída...")
        
        while True:
            rows = access_cursor.fetchmany(1000)
            if not rows:
                break
            
            for row in rows:
                try:
                    # Validar cliente
                    cliente_id = int(row[2]) if row[2] is not None else None
                    if cliente_id and cliente_id not in clientes:
                        clientes_nao_encontrados.add(cliente_id)
                        continue
        
                    # Validar vendedor
                    vendedor_id = None
                    if row[14] is not None:
                        try:
                            temp_vendedor_id = int(row[14])
                            if temp_vendedor_id > 0 and temp_vendedor_id in funcionarios:
                                vendedor_id = temp_vendedor_id
                            else:
                                funcionarios_nao_encontrados.add(temp_vendedor_id)
                        except (ValueError, TypeError):
                            pass
        
                    # Validar transportadora
                    transportadora_id = None
                    if row[16] and row[16] != '-':
                        try:
                            transportadora_id = int(row[16])
                            if transportadora_id not in transportadoras:
                                transportadoras_nao_encontradas.add(transportadora_id)
                                transportadora_id = None
                        except (ValueError, TypeError):
                            transportadora_id = None
        
                    dados = (
                        clean_string(row[0]),       # numero_nota
                        row[1],                     # data
                        cliente_id,                 # cliente_id
                        clean_decimal(row[3]),      # valor_produtos
                        clean_decimal(row[4]),      # base_calculo
                        clean_decimal(row[5]),      # desconto
                        clean_decimal(row[6]),      # valor_frete
                        clean_string(row[7]),       # tipo_frete
                        clean_decimal(row[8]),      # valor_icms
                        clean_decimal(row[9]),      # valor_ipi
                        clean_decimal(row[10]),     # valor_icms_fonte
                        clean_decimal(row[11]),     # valor_total_nota
                        clean_string(row[12]),      # forma_pagamento
                        clean_string(row[13]),      # condicoes
                        vendedor_id,                # vendedor_id (agora pode ser None)
                        clean_string(row[15]),      # operador
                        transportadora_id,          # transportadora_id
                        clean_string(row[17]),      # formulario
                        clean_decimal(row[18]),     # peso
                        clean_decimal(row[19]),     # volume
                        clean_string(row[20]),      # obs
                        clean_string(row[21]),      # operacao
                        clean_string(row[22]),      # cfop
                        clean_decimal(row[23]),     # imposto_federal_total
                        clean_string(row[24]),      # n_serie
                        clean_decimal(row[25]),     # comissao
                        clean_string(row[26]),      # parcelas
                        clean_string(row[27]),      # val_ref
                        clean_decimal(row[28]),     # percentual_icms
                        clean_string(row[29]),      # detalhes
                        clean_string(row[30]),      # nf_referencia
                        clean_string(row[31]),      # finalidade
                        clean_decimal(row[32]) if row[32] is not None else Decimal('0.00'),     # outras_despesas
                        clean_decimal(row[33]) if row[33] is not None else Decimal('0.00')      # seguro
                    )
                    
                    pg_cursor.execute(insert_sql, dados)
                    pg_conn.commit()
                    contador += 1
                    
                    if contador % 100 == 0:
                        print(f"Migradas {contador} notas fiscais...")
                
                except Exception as e:
                    erros += 1
                    print(f"Erro ao migrar nota fiscal {row[0]}: {str(e)}")
                    print(f"Dados: {row}")
                    pg_conn.rollback()
                    continue

        print("\nMigração concluída!")
        print(f"Total de notas fiscais migradas: {contador}")
        print(f"Total de erros: {erros}")
        
        if clientes_nao_encontrados:
            print("\nClientes não encontrados:")
            for c in sorted(clientes_nao_encontrados):
                print(f"- {c}")
                
        if funcionarios_nao_encontrados:
            print("\nVendedores não encontrados:")
            for f in sorted(funcionarios_nao_encontrados):
                print(f"- {f}")
                
        if transportadoras_nao_encontradas:
            print("\nTransportadoras não encontradas:")
            for t in sorted(transportadoras_nao_encontradas):
                print(f"- {t}")
        
    except Exception as e:
        print(f"Erro durante a migração: {str(e)}")
        if 'pg_conn' in locals():
            pg_conn.rollback()
    finally:
        if 'access_conn' in locals():
            access_conn.close()
        if 'pg_conn' in locals():
            pg_conn.close()

if __name__ == "__main__":
    print("=== MIGRAÇÃO DE NOTAS FISCAIS DE SAÍDA ===")
    print("Início:", datetime.now())
    migrar_nfs()
    print("Fim:", datetime.now())