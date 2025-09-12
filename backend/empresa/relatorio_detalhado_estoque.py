import pandas as pd
import pyodbc
from datetime import datetime
from collections import Counter

def conectar_access():
    """Conecta ao banco Access"""
    try:
        conn_str = (
            r'DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};'
            r'DBQ=C:\Users\Cirilo\Documents\Bancos\Extratos\Extratos.mdb;'
            r'PWD=010182;'
        )
        conn = pyodbc.connect(conn_str)
        return conn
    except Exception as e:
        print(f"Erro ao conectar ao banco: {e}")
        return None

def analisar_movimentacoes():
    """Analisa os tipos de movimentações para validar a lógica"""
    conn = conectar_access()
    if not conn:
        return
    
    try:
        cursor = conn.cursor()
        
        # Busca amostra de movimentações
        query = """
        SELECT TOP 1000 Produto, Quantidade, Movimentacao, Historico, Data
        FROM [NotasFiscais]
        WHERE data <= ?
        ORDER BY Data DESC
        """
        
        data_corte = datetime(2025, 1, 1)
        cursor.execute(query, data_corte)
        movimentacoes = cursor.fetchall()
        
        print("=== ANÁLISE DE MOVIMENTAÇÕES ===")
        print(f"Analisando {len(movimentacoes)} movimentações...")
        
        # Análise dos tipos de movimentação
        tipos_movimentacao = []
        tipos_historico = []
        
        for row in movimentacoes:
            produto, quantidade, movimentacao, historico, data = row
            tipos_movimentacao.append(str(movimentacao) if movimentacao else 'NULL')
            tipos_historico.append(str(historico) if historico else 'NULL')
        
        print("\n=== TIPOS DE MOVIMENTAÇÃO ===")
        counter_mov = Counter(tipos_movimentacao)
        for tipo, count in counter_mov.most_common(10):
            print(f"{tipo}: {count}")
        
        print("\n=== TIPOS DE HISTÓRICO (TOP 20) ===")
        counter_hist = Counter(tipos_historico)
        for tipo, count in counter_hist.most_common(20):
            print(f"{tipo}: {count}")
        
        # Análise de quantidades
        quantidades = [float(row[1]) if row[1] else 0 for row in movimentacoes]
        df_quant = pd.DataFrame({'quantidade': quantidades})
        
        print("\n=== ANÁLISE DE QUANTIDADES ===")
        print(f"Quantidades positivas: {len(df_quant[df_quant['quantidade'] > 0])}")
        print(f"Quantidades negativas: {len(df_quant[df_quant['quantidade'] < 0])}")
        print(f"Quantidades zero: {len(df_quant[df_quant['quantidade'] == 0])}")
        
        # Procura por saldos iniciais
        print("\n=== PROCURANDO SALDOS INICIAIS ===")
        saldos_iniciais = 0
        for row in movimentacoes:
            historico = str(row[3]) if row[3] else ''
            if 'SALDO INICIAL' in historico.upper():
                saldos_iniciais += 1
                if saldos_iniciais <= 5:  # Mostra apenas os primeiros 5
                    print(f"Produto {row[0]}: {historico} - Quantidade: {row[1]}")
        
        print(f"Total de registros com SALDO INICIAL: {saldos_iniciais}")
        
    except Exception as e:
        print(f"Erro na análise: {e}")
    finally:
        conn.close()

def verificar_produtos_especificos():
    """Verifica movimentações de produtos específicos"""
    conn = conectar_access()
    if not conn:
        return
    
    try:
        cursor = conn.cursor()
        
        # Produtos com maior estoque segundo o relatório
        produtos_teste = [5828, 4094, 4390, 3998, 5587]
        
        for produto in produtos_teste:
            print(f"\n=== PRODUTO {produto} ===")
            
            query = """
            SELECT Data, Quantidade, Movimentacao, Historico
            FROM [NotasFiscais]
            WHERE Produto = ? AND data <= ?
            ORDER BY Data
            """
            
            data_corte = datetime(2025, 1, 1)
            cursor.execute(query, produto, data_corte)
            movs = cursor.fetchall()
            
            print(f"Total de movimentações: {len(movs)}")
            
            # Simula o cálculo do estoque
            estoque = 0
            saldo_inicial_encontrado = False
            
            for data, quantidade, movimentacao, historico in movs:
                historico_str = str(historico).upper() if historico else ''
                
                if 'SALDO INICIAL' in historico_str:
                    estoque = float(quantidade) if quantidade else 0
                    saldo_inicial_encontrado = True
                    print(f"  {data}: SALDO INICIAL = {estoque}")
                else:
                    # Lógica de entrada/saída
                    if quantidade:
                        if 'COMPRA' in historico_str or 'E' == str(movimentacao):
                            estoque += float(quantidade)
                        elif 'VENDA' in historico_str or 'S' == str(movimentacao):
                            estoque -= float(quantidade)
                        else:
                            # Analisa pela quantidade (positiva = entrada, negativa = saída)
                            estoque += float(quantidade)
            
            print(f"Estoque final calculado: {estoque}")
            print(f"Saldo inicial encontrado: {saldo_inicial_encontrado}")
            
            # Mostra últimas 5 movimentações
            print("Últimas movimentações:")
            for i, (data, quantidade, movimentacao, historico) in enumerate(movs[-5:]):
                print(f"  {data}: {quantidade} - {movimentacao} - {historico}")
    
    except Exception as e:
        print(f"Erro na verificação: {e}")
    finally:
        conn.close()

def gerar_relatorio_resumo():
    """Gera relatório resumo do estoque"""
    try:
        # Lê o arquivo CSV gerado
        df = pd.read_csv('estoque_01_01_2025_20250911_041127.csv')
        
        print("\n=== RELATÓRIO RESUMO DO ESTOQUE ===")
        print(f"Total de produtos: {len(df)}")
        print(f"Produtos com estoque > 0: {len(df[df['saldo_01_01_2025'] > 0])}")
        print(f"Produtos com estoque = 0: {len(df[df['saldo_01_01_2025'] == 0])}")
        print(f"Produtos com estoque < 0: {len(df[df['saldo_01_01_2025'] < 0])}")
        
        print(f"\nValor total do estoque (apenas quantidades): {df['saldo_01_01_2025'].sum():.2f}")
        
        print(f"\nProdutos com maior estoque:")
        top_produtos = df.nlargest(10, 'saldo_01_01_2025')
        for _, row in top_produtos.iterrows():
            print(f"  Produto {row['produto']}: {row['saldo_01_01_2025']}")
        
        print(f"\nProdutos com estoque negativo:")
        produtos_negativos = df[df['saldo_01_01_2025'] < 0].sort_values('saldo_01_01_2025')
        for _, row in produtos_negativos.head(10).iterrows():
            print(f"  Produto {row['produto']}: {row['saldo_01_01_2025']}")
        
        # Salva relatório detalhado
        with open('relatorio_resumo_estoque_01_01_2025.txt', 'w', encoding='utf-8') as f:
            f.write("RELATÓRIO RESUMO - ESTOQUE EM 01/01/2025\n")
            f.write("="*50 + "\n\n")
            f.write(f"Data/Hora da geração: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
            f.write(f"Arquivo base: estoque_01_01_2025_20250911_041127.csv\n\n")
            
            f.write("ESTATÍSTICAS GERAIS:\n")
            f.write(f"- Total de produtos: {len(df)}\n")
            f.write(f"- Produtos com estoque positivo: {len(df[df['saldo_01_01_2025'] > 0])}\n")
            f.write(f"- Produtos com estoque zero: {len(df[df['saldo_01_01_2025'] == 0])}\n")
            f.write(f"- Produtos com estoque negativo: {len(df[df['saldo_01_01_2025'] < 0])}\n")
            f.write(f"- Somatória total: {df['saldo_01_01_2025'].sum():.2f}\n\n")
            
            f.write("TOP 20 PRODUTOS COM MAIOR ESTOQUE:\n")
            for _, row in df.nlargest(20, 'saldo_01_01_2025').iterrows():
                f.write(f"Produto {row['produto']}: {row['saldo_01_01_2025']}\n")
            
            f.write(f"\nPRODUTOS COM ESTOQUE NEGATIVO:\n")
            for _, row in produtos_negativos.iterrows():
                f.write(f"Produto {row['produto']}: {row['saldo_01_01_2025']}\n")
        
        print(f"\nRelatório detalhado salvo em: relatorio_resumo_estoque_01_01_2025.txt")
        
    except Exception as e:
        print(f"Erro ao gerar relatório resumo: {e}")

if __name__ == "__main__":
    print("=== ANÁLISE DETALHADA DO ESTOQUE ===")
    
    # Analisa os tipos de movimentação
    analisar_movimentacoes()
    
    # Verifica produtos específicos
    verificar_produtos_especificos()
    
    # Gera relatório resumo
    gerar_relatorio_resumo()
