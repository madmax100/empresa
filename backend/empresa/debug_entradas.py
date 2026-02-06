import os
import django
from django.conf import settings
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

    print('--- RELATORIO DE ENTRADAS ---')
    total_geral = 0
    for i in qs:
        print(f"Data: {i['data_movimentacao__date']} | Doc: {i['documento_referencia']} | R$ {i['total']}")
        total_geral += i['total']
    print(f'TOTAL GERAL: R$ {total_geral}')
    print('--- FIM DO RELATORIO ---')

if __name__ == '__main__':
    run()
