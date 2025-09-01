#!/usr/bin/env python
import os
import sys
import django

# Configurar o Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'empresa.settings')
django.setup()

from django.db import connection

def detailed_future_accounts():
    """Mostra detalhes das contas a receber com vencimento futuro"""
    
    with connection.cursor() as cursor:
        # Buscar todas as contas com vencimento após agosto de 2025
        cursor.execute("""
            SELECT 
                id,
                documento,
                data,
                valor,
                vencimento,
                historico,
                status,
                cliente_id
            FROM contas_receber 
            WHERE vencimento > '2025-08-31'
            ORDER BY vencimento DESC
        """)
        
        contas = cursor.fetchall()
        
        print("=== CONTAS A RECEBER COM VENCIMENTO APÓS 31/08/2025 ===")
        print(f"Total: {len(contas)} contas\n")
        
        for conta in contas:
            id_conta, documento, data, valor, vencimento, historico, status, cliente_id = conta
            print(f"ID: {id_conta}")
            print(f"Documento: {documento}")
            print(f"Data emissão: {data}")
            print(f"Vencimento: {vencimento}")
            print(f"Valor: R$ {valor}")
            print(f"Cliente ID: {cliente_id}")
            print(f"Status: {status}")
            print(f"Histórico: {historico[:100] if historico else 'N/A'}{'...' if historico and len(historico) > 100 else ''}")
            print("-" * 50)
            
        # Verificar também a distribuição por mês
        print("\n=== DISTRIBUIÇÃO POR MÊS/ANO ===")
        cursor.execute("""
            SELECT 
                EXTRACT(YEAR FROM vencimento) as ano,
                EXTRACT(MONTH FROM vencimento) as mes,
                COUNT(*) as quantidade,
                SUM(valor) as valor_total
            FROM contas_receber 
            WHERE vencimento > '2025-08-31'
            GROUP BY EXTRACT(YEAR FROM vencimento), EXTRACT(MONTH FROM vencimento)
            ORDER BY ano, mes
        """)
        
        distribuicao = cursor.fetchall()
        for ano, mes, quantidade, valor_total in distribuicao:
            meses = ['', 'Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 
                    'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']
            mes_nome = meses[int(mes)]
            print(f"{mes_nome}/{int(ano)}: {quantidade} contas - R$ {valor_total}")

if __name__ == "__main__":
    detailed_future_accounts()
