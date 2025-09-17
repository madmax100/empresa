#!/usr/bin/env python3
"""
Teste do novo cálculo de estoque corrigido
"""

import os
import sys
import django
from datetime import datetime, date

# Configurar Django
sys.path.append('backend/empresa')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'empresa.settings')
django.setup()

from contas.models.access import Produtos
from contas.services.stock_calculation_service import StockCalculationService

def testar_novo_calculo():
    print("=== TESTE DO NOVO CÁLCULO DE ESTOQUE ===\n")
    
    # Testar produto 2867 que tinha diferença
    produto_id = 2867
    produto = Produtos.objects.get(id=produto_id)
    
    print(f"Produto: {produto.codigo} - {produto.nome}")
    print(f"Estoque Atual (importado): {produto.estoque_atual}")
    
    # Testar cálculo para hoje
    calc_hoje = StockCalculationService.calculate_stock_at_date(produto_id, date.today())
    print(f"Estoque Calculado (hoje): {calc_hoje}")
    print(f"Diferença: {float(produto.estoque_atual or 0) - float(calc_hoje)}")
    
    # Testar alguns outros produtos
    print("\n=== TESTE EM OUTROS PRODUTOS ===\n")
    
    produtos_teste = [4673, 5288, 4473, 5129]
    
    for pid in produtos_teste:
        try:
            produto = Produtos.objects.get(id=pid)
            calc = StockCalculationService.calculate_stock_at_date(pid, date.today())
            diferenca = float(produto.estoque_atual or 0) - float(calc)
            
            print(f"Produto {pid}: Estoque={produto.estoque_atual}, Calc={calc}, Dif={diferenca:.2f}")
        except Exception as e:
            print(f"Produto {pid}: ERRO - {e}")

if __name__ == "__main__":
    testar_novo_calculo()