import pyodbc

def find_nfs_database():
    banks_to_check = [
        r'C:\Users\Cirilo\Documents\Bancos\Movimentos.mdb',
        r'C:\Users\Cirilo\Documents\Bancos\Cadastros.mdb',
        r'C:\Users\Cirilo\Documents\Bancos\Contas\Contas.mdb'
    ]

    for bank_path in banks_to_check:
        try:
            # Tentar com senha 226cmm100
            conn = pyodbc.connect(f'DRIVER={{Microsoft Access Driver (*.mdb, *.accdb)}};DBQ={bank_path};PWD=226cmm100;')
            cursor = conn.cursor()
            
            # Verificar se existe tabela NFS
            try:
                cursor.execute('SELECT COUNT(*) FROM NFS WHERE YEAR(NFData) >= 2024')
                count = cursor.fetchone()[0]
                print(f'{bank_path}: {count} registros NFS de 2024+')
                
                # Se encontrou registros, verificar se tem a nota 41440
                if count > 0:
                    cursor.execute('SELECT COUNT(*) FROM NFS WHERE NFNumero = 41440')
                    nota_count = cursor.fetchone()[0]
                    print(f'  - Nota 41440: {"Existe" if nota_count > 0 else "Nao existe"}')
                    
                    if nota_count > 0:
                        return bank_path
                    
            except Exception as e:
                print(f'{bank_path}: Tabela NFS nao encontrada ou erro: {e}')
            
            conn.close()
        except Exception as e:
            print(f'{bank_path}: Erro ao conectar - {str(e)[:100]}')
    
    return None

if __name__ == "__main__":
    database_path = find_nfs_database()
    if database_path:
        print(f'Banco encontrado: {database_path}')
    else:
        print('Nenhum banco com NFS encontrado')
