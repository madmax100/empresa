import pyodbc
from datetime import datetime

def gerar_relatorio_access(movimentos_path, arquivo_saida):
    """
    Gera um relatório detalhado das tabelas do Access e salva em um arquivo
    """
    try:
        # Conecta ao banco Access
        conn_str = (
            r'Driver={Microsoft Access Driver (*.mdb, *.accdb)};'
            f'DBQ={movimentos_path};'
            'PWD=010182;'
        )
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()
        
        # Obtém lista de tabelas
        tabelas = []
        for table_info in cursor.tables(tableType='TABLE'):
            nome_tabela = table_info.table_name
            if not nome_tabela.startswith('~'):
                tabelas.append(nome_tabela)
        
        tabelas.sort()  # Ordena tabelas alfabeticamente
        
        # Abre arquivo para escrita
        with open(arquivo_saida, 'w', encoding='utf-8') as f:
            # Escreve cabeçalho do relatório
            f.write(f"RELATÓRIO DE ESTRUTURA DO BANCO DE DADOS ACCESS\n")
            f.write(f"Data de geração: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
            f.write(f"Arquivo: {movimentos_path}\n")
            f.write(f"Total de tabelas encontradas: {len(tabelas)}\n")
            f.write("-" * 100 + "\n\n")
            
            # Para cada tabela
            for num, nome_tabela in enumerate(tabelas, 1):
                f.write(f"\n{num}. Tabela: {nome_tabela}\n")
                f.write("-" * 50 + "\n")
                
                # Lista colunas
                f.write(f"{'Coluna':<30} {'Tipo':<15} {'Tamanho':<10} {'Nullable'}\n")
                f.write("-" * 70 + "\n")
                
                colunas = cursor.columns(table=nome_tabela)
                for coluna in colunas:
                    f.write(f"{coluna.column_name:<30} {coluna.type_name:<15} "
                           f"{str(coluna.column_size):<10} {coluna.nullable}\n")
                
                # Conta registros
                try:
                    cursor.execute(f"SELECT COUNT(*) FROM [{nome_tabela}]")
                    total_registros = cursor.fetchone()[0]
                    f.write(f"\nTotal de registros: {total_registros}\n")
                except Exception as e:
                    f.write(f"\nErro ao contar registros: {str(e)}\n")
                
                f.write("-" * 100 + "\n")
            
        print(f"\nRelatório gerado com sucesso em: {arquivo_saida}")
        
    except Exception as e:
        print(f"Erro ao gerar relatório: {str(e)}")
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    movimentos_path = r"C:\Users\Cirilo\Documents\empresa\Bancos\Cadastros\Cadastros.mdb"
    arquivo_saida = "relatorio_access.txt"
    gerar_relatorio_access(movimentos_path, arquivo_saida)