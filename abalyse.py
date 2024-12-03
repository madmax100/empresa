# analyze_movimentos.py
import os
import pyodbc
from datetime import datetime

def analyze_access_file(file_path):
    """Analisa um arquivo .mdb específico"""
    try:
        # Tenta conectar com senha
        try:
            conn_str = (
                r'Driver={Microsoft Access Driver (*.mdb, *.accdb)};'
                f'DBQ={file_path};'
                'PWD=010182;'
            )
            conn = pyodbc.connect(conn_str)
        except:
            # Se falhar, tenta sem senha
            conn_str = f'DRIVER={{Microsoft Access Driver (*.mdb, *.accdb)}};DBQ={file_path}'
            conn = pyodbc.connect(conn_str)

        cursor = conn.cursor()

        # Lista todas as tabelas
        tables = [row.table_name for row in cursor.tables(tableType='TABLE')]
        
        print(f"\nArquivo: {os.path.basename(file_path)}")
        print(f"Tamanho: {os.path.getsize(file_path):,} bytes")
        print(f"Data modificação: {datetime.fromtimestamp(os.path.getmtime(file_path))}")
        print(f"Tabelas encontradas: {len(tables)}")
        
        # Analisa cada tabela
        for table in tables:
            try:
                cursor.execute(f"SELECT COUNT(*) FROM [{table}]")
                count = cursor.fetchone()[0]
                
                # Pega amostra dos dados
                cursor.execute(f"SELECT TOP 1 * FROM [{table}]")
                columns = [column[0] for column in cursor.description]
                
                print(f"\nTabela: {table}")
                print(f"Registros: {count:,}")
                print(f"Colunas: {', '.join(columns)}")
                
                # Se for tabela de movimentos, analisa datas
                if "movimento" in table.lower():
                    try:
                        cursor.execute(f"""
                            SELECT 
                                MIN(Data) as data_inicial,
                                MAX(Data) as data_final
                            FROM [{table}]
                            WHERE Data IS NOT NULL
                        """)
                        data_inicial, data_final = cursor.fetchone()
                        print(f"Período: {data_inicial} a {data_final}")
                    except:
                        print("Não foi possível determinar o período dos dados")
            
            except Exception as e:
                print(f"Erro ao analisar tabela {table}: {str(e)}")
                continue
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"Erro ao analisar arquivo {file_path}: {str(e)}")

def analyze_directory():
    """Analisa todos os arquivos .mdb no diretório"""
    directory = r"C:\Users\Cirilo\Documents\empresa\Bancos\Contas"
    
    try:
        print(f"Analisando diretório: {directory}")
        
        # Lista todos os arquivos .mdb
        mdb_files = [f for f in os.listdir(directory) if f.lower().endswith('.mdb')]
        
        if not mdb_files:
            print("Nenhum arquivo .mdb encontrado no diretório")
            return
        
        print(f"\nEncontrados {len(mdb_files)} arquivos .mdb:")
        for file in mdb_files:
            file_path = os.path.join(directory, file)
            analyze_access_file(file_path)
            
    except Exception as e:
        print(f"Erro ao analisar diretório: {str(e)}")

if __name__ == "__main__":
    print("Iniciando análise dos arquivos de movimento...")
    analyze_directory()