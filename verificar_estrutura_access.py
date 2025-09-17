#!/usr/bin/env python3
"""
Verificar estrutura da tabela produtos no MS Access
"""

import pyodbc

def verificar_estrutura_access():
    access_path = r"C:\Users\Cirilo\Documents\Bancos\Cadastros\Cadastros.mdb"
    conn_str = (
        r'DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};'
        f'DBQ={access_path};'
        'PWD=010182;'
    )
    
    try:
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()
        
        # Listar colunas da tabela produtos
        print("Colunas da tabela 'produtos' no MS Access:")
        print("-" * 50)
        
        cursor.execute("SELECT * FROM produtos WHERE 1=0")  # Query que não retorna dados, só estrutura
        columns = [column[0] for column in cursor.description]
        
        for i, col in enumerate(columns, 1):
            print(f"{i:2d}. {col}")
        
        print(f"\nTotal de colunas: {len(columns)}")
        
        # Testar uma query simples
        print(f"\nTestando query simples...")
        cursor.execute("SELECT TOP 3 * FROM produtos")
        
        for row in cursor.fetchall():
            print(f"Primeiro registro: {row[:5]}...")  # Mostra apenas os primeiros 5 campos
            break
        
        conn.close()
        
    except Exception as e:
        print(f"Erro: {e}")

if __name__ == "__main__":
    verificar_estrutura_access()