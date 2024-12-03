import pyodbc
import psycopg2
import re
from datetime import datetime
from decimal import Decimal

def clean_string(value):
    if value is None:
        return None
    return str(value).strip()

def clean_cpf_cnpj(doc):
    if doc is None:
        return None
    return re.sub(r'[^\d]', '', str(doc))

def clean_phone(phone):
    if phone is None:
        return None
    return re.sub(r'[^\d]', '', str(phone))

def clean_decimal(value):
    if value is None:
        return Decimal('0.00')
    try:
        clean_value = re.sub(r'[^\d.,]', '', str(value))
        clean_value = clean_value.replace(',', '.')
        return Decimal(clean_value)
    except:
        return Decimal('0.00')

def limpar_tabelas(pg_conn):
    try:
        cursor = pg_conn.cursor()
        
        print("\nIniciando limpeza das tabelas...")
        cursor.execute("SET session_replication_role = 'replica';")
        
        tabelas = [
            'pagamentos_funcionarios',
            'funcionarios'
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

def criar_tabela_funcionarios(pg_cursor):
    """Cria a tabela funcionarios no PostgreSQL"""
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS funcionarios (
        id INTEGER PRIMARY KEY,  -- Usando Codigo como chave primária
        nome VARCHAR(100) NOT NULL,
        cpf VARCHAR(11),
        rg VARCHAR(20),
        data_nascimento DATE,
        data_admissao DATE,
        data_demissao DATE,
        cargo VARCHAR(50),
        salario_base DECIMAL(10,2),
        endereco VARCHAR(100),
        numero VARCHAR(10),
        complemento VARCHAR(50),
        bairro VARCHAR(50),
        cidade VARCHAR(50),
        estado VARCHAR(2),
        cep VARCHAR(8),
        telefone VARCHAR(20),
        email VARCHAR(100),
        setor VARCHAR(50),
        comissao DECIMAL(5,2),
        data_cadastro TIMESTAMP,
        ativo BOOLEAN DEFAULT true
    );

    CREATE INDEX IF NOT EXISTS idx_funcionarios_nome ON funcionarios (nome);
    CREATE INDEX IF NOT EXISTS idx_funcionarios_cpf ON funcionarios (cpf);
    """
    pg_cursor.execute(create_table_sql)

def migrar_funcionarios():
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
        
        # Limpar tabelas antes da importação
        if not limpar_tabelas(pg_conn):
            raise Exception("Falha na limpeza das tabelas. Abortando importação.")

        pg_cursor = pg_conn.cursor()
        
        # Criar/atualizar estrutura da tabela
        print("\nVerificando estrutura da tabela...")
        criar_tabela_funcionarios(pg_cursor)
        pg_conn.commit()

        # Busca dados do Access
        print("\nBuscando dados do Access...")
        access_cursor = access_conn.cursor()
        access_cursor.execute("""
            SELECT Codigo, nome, endereco, bairro, cidade, cep, 
                   fone, celular, cpf, rg, funcao, salario, 
                   dataadmissao
            FROM Funcionarios 
            ORDER BY Codigo
        """)

        # SQL de inserção
        insert_sql = """
            INSERT INTO funcionarios (
                id, nome, endereco, bairro, cidade, cep,
                telefone, cpf, rg, cargo, salario_base,
                data_admissao, data_cadastro, ativo
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
            )
        """

        # Processo de migração
        contador = 0
        erros = 0
        
        print("\nIniciando migração dos funcionários...")
        
        while True:
            rows = access_cursor.fetchmany(1000)
            if not rows:
                break
            
            for row in rows:
                try:
                    dados = (
                        int(row[0]),                # id (Codigo)
                        clean_string(row[1]),       # nome
                        clean_string(row[2]),       # endereco
                        clean_string(row[3]),       # bairro
                        clean_string(row[4]),       # cidade
                        clean_string(row[5]),       # cep
                        clean_phone(row[6]),        # telefone (fone)
                        clean_cpf_cnpj(row[8]),     # cpf
                        clean_string(row[9]),       # rg
                        clean_string(row[10]),      # cargo (funcao)
                        clean_decimal(row[11]),     # salario_base
                        row[12],                    # data_admissao
                        datetime.now(),             # data_cadastro
                        True                        # ativo
                    )
                    
                    pg_cursor.execute(insert_sql, dados)
                    pg_conn.commit()
                    contador += 1
                    
                    if contador % 10 == 0:
                        print(f"Migrados {contador} funcionários...")
                
                except Exception as e:
                    erros += 1
                    print(f"Erro ao migrar funcionário {row[0]}: {str(e)}")
                    print(f"Dados que causaram erro: {row}")
                    pg_conn.rollback()
                    continue

        print("\nMigração concluída!")
        print(f"Total de funcionários migrados: {contador}")
        print(f"Total de erros: {erros}")
        
        # Atualizar sequence
        pg_cursor.execute("""
            SELECT setval(pg_get_serial_sequence('funcionarios', 'id'), 
                         (SELECT MAX(id) FROM funcionarios));
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
    print("=== MIGRAÇÃO DE FUNCIONÁRIOS ===")
    print("Início:", datetime.now())
    migrar_funcionarios()
    print("Fim:", datetime.now())
