import os
import sys
import logging
from datetime import datetime
import pyodbc
import psycopg2
from psycopg2 import errorcodes
from decimal import Decimal, InvalidOperation
import re

# Importar configurações
from config import PG_CONFIG, CADASTROS_DB, ACCESS_PASSWORD

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('migration_produtos.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

class DatabaseConfig:
    """Configurações de conexão com os bancos de dados"""
    
    @staticmethod
    def get_postgres_conn():
        """Retorna conexão com PostgreSQL"""
        try:
            return psycopg2.connect(**PG_CONFIG)
        except Exception as e:
            logger.error(f"Erro ao conectar ao PostgreSQL: {str(e)}")
            raise

    @staticmethod
    def get_access_conn():
        """Retorna conexão com MS Access"""
        try:
            conn_str = (
                r'Driver={Microsoft Access Driver (*.mdb, *.accdb)};'
                f'DBQ={CADASTROS_DB};'
                f'PWD={ACCESS_PASSWORD};'
            )
            return pyodbc.connect(conn_str)
        except Exception as e:
            logger.error(f"Erro ao conectar ao Access: {str(e)}")
            raise

def clean_string(value):
    """Limpa e valida uma string"""
    if value is None:
        return None
    cleaned = str(value).strip()
    return cleaned if cleaned else None

def clean_decimal(value):
    """Limpa e valida valor decimal"""
    if value is None:
        return Decimal('0.00')
    try:
        if isinstance(value, str):
            cleaned = value.replace(',', '.')
        else:
            cleaned = str(value)
        return Decimal(cleaned).quantize(Decimal('0.01'))
    except:
        return Decimal('0.00')

def calculate_margin(custo, venda):
    """Calcula margem de lucro"""
    if not custo or not venda or custo == Decimal('0.00'):
        return Decimal('0.00')
    try:
        margem = ((venda - custo) / custo) * 100
        return margem.quantize(Decimal('0.01'))
    except:
        return Decimal('0.00')

def verify_table_exists(cursor, table_name):
    """Verifica se uma tabela existe no PostgreSQL"""
    try:
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = %s
            );
        """, (table_name,))
        return cursor.fetchone()[0]
    except Exception as e:
        logger.error(f"Erro ao verificar existência da tabela {table_name}: {str(e)}")
        raise

def create_table_if_not_exists(cursor):
    """Cria a tabela produtos se não existir"""
    try:
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS produtos (
            id INTEGER PRIMARY KEY,
            codigo VARCHAR(20),
            nome VARCHAR(100) NOT NULL,
            descricao TEXT,
            referencia VARCHAR(100),
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
            ativo BOOLEAN DEFAULT true,
            controla_lote BOOLEAN DEFAULT false,
            controla_validade BOOLEAN DEFAULT false
        );

        CREATE INDEX IF NOT EXISTS idx_produtos_codigo ON produtos (codigo);
        CREATE INDEX IF NOT EXISTS idx_produtos_nome ON produtos (nome);
        CREATE INDEX IF NOT EXISTS idx_produtos_grupo ON produtos (grupo_id);
        """)
        logger.info("Estrutura da tabela produtos verificada/criada com sucesso")
    except Exception as e:
        logger.error(f"Erro ao criar tabela produtos: {str(e)}")
        raise

def clean_tables(pg_conn):
    """Limpa as tabelas no PostgreSQL"""
    try:
        cursor = pg_conn.cursor()
        logger.info("Iniciando limpeza das tabelas...")
        
        cursor.execute("SET session_replication_role = 'replica';")
        
        tabelas_dependentes = [
            'itens_nf_entrada',
            'itens_nf_saida',
            'itens_contrato_locacao',
            'movimentacoes_estoque',
            'saldos_estoque',
            'produtos'
        ]
        
        for tabela in tabelas_dependentes:
            try:
                if verify_table_exists(cursor, tabela):
                    logger.info(f"Limpando tabela {tabela}...")
                    cursor.execute(f"TRUNCATE TABLE {tabela} CASCADE")
                    logger.info(f"Tabela {tabela} limpa com sucesso")
            except Exception as e:
                logger.error(f"Erro ao limpar tabela {tabela}: {str(e)}")
                raise
        
        cursor.execute("SET session_replication_role = 'origin';")
        pg_conn.commit()
        logger.info("Limpeza de tabelas concluída com sucesso")
        return True
        
    except Exception as e:
        logger.error(f"Erro durante processo de limpeza: {str(e)}")
        pg_conn.rollback()
        raise

def verificar_grupos(pg_cursor):
    """Verifica grupos existentes"""
    try:
        pg_cursor.execute("SELECT id FROM grupos")
        return {row[0] for row in pg_cursor.fetchall()}
    except Exception as e:
        logger.error(f"Erro ao verificar grupos: {str(e)}")
        raise

def migrate_produtos():
    """Função principal de migração dos produtos"""
    start_time = datetime.now()
    logger.info(f"Iniciando migração de produtos às {start_time}")
    
    access_conn = None
    pg_conn = None
    
    try:
        logger.info("Estabelecendo conexões com os bancos de dados...")
        access_conn = DatabaseConfig.get_access_conn()
        pg_conn = DatabaseConfig.get_postgres_conn()
        
        clean_tables(pg_conn)
        
        pg_cursor = pg_conn.cursor()
        create_table_if_not_exists(pg_cursor)
        
        # Verificar grupos existentes
        grupos_validos = verificar_grupos(pg_cursor)
        
        logger.info("Consultando dados do Access...")
        access_cursor = access_conn.cursor()
        access_cursor.execute("""
            SELECT Codigo, Descricao, Unidade, grupo, Fornecedor, 
                   Referencia, Custo, Revenda, Varejo, Estoque, 
                   Datacadastro, Ultimaalteracao, Status, 
                   Localizacao, EstoqueMinimo, NCM, CSTA, CSTB
            FROM Produtos 
            ORDER BY Codigo
        """)
        
        insert_sql = """
            INSERT INTO produtos (
                id, codigo, nome, unidade_medida, grupo_id,
                referencia, preco_custo, preco_venda, margem_lucro,
                estoque_atual, estoque_minimo, data_cadastro,
                ativo, controla_lote
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s
            )
        """
        
        contador = 0
        erros = 0
        grupos_nao_encontrados = set()
        
        logger.info("Iniciando migração dos registros...")
        
        for row in access_cursor.fetchall():
            try:
                produto_id = int(row[0])
                nome = clean_string(row[1])
                
                if not nome:
                    logger.warning(f"Produto {produto_id} ignorado: nome vazio")
                    continue
                
                # Validar grupo
                grupo_id = int(row[3]) if row[3] else None
                if grupo_id and grupo_id not in grupos_validos:
                    grupos_nao_encontrados.add(grupo_id)
                    grupo_id = None
                
                # Tratar preços
                preco_custo = clean_decimal(row[6])
                preco_venda = clean_decimal(row[8])  # Usando preço varejo
                margem_lucro = calculate_margin(preco_custo, preco_venda)
                
                # Status
                status = clean_string(row[12])
                ativo = False if status and status.upper() == 'INATIVO' else True
                
                dados = (
                    produto_id,                 # id
                    clean_string(row[0]),       # codigo
                    nome,                       # nome
                    clean_string(row[2]),       # unidade_medida
                    grupo_id,                   # grupo_id
                    clean_string(row[5]),       # referencia
                    preco_custo,               # preco_custo
                    preco_venda,               # preco_venda
                    margem_lucro,              # margem_lucro
                    int(row[9] or 0),          # estoque_atual
                    int(row[14] or 0),         # estoque_minimo
                    row[10] or datetime.now(),  # data_cadastro
                    ativo,                      # ativo
                    False                       # controla_lote (default)
                )
                
                pg_cursor.execute(insert_sql, dados)
                pg_conn.commit()
                contador += 1
                
                if contador % 100 == 0:
                    logger.info(f"Migrados {contador} produtos...")
                
            except Exception as e:
                erros += 1
                logger.error(f"Erro ao migrar produto {row[0]}: {str(e)}")
                pg_conn.rollback()
                continue
        
        # Atualizar sequence
        pg_cursor.execute("""
            SELECT setval(pg_get_serial_sequence('produtos', 'id'), 
                         COALESCE((SELECT MAX(id) FROM produtos), 1), 
                         true);
        """)
        pg_conn.commit()
        
        end_time = datetime.now()
        duration = end_time - start_time
        
        logger.info(f"""
        Migração concluída em {duration}:
        - Total de produtos migrados: {contador}
        - Total de erros: {erros}
        """)
        
        if grupos_nao_encontrados:
            logger.warning("Grupos não encontrados:")
            for grupo in sorted(grupos_nao_encontrados):
                logger.warning(f"- Grupo {grupo}")
        
        return True
        
    except Exception as e:
        logger.error(f"Erro durante a migração: {str(e)}")
        if pg_conn:
            pg_conn.rollback()
        return False
        
    finally:
        if access_conn:
            access_conn.close()
        if pg_conn:
            pg_conn.close()

if __name__ == "__main__":
    try:
        migrate_produtos()
    except KeyboardInterrupt:
        logger.info("Migração interrompida pelo usuário")
    except Exception as e:
        logger.error(f"Erro não tratado: {str(e)}")