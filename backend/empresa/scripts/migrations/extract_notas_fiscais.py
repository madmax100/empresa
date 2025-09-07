#!/usr/bin/env python
"""
Script para extrair dados da tabela NotasFiscais do arquivo Extratos.mdb
"""

import pyodbc
import pandas as pd
from datetime import datetime
import logging

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('extract_notas_fiscais.log'),
        logging.StreamHandler()
    ]
)

def extract_notas_fiscais():
    """
    Extrai dados da tabela NotasFiscais do arquivo Extratos.mdb
    """
    # Caminho do arquivo Access
    mdb_file = r"C:\Users\Cirilo\Documents\Bancos\Extratos\Extratos.mdb"
    
    try:
        # String de conexão para Access
        conn_str = (
            r'DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};'
            f'DBQ={mdb_file};'
        )
        
        logging.info(f"Conectando ao banco de dados: {mdb_file}")
        
        # Lista de senhas para tentar
        passwords = ['010182', '', '12345678', '123456', 'admin', 'password', 'extratos', 'banco']
        
        conn = None
        for pwd in passwords:
            try:
                if pwd:
                    conn_str_with_pwd = (
                        r'DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};'
                        f'DBQ={mdb_file};'
                        f'PWD={pwd};'
                    )
                    logging.info(f"Tentando senha: {'*' * len(pwd)}")
                    conn = pyodbc.connect(conn_str_with_pwd)
                else:
                    logging.info("Tentando sem senha...")
                    conn = pyodbc.connect(conn_str)
                
                logging.info("Conexão estabelecida com sucesso!")
                break
            except pyodbc.Error as e:
                if pwd:
                    logging.debug(f"Senha '{pwd}' falhou: {e}")
                else:
                    logging.debug(f"Conexão sem senha falhou: {e}")
                continue
        
        if conn is None:
            raise Exception("Não foi possível conectar com nenhuma das senhas testadas")
        cursor = conn.cursor()
        
        # Primeiro, vamos verificar se a tabela existe
        logging.info("Verificando tabelas disponíveis...")
        tables = cursor.tables(tableType='TABLE')
        table_names = [table.table_name for table in tables]
        
        logging.info(f"Tabelas encontradas: {table_names}")
        
        # Verificar se a tabela NotasFiscais existe
        if 'NotasFiscais' not in table_names:
            logging.error("Tabela 'NotasFiscais' não encontrada!")
            # Listar tabelas que contêm 'nota' no nome
            nota_tables = [name for name in table_names if 'nota' in name.lower()]
            if nota_tables:
                logging.info(f"Tabelas com 'nota' no nome: {nota_tables}")
            return
        
        # Obter estrutura da tabela
        logging.info("Analisando estrutura da tabela NotasFiscais...")
        cursor.execute("SELECT * FROM NotasFiscais WHERE 1=0")  # Query que retorna apenas colunas
        columns = [column[0] for column in cursor.description]
        logging.info(f"Colunas encontradas: {columns}")
        
        # Contar registros
        cursor.execute("SELECT COUNT(*) FROM NotasFiscais")
        total_records = cursor.fetchone()[0]
        logging.info(f"Total de registros na tabela: {total_records}")
        
        if total_records == 0:
            logging.warning("A tabela NotasFiscais está vazia!")
            return
        
        # Extrair uma amostra dos dados (primeiros 10 registros)
        logging.info("Extraindo amostra dos dados...")
        cursor.execute("SELECT TOP 10 * FROM NotasFiscais")
        sample_data = cursor.fetchall()
        
        logging.info("=== AMOSTRA DOS DADOS ===")
        for i, row in enumerate(sample_data, 1):
            logging.info(f"Registro {i}:")
            for j, value in enumerate(row):
                logging.info(f"  {columns[j]}: {value}")
            logging.info("-" * 50)
        
        # Extrair todos os dados
        logging.info("Extraindo todos os dados...")
        cursor.execute("SELECT * FROM NotasFiscais")
        all_data = cursor.fetchall()
        
        # Converter para DataFrame do pandas para facilitar manipulação
        df = pd.DataFrame(all_data, columns=columns)
        
        # Salvar em CSV para análise posterior
        csv_filename = f"notas_fiscais_extratos_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        df.to_csv(csv_filename, index=False, encoding='utf-8-sig')
        logging.info(f"Dados salvos em: {csv_filename}")
        
        # Mostrar estatísticas básicas
        logging.info("=== ESTATÍSTICAS ===")
        logging.info(f"Total de registros: {len(df)}")
        logging.info(f"Total de colunas: {len(df.columns)}")
        
        # Verificar campos de data
        date_columns = [col for col in df.columns if 'data' in col.lower() or 'date' in col.lower()]
        if date_columns:
            logging.info(f"Colunas de data encontradas: {date_columns}")
            for col in date_columns:
                non_null_dates = df[col].dropna()
                if len(non_null_dates) > 0:
                    logging.info(f"  {col}: {len(non_null_dates)} valores não nulos")
                    if pd.api.types.is_datetime64_any_dtype(non_null_dates) or pd.api.types.is_object_dtype(non_null_dates):
                        try:
                            dates = pd.to_datetime(non_null_dates, errors='coerce')
                            valid_dates = dates.dropna()
                            if len(valid_dates) > 0:
                                logging.info(f"    Data mais antiga: {valid_dates.min()}")
                                logging.info(f"    Data mais recente: {valid_dates.max()}")
                        except:
                            pass
        
        # Verificar campos numéricos
        numeric_columns = df.select_dtypes(include=['number']).columns.tolist()
        if numeric_columns:
            logging.info(f"Colunas numéricas: {numeric_columns}")
        
        conn.close()
        logging.info("Extração concluída com sucesso!")
        
        return df
        
    except pyodbc.Error as e:
        logging.error(f"Erro de conexão com o banco de dados: {e}")
        return None
    except Exception as e:
        logging.error(f"Erro inesperado: {e}")
        return None

if __name__ == "__main__":
    print("Iniciando extração da tabela NotasFiscais...")
    result = extract_notas_fiscais()
    
    if result is not None:
        print(f"\nExtração concluída! {len(result)} registros extraídos.")
        print("Verifique o arquivo CSV gerado e o log para mais detalhes.")
    else:
        print("Falha na extração. Verifique o log para detalhes do erro.")
