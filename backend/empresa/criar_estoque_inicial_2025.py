#!/usr/bin/env python3
"""
SCRIPT PARA CRIAR ESTOQUE INICIAL DE 2025
Cria estoque inicial de 10 unidades para todos os produtos movimentados em 2025
"""

import os
import sys
import django

# Configuração do Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'empresa.settings')
django.setup()

from contas.models.access import MovimentacoesEstoque, Produtos, TiposMovimentacaoEstoque
from datetime import datetime, date
from decimal import Decimal

def criar_estoque_inicial():
    """Cria estoque inicial para produtos movimentados em 2025"""
    
    print("🔄 CRIANDO ESTOQUE INICIAL PARA PRODUTOS MOVIMENTADOS EM 2025")
    print("=" * 70)
    
    # 1. Busca produtos movimentados em 2025
    produtos_2025_ids = MovimentacoesEstoque.objects.filter(
        data_movimentacao__year=2025
    ).values_list('produto_id', flat=True).distinct()
    
    produtos_unicos = list(set([pid for pid in produtos_2025_ids if pid]))
    print(f"📦 Produtos encontrados: {len(produtos_unicos)}")
    
    # 2. Verifica se já existe estoque inicial
    estoque_inicial_existente = MovimentacoesEstoque.objects.filter(
        documento_referencia='EST_INICIAL_2025'
    ).count()
    
    if estoque_inicial_existente > 0:
        print(f"⚠️  Já existem {estoque_inicial_existente} registros de estoque inicial!")
        resposta = input("Deseja continuar e sobrescrever? (s/n): ")
        if resposta.lower() != 's':
            print("❌ Operação cancelada")
            return
        
        # Remove estoque inicial existente
        MovimentacoesEstoque.objects.filter(
            documento_referencia='EST_INICIAL_2025'
        ).delete()
        print("🗑️  Estoque inicial anterior removido")
    
    # 3. Busca ou cria tipo de movimentação
    try:
        tipo_estoque_inicial = TiposMovimentacaoEstoque.objects.get(id=3)
        print(f"✅ Tipo de movimentação encontrado: {tipo_estoque_inicial}")
    except TiposMovimentacaoEstoque.DoesNotExist:
        print("❌ Tipo de movimentação 'Estoque Inicial' (ID=3) não encontrado")
        return
    
    # 4. Configurações do estoque inicial
    data_inicial = datetime(2025, 1, 1, 0, 0, 0)
    quantidade_inicial = Decimal('10.0')
    custo_unitario_padrao = Decimal('50.0')  # R$ 50,00 por unidade
    
    # 5. Cria estoque inicial para cada produto
    registros_criados = 0
    erros = 0
    
    print(f"\n🚀 Criando estoque inicial...")
    print(f"📅 Data: {data_inicial.strftime('%d/%m/%Y')}")
    print(f"📦 Quantidade por produto: {quantidade_inicial}")
    print(f"💰 Custo unitário padrão: R$ {custo_unitario_padrao}")
    print("-" * 50)
    
    for i, produto_id in enumerate(produtos_unicos, 1):
        try:
            # Verifica se produto existe
            try:
                produto = Produtos.objects.get(id=produto_id)
                nome_produto = produto.nome[:30] + "..." if len(produto.nome) > 30 else produto.nome
            except Produtos.DoesNotExist:
                print(f"⚠️  Produto ID {produto_id} não encontrado, pulando...")
                erros += 1
                continue
            
            # Calcula valor total
            valor_total = quantidade_inicial * custo_unitario_padrao
            
            # Cria movimentação de estoque inicial
            movimentacao = MovimentacoesEstoque.objects.create(
                data_movimentacao=data_inicial,
                tipo_movimentacao=tipo_estoque_inicial,
                produto_id=produto_id,
                quantidade=quantidade_inicial,
                custo_unitario=custo_unitario_padrao,
                valor_total=valor_total,
                documento_referencia='EST_INICIAL_2025',
                observacoes=f'Estoque inicial criado automaticamente para produtos movimentados em 2025'
            )
            
            registros_criados += 1
            
            # Progress
            if i % 50 == 0 or i == len(produtos_unicos):
                print(f"📦 Processado: {i}/{len(produtos_unicos)} - {nome_produto}")
        
        except Exception as e:
            print(f"❌ Erro ao criar estoque para produto {produto_id}: {str(e)}")
            erros += 1
            continue
    
    # 6. Relatório final
    print("\n" + "=" * 70)
    print("📊 RELATÓRIO FINAL")
    print("=" * 70)
    print(f"✅ Registros criados: {registros_criados}")
    print(f"❌ Erros: {erros}")
    print(f"💰 Valor total do estoque inicial: R$ {registros_criados * quantidade_inicial * custo_unitario_padrao:,.2f}")
    
    if registros_criados > 0:
        print("\n🎉 ESTOQUE INICIAL CRIADO COM SUCESSO!")
        print("\n📋 Próximos passos:")
        print("1. Testar endpoint: /contas/estoque-controle/estoque_atual/")
        print("2. Verificar produtos com estoque zerado")
        print("3. Validar cálculos de movimentação")
    else:
        print("\n❌ NENHUM REGISTRO FOI CRIADO")

def verificar_resultado():
    """Verifica o resultado da criação do estoque inicial"""
    print("\n🔍 VERIFICANDO RESULTADO...")
    
    # Conta registros criados
    total_estoque_inicial = MovimentacoesEstoque.objects.filter(
        documento_referencia='EST_INICIAL_2025'
    ).count()
    
    print(f"📦 Total de registros de estoque inicial: {total_estoque_inicial}")
    
    if total_estoque_inicial > 0:
        # Mostra alguns exemplos
        exemplos = MovimentacoesEstoque.objects.filter(
            documento_referencia='EST_INICIAL_2025'
        ).select_related('produto')[:3]
        
        print("\n📋 Exemplos criados:")
        for mov in exemplos:
            produto_nome = mov.produto.nome[:20] if mov.produto else f"ID {mov.produto_id}"
            print(f"- Produto: {produto_nome} | Qtd: {mov.quantidade} | Valor: R$ {mov.valor_total}")

if __name__ == '__main__':
    try:
        criar_estoque_inicial()
        verificar_resultado()
    except KeyboardInterrupt:
        print("\n\n⚠️  Operação interrompida pelo usuário")
    except Exception as e:
        print(f"\n❌ Erro geral: {str(e)}")
        import traceback
        traceback.print_exc()
