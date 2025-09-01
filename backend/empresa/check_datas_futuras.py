#!/usr/bin/env python
import os
import sys
import django

# Configurar o Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'empresa.settings')
django.setup()

from django.db import connection
from datetime import datetime

def check_contas_receber_after_august_2025():
    """Verifica contas a receber com datas após agosto de 2025"""
    
    with connection.cursor() as cursor:
        # Primeiro, vamos ver a estrutura da tabela
        cursor.execute("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'contas_receber' 
            AND table_schema = 'public'
            ORDER BY ordinal_position;
        """)
        
        columns = cursor.fetchall()
        print("=== ESTRUTURA DA TABELA CONTAS_RECEBER ===")
        for column_name, data_type in columns:
            print(f"{column_name}: {data_type}")
        
        print("\n=== VERIFICANDO DATAS ===")
        
        # Buscar campos que parecem ser datas
        date_fields = [col[0] for col in columns if 'date' in col[1] or 'timestamp' in col[1]]
        
        if date_fields:
            print(f"Campos de data encontrados: {date_fields}")
            
            for field in date_fields:
                try:
                    # Verificar registros após agosto de 2025
                    cursor.execute(f"""
                        SELECT COUNT(*) 
                        FROM contas_receber 
                        WHERE {field} > '2025-08-31'
                    """)
                    count = cursor.fetchone()[0]
                    print(f"Registros com {field} após 31/08/2025: {count}")
                    
                    if count > 0:
                        # Mostrar alguns exemplos
                        cursor.execute(f"""
                            SELECT id, {field}
                            FROM contas_receber 
                            WHERE {field} > '2025-08-31'
                            ORDER BY {field} DESC
                            LIMIT 10
                        """)
                        examples = cursor.fetchall()
                        print(f"Primeiros 10 registros com {field} futuro:")
                        for id_conta, data in examples:
                            print(f"  ID: {id_conta}, {field}: {data}")
                        
                except Exception as e:
                    print(f"Erro ao verificar campo {field}: {e}")
        else:
            print("Nenhum campo de data encontrado na tabela")
            
        # Verificar também data de vencimento se existir
        try:
            cursor.execute("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'contas_receber' 
                AND table_schema = 'public'
                AND (
                    column_name ILIKE '%vencimento%' 
                    OR column_name ILIKE '%data%'
                    OR column_name ILIKE '%prazo%'
                )
            """)
            
            date_like_fields = cursor.fetchall()
            print(f"\nCampos relacionados a datas: {[field[0] for field in date_like_fields]}")
            
        except Exception as e:
            print(f"Erro ao buscar campos de data: {e}")

if __name__ == "__main__":
    check_contas_receber_after_august_2025()
