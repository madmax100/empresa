#!/usr/bin/env python3
"""
Script para testar os endpoints de contas a pagar e contas a receber
"""

import os
import sys
import django
from django.conf import settings

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'empresa.settings')
django.setup()

def testar_endpoints():
    print("=== 📋 ENDPOINTS DE CONTAS A PAGAR E CONTAS A RECEBER ===\n")
    
    # Importar depois do setup do Django
    from contas.views.access import ContasPagarViewSet, ContasReceberViewSet
    from rest_framework.routers import DefaultRouter
    
    # Testar se os ViewSets existem
    print("✅ ViewSets encontrados:")
    print(f"   - ContasPagarViewSet: {ContasPagarViewSet}")
    print(f"   - ContasReceberViewSet: {ContasReceberViewSet}")
    
    # Simular registro no router
    router = DefaultRouter()
    router.register(r'contas_pagar', ContasPagarViewSet)
    router.register(r'contas_receber', ContasReceberViewSet)
    
    print(f"\n🔗 Endpoints gerados pelo Router:")
    for pattern in router.urls:
        print(f"   {pattern.pattern}")
    
    # Verificar URLs atuais do projeto
    print(f"\n📁 Verificando arquivo de URLs atual...")
    
    try:
        from django.urls import get_resolver
        resolver = get_resolver()
        
        print(f"\n🔍 URLs relacionadas a 'contas':")
        for url_pattern in resolver.url_patterns:
            if hasattr(url_pattern, 'pattern'):
                pattern_str = str(url_pattern.pattern)
                if 'contas' in pattern_str.lower():
                    print(f"   {pattern_str}")
        
    except Exception as e:
        print(f"   Erro ao verificar URLs: {e}")
    
    # Testar acesso aos modelos
    from contas.models.access import ContasPagar, ContasReceber
    
    print(f"\n📊 Dados nos modelos:")
    print(f"   - ContasPagar: {ContasPagar.objects.count()} registros")
    print(f"   - ContasReceber: {ContasReceber.objects.count()} registros")

if __name__ == "__main__":
    testar_endpoints()
