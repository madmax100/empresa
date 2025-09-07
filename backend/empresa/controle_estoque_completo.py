#!/usr/bin/env python3
"""
SISTEMA DE CONTROLE DE ESTOQUE COM MOVIMENTAÇÕES
Calcula estoque atual baseado no estoque inicial de 01/01/2025
e todas as movimentações até uma data específica
"""

import os
import django
import sys
from datetime import datetime, date
from decimal import Decimal
from collections import defaultdict

# Configuração do Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'empresa.settings')
django.setup()

from contas.models.access import MovimentacoesEstoque, Produtos

class ControleEstoque:
    def __init__(self):
        self.estoque_inicial = {}
        self.movimentacoes = defaultdict(list)
        
    def carregar_estoque_inicial(self):
        """Carrega o estoque inicial de 01/01/2025"""
        print("📦 Carregando estoque inicial de 01/01/2025...")
        
        movimentacoes_iniciais = MovimentacoesEstoque.objects.filter(
            documento_referencia='EST_INICIAL_2025',
            data_movimentacao__date='2025-01-01',
            tipo_movimentacao=3  # Tipo 3 = Estoque inicial
        ).select_related('produto')
        
        for mov in movimentacoes_iniciais:
            produto_id = mov.produto if isinstance(mov.produto, int) else mov.produto.id
            
            self.estoque_inicial[produto_id] = {
                'produto_id': produto_id,
                'quantidade_inicial': mov.quantidade,
                'custo_unitario': mov.custo_unitario,
                'valor_total_inicial': mov.valor_total,
                'data_inicial': mov.data_movimentacao.date(),
                'documento': mov.documento_referencia
            }
            
        print(f"✅ Carregados {len(self.estoque_inicial)} produtos com estoque inicial")
        
    def carregar_movimentacoes(self, data_final=None):
        """Carrega todas as movimentações até a data especificada"""
        if not data_final:
            data_final = date.today()
            
        print(f"🔄 Carregando movimentações até {data_final.strftime('%d/%m/%Y')}...")
        
        # Busca movimentações após 01/01/2025 até a data final
        movimentacoes = MovimentacoesEstoque.objects.filter(
            data_movimentacao__date__gt='2025-01-01',
            data_movimentacao__date__lte=data_final
        ).exclude(
            documento_referencia='EST_INICIAL_2025'
        ).select_related('produto').order_by('data_movimentacao')
        
        for mov in movimentacoes:
            produto_id = mov.produto if isinstance(mov.produto, int) else mov.produto.id
            
            self.movimentacoes[produto_id].append({
                'id': mov.id,
                'data': mov.data_movimentacao.date(),
                'quantidade': mov.quantidade,
                'tipo_movimentacao': mov.tipo_movimentacao,
                'custo_unitario': mov.custo_unitario,
                'valor_total': mov.valor_total,
                'documento': mov.documento_referencia,
                'observacoes': mov.observacoes
            })
            
        total_movs = sum(len(movs) for movs in self.movimentacoes.values())
        print(f"✅ Carregadas {total_movs} movimentações para {len(self.movimentacoes)} produtos")
        
    def calcular_estoque_atual(self, data_final=None):
        """Calcula o estoque atual baseado no inicial + movimentações"""
        if not data_final:
            data_final = date.today()
            
        print(f"🧮 Calculando estoque atual até {data_final.strftime('%d/%m/%Y')}...")
        
        estoque_atual = {}
        
        # Para cada produto com estoque inicial
        for produto_id, dados_iniciais in self.estoque_inicial.items():
            quantidade_atual = dados_iniciais['quantidade_inicial']
            valor_total_atual = dados_iniciais['valor_total_inicial']
            
            # Aplica as movimentações
            movimentacoes_produto = self.movimentacoes.get(produto_id, [])
            
            for mov in movimentacoes_produto:
                if mov['data'] <= data_final:
                    # Tipo 1 = Entrada, Tipo 2 = Saída, Tipo 3 = Ajuste
                    if mov['tipo_movimentacao'] in [1, 3]:  # Entrada/Ajuste
                        quantidade_atual += mov['quantidade']
                        valor_total_atual += mov['valor_total']
                    elif mov['tipo_movimentacao'] == 2:  # Saída
                        quantidade_atual -= mov['quantidade']
                        valor_total_atual -= mov['valor_total']
            
            # Busca informações do produto
            try:
                produto = Produtos.objects.get(id=produto_id)
                nome_produto = produto.nome
                referencia = produto.referencia
            except:
                nome_produto = f"Produto ID {produto_id}"
                referencia = "N/A"
            
            estoque_atual[produto_id] = {
                'produto_id': produto_id,
                'nome': nome_produto,
                'referencia': referencia,
                'quantidade_inicial': dados_iniciais['quantidade_inicial'],
                'quantidade_atual': quantidade_atual,
                'custo_unitario_inicial': dados_iniciais['custo_unitario'],
                'valor_inicial': dados_iniciais['valor_total_inicial'],
                'valor_atual': valor_total_atual,
                'total_movimentacoes': len(movimentacoes_produto),
                'data_calculo': data_final
            }
            
        return estoque_atual
        
    def gerar_relatorio(self, data_final=None, salvar_arquivo=True):
        """Gera relatório completo do estoque"""
        if not data_final:
            data_final = date.today()
            
        print(f"\n📊 GERANDO RELATÓRIO DE ESTOQUE - {data_final.strftime('%d/%m/%Y')}")
        print("=" * 80)
        
        # Carrega dados
        self.carregar_estoque_inicial()
        self.carregar_movimentacoes(data_final)
        estoque_atual = self.calcular_estoque_atual(data_final)
        
        # Estatísticas gerais
        total_produtos = len(estoque_atual)
        produtos_com_estoque = len([p for p in estoque_atual.values() if p['quantidade_atual'] > 0])
        produtos_zerados = total_produtos - produtos_com_estoque
        
        valor_total_inicial = sum(p['valor_inicial'] for p in estoque_atual.values())
        valor_total_atual = sum(p['valor_atual'] for p in estoque_atual.values())
        
        print(f"Total de produtos: {total_produtos}")
        print(f"Produtos com estoque: {produtos_com_estoque}")
        print(f"Produtos zerados: {produtos_zerados}")
        print(f"Valor total inicial: R$ {valor_total_inicial:,.2f}")
        print(f"Valor total atual: R$ {valor_total_atual:,.2f}")
        print(f"Variação: R$ {valor_total_atual - valor_total_inicial:,.2f}")
        
        # Produtos com maior movimentação
        produtos_mais_movimentados = sorted(
            estoque_atual.values(), 
            key=lambda x: x['total_movimentacoes'], 
            reverse=True
        )[:10]
        
        print(f"\n🔝 TOP 10 PRODUTOS MAIS MOVIMENTADOS:")
        for i, produto in enumerate(produtos_mais_movimentados, 1):
            print(f"{i:2d}. {produto['nome'][:50]:<50} - {produto['total_movimentacoes']} movs")
        
        # Produtos com estoque crítico (menos de 5 unidades)
        estoque_critico = [p for p in estoque_atual.values() if 0 < p['quantidade_atual'] < 5]
        
        if estoque_critico:
            print(f"\n⚠️  PRODUTOS COM ESTOQUE CRÍTICO (<5 unidades):")
            for produto in sorted(estoque_critico, key=lambda x: x['quantidade_atual'])[:10]:
                print(f"   {produto['nome'][:50]:<50} - {produto['quantidade_atual']:.0f} unids")
        
        # Salva arquivo CSV se solicitado
        if salvar_arquivo:
            nome_arquivo = f"estoque_{data_final.strftime('%Y%m%d')}.csv"
            self.salvar_csv(estoque_atual, nome_arquivo)
            print(f"\n💾 Relatório salvo em: {nome_arquivo}")
        
        return estoque_atual
        
    def salvar_csv(self, estoque_atual, nome_arquivo):
        """Salva o relatório em arquivo CSV"""
        import csv
        
        with open(nome_arquivo, 'w', newline='', encoding='utf-8') as arquivo:
            writer = csv.writer(arquivo, delimiter=';')
            
            # Cabeçalho
            writer.writerow([
                'ID Produto', 'Nome', 'Referência', 
                'Qtd Inicial', 'Qtd Atual', 'Variação Qtd',
                'Valor Inicial', 'Valor Atual', 'Variação Valor',
                'Total Movimentações', 'Data Cálculo'
            ])
            
            # Dados
            for produto in estoque_atual.values():
                writer.writerow([
                    produto['produto_id'],
                    produto['nome'],
                    produto['referencia'],
                    f"{produto['quantidade_inicial']:.3f}",
                    f"{produto['quantidade_atual']:.3f}",
                    f"{produto['quantidade_atual'] - produto['quantidade_inicial']:.3f}",
                    f"{produto['valor_inicial']:.2f}",
                    f"{produto['valor_atual']:.2f}",
                    f"{produto['valor_atual'] - produto['valor_inicial']:.2f}",
                    produto['total_movimentacoes'],
                    produto['data_calculo'].strftime('%d/%m/%Y')
                ])

def main():
    """Função principal"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Controle de Estoque com Movimentações')
    parser.add_argument('--data', type=str, help='Data final (YYYY-MM-DD)', default=None)
    parser.add_argument('--produto', type=int, help='ID de produto específico', default=None)
    
    args = parser.parse_args()
    
    # Converte data se fornecida
    data_final = None
    if args.data:
        try:
            data_final = datetime.strptime(args.data, '%Y-%m-%d').date()
        except ValueError:
            print("❌ Formato de data inválido. Use YYYY-MM-DD")
            return
    
    controle = ControleEstoque()
    
    if args.produto:
        # Relatório de produto específico
        print(f"🔍 Analisando produto ID {args.produto}...")
        controle.carregar_estoque_inicial()
        controle.carregar_movimentacoes(data_final)
        estoque = controle.calcular_estoque_atual(data_final)
        
        if args.produto in estoque:
            produto = estoque[args.produto]
            print(f"\n📦 PRODUTO: {produto['nome']}")
            print(f"Referência: {produto['referencia']}")
            print(f"Quantidade inicial: {produto['quantidade_inicial']:.3f}")
            print(f"Quantidade atual: {produto['quantidade_atual']:.3f}")
            print(f"Movimentações: {produto['total_movimentacoes']}")
            print(f"Valor inicial: R$ {produto['valor_inicial']:.2f}")
            print(f"Valor atual: R$ {produto['valor_atual']:.2f}")
        else:
            print(f"❌ Produto {args.produto} não encontrado no estoque inicial")
    else:
        # Relatório geral
        controle.gerar_relatorio(data_final)

if __name__ == "__main__":
    main()
