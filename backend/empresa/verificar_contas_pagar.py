#!/usr/bin/env python
"""
Script para verificar dados na tabela ContasPagar
"""
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'empresa.settings')
django.setup()

from contas.models.access import Fornecedores, ContasPagar
from datetime import datetime, date, timedelta
from django.db.models import Q, Sum, Count, Min, Max

def verificar_contas_pagar():
    """Verifica dados na tabela ContasPagar"""
    
    print("🔍 ANÁLISE DA TABELA CONTAS A PAGAR")
    print("="*50)
    
    # 1. Total de registros
    total_contas = ContasPagar.objects.count()
    print(f"📊 Total de contas na base: {total_contas}")
    
    if total_contas > 0:
        # 2. Período dos dados
        periodo = ContasPagar.objects.aggregate(
            data_min=Min('data'),
            data_max=Max('data'),
            venc_min=Min('vencimento'),
            venc_max=Max('vencimento'),
            pag_min=Min('data_pagamento'),
            pag_max=Max('data_pagamento')
        )
        
        print(f"\n📅 PERÍODO DOS DADOS:")
        print(f"  - Emissão: {periodo['data_min']} até {periodo['data_max']}")
        print(f"  - Vencimento: {periodo['venc_min']} até {periodo['venc_max']}")
        print(f"  - Pagamento: {periodo['pag_min']} até {periodo['pag_max']}")
        
        # 3. Status das contas
        status_dist = ContasPagar.objects.values('status').annotate(
            quantidade=Count('id'),
            valor_total=Sum('valor')
        ).order_by('-quantidade')
        
        print(f"\n📋 DISTRIBUIÇÃO POR STATUS:")
        for item in status_dist:
            status_nome = dict(ContasPagar.STATUS_CHOICES).get(item['status'], item['status'])
            qtd = item['quantidade']
            valor = item['valor_total'] or 0
            print(f"  - {status_nome}: {qtd} contas (R$ {valor:,.2f})")
        
        # 4. Contas com fornecedor
        com_fornecedor = ContasPagar.objects.filter(fornecedor__isnull=False).count()
        sem_fornecedor = ContasPagar.objects.filter(fornecedor__isnull=True).count()
        
        print(f"\n🏢 FORNECEDORES:")
        print(f"  - Contas com fornecedor: {com_fornecedor}")
        print(f"  - Contas sem fornecedor: {sem_fornecedor}")
        
        # 5. Contas pagas
        contas_pagas = ContasPagar.objects.filter(status='P')
        total_pagas = contas_pagas.count()
        valor_total_pago = contas_pagas.aggregate(total=Sum('valor_total_pago'))['total'] or 0
        
        print(f"\n💰 CONTAS PAGAS:")
        print(f"  - Quantidade: {total_pagas}")
        print(f"  - Valor total pago: R$ {valor_total_pago:,.2f}")
        
        if total_pagas > 0:
            # Contas pagas com data de pagamento
            pagas_com_data = contas_pagas.filter(data_pagamento__isnull=False).count()
            print(f"  - Com data de pagamento: {pagas_com_data}")
            
            # Últimas contas pagas
            ultimas_pagas = contas_pagas.filter(
                data_pagamento__isnull=False
            ).select_related('fornecedor').order_by('-data_pagamento')[:5]
            
            if ultimas_pagas:
                print(f"\n💳 ÚLTIMAS 5 CONTAS PAGAS:")
                for i, conta in enumerate(ultimas_pagas, 1):
                    data_pag = conta.data_pagamento.strftime('%Y-%m-%d') if conta.data_pagamento else 'N/A'
                    valor = conta.valor_total_pago or conta.valor_pago or conta.valor
                    fornecedor = conta.fornecedor.nome if conta.fornecedor else 'SEM FORNECEDOR'
                    tipo_fornecedor = conta.fornecedor.tipo if conta.fornecedor and conta.fornecedor.tipo else 'SEM TIPO'
                    historico = conta.historico[:50] if conta.historico else 'N/A'
                    print(f"  {i}. {data_pag} - R$ {valor:,.2f} - {fornecedor} ({tipo_fornecedor})")
                    print(f"     {historico}...")
        
        # 6. Verificar fornecedores com tipos fixos
        print(f"\n🔍 VERIFICANDO FORNECEDORES COM TIPOS FIXOS:")
        
        fornecedores_fixos = Fornecedores.objects.filter(
            Q(tipo__icontains='DESPESA FIXA') | Q(tipo__icontains='CUSTO FIXO')
        )
        
        print(f"  - Fornecedores com tipos fixos: {fornecedores_fixos.count()}")
        
        # Contas desses fornecedores
        contas_fornecedores_fixos = ContasPagar.objects.filter(
            fornecedor__in=fornecedores_fixos
        )
        
        total_contas_fixos = contas_fornecedores_fixos.count()
        contas_pagas_fixos = contas_fornecedores_fixos.filter(status='P').count()
        
        print(f"  - Total de contas desses fornecedores: {total_contas_fixos}")
        print(f"  - Contas pagas desses fornecedores: {contas_pagas_fixos}")
        
        if contas_pagas_fixos > 0:
            valor_pago_fixos = contas_fornecedores_fixos.filter(status='P').aggregate(
                total=Sum('valor_total_pago')
            )['total'] or 0
            
            print(f"  - Valor total pago para fornecedores fixos: R$ {valor_pago_fixos:,.2f}")
            
            # Exemplos
            exemplos_fixos = contas_fornecedores_fixos.filter(
                status='P', 
                data_pagamento__isnull=False
            ).select_related('fornecedor').order_by('-data_pagamento')[:3]
            
            if exemplos_fixos:
                print(f"\n📋 EXEMPLOS DE CONTAS PAGAS DE FORNECEDORES FIXOS:")
                for i, conta in enumerate(exemplos_fixos, 1):
                    data_pag = conta.data_pagamento.strftime('%Y-%m-%d')
                    valor = conta.valor_total_pago or conta.valor_pago or conta.valor
                    fornecedor = conta.fornecedor.nome
                    tipo = conta.fornecedor.tipo
                    print(f"  {i}. {data_pag} - R$ {valor:,.2f} - {fornecedor} ({tipo})")
    
    print("\n" + "="*50)
    print("✅ ANÁLISE CONCLUÍDA!")

if __name__ == "__main__":
    verificar_contas_pagar()
