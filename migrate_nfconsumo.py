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
            'notas_fiscais_consumo'
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

def carregar_fornecedores(pg_cursor):
    """Carrega o mapeamento de fornecedores"""
    pg_cursor.execute("SELECT id FROM fornecedores")
    ids = {row[0] for row in pg_cursor.fetchall()}
    print(f"Fornecedores encontrados: {ids}")
    return ids

def migrar_nf_consumo():
    pg_config = {
        'dbname': 'c3mcopiasdb2',
        'user': 'cirilomax',
        'password': '226cmm100',
        'host': 'localhost',
        'port': '5432'
    }

    db_path = r"C:\Users\Cirilo\Documents\c3mcopias\Bancos\Movimentos\Outrosmovimentos.mdb"
    
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
        fornecedores = carregar_fornecedores(pg_cursor)
        print(f"Fornecedores carregados: {len(fornecedores)}")
        
        # Query simplificada sem comentários
        query = """
        SELECT CodNFConsumo, 
               NumNFConsumo, 
               Data, 
               Fornecedor, 
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
               CFOP, 
               Formulario, 
               DataConhec, 
               DataSelo, 
               DataEntrada, 
               Tipo, 
               Chave, 
               Serie 
        FROM NFConsumo 
        ORDER BY CodNFConsumo
        """
        
        print("\nBuscando dados do Access...")
        access_cursor = access_conn.cursor()
        access_cursor.execute(query)

        # SQL de inserção
        insert_sql = """
            INSERT INTO notas_fiscais_consumo (
                id, 
                numero_nota, 
                data_emissao, 
                fornecedor_id,
                valor_produtos, 
                base_calculo_icms, 
                valor_desconto, 
                valor_frete,
                modalidade_frete, 
                valor_icms, 
                valor_ipi, 
                valor_icms_st,
                valor_total, 
                forma_pagamento, 
                condicoes_pagamento, 
                cfop,
                formulario, 
                data_conhecimento, 
                data_selo, 
                data_entrada, 
                tipo_nota, 
                chave_nfe, 
                serie_nota
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                %s, %s, %s
            )
        """

        # Processo de migração
        contador = 0
        erros = 0
        
        print("\nIniciando migração das notas fiscais...")
        
        while True:
            rows = access_cursor.fetchmany(1000)
            if not rows:
                break
            
            for row in rows:
                try:
                    fornecedor_id = int(row[3])  # Fornecedor
                    if fornecedor_id not in fornecedores:
                        print(f"Fornecedor não encontrado: {fornecedor_id}")
                        continue

                    dados = (
                        int(row[0]),                # id (CodNFConsumo)
                        clean_string(row[1]),       # numero_nota
                        row[2],                     # data_emissao
                        fornecedor_id,              # fornecedor_id
                        clean_decimal(row[4]),      # valor_produtos
                        clean_decimal(row[5]),      # base_calculo_icms
                        clean_decimal(row[6]),      # valor_desconto
                        clean_decimal(row[7]),      # valor_frete
                        clean_string(row[8]),       # modalidade_frete
                        clean_decimal(row[9]),      # valor_icms
                        clean_decimal(row[10]),     # valor_ipi
                        clean_decimal(row[11]),     # valor_icms_st
                        clean_decimal(row[12]),     # valor_total
                        clean_string(row[13]),      # forma_pagamento
                        clean_string(row[14]),      # condicoes_pagamento
                        clean_string(row[15]),      # cfop
                        clean_string(row[16]),      # formulario
                        row[17],                    # data_conhecimento (DataConhec)
                        row[18],                    # data_selo
                        row[19],                    # data_entrada
                        clean_string(row[20]),      # tipo_nota
                        clean_string(row[21]),      # chave_nfe
                        clean_string(row[22])       # serie_nota
                    )
                    
                    pg_cursor.execute(insert_sql, dados)
                    pg_conn.commit()
                    contador += 1
                    
                    if contador % 50 == 0:
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
        
        # Atualizar sequence
        pg_cursor.execute("""
            SELECT setval('notas_fiscais_consumo_id_seq', 
                         COALESCE((SELECT MAX(id) FROM notas_fiscais_consumo), 1), 
                         true);
        """)
        pg_conn.commit()
        
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
    print("=== MIGRAÇÃO DE NOTAS FISCAIS DE CONSUMO ===")
    print("Início:", datetime.now())
    migrar_nf_consumo()
    print("Fim:", datetime.now())