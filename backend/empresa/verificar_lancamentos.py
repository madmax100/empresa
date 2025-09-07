#!/usr/bin/env python
"""
Script para verificar os dados do FluxoCaixaLancamento
"""
import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'empresa.settings')
django.setup()

from contas.models.fluxo_caixa import FluxoCaixaLancamento
from datetime import date, datetime

def verificar_lancamentos():
    """Verifica os lançamentos existentes"""
    print("🔍 ANÁLISE DOS LANÇAMENTOS DE FLUXO DE CAIXA")
    print("="*60)
    
    total = FluxoCaixaLancamento.objects.count()
    print(f"Total de lançamentos: {total}")
    
    if total == 0:
        print("❌ Não há lançamentos na base de dados!")
        return
    
    print("\n📊 Lançamentos por status:")
    realizados = FluxoCaixaLancamento.objects.filter(realizado=True).count()
    nao_realizados = FluxoCaixaLancamento.objects.filter(realizado=False).count()
    print(f"- Realizados: {realizados}")
    print(f"- Não realizados: {nao_realizados}")
    
    print("\n📊 Lançamentos por tipo:")
    entradas = FluxoCaixaLancamento.objects.filter(tipo='entrada').count()
    saidas = FluxoCaixaLancamento.objects.filter(tipo='saida').count()
    print(f"- Entradas: {entradas}")
    print(f"- Saídas: {saidas}")
    
    print("\n📅 Lançamentos mais recentes:")
    for lancamento in FluxoCaixaLancamento.objects.order_by('-data')[:5]:
        status = "✅ Realizado" if lancamento.realizado else "⏳ Pendente"
        print(f"- {lancamento.data}: {lancamento.tipo.upper()} R$ {lancamento.valor}")
        print(f"  {lancamento.descricao} ({status})")
    
    print("\n📅 Range de datas:")
    primeira_data = FluxoCaixaLancamento.objects.order_by('data').first()
    ultima_data = FluxoCaixaLancamento.objects.order_by('-data').first()
    
    if primeira_data and ultima_data:
        print(f"- Primeira data: {primeira_data.data}")
        print(f"- Última data: {ultima_data.data}")
        
        # Verificar se há dados no período atual do dashboard
        hoje = date.today()
        print(f"\n📊 Lançamentos a partir de hoje ({hoje}):")
        lancamentos_futuros = FluxoCaixaLancamento.objects.filter(data__gte=hoje).count()
        print(f"- Total: {lancamentos_futuros}")
        
        if lancamentos_futuros == 0:
            print("❌ Não há lançamentos para o período atual do dashboard!")
            print("   O dashboard está mostrando zeros porque não há dados futuros.")
            
            print("\n💡 SOLUÇÕES:")
            print("1. Criar lançamentos de teste para o período atual")
            print("2. Modificar o período do dashboard para incluir dados históricos")
            print("3. Importar dados reais se existirem")

def criar_lancamentos_teste():
    """Cria alguns lançamentos de teste"""
    print("\n🔧 CRIANDO LANÇAMENTOS DE TESTE...")
    
    from decimal import Decimal
    
    # Lançamentos para o período atual
    lancamentos_teste = [
        {
            'data': date(2025, 9, 10),
            'tipo': 'entrada',
            'valor': Decimal('1500.00'),
            'descricao': 'Venda de produtos - Teste',
            'categoria': 'vendas',
            'realizado': True
        },
        {
            'data': date(2025, 9, 15),
            'tipo': 'saida',
            'valor': Decimal('800.00'),
            'descricao': 'Compra de materiais - Teste',
            'categoria': 'compras',
            'realizado': True
        },
        {
            'data': date(2025, 9, 20),
            'tipo': 'entrada',
            'valor': Decimal('2000.00'),
            'descricao': 'Prestação de serviço - Teste',
            'categoria': 'servicos',
            'realizado': False
        },
        {
            'data': date(2025, 10, 5),
            'tipo': 'saida',
            'valor': Decimal('1200.00'),
            'descricao': 'Pagamento de fornecedor - Teste',
            'categoria': 'despesas',
            'realizado': False
        },
        {
            'data': date(2025, 10, 15),
            'tipo': 'entrada',
            'valor': Decimal('3000.00'),
            'descricao': 'Recebimento de cliente - Teste',
            'categoria': 'vendas',
            'realizado': False
        }
    ]
    
    created_count = 0
    for dados in lancamentos_teste:
        lancamento, created = FluxoCaixaLancamento.objects.get_or_create(
            data=dados['data'],
            tipo=dados['tipo'],
            descricao=dados['descricao'],
            defaults=dados
        )
        
        if created:
            created_count += 1
            print(f"✅ Criado: {dados['data']} - {dados['tipo']} R$ {dados['valor']}")
    
    print(f"\n🎉 {created_count} lançamentos de teste criados!")
    print("Agora o dashboard deve mostrar dados.")

if __name__ == "__main__":
    verificar_lancamentos()
    
    resposta = input("\n❓ Deseja criar lançamentos de teste? (s/n): ")
    if resposta.lower() in ['s', 'sim', 'y', 'yes']:
        criar_lancamentos_teste()
        print("\n✅ Processo concluído! Teste o dashboard novamente.")
    else:
        print("\n📝 Para criar dados manualmente, use o admin do Django ou crie via shell.")
