
import os
import django
from datetime import date
from django.db.models import Sum
from collections import defaultdict
from decimal import Decimal

# Setup Django
import sys
sys.path.append(r'c:\Users\Cirilo\Documents\programas\empresa\backend\empresa')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'empresa.settings')
django.setup()

from contas.models.access import (
    ItensNfEntrada, ItensNfSaida, MovimentacoesEstoque, Produtos
)

def analyze_jan_2026():
    data_inicio = date(2026, 1, 1)
    data_fim = date(2026, 1, 31)
    
    print(f"--- Analyzing Stock Comparing: {data_inicio} to {data_fim} ---")

    # 1. Fiscal Data
    print("\n[Fiscal] Calculating...")
    entradas_nf = ItensNfEntrada.objects.filter(
        nota_fiscal__data_entrada__range=[data_inicio, data_fim]
    ).values('produto_id').annotate(total_qtd=Sum('quantidade'), total_val=Sum('valor_total'))
    
    saidas_nf = ItensNfSaida.objects.filter(
        nota_fiscal__data__range=[data_inicio, data_fim]
    ).values('produto_id').annotate(total_qtd=Sum('quantidade'), total_val=Sum('valor_total'))
    
    fiscal_map = defaultdict(lambda: {'entrada': 0, 'saida': 0, 'val_entrada': 0, 'val_saida': 0})
    
    for x in entradas_nf:
        if x['produto_id']:
            fiscal_map[x['produto_id']]['entrada'] = x['total_qtd'] or 0
            fiscal_map[x['produto_id']]['val_entrada'] = x['total_val'] or 0
            
    for x in saidas_nf:
        if x['produto_id']:
            fiscal_map[x['produto_id']]['saida'] = x['total_qtd'] or 0
            fiscal_map[x['produto_id']]['val_saida'] = x['total_val'] or 0

    # 3. Valuation (Mimic View Logic)
    print("\n[Valuation Logic]")
    # Calculate Average Price from Fiscal Entries
    avg_prices = {}
    for pid, vals in fiscal_map.items():
        qty = vals['entrada']
        val = vals['val_entrada']
        if qty > 0:
            avg_prices[pid] = val / qty
            
    # Fallback to Product Cost
    prod_costs = {p.id: p.preco_custo for p in Produtos.objects.filter(id__in=all_pids)}
    
    # Calculate Physical Values using Logic
    view_physical_map = defaultdict(lambda: {'entrada': 0, 'saida': 0, 'val_entrada': 0, 'val_saida': 0})
    
    for pid, vals in physical_map.items():
        qty_ent = vals['entrada']
        qty_sai = vals['saida']
        
        # Determine cost ref
        if pid in avg_prices:
            custo_ref = avg_prices[pid]
            source = "AvgFiscal"
        else:
            custo_ref = prod_costs.get(pid) or Decimal(0)
            source = "ProdCost"
            
        view_physical_map[pid]['entrada'] = qty_ent
        view_physical_map[pid]['saida'] = qty_sai
        view_physical_map[pid]['val_entrada'] = qty_ent * custo_ref
        view_physical_map[pid]['val_saida'] = qty_sai * custo_ref
        
        if pid == 6474:
             print(f"Product 6474 Debug:")
             print(f"  Fiscal Qty: {fiscal_map[pid]['entrada']}, Val: {fiscal_map[pid]['val_entrada']}")
             print(f"  Avg Price: {avg_prices.get(pid)}")
             print(f"  Prod Cost: {prod_costs.get(pid)}")
             print(f"  Used Source: {source}, Custo Ref: {custo_ref}")
             print(f"  Physical Qty: {qty_ent}")
             print(f"  Calc Val: {view_physical_map[pid]['val_entrada']}")

    # 4. Compare View Logic vs Fiscal
    total_fiscal_variation = 0
    total_view_physical_variation = 0
    
    discrepancies = []
    
    for pid in all_pids:
        f = fiscal_map[pid]
        p = view_physical_map[pid]
        
        fiscal_var_val = f['val_entrada'] - f['val_saida']
        physical_var_val = p['val_entrada'] - p['val_saida']
        
        total_fiscal_variation += fiscal_var_val
        total_view_physical_variation += physical_var_val
        
        diff_val = fiscal_var_val - physical_var_val
        
        if abs(diff_val) > 0.01: 
            discrepancies.append({
                'id': pid,
                'nome': products.get(pid, 'Unknown'),
                'fiscal': f,
                'physical': p,
                'diff': diff_val
            })

    with open('debug_result_utf8.txt', 'w', encoding='utf-8') as f:
        f.write(f"--- Analyzing Stock Comparing: {data_inicio} to {data_fim} ---\n")
        f.write(f"\n[Totals - View Logic]\n")
        f.write(f"Total Fiscal Variation (Val): R$ {total_fiscal_variation:,.2f}\n")
        f.write(f"Total Physical Variation (Val): R$ {total_view_physical_variation:,.2f}\n")
        f.write(f"Difference: R$ {total_fiscal_variation - total_view_physical_variation:,.2f}\n")
        
        f.write("\n[Top Discrepancies (Fiscal - ViewPhysical)]\n")
        for d in discrepancies[:10]:
            f.write(f"\nProduct: {d['nome']} ({d['id']})\n")
            f.write(f"  Fiscal: Ent R${d['fiscal']['val_entrada']:,.2f} - Sai R${d['fiscal']['val_saida']:,.2f} = Var R${d['fiscal']['val_entrada'] - d['fiscal']['val_saida']:,.2f}\n")
            f.write(f"  Physical: Ent R${d['physical']['val_entrada']:,.2f} - Sai R${d['physical']['val_saida']:,.2f} = Var R${d['physical']['val_entrada'] - d['physical']['val_saida']:,.2f}\n")
            f.write(f"  Diff: R$ {d['diff']:,.2f}\n")
            
    print("Analysis complete. Check debug_result_utf8.txt")

if __name__ == '__main__':
    analyze_jan_2026()
