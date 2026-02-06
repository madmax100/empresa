import os
import django
import json
from django.db.models import Sum

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'empresa.settings')
django.setup()

from contas.models.access import MovimentacoesEstoque

def run():
    start = '2026-02-02'
    end = '2026-02-05'
    qs = MovimentacoesEstoque.objects.filter(
        data_movimentacao__date__range=(start, end), 
        tipo_movimentacao__tipo='E'
    ).values('documento_referencia', 'data_movimentacao__date').annotate(total=Sum('valor_total')).order_by('data_movimentacao__date')

    data = []
    for i in qs:
        data.append({
            'data': str(i['data_movimentacao__date']),
            'doc': i['documento_referencia'],
            'valor': float(i['total'])
        })
    print(json.dumps(data))

if __name__ == '__main__':
    run()
