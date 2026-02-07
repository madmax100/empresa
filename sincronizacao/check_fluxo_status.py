
import os
import django
from datetime import date
import sys

# Setup Django
sys.path.append(r"c:\Users\Cirilo\Documents\programas\empresa\backend\empresa")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "empresa.settings")
django.setup()

from contas.models.fluxo_caixa import FluxoCaixaLancamento
from contas.models.access import NotasFiscaisEntrada, NotasFiscaisSaida, ContasPagar, ContasReceber
from contas.views.fluxo_caixa2 import FluxoCaixaViewSet

def check_status():
    start = date(2025, 1, 1)
    end = date(2025, 12, 31)
    
    print(f"Checking FluxoCaixaLancamento for {start} to {end}...")
    
    count_fluxo = FluxoCaixaLancamento.objects.filter(data__range=[start, end]).count()
    print(f"Total FluxoCaixaLancamento (Pre-Sync): {count_fluxo}")
    
    # Always check sources and sync for verification
    count_nfe = NotasFiscaisEntrada.objects.filter(data_emissao__range=[start, end]).count()
    count_nfs = NotasFiscaisSaida.objects.filter(data__range=[start, end]).count()
    count_cp = ContasPagar.objects.filter(vencimento__range=[start, end]).count()
    count_cr = ContasReceber.objects.filter(vencimento__range=[start, end]).count()
    
    print(f"NFe (Source): {count_nfe}")
    print(f"NFS (Source): {count_nfs}")
    print(f"CP (Source): {count_cp}")
    print(f"CR (Source): {count_cr}")
    
    print("\nRunning synchronization manually...")
    view = FluxoCaixaViewSet()
    try:
        view._sincronizar_contas_com_fluxo(start, end)
        print("Synchronization method executed.")
        
        count_fluxo_after = FluxoCaixaLancamento.objects.filter(data__range=[start, end]).count()
        print(f"Total FluxoCaixaLancamento AFTER sync: {count_fluxo_after}")
    except Exception as e:
        print(f"Error executing sync: {e}")
        import traceback
        traceback.print_exc()

    print("Distribution by source:")
    for tipo in ['nfe', 'nfs', 'contas_pagar', 'contas_receber']:
        c = FluxoCaixaLancamento.objects.filter(data__range=[start, end], fonte_tipo=tipo).count()
        print(f"  {tipo}: {c}")

if __name__ == "__main__":
    check_status()
