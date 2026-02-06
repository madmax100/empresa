
import os
import django
from django.db.models import Count

# Configure Django standalone
import sys
sys.path.append('c:\\Users\\Cirilo\\Documents\\programas\\empresa\\backend\\empresa')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'empresa.settings')
django.setup()

from contas.models.access import ContasReceber, NotasFiscaisSaida

def check_correlation():
    # Get sample valid NFS (not remittances)
    sample_nfs = NotasFiscaisSaida.objects.exclude(
        operacao__icontains='REMESSA'
    ).exclude(
        cfop__startswith='5.9'
    ).values_list('numero_nota', flat=True)[:100]

    # Check matches in CR
    matches = ContasReceber.objects.filter(documento__in=sample_nfs).count()
    
    print(f"Sample size: {len(sample_nfs)}")
    print(f"Matches in CR (by documento): {matches}")
    
    # Check distinct condition of matched vs unmatched
    matched_nfs = NotasFiscaisSaida.objects.filter(numero_nota__in=ContasReceber.objects.values('documento'))
    unmatched_nfs = NotasFiscaisSaida.objects.exclude(numero_nota__in=ContasReceber.objects.values('documento'))
    
    print("\n--- Matched (In CR) Conditions Sample ---")
    for nf in matched_nfs.order_by('-data')[:5]:
        print(f"Nota: {nf.numero_nota}, Cond: {nf.condicoes}, Op: {nf.operacao}")

    print("\n--- Unmatched (Not in CR) Conditions Sample ---")
    for nf in unmatched_nfs.order_by('-data')[:5]:
        print(f"Nota: {nf.numero_nota}, Cond: {nf.condicoes}, Op: {nf.operacao}")

    # Check specific 'A Prazo' unmatched
    prazo_unmatched = unmatched_nfs.filter(condicoes__icontains='PRAZO').count()
    print(f"\nUnmatched NFS with 'PRAZO' in condition: {prazo_unmatched}")

    # Check specific 'A Vista' matched
    vista_matched = matched_nfs.filter(condicoes__icontains='VISTA').count()
    print(f"Matched NFS with 'VISTA' in condition: {vista_matched}")

if __name__ == "__main__":
    check_correlation()
