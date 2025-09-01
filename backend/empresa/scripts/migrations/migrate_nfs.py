import os
import sys
import logging
from datetime import datetime, date
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
        logging.FileHandler('migration_nfs.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

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

def clean_id(value):
    """Limpa e valida um ID"""
    if value is None or value == '-':
        return None
    try:
        id_value = int(str(value).strip())
        return id_value if id_value > 0 else None
    except (ValueError, TypeError):
        return None

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

def clean_tables(pg_conn):
    """Limpa as tabelas no PostgreSQL"""
    try:
        cursor = pg_conn.cursor()
        logger.info("Iniciando limpeza das tabelas...")
        
        cursor.execute("SET session_replication_role = 'replica';")
        
        tabelas = ['itens_nf_saida', 'notas_fiscais_saida']
        
        for tabela in tabelas:
            try:
                logger.info(f"Limpando tabela {tabela}...")
                cursor.execute(f"TRUNCATE TABLE {tabela} CASCADE")
                logger.info(f"Tabela {tabela} limpa com sucesso")
            except Exception as e:
                logger.error(f"Erro ao limpar tabela {tabela}: {str(e)}")
                raise
        
        cursor.execute("SET session_replication_role = 'origin';")
        pg_conn.commit()
        return True
        
    except Exception as e:
        logger.error(f"Erro durante processo de limpeza: {str(e)}")
        pg_conn.rollback()
        raise

def carregar_dependencias(pg_cursor):
    """Carrega dados das tabelas relacionadas"""
    try:
        # Carregar clientes
        pg_cursor.execute("SELECT id FROM clientes")
        clientes = {row[0] for row in pg_cursor.fetchall()}
        logger.info(f"Clientes encontrados: {len(clientes)}")
        
        # Carregar vendedores (funcionários)
        pg_cursor.execute("SELECT id FROM funcionarios")
        vendedores = {row[0] for row in pg_cursor.fetchall()}
        logger.info(f"Vendedores encontrados: {len(vendedores)}")
        
        # Carregar transportadoras
        pg_cursor.execute("SELECT id FROM transportadoras")
        transportadoras = {row[0] for row in pg_cursor.fetchall()}
        logger.info(f"Transportadoras encontradas: {len(transportadoras)}")
        
        return clientes, vendedores, transportadoras
        
    except Exception as e:
        logger.error(f"Erro ao carregar dependências: {str(e)}")
        raise

def migrar_nfs():
    """Função principal de migração das notas fiscais de saída"""
    try:
        logger.info("Conectando aos bancos de dados...")
        access_conn = get_access_connection()
        pg_conn = get_pg_connection()
        
        clean_tables(pg_conn)
        pg_cursor = pg_conn.cursor()
        
        # Carregar dependências
        clientes_validos, vendedores_validos, transportadoras_validas = carregar_dependencias(pg_cursor)
        
        # Query para buscar dados do Access com filtro de data
        query = """
        SELECT NumNFS, Data, Cliente, ValorProdutos,
               BaseCalculo, Desconto, ValorFrete, TipoFrete,
               Valoricms, Valoripi, Valoricmsfonte, Valortotalnota,
               FormaPagto, Condicoes, vendedor, Operador,
               Transportadora, Formulario, Peso, Volume,
               Obs, Operacao, CFOP, ImpostoFederalTotal,
               NSerie, Comissao, Parcelas, ValRef,
               PercentualICMS, Detalhes, NFReferencia,
               Finalidade, OutrasDespesas, Seguro
        FROM NFS 
        WHERE Data >= #2024/01/01#
        ORDER BY NumNFS
        """
        
        logger.info("Consultando dados do Access...")
        access_cursor = access_conn.cursor()
        access_cursor.execute(query)

        # SQL de inserção
        insert_sql = """
            INSERT INTO notas_fiscais_saida (
                numero_nota, data, cliente_id, valor_produtos,
                base_calculo, desconto, valor_frete, tipo_frete,
                valor_icms, valor_ipi, valor_icms_fonte,
                valor_total_nota, forma_pagamento, condicoes,
                vendedor_id, operador, transportadora_id,
                formulario, peso, volume, obs, operacao,
                cfop, imposto_federal_total, n_serie, comissao,
                parcelas, val_ref, percentual_icms, detalhes,
                nf_referencia, finalidade, outras_despesas, seguro
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s
            )
        """
        
        contador = 0
        erros = 0
        clientes_nao_encontrados = set()
        vendedores_nao_encontrados = set()
        transportadoras_nao_encontradas = set()
        
        logger.info("Iniciando migração dos registros...")
        
        for row in access_cursor.fetchall():
            try:
                # Validar cliente
                cliente_id = clean_id(row[2])
                if not cliente_id or cliente_id not in clientes_validos:
                    if cliente_id:
                        clientes_nao_encontrados.add(cliente_id)
                    continue
                
                # Validar vendedor
                vendedor_id = clean_id(row[14])
                if vendedor_id and vendedor_id not in vendedores_validos:
                    vendedores_nao_encontrados.add(vendedor_id)
                    vendedor_id = None
                
                # Validar transportadora
                transportadora_id = clean_id(row[16])
                if transportadora_id and transportadora_id not in transportadoras_validas:
                    transportadoras_nao_encontradas.add(transportadora_id)
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
                    vendedor_id,                # vendedor_id
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
                    clean_decimal(row[32]),     # outras_despesas
                    clean_decimal(row[33])      # seguro
                )
                
                pg_cursor.execute(insert_sql, dados)
                contador += 1
                
                if contador % 100 == 0:
                    pg_conn.commit()
                    logger.info(f"Migradas {contador} notas fiscais...")
            
            except Exception as e:
                erros += 1
                logger.error(f"Erro ao migrar nota fiscal {row[0]}: {str(e)}")
                continue
        
        # Commit final
        pg_conn.commit()
        
        # Log resultados
        logger.info(f"""
        Migração concluída:
        - Total de notas fiscais migradas: {contador}
        - Total de erros: {erros}
        """)
        
        if clientes_nao_encontrados:
            logger.warning("Clientes não encontrados:")
            for c in sorted(clientes_nao_encontrados):
                logger.warning(f"- Cliente {c}")
        
        if vendedores_nao_encontrados:
            logger.warning("Vendedores não encontrados:")
            for v in sorted(vendedores_nao_encontrados):
                logger.warning(f"- Vendedor {v}")
        
        if transportadoras_nao_encontradas:
            logger.warning("Transportadoras não encontradas:")
            for t in sorted(transportadoras_nao_encontradas):
                logger.warning(f"- Transportadora {t}")
        
        return True
        
    except Exception as e:
        logger.error(f"Erro durante a migração: {str(e)}")
        if 'pg_conn' in locals():
            pg_conn.rollback()
        return False
        
    finally:
        if 'access_conn' in locals():
            access_conn.close()
        if 'pg_conn' in locals():
            pg_conn.close()

if __name__ == "__main__":
    try:
        logger.info("=== MIGRAÇÃO DE NOTAS FISCAIS DE SAÍDA ===")
        logger.info(f"Início: {datetime.now()}")
        migrar_nfs()
        logger.info(f"Fim: {datetime.now()}")
    except KeyboardInterrupt:
        logger.info("Migração interrompida pelo usuário")
    except Exception as e:
        logger.error(f"Erro não tratado: {str(e)}")