import os
import django
from datetime import date
from django.db.models import Sum, Count, Case, When, Value, DecimalField, F
from django.db.models.functions import Coalesce, TruncDay

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'empresa.settings')
django.setup()

from contas.models import ContasPagar, ContasReceber

def test_query():
    print("Testing resumo_diario query...")
    data_inicio = date(2025, 1, 1)
    data_fim = date(2025, 1, 31)
    
    try:
        pagar_diario = ContasPagar.objects.annotate(
            data_efetiva=Coalesce('data_pagamento', 'vencimento')
        ).filter(
            data_efetiva__gte=data_inicio,
            data_efetiva__lte=data_fim,
            status='P'
        ).annotate(
            dia=TruncDay('data_efetiva'),
            valor_final=Case(
                When(valor_total_pago__gt=0, then='valor_total_pago'),
                default='valor',
                output_field=DecimalField()
            )
        ).values('dia').annotate(
            total=Sum('valor_final'),
            quantidade=Count('id')
        )
        
        print(f"Query constructed. Executing...")
        results = list(pagar_diario)
        print(f"Success! Got {len(results)} results.")
        for r in results[:3]:
            print(r)

    except Exception as e:
        print(f"CAUGHT EXCEPTION: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_query()
