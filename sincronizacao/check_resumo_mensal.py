
import os
import sys
import json
from decimal import Decimal

sys.path.append(r'c:\Users\Cirilo\Documents\programas\empresa\backend\empresa')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'empresa.settings')

import django
django.setup()

from rest_framework.test import APIRequestFactory
from contas.views.fluxo_caixa_realizado import FluxoCaixaRealizadoViewSet

def check():
    factory = APIRequestFactory()
    view = FluxoCaixaRealizadoViewSet.as_view({'get': 'resumo_mensal'})
    
    # Request for 2025
    request = factory.get('/api/fluxo-caixa-realizado/resumo_mensal/', {
        'data_inicio': '2025-01-01',
        'data_fim': '2025-12-31'
    })
    
    response = view(request)
    
    print("Status Code:", response.status_code)
    if response.status_code == 200:
        data = response.data
        print("\n--- TOTAIS 2025 ---")
        print(json.dumps(data['totais'], indent=2, default=str))
        
        print("\n--- MESES (First 3) ---")
        for mes in data['meses'][:3]:
            print(json.dumps(mes, indent=2, default=str))
            
        # Verify Total Outflows matches Realizado (approx 845k)
        total_saidas = data['totais']['total_saidas']
        print(f"\nTotal Saídas: {total_saidas}")
        
        # Expected around 845,851.68
        if abs(float(total_saidas) - 845851.68) < 1.0:
            print("SUCCESS: Matches expected Realizado total!")
        else:
            print(f"WARNING: Mismatch! Expected ~845,851.68")

if __name__ == '__main__':
    check()
