#!/usr/bin/env python
import os
import sys
import django

# Configurar o Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'empresa.settings')
django.setup()

from django.db import connection

def check_tables():
    """Verifica quais tabelas foram criadas e quantos registros há em cada uma"""
    
    with connection.cursor() as cursor:
        # Listar todas as tabelas
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_type = 'BASE TABLE'
            ORDER BY table_name;
        """)
        
        tables = cursor.fetchall()
        print("=== TABELAS NO BANCO DE DADOS ===")
        
        for (table_name,) in tables:
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {table_name};")
                count = cursor.fetchone()[0]
                print(f"{table_name}: {count} registros")
            except Exception as e:
                print(f"{table_name}: Erro ao contar - {e}")

if __name__ == "__main__":
    check_tables()
