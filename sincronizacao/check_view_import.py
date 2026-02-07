
import os
import sys
sys.path.append(r'c:\Users\Cirilo\Documents\programas\empresa\backend\empresa')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'empresa.settings')
import django
django.setup()

try:
    from contas.views.fluxo_caixa_realizado import FluxoCaixaRealizadoViewSet
    print("Import successful")
except Exception as e:
    print(f"Import failed: {e}")
