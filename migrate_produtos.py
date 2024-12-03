
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
            'itens_nf_compra',
            'itens_nf_venda',
            'itens_contrato_locacao',
            'movimentacoes_estoque',
            'saldos_estoque',
            'produtos'
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

def criar_tabela_produtos(pg_cursor):
    """Cria a tabela produtos no PostgreSQL"""
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS produtos (
        id INTEGER PRIMARY KEY,  -- Usando Codigo como chave primária
        codigo VARCHAR(20),
        nome VARCHAR(100) NOT NULL,
        descricao TEXT,
        grupo_id INTEGER REFERENCES grupos(id),
        unidade_medida VARCHAR(10),
        preco_custo DECIMAL(10,2),
        preco_venda DECIMAL(10,2),
        margem_lucro DECIMAL(5,2),
        estoque_minimo INTEGER,
        estoque_atual INTEGER DEFAULT 0,
        disponivel_locacao BOOLEAN DEFAULT false,
        valor_locacao_diaria DECIMAL(10,2),
        data_cadastro TIMESTAMP,
        data_ultima_alteracao TIMESTAMP,
        ativo BOOLEAN DEFAULT true,
        controla_lote BOOLEAN DEFAULT false,
        controla_validade BOOLEAN DEFAULT false
    );

    CREATE INDEX IF NOT EXISTS idx_produtos_codigo ON produtos (codigo);
    CREATE INDEX IF NOT EXISTS idx_produtos_nome ON produtos (nome);
    CREATE INDEX IF NOT EXISTS idx_produtos_grupo ON produtos (grupo_id);
    """
    pg_cursor.execute(create_table_sql)

def migrar_produtos():
    pg_config = {
        'dbname': 'c3mcopiasdb2',
        'user': 'cirilomax',
        'password': '226cmm100',
        'host': 'localhost',
        'port': '5432'
    }

    db_path = r"C:\Users\Cirilo\Documents\empresa\Bancos\cadastros\Cadastros.mdb"
    
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
        
        # Criar/atualizar estrutura da tabela
        print("\nVerificando estrutura da tabela...")
        criar_tabela_produtos(pg_cursor)
        pg_conn.commit()

        # Busca dados do Access
        print("\nBuscando dados do Access...")
        access_cursor = access_conn.cursor()
        access_cursor.execute("""
            SELECT Codigo, Descricao, Unidade, grupo, Fornecedor, 
                   Referencia, Custo, Revenda, Varejo, Estoque, 
                   Datacadastro, Ultimaalteracao, Status, 
                   Localizacao, EstoqueMinimo, NCM, CSTA, CSTB
            FROM Produtos 
            ORDER BY Codigo
        """)

        # SQL de inserção
        insert_sql = """
            INSERT INTO produtos (
                id, codigo, nome, unidade_medida, grupo_id,
                referencia, preco_custo, preco_venda,
                estoque_atual, data_cadastro,
                ativo, estoque_minimo
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
            )
        """

        # Processo de migração
        contador = 0
        erros = 0
        
        print("\nIniciando migração dos produtos...")
        
        while True:
            rows = access_cursor.fetchmany(1000)
            if not rows:
                break
            
            for row in rows:
                try:
                    # Determinar status
                    ativo = True if row[12] is None or row[12].upper() != 'INATIVO' else False
                    
                    dados = (
                        int(row[0]),                # id (Codigo)
                        clean_string(row[0]),       # codigo
                        clean_string(row[1]),       # nome (Descricao)
                        clean_string(row[2]),       # unidade_medida
                        int(row[3]) if row[3] else None,  # grupo_id
                        clean_string(row[5]),       # referencia
                        clean_decimal(row[6]),      # preco_custo (Custo)
                        clean_decimal(row[8]),      # preco_venda (Varejo)
                        int(row[9]) if row[9] else 0,  # estoque_atual
                        row[10] if row[10] else datetime.now(),  # data_cadastro
                        ativo,                      # ativo
                        int(row[14]) if row[14] else 0,  # estoque_minimo
                    )
                    
                    pg_cursor.execute(insert_sql, dados)
                    pg_conn.commit()
                    contador += 1
                    
                    if contador % 100 == 0:
                        print(f"Migrados {contador} produtos...")
                
                except Exception as e:
                    erros += 1
                    print(f"Erro ao migrar produto {row[0]}: {str(e)}")
                    pg_conn.rollback()
                    continue

        print("\nMigração concluída!")
        print(f"Total de produtos migrados: {contador}")
        print(f"Total de erros: {erros}")
        
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
    print("=== MIGRAÇÃO DE PRODUTOS ===")
    print("Início:", datetime.now())
    migrar_produtos()
    print("Fim:", datetime.now())
