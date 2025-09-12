import pyodbc
import pandas as pd
from datetime import datetime

def conectar_access_extratos():
    """Conecta ao banco Access de extratos"""
    try:
        conn_str = (
            r'DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};'
            r'DBQ=C:\Users\Cirilo\Documents\Bancos\Extratos\Extratos.mdb;'
            r'PWD=010182;'
        )
        conn = pyodbc.connect(conn_str)
        return conn
    except Exception as e:
        print(f"Erro ao conectar ao banco de extratos: {e}")
        return None

def conectar_access_cadastros():
    """Conecta ao banco Access de cadastros"""
    try:
        conn_str = (
            r'DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};'
            r'DBQ=C:\Users\Cirilo\Documents\Bancos\Cadastros\Cadastros.mdb;'
            r'PWD=010182;'
        )
        conn = pyodbc.connect(conn_str)
        return conn
    except Exception as e:
        print(f"Erro ao conectar ao banco de cadastros: {e}")
        return None

def listar_produtos_disponiveis():
    """Lista produtos que têm movimentações e estão no cadastro"""
    print("=== PRODUTOS DISPONÍVEIS PARA ANÁLISE ===")
    print("="*60)
    
    conn_extratos = conectar_access_extratos()
    conn_cadastros = conectar_access_cadastros()
    
    if not conn_extratos or not conn_cadastros:
        return
    
    try:
        cursor_extratos = conn_extratos.cursor()
        cursor_cadastros = conn_cadastros.cursor()
        
        # Busca produtos com mais movimentações até 01/01/2025
        data_corte = datetime(2025, 1, 1)
        
        query = """
        SELECT Produto, COUNT(*) as Total_Movimentacoes
        FROM [NotasFiscais]
        WHERE Data <= ?
        GROUP BY Produto
        ORDER BY COUNT(*) DESC
        """
        
        cursor_extratos.execute(query, data_corte)
        produtos_com_movimento = cursor_extratos.fetchall()
        
        print(f"Total de produtos com movimentações até 01/01/2025: {len(produtos_com_movimento)}")
        
        # Mostra os top 20 produtos com mais movimentações
        print(f"\nTOP 20 PRODUTOS COM MAIS MOVIMENTAÇÕES:")
        print("-" * 80)
        print(f"{'Código':<8} {'Nome':<50} {'Movimentações':<15}")
        print("-" * 80)
        
        for i, (codigo, total_mov) in enumerate(produtos_com_movimento[:20]):
            # Busca nome do produto
            cursor_cadastros.execute("SELECT Descricao FROM [Produtos] WHERE Codigo = ?", codigo)
            nome_resultado = cursor_cadastros.fetchone()
            nome = nome_resultado[0][:47] + "..." if nome_resultado and len(nome_resultado[0]) > 50 else (nome_resultado[0] if nome_resultado else "Nome não encontrado")
            
            print(f"{codigo:<8} {nome:<50} {total_mov:<15}")
        
        # Mostra produtos com saldos iniciais
        print(f"\n\nPRODUTOS COM SALDO INICIAL:")
        print("-" * 80)
        
        cursor_extratos.execute("""
            SELECT DISTINCT Produto, COUNT(*) as Saldos_Iniciais
            FROM [NotasFiscais]
            WHERE Historico LIKE '%SALDO INICIAL%' AND Data <= ?
            GROUP BY Produto
            ORDER BY COUNT(*) DESC
        """, data_corte)
        
        produtos_saldo_inicial = cursor_extratos.fetchall()
        
        print(f"{'Código':<8} {'Nome':<50} {'Saldos Iniciais':<15}")
        print("-" * 80)
        
        for codigo, total_saldos in produtos_saldo_inicial[:10]:
            cursor_cadastros.execute("SELECT Descricao FROM [Produtos] WHERE Codigo = ?", codigo)
            nome_resultado = cursor_cadastros.fetchone()
            nome = nome_resultado[0][:47] + "..." if nome_resultado and len(nome_resultado[0]) > 50 else (nome_resultado[0] if nome_resultado else "Nome não encontrado")
            
            print(f"{codigo:<8} {nome:<50} {total_saldos:<15}")
        
        # Produtos com estoque alto no relatório
        print(f"\n\nPRODUTOS COM MAIOR ESTOQUE (do relatório CSV):")
        print("-" * 80)
        
        try:
            df_relatorio = pd.read_csv('estoque_com_nomes_01_01_2025_20250911_041819.csv')
            top_estoque = df_relatorio.nlargest(15, 'quantidade')
            
            print(f"{'Código':<8} {'Nome':<50} {'Quantidade':<15}")
            print("-" * 80)
            
            for _, row in top_estoque.iterrows():
                codigo = row['codigo']
                nome = str(row['nome'])[:47] + "..." if len(str(row['nome'])) > 50 else str(row['nome'])
                quantidade = row['quantidade']
                
                print(f"{codigo:<8} {nome:<50} {quantidade:<15}")
        
        except Exception as e:
            print(f"Erro ao ler relatório CSV: {e}")
        
        # Produtos com estoque negativo
        print(f"\n\nPRODUTOS COM ESTOQUE NEGATIVO:")
        print("-" * 80)
        
        try:
            estoque_negativo = df_relatorio[df_relatorio['quantidade'] < 0].sort_values('quantidade')
            
            print(f"{'Código':<8} {'Nome':<50} {'Quantidade':<15}")
            print("-" * 80)
            
            for _, row in estoque_negativo.iterrows():
                codigo = row['codigo']
                nome = str(row['nome'])[:47] + "..." if len(str(row['nome'])) > 50 else str(row['nome'])
                quantidade = row['quantidade']
                
                print(f"{codigo:<8} {nome:<50} {quantidade:<15}")
        
        except Exception as e:
            print(f"Erro ao processar produtos com estoque negativo: {e}")
        
        print(f"\n" + "="*60)
        print("SUGESTÕES DE PRODUTOS PARA ANÁLISE:")
        print("- Produtos com muitas movimentações (ex: 4094, 4390, 3998)")
        print("- Produtos com saldo inicial (ex: 6036)")
        print("- Produtos com estoque alto (ex: 5828)")
        print("- Produtos com estoque negativo (ex: 3057)")
        
    except Exception as e:
        print(f"Erro na consulta: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        conn_extratos.close()
        conn_cadastros.close()

if __name__ == "__main__":
    listar_produtos_disponiveis()
