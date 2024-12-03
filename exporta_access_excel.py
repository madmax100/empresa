import pyodbc
import pandas as pd
from datetime import datetime

def exportar_tabela_para_excel(database_path, tabela, output_path=None):
    try:
        # Conectar ao banco Access
        conn_str = (
            r'Driver={Microsoft Access Driver (*.mdb, *.accdb)};'
            f'DBQ={database_path};'
            'PWD=010182;'
        )
        conn = pyodbc.connect(conn_str)
        
        # Criar nome do arquivo de saída
        if output_path is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_path = f'export_{tabela}_{timestamp}.xlsx'
        
        # Ler a tabela usando pandas
        query = f'SELECT * FROM [{tabela}]'
        df = pd.read_sql(query, conn)
        
        # Exportar para Excel
        print(f'Exportando {len(df)} registros...')
        writer = pd.ExcelWriter(output_path, engine='openpyxl')
        
        # Formatar e escrever os dados
        df.to_excel(
            writer, 
            sheet_name=tabela,
            index=False,
            freeze_panes=(1,0)  # Congelar primeira linha
        )
        
        # Ajustar largura das colunas
        worksheet = writer.sheets[tabela]
        for idx, col in enumerate(df.columns):
            max_length = max(
                df[col].astype(str).apply(len).max(),
                len(str(col))
            ) + 2
            worksheet.column_dimensions[worksheet.cell(1, idx+1).column_letter].width = max_length
        
        # Salvar arquivo
        writer.close()
        print(f'Arquivo exportado com sucesso: {output_path}')
        
        # Mostrar informações sobre os dados
        print('\nInformações dos dados exportados:')
        print(df.info())
        
        return True
        
    except Exception as e:
        print(f'Erro ao exportar: {str(e)}')
        return False
    finally:
        if 'conn' in locals():
            conn.close()

def listar_tabelas_access(database_path):
    try:
        conn_str = (
            r'Driver={Microsoft Access Driver (*.mdb, *.accdb)};'
            f'DBQ={database_path};'
            'PWD=010182;'
        )
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()
        
        tabelas = []
        for row in cursor.tables():
            if row.table_type == 'TABLE':
                tabelas.append(row.table_name)
        
        return sorted(tabelas)
        
    except Exception as e:
        print(f'Erro ao listar tabelas: {str(e)}')
        return []
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == '__main__':
    # Caminho do seu banco de dados
    database_path = r"C:\Users\Cirilo\Documents\empresa\Bancos\Movimentos\Movimentos.mdb"
    
    # Listar tabelas disponíveis
    print('Tabelas disponíveis:')
    tabelas = listar_tabelas_access(database_path)
    for i, tabela in enumerate(tabelas, 1):
        print(f'{i}. {tabela}')
    
    # Solicitar qual tabela exportar
    try:
        escolha = int(input('\nEscolha o número da tabela para exportar: ')) - 1
        if 0 <= escolha < len(tabelas):
            tabela_escolhida = tabelas[escolha]
            
            # Definir caminho de saída personalizado (opcional)
            output_path = input('Digite o caminho de saída (ou Enter para padrão): ').strip()
            if not output_path:
                output_path = None
            
            # Exportar
            print(f'\nExportando tabela: {tabela_escolhida}')
            exportar_tabela_para_excel(database_path, tabela_escolhida, output_path)
        else:
            print('Escolha inválida!')
    except ValueError:
        print('Por favor, digite um número válido!')
    except Exception as e:
        print(f'Erro: {str(e)}')
