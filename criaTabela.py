# create_tables.py
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

def create_tables():
    # Configurações de conexão
    config = {
        'dbname': 'nova_empresa',
        'user': 'cirilomax',
        'password': '226cmm100',  # Altere para sua senha
        'host': 'localhost',
        'port': '5432',
        'client_encoding': 'UTF8'
    }

    # Queries de criação das tabelas
    queries = [
        """
        CREATE TABLE IF NOT EXISTS enderecos (
            id SERIAL PRIMARY KEY,
            cep VARCHAR(10),
            logradouro VARCHAR(100),
            bairro VARCHAR(50),
            cidade VARCHAR(50),
            uf VARCHAR(2),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS fornecedores (
            id SERIAL PRIMARY KEY,
            codigo_antigo INTEGER,
            nome VARCHAR(100),
            cnpj VARCHAR(20),
            inscricao_estadual VARCHAR(20),
            endereco_id INTEGER REFERENCES enderecos(id),
            telefone VARCHAR(20),
            celular VARCHAR(20),
            email VARCHAR(100),
            contato VARCHAR(50),
            data_cadastro DATE,
            tipo VARCHAR(50),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS funcionarios (
            id SERIAL PRIMARY KEY,
            codigo_antigo INTEGER,
            nome VARCHAR(100),
            cpf VARCHAR(14),
            rg VARCHAR(20),
            endereco_id INTEGER REFERENCES enderecos(id),
            telefone VARCHAR(20),
            celular VARCHAR(20),
            funcao VARCHAR(50),
            setor VARCHAR(50),
            salario DECIMAL(10,2),
            comissao DECIMAL(5,2),
            data_admissao DATE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS grupos (
            id SERIAL PRIMARY KEY,
            codigo_antigo INTEGER,
            descricao VARCHAR(100),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS produtos (
            id SERIAL PRIMARY KEY,
            codigo_antigo INTEGER,
            descricao VARCHAR(100),
            unidade VARCHAR(10),
            grupo_id INTEGER REFERENCES grupos(id),
            fornecedor_id INTEGER REFERENCES fornecedores(id),
            referencia VARCHAR(50),
            custo DECIMAL(10,2),
            preco_revenda DECIMAL(10,2),
            preco_varejo DECIMAL(10,2),
            estoque DECIMAL(10,2),
            estoque_minimo DECIMAL(10,2),
            data_cadastro DATE,
            ultima_alteracao DATE,
            status VARCHAR(20),
            ncm VARCHAR(20),
            localizacao VARCHAR(50),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS movimentos_financeiros (
            id SERIAL PRIMARY KEY,
            data DATE,
            hora TIME,
            tipo VARCHAR(20),
            conta VARCHAR(50),
            credito DECIMAL(10,2),
            debito DECIMAL(10,2),
            historico VARCHAR(200),
            operador VARCHAR(50),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """,
        """
        -- Índices para melhorar performance
        CREATE INDEX IF NOT EXISTS idx_fornecedores_cnpj ON fornecedores(cnpj);
        CREATE INDEX IF NOT EXISTS idx_funcionarios_cpf ON funcionarios(cpf);
        CREATE INDEX IF NOT EXISTS idx_produtos_codigo_antigo ON produtos(codigo_antigo);
        CREATE INDEX IF NOT EXISTS idx_movimentos_data ON movimentos_financeiros(data);
        """
    ]

    try:
        # Conecta ao banco de dados
        print("Conectando ao banco de dados...")
        conn = psycopg2.connect(**config)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cur = conn.cursor()

        # Executa cada query de criação
        for query in queries:
            print("\nExecutando query:")
            print(query[:70] + "..." if len(query) > 70 else query)
            try:
                cur.execute(query)
                print("Query executada com sucesso!")
            except psycopg2.Error as e:
                print(f"Erro ao executar query: {e}")
                raise

        print("\nTodas as tabelas foram criadas com sucesso!")
        
        # Verifica as tabelas criadas
        cur.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
        """)
        
        print("\nTabelas criadas no banco:")
        for table in cur.fetchall():
            print(f"- {table[0]}")

    except Exception as e:
        print(f"Erro durante a criação das tabelas: {e}")
        raise
    finally:
        if 'cur' in locals():
            cur.close()
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    create_tables()