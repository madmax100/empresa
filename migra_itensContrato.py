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
        
        tabelas = ['itens_contrato_locacao']
        
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

def carregar_dados_relacionados(pg_cursor):
    """Carrega os mapeamentos necessários das tabelas relacionadas"""
    
    # Carregar contratos
    pg_cursor.execute("SELECT id, contrato FROM contratos_locacao")
    contratos = {row[1]: row[0] for row in pg_cursor.fetchall()}
    
    # Carregar categorias
    pg_cursor.execute("SELECT id, id FROM categorias_produtos")
    categorias = {str(row[0]): row[1] for row in pg_cursor.fetchall()}
    
    return contratos, categorias

def migrar_itens_contrato():
    pg_config = {
        'dbname': 'c3mcopiasdb2',
        'user': 'cirilomax',
        'password': '226cmm100',
        'host': 'localhost',
        'port': '5432'
    }

    db_path = r"C:\Users\Cirilo\Documents\c3mcopias\Bancos\cadastros\Cadastros.mdb"
    
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
        
        # Limpar tabelas
        if not limpar_tabelas(pg_conn):
            raise Exception("Falha na limpeza das tabelas. Abortando importação.")

        pg_cursor = pg_conn.cursor()
        
        # Carregar dados relacionados
        print("\nCarregando dados relacionados...")
        contratos, categorias = carregar_dados_relacionados(pg_cursor)
        
        # Busca dados do Access
        print("\nBuscando dados do Access...")
        access_cursor = access_conn.cursor()
        access_cursor.execute("""
            SELECT Codigo, Contrato, Serie, Categoria, 
                   Modelo, Inicio, Fim
            FROM [Itens dos Contratos]
            ORDER BY Codigo
        """)

        # SQL de inserção
        insert_sql = """
            INSERT INTO itens_contrato_locacao (
                id, contrato_id, numeroserie, categoria_id, modelo,
                inicio, fim
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s
            )
        """

        # Processo de migração
        contador = 0
        erros = 0
        
        print("\nIniciando migração dos itens de contrato...")
        
        while True:
            rows = access_cursor.fetchmany(1000)
            if not rows:
                break
            
            for row in rows:
                try:
                    # Obter IDs relacionados
                    contrato_numero = row[1]  # Contrato
                    contrato_id = contratos.get(contrato_numero)
                    categoria_codigo = str(row[3]) if row[3] is not None else None  # Categoria
                    categoria_id = categorias.get(categoria_codigo)
                    
                    if not contrato_id:
                        print(f"Contrato não encontrado: {contrato_numero}")
                        continue
                        
                    if not categoria_id and categoria_codigo:
                        print(f"Categoria não encontrada: {categoria_codigo}")
                        continue
                    
                    dados = (
                        int(row[0]),                # id (Codigo)
                        contrato_id,                # contrato_id
                        clean_string(row[2]),       # numeroserie (Serie)
                        categoria_id,               # categoria_id
                        clean_string(row[4]),       #modelo
                        row[5],                    # data_inicio (Inicio)
                        row[6],                    # data_fim (Fim)
                    )
                    
                    pg_cursor.execute(insert_sql, dados)
                    pg_conn.commit()
                    contador += 1
                    
                    if contador % 50 == 0:
                        print(f"Migrados {contador} itens...")
                
                except Exception as e:
                    erros += 1
                    print(f"Erro ao migrar item {row[0]}: {str(e)}")
                    print(f"Dados: {row}")
                    pg_conn.rollback()
                    continue

        print("\nMigração concluída!")
        print(f"Total de itens migrados: {contador}")
        print(f"Total de erros: {erros}")
        
        # Atualizar sequence
        pg_cursor.execute("""
            SELECT setval('itens_contrato_locacao_id_seq', 
                         (SELECT MAX(id) FROM itens_contrato_locacao));
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
    print("=== MIGRAÇÃO DE ITENS DE CONTRATO ===")
    print("Início:", datetime.now())
    migrar_itens_contrato()
    print("Fim:", datetime.now())
