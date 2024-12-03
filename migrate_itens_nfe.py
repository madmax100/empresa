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
            'itens_nf_entrada'
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

def carregar_notas_fiscais(pg_cursor):
    """Carrega o mapeamento de notas fiscais (numero_nota -> id)"""
    pg_cursor.execute("""
        SELECT id, numero_nota 
        FROM notas_fiscais_entrada 
        WHERE numero_nota IS NOT NULL
    """)
    mapeamento = {}
    for row in pg_cursor.fetchall():
        if row[1]:  # apenas se número da nota não for nulo
            mapeamento[clean_string(row[1])] = row[0]
    print(f"Notas Fiscais encontradas: {len(mapeamento)}")
    return mapeamento

def carregar_produtos(pg_cursor):
    """Carrega o mapeamento de produtos"""
    pg_cursor.execute("SELECT id FROM produtos")
    ids = {row[0] for row in pg_cursor.fetchall()}
    print(f"Produtos encontrados: {len(ids)}")
    return ids

def migrar_itens_nfe():
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
        notas_fiscais = carregar_notas_fiscais(pg_cursor)
        produtos = carregar_produtos(pg_cursor)
        
        # Query para buscar dados do Access
        query = """
        SELECT NumNFE,
               Data,
               Produtos,
               Qtde,
               Valor,
               Total,
               PercIpi,
               Status,
               Aliquota,
               Desconto,
               CFOP,
               BaseSubstituicao,
               ICMSSubstituicao,
               OutrasDespesas,
               frete,
               AliquotaSubstituicao,
               ContNCM,
               Controle
        FROM [Itens da NFE] 
        ORDER BY NumNFE
        """
        
        print("\nBuscando dados do Access...")
        access_cursor = access_conn.cursor()
        access_cursor.execute(query)

        # SQL de inserção
        insert_sql = """
            INSERT INTO itens_nf_entrada (
                nota_fiscal_id,
                data,
                produto_id,
                quantidade,
                valor_unitario,
                valor_total,
                percentual_ipi,
                status,
                aliquota,
                desconto,
                cfop,
                base_substituicao,
                icms_substituicao,
                outras_despesas,
                frete,
                aliquota_substituicao,
                ncm,
                controle
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, %s, %s, %s
            )
        """

        # Processo de migração
        contador = 0
        erros = 0
        notas_nao_encontradas = set()
        produtos_nao_encontrados = set()
        
        print("\nIniciando migração dos itens de nota fiscal...")
        
        while True:
            rows = access_cursor.fetchmany(1000)
            if not rows:
                break
            
            for row in rows:
                try:
                    # Validar nota fiscal pelo número
                    num_nfe = clean_string(str(row[0]))
                    nota_fiscal_id = notas_fiscais.get(num_nfe)
                    
                    if not nota_fiscal_id:
                        notas_nao_encontradas.add(num_nfe)
                        continue

                    # Validar produto
                    produto_id = int(row[2]) if row[2] is not None else None
                    if produto_id not in produtos:
                        produtos_nao_encontrados.add(produto_id)
                        continue

                    dados = (
                        nota_fiscal_id,             # nota_fiscal_id
                        row[1],                     # data
                        produto_id,                 # produto_id
                        clean_decimal(row[3]),      # quantidade
                        clean_decimal(row[4]),      # valor_unitario
                        clean_decimal(row[5]),      # valor_total
                        clean_decimal(row[6]),      # percentual_ipi
                        clean_string(row[7]),       # status
                        clean_decimal(row[8]),      # aliquota
                        clean_decimal(row[9]),      # desconto
                        clean_string(row[10]),      # cfop
                        clean_decimal(row[11]),     # base_substituicao
                        clean_decimal(row[12]),     # icms_substituicao
                        clean_decimal(row[13]),     # outras_despesas
                        clean_decimal(row[14]),     # frete
                        clean_decimal(row[15]),     # aliquota_substituicao
                        clean_string(row[16]),      # ncm
                        clean_string(row[17])       # controle
                    )
                    
                    pg_cursor.execute(insert_sql, dados)
                    pg_conn.commit()
                    contador += 1
                    
                    if contador % 100 == 0:
                        print(f"Migrados {contador} itens...")
                
                except Exception as e:
                    erros += 1
                    print(f"Erro ao migrar item da nota fiscal {row[0]}: {str(e)}")
                    print(f"Dados: {row}")
                    pg_conn.rollback()
                    continue

        print("\nMigração concluída!")
        print(f"Total de itens migrados: {contador}")
        print(f"Total de erros: {erros}")
        
        if notas_nao_encontradas:
            print("\nNúmeros de notas fiscais não encontradas:")
            for nf in sorted(notas_nao_encontradas):
                print(f"- {nf}")
                
        if produtos_nao_encontrados:
            print("\nProdutos não encontrados:")
            for p in sorted(produtos_nao_encontrados):
                print(f"- {p}")
        
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
    print("=== MIGRAÇÃO DE ITENS DE NOTAS FISCAIS DE ENTRADA ===")
    print("Início:", datetime.now())
    migrar_itens_nfe()
    print("Fim:", datetime.now())