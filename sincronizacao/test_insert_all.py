
import psycopg2
from datetime import datetime
from decimal import Decimal
from config import PG_CONFIG

try:
    conn = psycopg2.connect(**PG_CONFIG)
    cur = conn.cursor()
    
    # Columns from migrate_nfe.py
    cols = [
        'id', 'numero_nota', 'data_emissao', 'fornecedor_id', 'valor_produtos',
        'base_calculo_icms', 'valor_desconto', 'valor_frete', 'tipo_frete',
        'valor_icms', 'valor_ipi', 'valor_icms_st', 'valor_total', 'forma_pagamento',
        'condicoes_pagamento', 'comprador', 'operador', 'frete_id', 'observacao',
        'outros_encargos', 'parcelas', 'operacao', 'cfop', 'data_entrada',
        'chave_nfe', 'serie_nota', 'protocolo', 'natureza_operacao',
        'base_calculo_st', 'outras_despesas'
    ]
    
    # Dummy data
    data = (
        999999, 'TESTE', datetime.now(), None, Decimal('0'),
        Decimal('0'), Decimal('0'), Decimal('0'), 'T',
        Decimal('0'), Decimal('0'), Decimal('0'), Decimal('0'), 'V',
        'C', 'C', 'O', None, 'Obs',
        Decimal('0'), 'P', 'OP', '1234', datetime.now(),
        'KEY', '1', 'PROT', 'NAT',
        Decimal('0'), Decimal('0')
    )
    
    placeholders = ', '.join(['%s'] * len(cols))
    col_str = ', '.join(cols)
    
    sql = f"INSERT INTO notas_fiscais_entrada ({col_str}) VALUES ({placeholders}) ON CONFLICT (id) DO NOTHING"
    
    print("Executing SQL...")
    cur.execute(sql, data)
    print("Success!")
    
    conn.rollback()

except Exception as e:
    print(f"FAILED: {e}")
finally:
    if 'conn' in locals():
        conn.close()
