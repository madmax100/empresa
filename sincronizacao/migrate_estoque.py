#!/usr/bin/env python
"""
Módulo para migrar dados da tabela NotasFiscais (movimentações) do arquivo Extratos.mdb 
para a tabela MovimentacoesEstoque no banco de dados PostgreSQL do Django.
Adaptado para ser usado pelo sync_database.py
"""

import os
import sys
import django
import pyodbc
import pandas as pd
from datetime import datetime, date, time
import logging
from decimal import Decimal, InvalidOperation
import pytz

# Configurar o path para encontrar o projeto Django
current_dir = os.path.dirname(os.path.abspath(__file__))
base_dir = os.path.dirname(current_dir)
backend_dir = os.path.join(base_dir, 'backend', 'empresa')

if backend_dir not in sys.path:
    sys.path.append(backend_dir)

# Configurar Django se ainda não estiver configurado
try:
    django.setup()
except Exception:
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'empresa.settings')
    try:
        django.setup()
    except Exception as e:
        print(f"Aviso: Django setup falhou ou já estava configurado: {e}")

from contas.models.access import MovimentacoesEstoque, Produtos, TiposMovimentacaoEstoque
from django.db import transaction
from django.utils import timezone
try:
    from config import EXTRATOS_DB
except ImportError:
    # Fallback se executado diretamente
    EXTRATOS_DB = r"C:\Users\Cirilo\Documents\programas\empresa\InterMax.03.02.2026\Bancos\Extratos\Extratos.mdb"

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('migrate_estoque.log'),
        logging.StreamHandler()
    ]
)

class MovimentacoesExtratosImporter:
    def __init__(self):
        self.mdb_file = EXTRATOS_DB
        self.imported_count = 0
        self.error_count = 0
        self.skipped_count = 0
        
        # Carregar tipos de movimentação
        self.tipo_entrada = None
        self.tipo_saida = None
        self.load_tipos_movimentacao()
        
    def load_tipos_movimentacao(self):
        """Carrega ou cria os tipos de movimentação do banco de dados"""
        try:
            # Buscar ou criar tipo de entrada
            self.tipo_entrada = TiposMovimentacaoEstoque.objects.filter(
                descricao__icontains='entrada'
            ).first()
            
            if not self.tipo_entrada:
                self.tipo_entrada = TiposMovimentacaoEstoque.objects.filter(tipo='E').first()
            
            if not self.tipo_entrada:
                logging.info("Criando tipo de movimentação: Entrada")
                self.tipo_entrada = TiposMovimentacaoEstoque.objects.create(
                    tipo='E',
                    descricao='Entrada por Compra'
                )
            
            # Buscar ou criar tipo de saída
            self.tipo_saida = TiposMovimentacaoEstoque.objects.filter(
                descricao__icontains='saida'
            ).first()
            
            if not self.tipo_saida:
                self.tipo_saida = TiposMovimentacaoEstoque.objects.filter(tipo='S').first()
                
            if not self.tipo_saida:
                logging.info("Criando tipo de movimentação: Saída")
                self.tipo_saida = TiposMovimentacaoEstoque.objects.create(
                    tipo='S',
                    descricao='Saída por Venda'
                )
            
        except Exception as e:
            logging.error(f"Erro ao carregar tipos de movimentação: {e}")
            raise
        
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
        """Extrai dados da tabela NotasFiscais (movimentações) do Access"""
        conn = self.connect_to_access()
        if not conn:
            return None
            
        try:
            # Verificar se a tabela existe
            cursor = conn.cursor()
            tables = [table.table_name for table in cursor.tables(tableType='TABLE')]
            
            if 'NotasFiscais' not in tables:
                logging.error("Tabela 'NotasFiscais' não encontrada!")
                return None
            
            # Extrair todos os dados
            logging.info("Extraindo dados da tabela NotasFiscais (movimentações)...")
            query = "SELECT * FROM NotasFiscais"
            df = pd.read_sql(query, conn)
            
            logging.info(f"Extraídos {len(df)} registros da tabela NotasFiscais")
            
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
            # logging.warning(f"Valor inválido para decimal: {value}")
            return Decimal('0.00')
    
    def clean_datetime_value(self, date_value, time_value):
        """Combina data e hora em datetime"""
        try:
            # Limpar data
            if pd.isna(date_value) or date_value is None:
                return None
            
            # Converter data
            if hasattr(date_value, 'date'):
                clean_date = date_value.date()
            elif isinstance(date_value, str):
                try:
                    clean_date = datetime.strptime(date_value, '%Y-%m-%d').date()
                except ValueError:
                    try:
                        clean_date = datetime.strptime(date_value, '%Y-%m-%d %H:%M:%S').date()
                    except ValueError:
                        clean_date = datetime.now().date()
            else:
                clean_date = date_value
            
            # Limpar hora
            clean_time = None
            if not pd.isna(time_value) and time_value is not None:
                if hasattr(time_value, 'time'):
                    clean_time = time_value.time()
                elif isinstance(time_value, str):
                    try:
                        # Se time_value tem formato datetime completo, extrair só a hora
                        if ' ' in time_value:
                            time_part = time_value.split(' ')[1]
                        else:
                            time_part = time_value
                        clean_time = datetime.strptime(time_part, '%H:%M:%S').time()
                    except ValueError:
                        clean_time = time(12, 0)
                elif hasattr(time_value, 'hour'):
                    # time_value já é um objeto time
                    clean_time = time_value
                else:
                    clean_time = time(12, 0)
            else:
                clean_time = time(12, 0)
            
            # Combinar data e hora
            combined_datetime = datetime.combine(clean_date, clean_time)
            
            # Converter para timezone aware (UTC)
            if timezone.is_naive(combined_datetime):
                # Assumir que as datas do Access estão em horário local do Brasil
                brazil_tz = pytz.timezone('America/Sao_Paulo')
                combined_datetime = brazil_tz.localize(combined_datetime)
                combined_datetime = combined_datetime.astimezone(pytz.UTC)
            
            return combined_datetime
            
        except Exception as e:
            logging.warning(f"Erro ao processar datetime: {e}, ignorando registro")
            return None
    
    def find_or_create_produto(self, produto_codigo):
        """Encontra ou cria um produto baseado no código"""
        if not produto_codigo or pd.isna(produto_codigo):
            return None
        
        try:
            codigo = int(produto_codigo)
            
            # Tentar encontrar produto existente
            produto = Produtos.objects.filter(codigo=codigo).first()
            if produto:
                return produto
            
            # Se não encontrar, criar um produto básico
            produto = Produtos.objects.create(
                codigo=codigo,
                nome=f"Produto {codigo}",
                ativo=True,
                preco_venda=Decimal('0.00'),
                grupo_id=None
            )
            # logging.info(f"Produto criado: {produto.nome} (código: {codigo})")
            return produto
            
        except Exception as e:
            # logging.warning(f"Erro ao processar produto '{produto_codigo}': {e}")
            return None
    
    def map_movimentacao_data(self, row):
        """Mapeia os dados do Access para o modelo MovimentacoesEstoque"""
        try:
            # Encontrar produto
            produto = self.find_or_create_produto(row.get('Produto'))
            if not produto:
                # logging.warning(f"Produto não encontrado para código: {row.get('Produto')}")
                return None
            
            # Criar datetime
            data_movimento = self.clean_datetime_value(row.get('Data'), row.get('Horario'))
            if not data_movimento:
                return None
            
            # Determinar tipo de movimentação
            movimentacao_tipo = str(row.get('Movimentacao', '')).upper().strip()
            tipo_movimentacao = None
            
            if movimentacao_tipo == 'ENTRADA':
                tipo_movimentacao = self.tipo_entrada
            elif movimentacao_tipo == 'SAIDA':
                tipo_movimentacao = self.tipo_saida
            else:
                return None
            
            mapped_data = {
                'produto': produto,
                'tipo_movimentacao': tipo_movimentacao,
                'data_movimentacao': data_movimento,
                'quantidade': self.clean_decimal_value(row.get('Quantidade', 0)),
                'custo_unitario': self.clean_decimal_value(row.get('Unitario', 0)),
                'documento_referencia': str(row.get('Documento', ''))[:50],
                'observacoes': f"{row.get('Historico', '')} - {row.get('Movimentacao', '')} - Operador: {row.get('OPERADOR', '')}"[:500],
            }
            
            # Calcular valor total
            mapped_data['valor_total'] = mapped_data['quantidade'] * mapped_data['custo_unitario']
            
            return mapped_data
            
        except Exception as e:
            logging.error(f"Erro ao mapear dados da linha: {e}")
            return None
    
    def import_to_postgresql(self, df):
        """Importa os dados para o PostgreSQL"""
        logging.info("Iniciando importação para PostgreSQL...")
        
        # Otimização: Carregar chaves existentes para evitar queries repetitivas
        # Como a tabela pode ser grande, vamos filtrar por data ou assumir verificação one-by-one se necessário
        # Para simplificar e manter segurança, verificamos um a um mas com transação em lote
        
        batch_size = 1000
        batch_data = []
        
        for index, row in df.iterrows():
            try:
                mapped_data = self.map_movimentacao_data(row)
                if not mapped_data:
                    self.error_count += 1
                    continue
                
                # Verificação de existência
                if MovimentacoesEstoque.objects.filter(
                    produto=mapped_data['produto'],
                    data_movimentacao=mapped_data['data_movimentacao'],
                    documento_referencia=mapped_data['documento_referencia'],
                    quantidade=mapped_data['quantidade']
                ).exists():
                    self.skipped_count += 1
                    continue
                
                batch_data.append(MovimentacoesEstoque(**mapped_data))
                self.imported_count += 1
                
                if len(batch_data) >= batch_size:
                    with transaction.atomic():
                        MovimentacoesEstoque.objects.bulk_create(batch_data)
                    logging.info(f"Importados {self.imported_count} registros...")
                    batch_data = []
                
            except Exception as e:
                self.error_count += 1
                logging.error(f"Erro ao processar linha {index}: {e}")
                continue
        
        # Processar restante
        if batch_data:
            with transaction.atomic():
                MovimentacoesEstoque.objects.bulk_create(batch_data)
            logging.info(f"Importados {self.imported_count} registros (final)...")

    def run_migration(self):
        """Executa a migração completa"""
        logging.info("=== INICIANDO MIGRAÇÃO DE MOVIMENTAÇÕES (EXTRATOS) ===")
        
        df = self.extract_data_from_access()
        if df is None or df.empty:
            logging.error("Nenhum dado extraído do Access")
            return False
        
        logging.info(f"Dados extraídos: {len(df)} registros")
        self.import_to_postgresql(df)
        
        logging.info("=== RELATÓRIO FINAL ===")
        logging.info(f"Total processados: {len(df)}")
        logging.info(f"Importados: {self.imported_count}")
        logging.info(f"Pulados: {self.skipped_count}")
        logging.info(f"Erros: {self.error_count}")
        
        return True

def migrar_estoque():
    importer = MovimentacoesExtratosImporter()
    return importer.run_migration()

if __name__ == "__main__":
    migrar_estoque()
