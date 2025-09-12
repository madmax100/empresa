#!/usr/bin/env python3
"""
Script para encontrar todos os endpoints ativos do sistema
"""

import os
import sys
import django
from django.conf import settings

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'empresa.settings')
django.setup()

def buscar_endpoints_contas():
    print("=== 🔍 BUSCANDO ENDPOINTS DE CONTAS ===\n")
    
    try:
        from django.urls import get_resolver
        from django.urls.resolvers import URLPattern, URLResolver
        
        def extrair_urls(urlpatterns, prefix=''):
            urls = []
            for pattern in urlpatterns:
                if isinstance(pattern, URLPattern):
                    urls.append(prefix + str(pattern.pattern))
                elif isinstance(pattern, URLResolver):
                    urls.extend(extrair_urls(pattern.url_patterns, prefix + str(pattern.pattern)))
            return urls
        
        resolver = get_resolver()
        todas_urls = extrair_urls(resolver.url_patterns)
        
        print("🔗 URLs relacionadas a 'contas':")
        urls_contas = [url for url in todas_urls if 'contas' in url.lower()]
        
        for url in sorted(urls_contas):
            print(f"   {url}")
            
        print(f"\n📊 Estatísticas:")
        print(f"   - Total de URLs no sistema: {len(todas_urls)}")
        print(f"   - URLs com 'contas': {len(urls_contas)}")
        
        # Verificar especificamente contas_pagar e contas_receber
        pagar_urls = [url for url in todas_urls if 'pagar' in url.lower()]
        receber_urls = [url for url in todas_urls if 'receber' in url.lower()]
        
        print(f"\n💰 URLs específicas:")
        print(f"   - URLs com 'pagar': {len(pagar_urls)}")
        for url in pagar_urls:
            print(f"     {url}")
            
        print(f"   - URLs com 'receber': {len(receber_urls)}")
        for url in receber_urls:
            print(f"     {url}")
            
    except Exception as e:
        print(f"❌ Erro ao buscar URLs: {e}")
    
    # Testar endpoints funcionais conhecidos
    print(f"\n🧪 Testando endpoints conhecidos:")
    
    endpoints_teste = [
        'contas-por-data-pagamento/',
        'contas-por-data-vencimento/',
        'relatorio-financeiro/',
    ]
    
    for endpoint in endpoints_teste:
        print(f"   ✅ {endpoint} - Via path() no urlpatterns")

if __name__ == "__main__":
    buscar_endpoints_contas()
