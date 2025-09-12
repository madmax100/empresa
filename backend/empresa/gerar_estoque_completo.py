import pyodbc
import pandas as pd
from datetime import datetime

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

def analisar_tabelas_produtos():
    """Analisa as tabelas para encontrar informações dos produtos"""
    conn = conectar_access()
    if not conn:
        return
    
    try:
        cursor = conn.cursor()
        
        # Lista todas as tabelas
        print("=== TABELAS DISPONÍVEIS ===")
        cursor.execute("SELECT name FROM MSysObjects WHERE Type=1 AND Flags=0")
        tabelas = cursor.fetchall()
        
        tabelas_produto = []
        for tabela in tabelas:
            nome = tabela[0].lower()
            if any(termo in nome for termo in ['produto', 'item', 'cadastro']):
                tabelas_produto.append(tabela[0])
        
        print("Tabelas que podem conter dados de produtos:")
        for tabela in tabelas_produto:
            print(f"- {tabela}")
        
        # Analisa cada tabela de produto
        for tabela in tabelas_produto:
            try:
                print(f"\n=== ANALISANDO TABELA: {tabela} ===")
                cursor.execute(f"SELECT TOP 1 * FROM [{tabela}]")
                columns = [column[0] for column in cursor.description]
                print(f"Campos: {', '.join(columns)}")
                
                # Mostra algumas linhas
                cursor.execute(f"SELECT TOP 5 * FROM [{tabela}]")
                rows = cursor.fetchall()
                print(f"Registros encontrados: {len(rows)}")
                
                if rows:
                    print("Exemplos:")
                    for i, row in enumerate(rows):
                        print(f"  {dict(zip(columns, row))}")
                        
            except Exception as e:
                print(f"Erro ao analisar {tabela}: {e}")
        
        # Tenta algumas consultas específicas
        print("\n=== BUSCANDO TABELA DE PRODUTOS ===")
        
        # Tenta nomes comuns
        nomes_teste = ['Produtos', 'produtos', 'PRODUTOS', 'Cadastro', 'cadastro', 'Items', 'items']
        
        for nome in nomes_teste:
            try:
                cursor.execute(f"SELECT TOP 3 * FROM [{nome}]")
                columns = [column[0] for column in cursor.description]
                rows = cursor.fetchall()
                
                print(f"\nTabela '{nome}' encontrada!")
                print(f"Campos: {columns}")
                print("Primeiros registros:")
                for row in rows:
                    print(f"  {dict(zip(columns, row))}")
                break
                
            except:
                continue
        
    except Exception as e:
        print(f"Erro geral: {e}")
    finally:
        conn.close()

def gerar_relatorio_completo():
    """Gera relatório com código, nome e quantidade"""
    conn = conectar_access()
    if not conn:
        return
    
    try:
        cursor = conn.cursor()
        
        # Primeiro, processa o estoque como antes
        print("=== PROCESSANDO MOVIMENTAÇÕES ===")
        
        # Busca movimentações até 01/01/2025
        data_corte = datetime(2025, 1, 1)
        query_movimentacoes = """
        SELECT Produto, Quantidade, Movimentacao, Historico, Data
        FROM [NotasFiscais]
        WHERE data <= ?
        ORDER BY Produto, Data
        """
        
        cursor.execute(query_movimentacoes, data_corte)
        movimentacoes = cursor.fetchall()
        
        print(f"Processando {len(movimentacoes)} movimentações...")
        
        # Processa estoque
        estoque = {}
        for row in movimentacoes:
            produto, quantidade, movimentacao, historico, data = row
            
            if not produto:
                continue
                
            produto = str(produto).strip()
            historico_str = str(historico).upper() if historico else ''
            quantidade_val = float(quantidade) if quantidade else 0
            
            # Se for SALDO INICIAL, zera e define novo saldo
            if 'SALDO INICIAL' in historico_str:
                estoque[produto] = quantidade_val
            else:
                # Inicializa se não existir
                if produto not in estoque:
                    estoque[produto] = 0
                
                # Determina entrada ou saída
                if 'COMPRA' in historico_str or str(movimentacao) == 'ENTRADA':
                    estoque[produto] += quantidade_val
                elif 'VENDA' in historico_str or str(movimentacao) == 'SAIDA':
                    estoque[produto] -= quantidade_val
                elif 'EXCLUSAO' in historico_str and 'VENDA' in historico_str:
                    # Exclusão de venda = entrada (estorno)
                    estoque[produto] += quantidade_val
                elif 'EXCLUSAO' in historico_str and 'COMPRA' in historico_str:
                    # Exclusão de compra = saída (estorno)
                    estoque[produto] -= quantidade_val
                else:
                    # Default: quantidade positiva = entrada
                    estoque[produto] += quantidade_val
        
        print(f"Estoque calculado para {len(estoque)} produtos")
        
        # Agora busca nomes dos produtos
        print("\n=== BUSCANDO NOMES DOS PRODUTOS ===")
        
        # Tenta diferentes tabelas de produtos
        tabelas_produtos = ['Produtos', 'produtos', 'PRODUTOS', 'Cadastro', 'cadastro', 'Items', 'items']
        
        nomes_produtos = {}
        tabela_produtos_encontrada = None
        
        for tabela in tabelas_produtos:
            try:
                # Testa se a tabela existe
                cursor.execute(f"SELECT TOP 1 * FROM [{tabela}]")
                columns = [column[0] for column in cursor.description]
                
                print(f"Tabela '{tabela}' encontrada com campos: {columns}")
                
                # Procura campo de código e nome
                campo_codigo = None
                campo_nome = None
                
                for col in columns:
                    col_lower = col.lower()
                    if 'codigo' in col_lower or 'cod' in col_lower or col_lower in ['id', 'produto']:
                        campo_codigo = col
                    elif 'nome' in col_lower or 'descricao' in col_lower or 'desc' in col_lower:
                        campo_nome = col
                
                if campo_codigo and campo_nome:
                    print(f"Usando campos: {campo_codigo} (código) e {campo_nome} (nome)")
                    
                    # Busca todos os produtos
                    cursor.execute(f"SELECT [{campo_codigo}], [{campo_nome}] FROM [{tabela}]")
                    produtos = cursor.fetchall()
                    
                    for prod_row in produtos:
                        codigo = str(prod_row[0]).strip() if prod_row[0] else ''
                        nome = str(prod_row[1]).strip() if prod_row[1] else ''
                        if codigo:
                            nomes_produtos[codigo] = nome
                    
                    tabela_produtos_encontrada = tabela
                    print(f"Carregados {len(nomes_produtos)} nomes de produtos")
                    break
                
            except Exception as e:
                continue
        
        if not nomes_produtos:
            print("Não foi possível encontrar tabela de produtos. Usando apenas códigos.")
        
        # Cria DataFrame final
        resultado = []
        for produto, quantidade in estoque.items():
            nome_produto = nomes_produtos.get(produto, 'Nome não encontrado')
            resultado.append({
                'codigo': produto,
                'nome': nome_produto,
                'quantidade': quantidade
            })
        
        df_resultado = pd.DataFrame(resultado)
        df_resultado = df_resultado.sort_values('codigo')
        
        # Salva arquivo CSV
        nome_arquivo = f'estoque_completo_01_01_2025_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
        df_resultado.to_csv(nome_arquivo, index=False, encoding='utf-8-sig')
        
        print(f"\n=== RELATÓRIO COMPLETO GERADO ===")
        print(f"Arquivo: {nome_arquivo}")
        print(f"Total de produtos: {len(df_resultado)}")
        print(f"Produtos com nome encontrado: {len(df_resultado[df_resultado['nome'] != 'Nome não encontrado'])}")
        
        print(f"\nPrimeiros 10 registros:")
        print(df_resultado.head(10))
        
        return nome_arquivo
        
    except Exception as e:
        print(f"Erro ao gerar relatório completo: {e}")
        import traceback
        traceback.print_exc()
        return None
    
    finally:
        conn.close()

if __name__ == "__main__":
    print("=== GERAÇÃO DE RELATÓRIO COMPLETO DE ESTOQUE ===")
    
    # Primeiro analisa as tabelas para encontrar produtos
    analisar_tabelas_produtos()
    
    print("\n" + "="*60)
    
    # Gera o relatório completo
    gerar_relatorio_completo()
