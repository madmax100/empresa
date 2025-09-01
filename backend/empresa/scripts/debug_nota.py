#!/usr/bin/env python3

import pyodbc

try:
    # Conectar ao MS Access
    access_conn_str = r'Driver={Microsoft Access Driver (*.mdb, *.accdb)};DBQ=C:\Users\Cirilo\Documents\Bancos\Movimentos\Movimentos.mdb;PWD=010182;'
    access_conn = pyodbc.connect(access_conn_str)
    access_cursor = access_conn.cursor()
    
    # Buscar dados da nota 41009
    query = '''
        SELECT NumNFS, Data, Cliente, FormaPagto, Formulario, NFReferencia
        FROM NFS 
        WHERE NumNFS = 41009
    '''
    access_cursor.execute(query)
    nota = access_cursor.fetchone()
    
    if nota:
        print(f'Nota 41009 encontrada:')
        print(f'  NumNFS: {nota[0]}')
        print(f'  Data: {nota[1]}')
        print(f'  Cliente: {nota[2]}')
        print(f'  FormaPagto: "{nota[3]}" (tamanho: {len(str(nota[3])) if nota[3] else 0})')
        print(f'  Formulario: "{nota[4]}" (tamanho: {len(str(nota[4])) if nota[4] else 0})')
        print(f'  NFReferencia: "{nota[5]}" (tamanho: {len(str(nota[5])) if nota[5] else 0})')
    else:
        print('Nota 41009 não encontrada')
        
    access_conn.close()
    
except Exception as e:
    print(f'Erro: {e}')
