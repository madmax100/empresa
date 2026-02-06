
import os
import sys
import django
from decimal import Decimal
from django.db.models import Sum

sys.path.append(r'c:\Users\Cirilo\Documents\programas\empresa\backend\empresa')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'empresa.settings')
django.setup()

from contas.models.access import ItensNfEntrada, MovimentacoesEstoque, Produtos
from datetime import date

def analyze():
    pid = 6474
    d_ini = date(2026, 1, 1)
    d_fim = date(2026, 1, 31)
    
    print(f"--- Deep Dive Product {pid} ---")
    
    # 1. Fiscal
    nf_items = ItensNfEntrada.objects.filter(nota_fiscal__data_entrada__range=[d_ini, d_fim], produto_id=pid)
    fiscal_qtd = 0
    fiscal_val = 0
    print("\n[Fiscal Records]")
    for item in nf_items:
        print(f"NF: {item.nota_fiscal.numero_nota} | Qtd: {item.quantidade} | Val Unit: {item.valor_unitario} | Val Total: {item.valor_total}")
        fiscal_qtd += item.quantidade or 0
        fiscal_val += item.valor_total or 0
        
    avg_price = fiscal_val / fiscal_qtd if fiscal_qtd else 0
    print(f"Total Fiscal: Qtd {fiscal_qtd} | Val {fiscal_val} | Avg Price {avg_price}")

    # 2. Physical Recorded
    movs = MovimentacoesEstoque.objects.filter(
        data_movimentacao__date__range=[d_ini, d_fim], 
        produto_id=pid,
        tipo_movimentacao__tipo='E'
    )
    
    phys_qtd = 0
    phys_val_recorded = 0
    
    print("\n[Physical Records]")
    for m in movs:
        print(f"Doc: {m.documento_referencia} | Tipo: {m.tipo_movimentacao} | Qtd: {m.quantidade} | Custo Unit: {m.custo_unitario} | Val Total: {m.valor_total}")
        phys_qtd += m.quantidade or 0
        phys_val_recorded += m.valor_total or 0
        
    print(f"Total Physical (Recorded): Qtd {phys_qtd} | Val {phys_val_recorded}")
    
    # 3. View Logic Calculation
    phys_val_calc = phys_qtd * avg_price
    print(f"Total Physical (View Logic): {phys_val_calc} (using Avg Price {avg_price})")
    
    diff_recorded = fiscal_val - phys_val_recorded
    diff_calc = fiscal_val - phys_val_calc
    
    print(f"\n[Comparison]")
    print(f"Fiscal vs Recorded Diff: {diff_recorded}")
    print(f"Fiscal vs Calculated Diff: {diff_calc}")

if __name__ == '__main__':
    with open('debug_final_result.txt', 'w', encoding='utf-8') as f:
        sys.stdout = f
        analyze()
