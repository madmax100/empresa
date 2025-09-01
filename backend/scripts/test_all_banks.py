import pyodbc

# Bancos para testar
bancos = [
    'C:/Users/Cirilo/Documents/Bancos/Movimentos/Movimentos.mdb',
    'C:/Users/Cirilo/Documents/Bancos/Movimentos/A1Movimentos.mdb',
    'C:/Users/Cirilo/Documents/Bancos/Movimentos/Outrosmovimentos.mdb',
    'C:/Users/Cirilo/Documents/empresa/Bancos/Movimentos.mdb',
    'C:/Users/Cirilo/Documents/empresa/Bancos/Movimentos/Movimentos.mdb'
]

# Senhas para tentar
senhas = ['226cmm100', '226cmm', '100', '', '226', 'admin', 'password']

for banco in bancos:
    print(f'\n=== Testando banco: {banco} ===')
    for senha in senhas:
        try:
            # Conectar ao banco
            if senha:
                conn_str = f'DRIVER={{Microsoft Access Driver (*.mdb, *.accdb)}};DBQ={banco};PWD={senha}'
            else:
                conn_str = f'DRIVER={{Microsoft Access Driver (*.mdb, *.accdb)}};DBQ={banco}'
            
            conn = pyodbc.connect(conn_str)
            cursor = conn.cursor()
            
            print(f'✓ Conexão bem-sucedida com senha: "{senha}"')
            
            # Verificar se existe tabela NFS
            tables = cursor.tables(tableType='TABLE')
            table_names = [table.table_name for table in tables]
            
            # Procurar tabelas relacionadas a notas fiscais
            nfs_tables = [table for table in table_names if 'nf' in table.lower() or 'nota' in table.lower() or 'fiscal' in table.lower()]
            print(f'Tabelas relacionadas a notas fiscais: {nfs_tables}')
            
            # Se encontrou NFS, verificar quantos registros
            if 'NFS' in table_names:
                cursor.execute('SELECT COUNT(*) FROM NFS WHERE Year(DataEmissao) >= 2024')
                count = cursor.fetchone()[0]
                print(f'Registros NFS >= 2024: {count}')
                
                # Verificar se existe nota 41440
                cursor.execute('SELECT TOP 1 NumeroNF FROM NFS WHERE NumeroNF = 41440')
                nota = cursor.fetchone()
                if nota:
                    print('✓ Nota 41440 ENCONTRADA!')
                else:
                    print('✗ Nota 41440 não encontrada')
            
            conn.close()
            break  # Se conectou, sair do loop de senhas
            
        except Exception as e:
            if 'Senha inválida' in str(e):
                continue  # Tentar próxima senha
            else:
                print(f'✗ Erro: {e}')
                break  # Se não é erro de senha, pular para próximo banco
