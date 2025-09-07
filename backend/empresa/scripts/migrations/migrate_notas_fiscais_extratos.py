#!/usr/bin/env python
"""
Script para migrar dados da tabela NotasFiscais do arquivo Extratos.mdb 
para o banco de dados PostgreSQL do Django
"""

import os
import sys
import django
import pyodbc
import pandas as pd
from datetime import datetime
import logging
from decimal import Decimal, InvalidOperation

# Configurar o ambiente Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'empresa.settings')
django.setup()

from contas.models.access import NotasFiscaisSaida, Clientes
from django.db import transaction

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('migrate_notas_fiscais_extratos.log'),
        logging.StreamHandler()
    ]
)

class NotasFiscaisExtratosImporter:
    def __init__(self):
        self.mdb_file = r"C:\Users\Cirilo\Documents\Bancos\Extratos\Extratos.mdb"
        self.imported_count = 0
        self.error_count = 0
        self.skipped_count = 0
        
    def connect_to_access(self):
        """Conecta ao banco de dados Access"""
        try:
            conn_str = (
                r'DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};'
                f'DBQ={self.mdb_file};'
                'PWD=010182;'
            )
            return pyodbc.connect(conn_str)
        except Exception as e:
            logging.error(f"Erro ao conectar ao Access: {e}")
            return None
    
    def extract_data_from_access(self):
        """Extrai dados da tabela NotasFiscais do Access"""
        conn = self.connect_to_access()
        if not conn:
            return None
            
        try:
            # Verificar se a tabela existe
            cursor = conn.cursor()
            tables = [table.table_name for table in cursor.tables(tableType='TABLE')]
            
            if 'NotasFiscais' not in tables:
                logging.error("Tabela 'NotasFiscais' não encontrada!")
                # Procurar tabelas similares
                similar_tables = [t for t in tables if 'nota' in t.lower() or 'fiscal' in t.lower()]
                if similar_tables:
                    logging.info(f"Tabelas similares encontradas: {similar_tables}")
                return None
            
            # Extrair todos os dados
            logging.info("Extraindo dados da tabela NotasFiscais...")
            query = "SELECT * FROM NotasFiscais"
            df = pd.read_sql(query, conn)
            
            logging.info(f"Extraídos {len(df)} registros da tabela NotasFiscais")
            logging.info(f"Colunas: {list(df.columns)}")
            
            return df
            
        except Exception as e:
            logging.error(f"Erro ao extrair dados: {e}")
            return None
        finally:
            conn.close()
    
    def clean_decimal_value(self, value):
        """Limpa e converte valores para Decimal"""
        if pd.isna(value) or value is None:
            return Decimal('0.00')
        
        try:
            # Converter para string e limpar
            str_value = str(value).strip().replace(',', '.')
            return Decimal(str_value)
        except (InvalidOperation, ValueError):
            logging.warning(f"Valor inválido para decimal: {value}")
            return Decimal('0.00')
    
    def clean_date_value(self, value):
        """Limpa e converte valores para data"""
        if pd.isna(value) or value is None:
            return None
        
        try:
            if isinstance(value, str):
                # Tentar diferentes formatos de data
                for fmt in ['%Y-%m-%d', '%d/%m/%Y', '%m/%d/%Y', '%Y-%m-%d %H:%M:%S']:
                    try:
                        return datetime.strptime(value, fmt).date()
                    except ValueError:
                        continue
            elif hasattr(value, 'date'):
                return value.date()
            elif hasattr(value, 'strftime'):
                return value
            return None
        except Exception:
            logging.warning(f"Valor inválido para data: {value}")
            return None
    
    def find_or_create_cliente(self, cliente_info):
        """Encontra ou cria um cliente baseado nas informações disponíveis"""
        if not cliente_info or pd.isna(cliente_info):
            return None
        
        try:
            # Tentar encontrar cliente existente
            cliente = Clientes.objects.filter(nome__icontains=str(cliente_info).strip()).first()
            if cliente:
                return cliente
            
            # Se não encontrar, criar um novo cliente básico
            cliente = Clientes.objects.create(
                nome=str(cliente_info).strip()[:100],  # Limitar o tamanho
                ativo=True
            )
            logging.info(f"Cliente criado: {cliente.nome}")
            return cliente
            
        except Exception as e:
            logging.warning(f"Erro ao processar cliente '{cliente_info}': {e}")
            return None
    
    def map_nota_fiscal_data(self, row):
        """Mapeia os dados do Access para o modelo Django"""
        try:
            # Mapeamento básico - ajustar conforme a estrutura real da tabela
            mapped_data = {
                'numero_nota': str(row.get('NumeroNota', row.get('Numero', '')))[:20],
                'data': self.clean_date_value(row.get('Data', row.get('DataEmissao'))),
                'valor_total_nota': self.clean_decimal_value(row.get('ValorTotal', row.get('Valor', 0))),
                'valor_produtos': self.clean_decimal_value(row.get('ValorProdutos', row.get('Valor', 0))),
                'operacao': str(row.get('Operacao', ''))[:50] if row.get('Operacao') else '',
                'cfop': str(row.get('CFOP', ''))[:10] if row.get('CFOP') else '',
                'obs': str(row.get('Observacoes', row.get('Obs', '')))[:500] if row.get('Observacoes') or row.get('Obs') else '',
            }
            
            # Tentar mapear cliente
            cliente_field = None
            for field_name in ['Cliente', 'NomeCliente', 'ClienteNome']:
                if field_name in row and not pd.isna(row[field_name]):
                    cliente_field = row[field_name]
                    break
            
            if cliente_field:
                cliente = self.find_or_create_cliente(cliente_field)
                mapped_data['cliente'] = cliente
            
            return mapped_data
            
        except Exception as e:
            logging.error(f"Erro ao mapear dados da linha: {e}")
            return None
    
    def import_to_postgresql(self, df):
        """Importa os dados para o PostgreSQL"""
        logging.info("Iniciando importação para PostgreSQL...")
        
        for index, row in df.iterrows():
            try:
                # Mapear dados
                mapped_data = self.map_nota_fiscal_data(row)
                if not mapped_data:
                    self.error_count += 1
                    continue
                
                # Verificar se já existe
                numero_nota = mapped_data['numero_nota']
                if NotasFiscaisSaida.objects.filter(numero_nota=numero_nota).exists():
                    logging.info(f"Nota fiscal {numero_nota} já existe - pulando")
                    self.skipped_count += 1
                    continue
                
                # Criar nova nota fiscal
                with transaction.atomic():
                    nota = NotasFiscaisSaida.objects.create(**mapped_data)
                    self.imported_count += 1
                    
                    if self.imported_count % 100 == 0:
                        logging.info(f"Importados {self.imported_count} registros...")
                
            except Exception as e:
                self.error_count += 1
                logging.error(f"Erro ao importar linha {index}: {e}")
                continue
    
    def run_migration(self):
        """Executa a migração completa"""
        logging.info("=== INICIANDO MIGRAÇÃO DE NOTAS FISCAIS (EXTRATOS) ===")
        
        # Extrair dados do Access
        df = self.extract_data_from_access()
        if df is None or df.empty:
            logging.error("Nenhum dado extraído do Access")
            return False
        
        logging.info(f"Dados extraídos: {len(df)} registros")
        
        # Mostrar amostra dos dados
        logging.info("=== AMOSTRA DOS DADOS ===")
        logging.info(f"Colunas disponíveis: {list(df.columns)}")
        if len(df) > 0:
            logging.info("Primeiros 3 registros:")
            for i in range(min(3, len(df))):
                logging.info(f"Registro {i+1}: {dict(df.iloc[i])}")
        
        # Importar para PostgreSQL
        self.import_to_postgresql(df)
        
        # Relatório final
        logging.info("=== RELATÓRIO FINAL ===")
        logging.info(f"Total de registros processados: {len(df)}")
        logging.info(f"Registros importados: {self.imported_count}")
        logging.info(f"Registros pulados (já existiam): {self.skipped_count}")
        logging.info(f"Registros com erro: {self.error_count}")
        
        return True

def main():
    importer = NotasFiscaisExtratosImporter()
    
    try:
        success = importer.run_migration()
        if success:
            print(f"\nMigração concluída!")
            print(f"Importados: {importer.imported_count}")
            print(f"Pulados: {importer.skipped_count}")
            print(f"Erros: {importer.error_count}")
        else:
            print("Falha na migração. Verifique o log para detalhes.")
            
    except Exception as e:
        logging.error(f"Erro geral na migração: {e}")
        print(f"Erro na migração: {e}")

if __name__ == "__main__":
    main()
