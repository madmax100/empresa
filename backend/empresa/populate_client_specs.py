
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'empresa.settings')
django.setup()

from django.db.models import Q
from contas.models.access import Clientes

# Keywords mapping for Clients
# Categories: 'GOVERNO', 'EMPRESA', 'EDUCAÇÃO', 'SAÚDE', 'PESSOA FÍSICA', 'OUTROS'
KEYWORDS = {
    'GOVERNO': [
        'MUNICIPIO', 'PREFEITURA', 'SECRETARIA', 'ESTADO', 'CAMARA', 'FUNDO', 'FUNDO MUNICIPAL', 
        'FUNDO ESTADUAL', 'CONSELHO', 'MINISTERIO', 'TRIBUNAL', 'ASSOCIACAO', 'SINDICATO'
    ],
    'EDUCAÇÃO': [
        'ESCOLA', 'COLEGIO', 'EDUCACIONAL', 'ENSINO', 'FACULDADE', 'UNIVERSIDADE', 'INSTITUTO', 
        'CENTRO EDUCACIONAL', 'CRECHE'
    ],
    'SAÚDE': [
        'HOSPITAL', 'CLINICA', 'SAUDE', 'FARMACIA', 'LABORATORIO', 'DENTISTA', 'MEDICO'
    ],
    'EMPRESA': [
        'LTDA', 'S.A.', 'S/A', 'ME', 'EPP', 'EIRELI', 'COMERCIO', 'INDUSTRIA', 'SERVICOS', 
        'SUPERMERCADO', 'POSTO', 'AUTO', 'CONST', 'ENGENHARIA', 'TRANSPORTE'
    ]
}

def run():
    updated_count = 0
    clients = Clientes.objects.all()
    
    total = clients.count()
    print(f"Processing {total} clients...")
    
    for c in clients:
        name = (c.nome or '').upper()
        found_spec = None
        
        # Check specific keywords
        for category, keywords in KEYWORDS.items():
            for kw in keywords:
                if kw in name:
                    found_spec = category
                    break
            if found_spec:
                break
        
        # Fallback logic
        if not found_spec:
            # If name has 3+ parts and no company keywords, assume Person?
            # Or assume 'OUTROS' if uncertain.
            # Usually simple names are Persons.
            # Let's check 'tipo_pessoa' if available/reliable (it defaults to 'F' in model)
            if c.tipo_pessoa == 'F':
                found_spec = 'PESSOA FÍSICA'
            else:
                found_spec = 'EMPRESA' # Default fallback for others if not matched
        
        if c.especificacao != found_spec:
            c.especificacao = found_spec
            c.save()
            updated_count += 1

    print(f"Update complete. {updated_count} clients updated.")

if __name__ == '__main__':
    run()
