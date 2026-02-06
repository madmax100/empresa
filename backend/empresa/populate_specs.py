
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'empresa.settings')
django.setup()

from django.db.models import Q
from contas.models.access import Fornecedores

# Keywords mapping
KEYWORDS = {
    'ALIMENTAÇÃO': ['REFEIÇÃO', 'REFEICAO', 'COPA', 'RESTAURANTE', 'PIZZARIA', 'ALIMENTOS', 'LANCHE', 'BUFFET'],
    'TRANSPORTE': [
        'TRANSPORTE', 'VIACAO', 'VIAÇÃO', 'CARGAS', 'FRETE', 'COMBUSTIVEL', 'VALE TRANSPORTE', 
        'IPVA', 'DETRAN', 'LICENCIAMENTO', 'PNEUS', 'MECANICA', 'POSTO', 'AUTO PECAS', 'OFICINA', 'ESTACIONAMENTO',
        'LUBRIFICANTES'
    ],
    'ESCRITÓRIO': ['ESCRITORIO', 'PAPELARIA', 'IMPRESSOS', 'COPIADORA', 'INFORMATICA', 'DIGITAL', 'CARTUCHO', 'SISTEMAS'],
    'SERVIÇOS': [
        'SERV.TERCEIROS', 'ADVOGADOS', 'CONTABILIDADE', 'LIMPEZA', 'DEDETIZADORA', 'SEGURANÇA', 'SEGURANCA', 
        'CHAVEIRO', 'SINDICATO', 'CARTORIO', 'CONSULTORIA', 'ASSESSORIA', 'CORREIOS'
    ],
    'FINANCEIRO': ['JUROS', 'TARIFAS', 'BANCO', 'EMPRESTIMO', 'CHEQUE', 'FINANC', 'CAIXA', 'SEGUROS', 'CONSORCIO'],
    'PESSOAL': [
        'FOLHA', 'SALARIO', 'FGTS', 'INSS', 'FERIAS', 'VALE', 'AJUDA CUSTO', 'RESCISAO', 'ADIANTAMENTO', 
        'PROLABORE', 'PRO-LABORE', 'ESTAGIARIO', 'BONIFICACAO'
    ],
    'IMPOSTOS': ['TRIBUTOS', 'DARF', 'DAS', 'IMPOSTO', 'RETENCAO', 'GUIA', 'ISS', 'ICMS', 'PIS', 'COFINS'],
    'UTILIDADES': [
        'AGUA', 'LUZ', 'ENERGIA', 'TELEFONE', 'INTERNET', 'CAGECE', 'COELCE', 'TELEMAR', 'TIM', 'VIVO', 'CLARO', 'OI', 
        'NET', 'SKY'
    ],
    'ALUGUEL': ['ALUGUEL', 'CONDOMINIO', 'IMOBILIARIA', 'PREDIO', 'SALA'],
    'MANUTENÇÃO': ['MANUTENÇÃO', 'MANUTENCAO', 'REPAROS', 'CONSTRUÇÃO', 'CONSTRUCAO', 'MATERIAL', 'ELETRICO', 'HIDRAULICO', 'FERRAGENS'],
    'MERCADORIA': ['DISTRIBUIDORA', 'ATACADO', 'COMERCIO', 'INDUSTRIA', 'LTDA', 'EIRELI', 'ME', 'S.A']
}

def run():
    updated_count = 0
    # Process only those with empty specifications
    suppliers = Fornecedores.objects.filter(Q(especificacao__isnull=True) | Q(especificacao=''))
    
    total = suppliers.count()
    print(f"Found {total} suppliers without specification.")
    
    for s in suppliers:
        name = (s.nome or '').upper()
        found_spec = None
        
        # Try to match keywords (prioritize longer matches or specific categories?)
        # Let's iterate through our categories
        for category, keywords in KEYWORDS.items():
            for kw in keywords:
                if kw in name:
                    found_spec = category
                    break
            if found_spec:
                break
        
        if found_spec:
            s.especificacao = found_spec
            s.save()
            updated_count += 1
            # print(f"Updated '{name}' -> {found_spec}")
        else:
            # Default fallback for leftovers? Maybe 'OUTROS'?
            # For now, leave empty or set to 'OUTROS' if we want to ensure filter has content.
            # Let's set to OUTROS to ensure everything has a category.
            s.especificacao = 'OUTROS'
            s.save()
            updated_count += 1

    print(f"Update complete. {updated_count} suppliers updated.")

if __name__ == '__main__':
    run()
