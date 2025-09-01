import os
import sys
import logging
from datetime import datetime
import pyodbc
import psycopg2
from decimal import Decimal
import re

# Importar configurações
from config import PG_CONFIG, MOVIMENTOS_DB, ACCESS_PASSWORD

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('migration_nfe.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

def clean_string(value):
    """Limpa e valida uma string"""
    if value is None:
        return None
    return str(value).strip()

def clean_decimal(value):
    """Limpa e valida valor decimal"""
    if value is None:
        return Decimal('0.00')
    try:
        clean_value = re.sub(r'[^\d.,\-]', '', str(value))
        clean_value = clean_value.replace(',', '.')
        return Decimal(clean_value).quantize(Decimal('0.01'))
    except:
        return Decimal('0.00')

def get_pg_connection():
    """Retorna conexão com PostgreSQL usando configurações"""
    try:
        return psycopg2.connect(**PG_CONFIG)
    except Exception as e:
        logger.error(f"Erro ao conectar ao PostgreSQL: {str(e)}")
        raise

def get_access_connection():
    """Retorna conexão com MS Access usando configurações"""
    try:
        conn_str = (
            r'Driver={Microsoft Access Driver (*.mdb, *.accdb)};'
            f'DBQ={MOVIMENTOS_DB};'
            f'PWD={ACCESS_PASSWORD};'
        )
        return pyodbc.connect(conn_str)
    except Exception as e:
        logger.error(f"Erro ao conectar ao Access: {str(e)}")
        raise

def limpar_tabelas(pg_conn):
    """Limpa as tabelas no PostgreSQL"""
    try:
        cursor = pg_conn.cursor()
        
        logger.info("Iniciando limpeza das tabelas...")
        cursor.execute("SET session_replication_role = 'replica';")
        
        tabelas = [
            'notas_fiscais_entrada'
        ]
        
        for tabela in tabelas:
            try:
                logger.info(f"Verificando tabela {tabela}...")
                cursor.execute(f"SELECT COUNT(*) FROM {tabela}")
                qtd_antes = cursor.fetchone()[0]
                logger.info(f"Registros encontrados em {tabela}: {qtd_antes}")
                
                if qtd_antes > 0:
                    logger.info(f"Limpando tabela {tabela}...")
                    cursor.execute(f"TRUNCATE TABLE {tabela} CASCADE")
                    pg_conn.commit()
                    logger.info(f"Tabela {tabela} limpa com sucesso!")
                
            except Exception as e:
                logger.error(f"Erro ao limpar tabela {tabela}: {str(e)}")
                pg_conn.rollback()
                raise
        
        cursor.execute("SET session_replication_role = 'origin';")
        pg_conn.commit()
        
        logger.info("Limpeza concluída com sucesso!")
        return True
        
    except Exception as e:
        logger.error(f"Erro durante a limpeza: {str(e)}")
        pg_conn.rollback()
        return False

def carregar_fornecedores(pg_cursor):
    """Carrega o mapeamento de fornecedores"""
    pg_cursor.execute("SELECT id FROM fornecedores")
    ids = {row[0] for row in pg_cursor.fetchall()}
    logger.info(f"Fornecedores encontrados: {len(ids)}")
    return ids

def migrar_nfe():
    """Função principal de migração das notas fiscais de entrada"""
    try:
        # Conexões
        logger.info("Conectando aos bancos de dados...")
        access_conn = get_access_connection()
        pg_conn = get_pg_connection()
        
        if not limpar_tabelas(pg_conn):
            raise Exception("Falha na limpeza das tabelas. Abortando importação.")

        pg_cursor = pg_conn.cursor()
        
        # Carregar mapeamentos
        fornecedores = carregar_fornecedores(pg_cursor)
        
        # Query para buscar dados do Access
        query = """
        SELECT CodNFE, NumNFE, Data, Fornecedor, ValorProdutos,
               BaseCalculo, Desconto, ValorFrete, TipoFrete,
               Valoricms, Valoripi, Valoricmsfonte, Valortotalnota,
               FormaPagto, Condicoes, Comprador, Operador,
               Formulario, Observação, OutrosEncargos, Parcelas,
               Operacao, CFOP, DataEntrada, Chave, Serie,
               Protocolo, Natureza, BaseSubstituicao,
               ICMSSubstituicao, OutrasDespesas
        FROM NFE 
        WHERE Data >= #2024/01/01# OR DataEntrada >= #2024/01/01#
        ORDER BY CodNFE
        """
        
        logger.info("Buscando dados do Access...")
        access_cursor = access_conn.cursor()
        access_cursor.execute(query)

        # SQL de inserção
        insert_sql = """
            INSERT INTO notas_fiscais_entrada (
                id, numero_nota, data_emissao, fornecedor_id,
                valor_produtos, base_calculo_icms, valor_desconto,
                valor_frete, tipo_frete, valor_icms, valor_ipi,
                valor_icms_st, valor_total, forma_pagamento,
                condicoes_pagamento, comprador, operador,
                observacao, outros_encargos, parcelas, operacao,
                cfop, data_entrada, chave_nfe, serie_nota,
                protocolo, natureza_operacao, base_calculo_st,
                outras_despesas
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, %s, %s, %s, %s
            )
        """

        # Processo de migração
        contador = 0
        erros = 0
        fornecedores_nao_encontrados = set()
        
        logger.info("Iniciando migração das notas fiscais...")
        
        while True:
            rows = access_cursor.fetchmany(1000)
            if not rows:
                break
            
            for row in rows:
                try:
                    # Validar fornecedor
                    fornecedor_id = int(row[3]) if row[3] is not None else None
                    if fornecedor_id not in fornecedores:
                        fornecedores_nao_encontrados.add(fornecedor_id)
                        continue

                    # Calcula valor total
                    valor_total = (
                        clean_decimal(row[4])    # valor_produtos
                        + clean_decimal(row[7])  # valor_frete
                        + clean_decimal(row[10]) # valor_ipi
                        + clean_decimal(row[11]) # valor_icms_st
                        + clean_decimal(row[30]) # outras_despesas
                        + clean_decimal(row[19]) # outros_encargos
                        - clean_decimal(row[6])  # valor_desconto
                    )

                    dados = (
                        int(row[0]),                # id (CodNFE)
                        clean_string(row[1]),       # numero_nota
                        row[2],                     # data_emissao
                        fornecedor_id,              # fornecedor_id
                        clean_decimal(row[4]),      # valor_produtos
                        clean_decimal(row[5]),      # base_calculo_icms
                        clean_decimal(row[6]),      # valor_desconto
                        clean_decimal(row[7]),      # valor_frete
                        clean_string(row[8]),       # tipo_frete
                        clean_decimal(row[9]),      # valor_icms
                        clean_decimal(row[10]),     # valor_ipi
                        clean_decimal(row[11]),     # valor_icms_st
                        valor_total,                # valor_total
                        clean_string(row[13]),      # forma_pagamento
                        clean_string(row[14]),      # condicoes_pagamento
                        clean_string(row[15]),      # comprador
                        clean_string(row[16]),      # operador
                        clean_string(row[18]),      # observacao
                        clean_decimal(row[19]),     # outros_encargos
                        clean_string(row[20]),      # parcelas
                        clean_string(row[21]),      # operacao
                        clean_string(row[22]),      # cfop
                        row[23],                    # data_entrada
                        clean_string(row[24]),      # chave_nfe
                        clean_string(row[25]),      # serie_nota
                        clean_string(row[26]),      # protocolo
                        clean_string(row[27]),      # natureza_operacao
                        clean_decimal(row[28]),     # base_calculo_st
                        clean_decimal(row[29])      # outras_despesas
                    )
                    
                    pg_cursor.execute(insert_sql, dados)
                    contador += 1
                    
                    # Commit a cada 100 registros
                    if contador % 100 == 0:
                        pg_conn.commit()
                        logger.info(f"Migradas {contador} notas fiscais...")
                
                except Exception as e:
                    erros += 1
                    logger.error(f"Erro ao migrar nota fiscal {row[0]}: {str(e)}")
                    pg_conn.rollback()
                    continue

        # Commit final
        pg_conn.commit()

        logger.info("Migração concluída!")
        logger.info(f"Total de notas fiscais migradas: {contador}")
        logger.info(f"Total de erros: {erros}")
        
        if fornecedores_nao_encontrados:
            logger.warning("Fornecedores não encontrados:")
            for f in sorted(fornecedores_nao_encontrados):
                logger.warning(f"- {f}")
        
        # Atualizar sequence
        pg_cursor.execute("""
            SELECT setval('notas_fiscais_entrada_id_seq', 
                         COALESCE((SELECT MAX(id) FROM notas_fiscais_entrada), 1), 
                         true);
        """)
        pg_conn.commit()
        
    except Exception as e:
        logger.error(f"Erro durante a migração: {str(e)}")
        if 'pg_conn' in locals():
            pg_conn.rollback()
    finally:
        if 'access_conn' in locals():
            access_conn.close()
        if 'pg_conn' in locals():
            pg_conn.close()

if __name__ == "__main__":
    logger.info("=== MIGRAÇÃO DE NOTAS FISCAIS DE ENTRADA ===")
    logger.info(f"Início: {datetime.now()}")
    migrar_nfe()
    logger.info(f"Fim: {datetime.now()}")