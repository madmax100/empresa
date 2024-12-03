import pyodbc
import pandas as pd
import numpy as np
from typing import Dict, List
import re

class AccessAnalyzer:
    def __init__(self, access_path: str):
        """Inicializa o analisador com o caminho do arquivo Access"""
        self.access_path = access_path
        self.conn = None
        
    def connect(self) -> bool:
        """Conecta ao banco Access"""
        try:
            conn_str = (
                r'Driver={Microsoft Access Driver (*.mdb, *.accdb)};'
                f'DBQ={access_path};'
                'PWD=010182;')            
            self.conn = pyodbc.connect(conn_str)
            return True
        except pyodbc.Error as e:
            print(f"Erro ao conectar ao banco de dados: {str(e)}")
            return False

    def get_tables(self) -> List[str]:
        """Retorna lista de tabelas do banco"""
        tables = []
        if self.conn:
            for row in self.conn.cursor().tables(tableType='TABLE'):
                if not row.table_name.startswith('~'):  # Ignora tabelas temporárias
                    tables.append(row.table_name)
        return tables

    def analyze_table(self, table_name: str) -> Dict:
        """Analisa estrutura e dados de uma tabela"""
        if not self.conn:
            return {}

        cursor = self.conn.cursor()
        
        # Análise de estrutura
        columns = []
        for row in cursor.columns(table=table_name):
            columns.append({
                'name': row.column_name,
                'type': row.type_name,
                'nullable': row.nullable,
                'size': row.column_size
            })

        # Análise de dados
        df = pd.read_sql(f"SELECT * FROM [{table_name}]", self.conn)
        
        analysis = {
            'table_name': table_name,
            'columns': columns,
            'row_count': len(df),
            'column_analysis': {}
        }

        for col in df.columns:
            col_analysis = {
                'sample_values': df[col].head().tolist(),
                'null_count': df[col].isnull().sum(),
                'unique_count': df[col].nunique(),
                'data_type': str(df[col].dtype)
            }
            
            # Análise específica por tipo de dados
            if df[col].dtype in ['object', 'string']:
                # Verifica se parece com CPF/CNPJ
                if df[col].str.contains(r'^\d{2}[\.]?\d{3}[\.]?\d{3}[\/]?\d{4}[-]?\d{2}$').any() or \
                   df[col].str.contains(r'^\d{3}[\.]?\d{3}[\.]?\d{3}[-]?\d{2}$').any():
                    col_analysis['appears_to_be'] = 'cpf_cnpj'
                
                # Verifica se parece com data
                elif df[col].str.contains(r'\d{2}[/-]\d{2}[/-]\d{4}').any():
                    col_analysis['appears_to_be'] = 'date'
                
                # Verifica tamanho máximo usado
                col_analysis['max_length'] = df[col].str.len().max()

            # Análise de campos numéricos
            elif df[col].dtype in ['int64', 'float64']:
                col_analysis.update({
                    'min': df[col].min(),
                    'max': df[col].max(),
                    'has_decimals': (df[col] % 1 != 0).any()
                })

            analysis['column_analysis'][col] = col_analysis

        return analysis

    def suggest_postgresql_type(self, access_type: str, column_analysis: Dict) -> str:
        """Sugere tipo PostgreSQL baseado na análise"""
        # Conversão básica de tipos
        type_mapping = {
            'COUNTER': 'SERIAL',
            'INTEGER': 'INTEGER',
            'LONG': 'BIGINT',
            'BYTE': 'SMALLINT',
            'SINGLE': 'REAL',
            'DOUBLE': 'DOUBLE PRECISION',
            'CURRENCY': 'DECIMAL(19,4)',
            'DATETIME': 'TIMESTAMP',
            'TEXT': 'VARCHAR',
            'MEMO': 'TEXT',
            'BIT': 'BOOLEAN',
            'YESNO': 'BOOLEAN'
        }

        base_type = access_type.upper()
        
        if base_type == 'TEXT':
            max_length = column_analysis.get('max_length', 0)
            if max_length:
                if max_length <= 50:
                    return 'VARCHAR(50)'
                elif max_length <= 100:
                    return 'VARCHAR(100)'
                elif max_length <= 255:
                    return 'VARCHAR(255)'
                else:
                    return 'TEXT'
                    
        if 'appears_to_be' in column_analysis:
            if column_analysis['appears_to_be'] == 'cpf_cnpj':
                return 'VARCHAR(14)'
            elif column_analysis['appears_to_be'] == 'date':
                return 'DATE'

        return type_mapping.get(base_type, 'VARCHAR(255)')

    def print_analysis(self, analysis: Dict):
        """Imprime análise em formato legível"""
        print(f"\nAnálise da tabela: {analysis['table_name']}")
        print(f"Total de registros: {analysis['row_count']}")
        print("\nEstrutura de colunas:")
        print("-" * 80)
        
        for col in analysis['columns']:
            col_analysis = analysis['column_analysis'][col['name']]
            pg_type = self.suggest_postgresql_type(col['type'], col_analysis)
            
            print(f"\nColuna: {col['name']}")
            print(f"Tipo Access: {col['type']}")
            print(f"Tipo sugerido PostgreSQL: {pg_type}")
            print(f"Permite NULL: {col['nullable']}")
            print(f"Valores únicos: {col_analysis['unique_count']}")
            print(f"Valores nulos: {col_analysis['null_count']}")
            print("Exemplos de valores:", col_analysis['sample_values'])
            
            if 'appears_to_be' in col_analysis:
                print(f"Parece ser: {col_analysis['appears_to_be']}")
            
            if 'max_length' in col_analysis:
                print(f"Tamanho máximo encontrado: {col_analysis['max_length']}")

def analyze_access_database(access_path: str):
    """Função principal para análise do banco Access"""
    analyzer = AccessAnalyzer(access_path)
    
    if not analyzer.connect():
        return
    
    print("Banco de dados conectado com sucesso!")
    print("\nTabelas encontradas:")
    tables = analyzer.get_tables()
    
    for i, table in enumerate(tables, 1):
        print(f"{i}. {table}")
    
    print("\nIniciando análise detalhada de cada tabela...")
    
    for table in tables:
        analysis = analyzer.analyze_table(table)
        analyzer.print_analysis(analysis)

# Uso do script
if __name__ == "__main__":
    access_path = r"C:\Users\Cirilo\Documents\empresa\Bancos\Cadastros\Cadastros.mdb"
    analyze_access_database(access_path)