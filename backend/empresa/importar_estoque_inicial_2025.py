#!/usr/bin/env python3
"""
Script para importar dados do MS Access e calcular estoque inicial de 01/01/2025
através de cálculo reverso a partir do estoque atual.

Funcionalidades:
1. Conecta ao banco MS Access
2. Importa produtos e movimentações
3. Calcula estoque reverso até 01/01/2025
4. Popula tabela estoque_inicial no PostgreSQL
"""

import os
import sys
import django
import pyodbc
import psycopg2
from datetime import datetime, date
from decimal import Decimal
from collections import defaultdict

# Configuração do Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'empresa.settings')
django.setup()

from django.db import transaction
from contas.models.access import Produtos, MovimentacoesEstoque, TiposMovimentacaoEstoque, EstoqueInicial, Grupos

class ImportadorEstoqueInicial:
    
    def __init__(self):
        # Configurações Access
        self.access_db_path = r"C:\Users\Cirilo\Documents\c3mcopias\backend\empresa\Extratos.mdb"
        self.cadastros_db_path = r"C:\Users\Cirilo\Documents\c3mcopias\backend\empresa\Cadastros.mdb"
        self.access_password = "010182"
        
        # Configurações PostgreSQL
        self.pg_config = {
            'host': 'localhost',
            'database': 'c3mcopiasdb2',
            'user': 'cirilomax',
            'password': '226cmm100',
            'port': '5432'
        }
        
        # Data de referência para estoque inicial
        self.data_estoque_inicial = date(2025, 1, 1)
        
        print(f"🚀 Iniciando importação de estoque inicial para {self.data_estoque_inicial}")

    def conectar_access_extratos(self):
        """Conecta ao banco Access Extratos.mdb"""
        try:
            conn_str = f'DRIVER={{Microsoft Access Driver (*.mdb, *.accdb)}};DBQ={self.access_db_path};PWD={self.access_password}'
            return pyodbc.connect(conn_str)
        except Exception as e:
            print(f"❌ Erro ao conectar Access Extratos: {e}")
            return None

    def conectar_access_cadastros(self):
        """Conecta ao banco Access Cadastros.mdb"""
        try:
            conn_str = f'DRIVER={{Microsoft Access Driver (*.mdb, *.accdb)}};DBQ={self.cadastros_db_path};PWD={self.access_password}'
            return pyodbc.connect(conn_str)
        except Exception as e:
            print(f"❌ Erro ao conectar Access Cadastros: {e}")
            return None

    def conectar_postgresql(self):
        """Conecta ao PostgreSQL"""
        try:
            return psycopg2.connect(**self.pg_config)
        except Exception as e:
            print(f"❌ Erro ao conectar PostgreSQL: {e}")
            return None

    def importar_produtos_access(self):
        """Importa produtos do Access para PostgreSQL"""
        print("📦 Importando produtos do Access...")
        
        conn_cadastros = self.conectar_access_cadastros()
        if not conn_cadastros:
            return False

        try:
            cursor = conn_cadastros.cursor()
            
            # Query para buscar produtos no Access
            query = """
            SELECT codigo, historico, referencia, grupo, unidade, 
                   preco_custo, preco_venda, estoque_atual, ativo
            FROM produtos 
            WHERE ativo = True
            ORDER BY codigo
            """
            
            cursor.execute(query)
            produtos_access = cursor.fetchall()
            
            produtos_importados = 0
            produtos_atualizados = 0
            
            with transaction.atomic():
                for row in produtos_access:
                    codigo, nome, referencia, grupo_id, unidade, preco_custo, preco_venda, estoque_atual, ativo = row
                    
                    # Criar ou atualizar produto
                    produto, created = Produtos.objects.get_or_create(
                        codigo=str(codigo),
                        defaults={
                            'nome': nome or f'Produto {codigo}',
                            'referencia': referencia,
                            'grupo_id': grupo_id,
                            'unidade_medida': unidade,
                            'preco_custo': Decimal(str(preco_custo or 0)),
                            'preco_venda': Decimal(str(preco_venda or 0)),
                            'estoque_atual': int(estoque_atual or 0),
                            'ativo': bool(ativo)
                        }
                    )
                    
                    if created:
                        produtos_importados += 1
                    else:
                        # Atualizar campos
                        produto.nome = nome or f'Produto {codigo}'
                        produto.referencia = referencia
                        produto.grupo_id = grupo_id
                        produto.unidade_medida = unidade
                        produto.preco_custo = Decimal(str(preco_custo or 0))
                        produto.preco_venda = Decimal(str(preco_venda or 0))
                        produto.estoque_atual = int(estoque_atual or 0)
                        produto.ativo = bool(ativo)
                        produto.save()
                        produtos_atualizados += 1

            print(f"✅ Produtos importados: {produtos_importados}")
            print(f"✅ Produtos atualizados: {produtos_atualizados}")
            
            conn_cadastros.close()
            return True
            
        except Exception as e:
            print(f"❌ Erro ao importar produtos: {e}")
            conn_cadastros.close()
            return False

    def importar_movimentacoes_access(self):
        """Importa movimentações do Access"""
        print("📋 Importando movimentações do Access...")
        
        conn_extratos = self.conectar_access_extratos()
        if not conn_extratos:
            return False

        try:
            cursor = conn_extratos.cursor()
            
            # Query para buscar movimentações
            query = """
            SELECT data_movimentacao, tipo_movimentacao, produto_id, quantidade,
                   custo_unitario, valor_total, documento_referencia, observacoes
            FROM movimentacoes_estoque 
            WHERE data_movimentacao >= #2024-01-01#
            ORDER BY data_movimentacao, produto_id
            """
            
            cursor.execute(query)
            movimentacoes_access = cursor.fetchall()
            
            movimentacoes_importadas = 0
            
            with transaction.atomic():
                for row in movimentacoes_access:
                    data_mov, tipo_mov, produto_id, quantidade, custo_unitario, valor_total, doc_ref, obs = row
                    
                    # Buscar produto
                    try:
                        produto = Produtos.objects.get(id=produto_id)
                    except Produtos.DoesNotExist:
                        continue
                    
                    # Buscar tipo de movimentação
                    tipo_movimentacao, _ = TiposMovimentacaoEstoque.objects.get_or_create(
                        id=tipo_mov,
                        defaults={'nome': f'Tipo {tipo_mov}'}
                    )
                    
                    # Criar movimentação
                    MovimentacoesEstoque.objects.get_or_create(
                        data_movimentacao=data_mov,
                        produto=produto,
                        tipo_movimentacao=tipo_movimentacao,
                        quantidade=Decimal(str(quantidade or 0)),
                        custo_unitario=Decimal(str(custo_unitario or 0)),
                        valor_total=Decimal(str(valor_total or 0)),
                        documento_referencia=doc_ref,
                        observacoes=obs
                    )
                    
                    movimentacoes_importadas += 1
            
            print(f"✅ Movimentações importadas: {movimentacoes_importadas}")
            
            conn_extratos.close()
            return True
            
        except Exception as e:
            print(f"❌ Erro ao importar movimentações: {e}")
            conn_extratos.close()
            return False

    def calcular_estoque_reverso(self):
        """Calcula o estoque reverso até 01/01/2025"""
        print("🔄 Calculando estoque reverso até 01/01/2025...")
        
        try:
            # Buscar todos os produtos ativos
            produtos = Produtos.objects.filter(ativo=True)
            estoques_calculados = 0
            
            with transaction.atomic():
                # Limpar estoque inicial anterior
                EstoqueInicial.objects.filter(data_inicial=self.data_estoque_inicial).delete()
                
                for produto in produtos:
                    # Estoque atual (base para cálculo reverso)
                    quantidade_atual = Decimal(str(produto.estoque_atual or 0))
                    preco_custo_atual = produto.preco_custo or Decimal('0')
                    valor_total_atual = quantidade_atual * preco_custo_atual
                    
                    # Buscar movimentações após 01/01/2025
                    movimentacoes = MovimentacoesEstoque.objects.filter(
                        produto=produto,
                        data_movimentacao__date__gt=self.data_estoque_inicial
                    ).exclude(
                        documento_referencia__in=['EST_INICIAL_2025', 'SALDO INICIAL']
                    ).order_by('data_movimentacao')
                    
                    # Calcular estoque reverso
                    quantidade_inicial = quantidade_atual
                    valor_unitario_medio = preco_custo_atual
                    
                    for mov in movimentacoes:
                        tipo_id = mov.tipo_movimentacao.id if mov.tipo_movimentacao else 0
                        quantidade_mov = mov.quantidade or Decimal('0')
                        
                        # Reverter movimentação
                        if tipo_id in [1, 3]:  # Entrada ou Estoque Inicial
                            quantidade_inicial -= quantidade_mov
                        elif tipo_id == 2:  # Saída
                            quantidade_inicial += quantidade_mov
                    
                    # Garantir que não seja negativo
                    if quantidade_inicial < 0:
                        quantidade_inicial = Decimal('0')
                    
                    # Calcular valor médio baseado em entradas
                    movs_entrada = MovimentacoesEstoque.objects.filter(
                        produto=produto,
                        tipo_movimentacao_id__in=[1, 3],
                        data_movimentacao__date__lte=self.data_estoque_inicial,
                        custo_unitario__gt=0
                    ).order_by('-data_movimentacao')[:5]  # Últimas 5 entradas
                    
                    if movs_entrada:
                        valor_unitario_medio = sum(m.custo_unitario for m in movs_entrada) / len(movs_entrada)
                    
                    valor_total_inicial = quantidade_inicial * valor_unitario_medio
                    
                    # Salvar estoque inicial
                    EstoqueInicial.objects.create(
                        produto=produto,
                        data_inicial=self.data_estoque_inicial,
                        quantidade_inicial=quantidade_inicial,
                        valor_unitario_inicial=valor_unitario_medio,
                        valor_total_inicial=valor_total_inicial
                    )
                    
                    estoques_calculados += 1
                    
                    if estoques_calculados % 100 == 0:
                        print(f"   Processados: {estoques_calculados} produtos...")
            
            print(f"✅ Estoque inicial calculado para {estoques_calculados} produtos")
            return True
            
        except Exception as e:
            print(f"❌ Erro ao calcular estoque reverso: {e}")
            return False

    def importar_grupos(self):
        """Importa grupos de produtos do Access"""
        print("🏷️ Importando grupos de produtos...")
        
        conn_cadastros = self.conectar_access_cadastros()
        if not conn_cadastros:
            return False

        try:
            cursor = conn_cadastros.cursor()
            
            # Query para buscar grupos
            query = "SELECT id, nome FROM grupos ORDER BY id"
            cursor.execute(query)
            grupos_access = cursor.fetchall()
            
            grupos_importados = 0
            
            with transaction.atomic():
                for row in grupos_access:
                    grupo_id, nome = row
                    
                    grupo, created = Grupos.objects.get_or_create(
                        id=grupo_id,
                        defaults={'nome': nome or f'Grupo {grupo_id}'}
                    )
                    
                    if created:
                        grupos_importados += 1

            print(f"✅ Grupos importados: {grupos_importados}")
            
            conn_cadastros.close()
            return True
            
        except Exception as e:
            print(f"❌ Erro ao importar grupos: {e}")
            conn_cadastros.close()
            return False

    def executar_importacao_completa(self):
        """Executa todo o processo de importação"""
        print("🎯 Iniciando importação completa...")
        print("=" * 60)
        
        try:
            # 1. Importar grupos
            if not self.importar_grupos():
                print("❌ Falha na importação de grupos")
                return False
            
            # 2. Importar produtos
            if not self.importar_produtos_access():
                print("❌ Falha na importação de produtos")
                return False
            
            # 3. Importar movimentações
            if not self.importar_movimentacoes_access():
                print("❌ Falha na importação de movimentações")
                return False
            
            # 4. Calcular estoque inicial
            if not self.calcular_estoque_reverso():
                print("❌ Falha no cálculo de estoque reverso")
                return False
            
            print("=" * 60)
            print("🎉 Importação completa realizada com sucesso!")
            
            # Estatísticas finais
            total_produtos = Produtos.objects.count()
            total_movimentacoes = MovimentacoesEstoque.objects.count()
            total_estoque_inicial = EstoqueInicial.objects.count()
            total_grupos = Grupos.objects.count()
            
            print(f"📊 Estatísticas finais:")
            print(f"   • Produtos: {total_produtos}")
            print(f"   • Movimentações: {total_movimentacoes}")
            print(f"   • Estoque inicial: {total_estoque_inicial}")
            print(f"   • Grupos: {total_grupos}")
            
            return True
            
        except Exception as e:
            print(f"❌ Erro geral na importação: {e}")
            return False


def main():
    """Função principal"""
    print("🚀 Sistema de Importação de Estoque Inicial 2025")
    print("=" * 60)
    
    importador = ImportadorEstoqueInicial()
    
    # Confirmar execução
    resposta = input("Deseja executar a importação completa? (s/N): ").lower()
    if resposta != 's':
        print("❌ Importação cancelada pelo usuário")
        return
    
    # Executar importação
    sucesso = importador.executar_importacao_completa()
    
    if sucesso:
        print("\n✅ Processo concluído com sucesso!")
        print("   O estoque inicial para 01/01/2025 foi calculado e salvo.")
        print("   Os endpoints agora podem usar estes dados como base.")
    else:
        print("\n❌ Processo finalizado com erros!")
        print("   Verifique os logs acima para identificar os problemas.")


if __name__ == "__main__":
    main()
