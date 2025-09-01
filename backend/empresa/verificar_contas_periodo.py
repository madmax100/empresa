#!/usr/bin/env python
import os
import sys
import django
from datetime import datetime, date

# Configurar o Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'empresa.settings')
django.setup()

from django.db import connection

def check_accounts_by_period(start_date, end_date):
    """Verifica contas a receber e pagar em um período específico"""
    
    print(f"=== VERIFICANDO CONTAS NO PERÍODO DE {start_date} A {end_date} ===\n")
    
    with connection.cursor() as cursor:
        
        # ========== CONTAS A RECEBER ==========
        print("📊 CONTAS A RECEBER:")
        print("-" * 50)
        
        # Por data de emissão
        cursor.execute("""
            SELECT COUNT(*), SUM(valor), MIN(data), MAX(data)
            FROM contas_receber 
            WHERE data >= %s AND data <= %s
        """, [start_date, end_date])
        
        count_rec_emissao, valor_rec_emissao, min_data, max_data = cursor.fetchone()
        valor_rec_emissao = valor_rec_emissao or 0
        
        print(f"Por DATA DE EMISSÃO ({start_date} a {end_date}):")
        print(f"  📈 Quantidade: {count_rec_emissao}")
        print(f"  💰 Valor Total: R$ {valor_rec_emissao:,.2f}")
        if min_data and max_data:
            print(f"  📅 Período real: {min_data.date()} a {max_data.date()}")
        
        # Por data de vencimento
        cursor.execute("""
            SELECT COUNT(*), SUM(valor), MIN(vencimento), MAX(vencimento)
            FROM contas_receber 
            WHERE vencimento >= %s AND vencimento <= %s
        """, [start_date, end_date])
        
        count_rec_venc, valor_rec_venc, min_venc, max_venc = cursor.fetchone()
        valor_rec_venc = valor_rec_venc or 0
        
        print(f"\nPor DATA DE VENCIMENTO ({start_date} a {end_date}):")
        print(f"  📈 Quantidade: {count_rec_venc}")
        print(f"  💰 Valor Total: R$ {valor_rec_venc:,.2f}")
        if min_venc and max_venc:
            print(f"  📅 Período real: {min_venc.date()} a {max_venc.date()}")
        
        # Status das contas a receber no período (por vencimento)
        if count_rec_venc > 0:
            cursor.execute("""
                SELECT status, COUNT(*), SUM(valor)
                FROM contas_receber 
                WHERE vencimento >= %s AND vencimento <= %s
                GROUP BY status
                ORDER BY COUNT(*) DESC
            """, [start_date, end_date])
            
            status_rec = cursor.fetchall()
            print(f"\n  📋 Por Status (vencimento no período):")
            for status, count, valor in status_rec:
                valor = valor or 0
                print(f"    {status or 'N/A'}: {count} contas - R$ {valor:,.2f}")
        
        # ========== CONTAS A PAGAR ==========
        print(f"\n\n💳 CONTAS A PAGAR:")
        print("-" * 50)
        
        # Por data de emissão
        cursor.execute("""
            SELECT COUNT(*), SUM(valor), MIN(data), MAX(data)
            FROM contas_pagar 
            WHERE data >= %s AND data <= %s
        """, [start_date, end_date])
        
        count_pag_emissao, valor_pag_emissao, min_data_pag, max_data_pag = cursor.fetchone()
        valor_pag_emissao = valor_pag_emissao or 0
        
        print(f"Por DATA DE EMISSÃO ({start_date} a {end_date}):")
        print(f"  📈 Quantidade: {count_pag_emissao}")
        print(f"  💰 Valor Total: R$ {valor_pag_emissao:,.2f}")
        if min_data_pag and max_data_pag:
            print(f"  📅 Período real: {min_data_pag.date()} a {max_data_pag.date()}")
        
        # Por data de vencimento
        cursor.execute("""
            SELECT COUNT(*), SUM(valor), MIN(vencimento), MAX(vencimento)
            FROM contas_pagar 
            WHERE vencimento >= %s AND vencimento <= %s
        """, [start_date, end_date])
        
        count_pag_venc, valor_pag_venc, min_venc_pag, max_venc_pag = cursor.fetchone()
        valor_pag_venc = valor_pag_venc or 0
        
        print(f"\nPor DATA DE VENCIMENTO ({start_date} a {end_date}):")
        print(f"  📈 Quantidade: {count_pag_venc}")
        print(f"  💰 Valor Total: R$ {valor_pag_venc:,.2f}")
        if min_venc_pag and max_venc_pag:
            print(f"  📅 Período real: {min_venc_pag.date()} a {max_venc_pag.date()}")
        
        # Status das contas a pagar no período (por vencimento)
        if count_pag_venc > 0:
            cursor.execute("""
                SELECT status, COUNT(*), SUM(valor)
                FROM contas_pagar 
                WHERE vencimento >= %s AND vencimento <= %s
                GROUP BY status
                ORDER BY COUNT(*) DESC
            """, [start_date, end_date])
            
            status_pag = cursor.fetchall()
            print(f"\n  📋 Por Status (vencimento no período):")
            for status, count, valor in status_pag:
                valor = valor or 0
                print(f"    {status or 'N/A'}: {count} contas - R$ {valor:,.2f}")
        
        # ========== RESUMO ==========
        print(f"\n\n📊 RESUMO DO PERÍODO ({start_date} a {end_date}):")
        print("=" * 60)
        print(f"🟢 Contas a RECEBER (vencimento): {count_rec_venc} contas - R$ {valor_rec_venc:,.2f}")
        print(f"🔴 Contas a PAGAR (vencimento):   {count_pag_venc} contas - R$ {valor_pag_venc:,.2f}")
        
        saldo = valor_rec_venc - valor_pag_venc
        if saldo > 0:
            print(f"💰 SALDO POSITIVO: R$ {saldo:,.2f}")
        elif saldo < 0:
            print(f"⚠️  SALDO NEGATIVO: R$ {saldo:,.2f}")
        else:
            print(f"⚖️  SALDO EQUILIBRADO: R$ 0,00")

def main():
    """Função principal com períodos predefinidos para teste"""
    
    print("🔍 VERIFICAÇÃO DE CONTAS POR PERÍODO")
    print("=" * 60)
    
    # Períodos para verificar
    periodos = [
        ("2025-09-01", "2025-09-30", "Setembro de 2025"),
        ("2025-10-01", "2025-10-31", "Outubro de 2025"),
        ("2025-11-01", "2025-11-30", "Novembro de 2025"),
        ("2025-01-01", "2025-12-31", "Todo o ano de 2025"),
        ("2024-01-01", "2024-12-31", "Todo o ano de 2024"),
    ]
    
    for start_date, end_date, descricao in periodos:
        print(f"\n{'='*20} {descricao.upper()} {'='*20}")
        check_accounts_by_period(start_date, end_date)
        print("\n" + "="*80)

if __name__ == "__main__":
    main()
