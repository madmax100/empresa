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
            'itens_nf_saida'
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
    pg_cursor.execute("SELECT id, numero_nota FROM notas_fiscais_saida")
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

def migrar_itens_nfs():
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
        SELECT CodItemNFS,
               NumNFS,
               Data,
               Produtos,
               Qtde,
               Valor,
               Total,
               PercIpi,
               Status,
               Aliquota,
               Reducao,
               Desconto,
               CSTA,
               CSTB,
               Controle,
               Frete,
               OutrasDespesas,
               Seguro
        FROM [Itens da NFS] 
        ORDER BY NumNFS
        """
        
        print("\nBuscando dados do Access...")
        access_cursor = access_conn.cursor()
        access_cursor.execute(query)

        # SQL de inserção
        insert_sql = """
            INSERT INTO itens_nf_saida (
                nota_fiscal_id,
                data,
                produto_id,
                quantidade,
                valor_unitario,
                valor_total,
                percentual_ipi,
                status,
                aliquota,
                reducao,
                desconto,
                cst_a,
                cst_b,
                controle,
                frete,
                outras_despesas,
                seguro
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, %s, %s
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
                    # Validar nota fiscal
                    num_nfs = clean_string(str(row[1]))
                    nota_fiscal_id = notas_fiscais.get(num_nfs)
                    
                    if not nota_fiscal_id:
                        notas_nao_encontradas.add(num_nfs)
                        continue

                    # Validar produto
                    produto_id = int(row[3]) if row[3] is not None else None
                    if produto_id not in produtos:
                        produtos_nao_encontrados.add(produto_id)
                        continue

                    dados = (
                        nota_fiscal_id,             # nota_fiscal_id
                        row[2],                     # data
                        produto_id,                 # produto_id
                        clean_decimal(row[4]),      # quantidade
                        clean_decimal(row[5]),      # valor_unitario
                        clean_decimal(row[6]),      # valor_total
                        clean_decimal(row[7]),      # percentual_ipi
                        clean_string(row[8]),       # status
                        clean_decimal(row[9]),      # aliquota
                        clean_decimal(row[10]),     # reducao
                        clean_decimal(row[11]),     # desconto
                        clean_string(row[12]),      # cst_a
                        clean_string(row[13]),      # cst_b
                        clean_string(row[14]),      # controle
                        clean_decimal(row[15]),     # frete
                        clean_decimal(row[16]),     # outras_despesas
                        clean_decimal(row[17])      # seguro
                    )
                    
                    pg_cursor.execute(insert_sql, dados)
                    pg_conn.commit()
                    contador += 1
                    
                    if contador % 1000 == 0:
                        print(f"Migrados {contador} itens...")
                
                except Exception as e:
                    erros += 1
                    print(f"Erro ao migrar item da nota fiscal {row[1]}: {str(e)}")
                    print(f"Dados: {row}")
                    pg_conn.rollback()
                    continue

        print("\nMigração concluída!")
        print(f"Total de itens migrados: {contador}")
        print(f"Total de erros: {erros}")
        
        if notas_nao_encontradas:
            print("\nNotas fiscais não encontradas:")
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
    print("=== MIGRAÇÃO DE ITENS DE NOTAS FISCAIS DE SAÍDA ===")
    print("Início:", datetime.now())
    migrar_itens_nfs()
    print("Fim:", datetime.now())