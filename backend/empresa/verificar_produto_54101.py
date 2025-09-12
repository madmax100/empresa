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

def verificar_produto_54101():
    """Verifica o produto 54101 em ambos os bancos"""
    codigo_produto = 54101
    
    print(f"=== VERIFICAÇÃO COMPLETA DO PRODUTO {codigo_produto} ===")
    print("="*60)
    
    # 1. Verifica no banco de cadastros
    print("1. VERIFICANDO NO BANCO DE CADASTROS...")
    conn_cadastros = conectar_access_cadastros()
    
    if conn_cadastros:
        try:
            cursor = conn_cadastros.cursor()
            
            # Busca o produto na tabela Produtos
            cursor.execute("SELECT * FROM [Produtos] WHERE Codigo = ?", codigo_produto)
            produto = cursor.fetchone()
            
            if produto:
                columns = [column[0] for column in cursor.description]
                produto_dict = dict(zip(columns, produto))
                
                print("✅ PRODUTO ENCONTRADO NO CADASTRO:")
                print(f"   Código: {produto_dict.get('Codigo')}")
                print(f"   Descrição: {produto_dict.get('Descricao')}")
                print(f"   Unidade: {produto_dict.get('Unidade')}")
                print(f"   Grupo: {produto_dict.get('grupo')}")
                print(f"   Status: {produto_dict.get('Status')}")
                print(f"   Estoque Atual: {produto_dict.get('Estoque')}")
                print(f"   Data Cadastro: {produto_dict.get('Datacadastro')}")
            else:
                print("❌ PRODUTO NÃO ENCONTRADO NO CADASTRO")
        
        except Exception as e:
            print(f"Erro ao consultar cadastro: {e}")
        
        finally:
            conn_cadastros.close()
    
    # 2. Verifica no banco de extratos (movimentações)
    print(f"\n2. VERIFICANDO MOVIMENTAÇÕES NO BANCO DE EXTRATOS...")
    conn_extratos = conectar_access_extratos()
    
    if conn_extratos:
        try:
            cursor = conn_extratos.cursor()
            
            # Busca todas as movimentações do produto (sem filtro de data)
            cursor.execute("SELECT COUNT(*) FROM [NotasFiscais] WHERE Produto = ?", codigo_produto)
            total_movimentacoes = cursor.fetchone()[0]
            
            print(f"Total de movimentações encontradas (todas as datas): {total_movimentacoes}")
            
            if total_movimentacoes > 0:
                # Busca algumas movimentações para análise
                cursor.execute("""
                    SELECT TOP 10 Data, Quantidade, Movimentacao, Historico, Documento
                    FROM [NotasFiscais] 
                    WHERE Produto = ?
                    ORDER BY Data DESC
                """, codigo_produto)
                
                movimentacoes = cursor.fetchall()
                
                print("\n✅ MOVIMENTAÇÕES ENCONTRADAS (últimas 10):")
                for i, (data, quantidade, movimentacao, historico, documento) in enumerate(movimentacoes):
                    print(f"   {i+1}. {data} - Doc: {documento} - Qtd: {quantidade} - {movimentacao} - {historico}")
                
                # Verifica movimentações até 01/01/2025
                data_corte = datetime(2025, 1, 1)
                cursor.execute("""
                    SELECT COUNT(*) FROM [NotasFiscais] 
                    WHERE Produto = ? AND Data <= ?
                """, codigo_produto, data_corte)
                
                movimentacoes_ate_2025 = cursor.fetchone()[0]
                print(f"\nMovimentações até 01/01/2025: {movimentacoes_ate_2025}")
                
                if movimentacoes_ate_2025 > 0:
                    print("Processando movimentações até 01/01/2025...")
                    
                    cursor.execute("""
                        SELECT Data, Quantidade, Movimentacao, Historico, Documento
                        FROM [NotasFiscais] 
                        WHERE Produto = ? AND Data <= ?
                        ORDER BY Data, Horario
                    """, codigo_produto, data_corte)
                    
                    movs_2025 = cursor.fetchall()
                    
                    # Calcula saldo
                    saldo = 0.0
                    saldos_iniciais = 0
                    
                    for data, quantidade, movimentacao, historico, documento in movs_2025:
                        historico_str = str(historico).upper() if historico else ''
                        quantidade_val = float(quantidade) if quantidade else 0.0
                        
                        if 'SALDO INICIAL' in historico_str:
                            saldo = quantidade_val
                            saldos_iniciais += 1
                        else:
                            if 'COMPRA' in historico_str or str(movimentacao) == 'ENTRADA':
                                saldo += quantidade_val
                            elif 'VENDA' in historico_str or str(movimentacao) == 'SAIDA':
                                saldo -= quantidade_val
                            elif 'EXCLUSAO' in historico_str and 'VENDA' in historico_str:
                                saldo += quantidade_val  # Estorno de venda
                            elif 'EXCLUSAO' in historico_str and 'COMPRA' in historico_str:
                                saldo -= quantidade_val  # Estorno de compra
                            else:
                                saldo += quantidade_val  # Default
                    
                    print(f"\n📊 RESULTADO DO CÁLCULO:")
                    print(f"   Saldo calculado em 01/01/2025: {saldo}")
                    print(f"   Saldos iniciais encontrados: {saldos_iniciais}")
                
            else:
                print("❌ NENHUMA MOVIMENTAÇÃO ENCONTRADA")
            
            # Busca produtos similares (códigos próximos)
            print(f"\n3. PROCURANDO PRODUTOS COM CÓDIGOS SIMILARES...")
            cursor.execute("""
                SELECT DISTINCT Produto FROM [NotasFiscais] 
                WHERE Produto BETWEEN ? AND ?
                ORDER BY Produto
            """, codigo_produto - 10, codigo_produto + 10)
            
            produtos_similares = cursor.fetchall()
            
            if produtos_similares:
                print("Produtos com códigos próximos encontrados:")
                for (prod,) in produtos_similares:
                    if prod != codigo_produto:
                        print(f"   - {prod}")
            
        except Exception as e:
            print(f"Erro ao consultar extratos: {e}")
            import traceback
            traceback.print_exc()
        
        finally:
            conn_extratos.close()
    
    # 3. Verifica se existe no relatório CSV
    print(f"\n4. VERIFICANDO NO RELATÓRIO CSV GERADO...")
    try:
        df_relatorio = pd.read_csv('estoque_com_nomes_01_01_2025_20250911_041819.csv')
        produto_relatorio = df_relatorio[df_relatorio['codigo'] == str(codigo_produto)]
        
        if not produto_relatorio.empty:
            print("✅ PRODUTO ENCONTRADO NO RELATÓRIO:")
            for _, row in produto_relatorio.iterrows():
                print(f"   Código: {row['codigo']}")
                print(f"   Nome: {row['nome']}")
                print(f"   Quantidade: {row['quantidade']}")
        else:
            print("❌ PRODUTO NÃO ENCONTRADO NO RELATÓRIO")
    
    except Exception as e:
        print(f"Erro ao verificar relatório: {e}")
    
    print("\n" + "="*60)
    print("VERIFICAÇÃO CONCLUÍDA")

if __name__ == "__main__":
    verificar_produto_54101()
