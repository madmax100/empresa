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

def buscar_nome_produto(codigo):
    """Busca o nome do produto no banco de cadastros"""
    conn = conectar_access_cadastros()
    if not conn:
        return "Nome não encontrado"
    
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT Descricao FROM [Produtos] WHERE Codigo = ?", codigo)
        resultado = cursor.fetchone()
        
        if resultado:
            return resultado[0]
        else:
            return "Produto não encontrado no cadastro"
    
    except Exception as e:
        print(f"Erro ao buscar nome do produto: {e}")
        return "Erro ao buscar nome"
    
    finally:
        conn.close()

def analisar_produto_54101():
    """Analisa detalhadamente o produto código 54101"""
    codigo_produto = 54101
    
    # Busca nome do produto
    nome_produto = buscar_nome_produto(codigo_produto)
    
    print(f"=== ANÁLISE DETALHADA DO PRODUTO {codigo_produto} ===")
    print(f"Nome: {nome_produto}")
    print("="*60)
    
    conn = conectar_access_extratos()
    if not conn:
        return
    
    try:
        cursor = conn.cursor()
        
        # Busca todas as movimentações do produto até 01/01/2025
        data_corte = datetime(2025, 1, 1)
        
        query = """
        SELECT Data, Quantidade, Movimentacao, Historico, Documento, Horario
        FROM [NotasFiscais]
        WHERE Produto = ? AND Data <= ?
        ORDER BY Data, Horario
        """
        
        cursor.execute(query, codigo_produto, data_corte)
        movimentacoes = cursor.fetchall()
        
        print(f"Total de movimentações encontradas: {len(movimentacoes)}")
        
        if len(movimentacoes) == 0:
            print("Nenhuma movimentação encontrada para este produto até 01/01/2025")
            return
        
        # Processa movimentações step by step
        print(f"\n=== PROCESSAMENTO DAS MOVIMENTAÇÕES ===")
        
        saldo_atual = 0.0
        saldo_inicial_encontrado = False
        
        for i, (data, quantidade, movimentacao, historico, documento, horario) in enumerate(movimentacoes):
            historico_str = str(historico).upper() if historico else ''
            quantidade_val = float(quantidade) if quantidade else 0.0
            movimentacao_str = str(movimentacao) if movimentacao else ''
            
            print(f"\n--- Movimentação {i+1} ---")
            print(f"Data: {data}")
            print(f"Horário: {horario}")
            print(f"Documento: {documento}")
            print(f"Quantidade: {quantidade_val}")
            print(f"Movimentação: {movimentacao_str}")
            print(f"Histórico: {historico}")
            
            # Aplica a lógica de cálculo
            if 'SALDO INICIAL' in historico_str:
                print(f">>> SALDO INICIAL DETECTADO <<<")
                print(f"Estoque anterior ({saldo_atual}) será ZERADO")
                saldo_atual = quantidade_val
                saldo_inicial_encontrado = True
                print(f"Novo saldo definido: {saldo_atual}")
            else:
                print(f"Saldo antes da movimentação: {saldo_atual}")
                
                # Determina se é entrada ou saída
                entrada = False
                saida = False
                
                if 'COMPRA' in historico_str or movimentacao_str == 'ENTRADA':
                    entrada = True
                elif 'VENDA' in historico_str or movimentacao_str == 'SAIDA':
                    saida = True
                elif 'EXCLUSAO' in historico_str and 'VENDA' in historico_str:
                    entrada = True  # Estorno de venda
                    print(">>> Estorno de venda (entrada)")
                elif 'EXCLUSAO' in historico_str and 'COMPRA' in historico_str:
                    saida = True  # Estorno de compra
                    print(">>> Estorno de compra (saída)")
                else:
                    # Default: quantidade positiva = entrada
                    if quantidade_val >= 0:
                        entrada = True
                    else:
                        saida = True
                        quantidade_val = abs(quantidade_val)
                
                if entrada:
                    saldo_atual += quantidade_val
                    print(f">>> ENTRADA: +{quantidade_val}")
                elif saida:
                    saldo_atual -= quantidade_val
                    print(f">>> SAÍDA: -{quantidade_val}")
                
                print(f"Saldo após movimentação: {saldo_atual}")
        
        # Resultado final
        print(f"\n" + "="*60)
        print(f"=== RESULTADO FINAL ===")
        print(f"Produto: {codigo_produto} - {nome_produto}")
        print(f"Saldo final em 01/01/2025: {saldo_atual}")
        print(f"Saldo inicial foi redefinido durante o período: {'SIM' if saldo_inicial_encontrado else 'NÃO'}")
        
        # Verifica se o resultado bate com o relatório
        try:
            df_relatorio = pd.read_csv('estoque_com_nomes_01_01_2025_20250911_041819.csv')
            produto_relatorio = df_relatorio[df_relatorio['codigo'] == str(codigo_produto)]
            
            if not produto_relatorio.empty:
                saldo_relatorio = produto_relatorio.iloc[0]['quantidade']
                print(f"Saldo no relatório CSV: {saldo_relatorio}")
                
                if abs(saldo_atual - saldo_relatorio) < 0.001:
                    print("✅ CÁLCULO CONFERE COM O RELATÓRIO!")
                else:
                    print("❌ DIVERGÊNCIA ENCONTRADA!")
            else:
                print("Produto não encontrado no relatório CSV")
        
        except Exception as e:
            print(f"Erro ao verificar relatório: {e}")
        
        # Salva detalhes em arquivo
        nome_arquivo = f'analise_produto_{codigo_produto}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.txt'
        
        with open(nome_arquivo, 'w', encoding='utf-8') as f:
            f.write(f"ANÁLISE DETALHADA DO PRODUTO {codigo_produto}\n")
            f.write(f"Nome: {nome_produto}\n")
            f.write(f"Data da análise: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
            f.write("="*60 + "\n\n")
            
            f.write(f"Total de movimentações: {len(movimentacoes)}\n")
            f.write(f"Saldo final: {saldo_atual}\n")
            f.write(f"Saldo inicial redefinido: {'SIM' if saldo_inicial_encontrado else 'NÃO'}\n\n")
            
            f.write("DETALHAMENTO DAS MOVIMENTAÇÕES:\n")
            f.write("-" * 40 + "\n")
            
            saldo_temp = 0.0
            for i, (data, quantidade, movimentacao, historico, documento, horario) in enumerate(movimentacoes):
                historico_str = str(historico).upper() if historico else ''
                quantidade_val = float(quantidade) if quantidade else 0.0
                
                f.write(f"\n{i+1}. {data} {horario}\n")
                f.write(f"   Documento: {documento}\n")
                f.write(f"   Quantidade: {quantidade_val}\n")
                f.write(f"   Movimentação: {movimentacao}\n")
                f.write(f"   Histórico: {historico}\n")
                
                if 'SALDO INICIAL' in historico_str:
                    f.write(f"   >>> SALDO INICIAL - Estoque zerado e redefinido para: {quantidade_val}\n")
                    saldo_temp = quantidade_val
                else:
                    saldo_anterior = saldo_temp
                    if 'COMPRA' in historico_str or str(movimentacao) == 'ENTRADA':
                        saldo_temp += quantidade_val
                        f.write(f"   >>> ENTRADA: {saldo_anterior} + {quantidade_val} = {saldo_temp}\n")
                    elif 'VENDA' in historico_str or str(movimentacao) == 'SAIDA':
                        saldo_temp -= quantidade_val
                        f.write(f"   >>> SAÍDA: {saldo_anterior} - {quantidade_val} = {saldo_temp}\n")
                    else:
                        saldo_temp += quantidade_val
                        f.write(f"   >>> DEFAULT (entrada): {saldo_anterior} + {quantidade_val} = {saldo_temp}\n")
        
        print(f"\nDetalhes salvos em: {nome_arquivo}")
        
    except Exception as e:
        print(f"Erro na análise: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        conn.close()

if __name__ == "__main__":
    analisar_produto_54101()
