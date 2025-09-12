import pyodbc
import pandas as pd
from datetime import datetime
import os

def conectar_access():
    """Conecta ao banco Access"""
    try:
        # String de conexão para Access com senha
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

def analisar_estrutura_tabela():
    """Analisa a estrutura da tabela notas fiscais"""
    conn = conectar_access()
    if not conn:
        return
    
    try:
        cursor = conn.cursor()
        
        # Lista todas as tabelas
        print("=== TABELAS DISPONÍVEIS ===")
        tables = cursor.tables(tableType='TABLE')
        for table in tables:
            print(f"- {table.table_name}")
        
        # Tenta encontrar a tabela de notas fiscais
        cursor.execute("SELECT name FROM MSysObjects WHERE Type=1 AND Flags=0")
        tabelas = cursor.fetchall()
        
        # Procura por tabelas relacionadas a notas fiscais
        tabelas_nf = []
        for tabela in tabelas:
            nome = tabela[0].lower()
            if any(termo in nome for termo in ['nota', 'fiscal', 'nf', 'movimentacao', 'estoque']):
                tabelas_nf.append(tabela[0])
        
        print(f"\n=== TABELAS RELACIONADAS A NOTAS FISCAIS ===")
        for tabela in tabelas_nf:
            print(f"- {tabela}")
            
            # Analisa estrutura da tabela
            try:
                cursor.execute(f"SELECT TOP 1 * FROM [{tabela}]")
                columns = [column[0] for column in cursor.description]
                print(f"  Campos: {', '.join(columns)}")
                
                # Mostra algumas linhas de exemplo
                cursor.execute(f"SELECT TOP 5 * FROM [{tabela}]")
                rows = cursor.fetchall()
                print(f"  Registros encontrados: {len(rows)}")
                
                if rows:
                    print("  Exemplo de dados:")
                    for i, row in enumerate(rows):
                        print(f"    Linha {i+1}: {dict(zip(columns, row))}")
                
            except Exception as e:
                print(f"  Erro ao analisar tabela {tabela}: {e}")
            
            print()
    
    except Exception as e:
        print(f"Erro ao analisar estrutura: {e}")
    
    finally:
        conn.close()

def gerar_relatorio_estoque():
    """Gera relatório de estoque em 01/01/2025"""
    conn = conectar_access()
    if not conn:
        return
    
    try:
        cursor = conn.cursor()
        
        # Primeiro, vamos encontrar a tabela correta
        # Tenta diferentes nomes possíveis
        nomes_tabelas = ['NotasFiscais', 'notas_fiscais', 'notas fiscais', 'movimentacoes', 'Movimentacoes']
        
        tabela_encontrada = None
        for nome in nomes_tabelas:
            try:
                cursor.execute(f"SELECT TOP 1 * FROM [{nome}]")
                tabela_encontrada = nome
                print(f"Tabela encontrada: {nome}")
                break
            except:
                continue
        
        if not tabela_encontrada:
            print("Não foi possível encontrar a tabela de notas fiscais")
            return
        
        # Busca estrutura da tabela
        cursor.execute(f"SELECT TOP 1 * FROM [{tabela_encontrada}]")
        columns = [column[0] for column in cursor.description]
        print(f"Campos da tabela: {columns}")
        
        # Busca todos os registros até 01/01/2025
        data_corte = datetime(2025, 1, 1)
        
        # Query para buscar movimentações
        query = f"""
        SELECT * FROM [{tabela_encontrada}]
        WHERE data <= ?
        ORDER BY produto, data, historico
        """
        
        cursor.execute(query, data_corte)
        movimentacoes = cursor.fetchall()
        
        print(f"Total de movimentações encontradas até 01/01/2025: {len(movimentacoes)}")
        
        if len(movimentacoes) > 0:
            # Converte para DataFrame corretamente
            df = pd.DataFrame([list(row) for row in movimentacoes], columns=columns)
            
            print("\n=== ESTRUTURA DOS DADOS ===")
            print(f"Colunas: {df.columns.tolist()}")
            print(f"Shape: {df.shape}")
            
            print(f"\nPrimeiras 3 linhas:")
            print(df.head(3))
            
            # Processa o estoque
            resultado = processar_estoque_com_dataframe(df)
            return resultado
        else:
            print("Nenhuma movimentação encontrada")
            return None
        
    except Exception as e:
        print(f"Erro ao gerar relatório: {e}")
        import traceback
        traceback.print_exc()
        return None
    
    finally:
        conn.close()

def processar_estoque_com_dataframe(df):
    """Processa o estoque com DataFrame usando a lógica de saldo inicial"""
    try:
        # Identifica os campos automaticamente
        campos_map = {}
        for col in df.columns:
            col_lower = col.lower()
            if 'produto' in col_lower:
                campos_map['produto'] = col
            elif 'quantidade' in col_lower:
                campos_map['quantidade'] = col
            elif 'movimentacao' in col_lower or 'movimento' in col_lower:
                campos_map['movimentacao'] = col
            elif 'historico' in col_lower:
                campos_map['historico'] = col
            elif 'data' in col_lower:
                campos_map['data'] = col
        
        print(f"\n=== MAPEAMENTO DE CAMPOS ===")
        for campo, coluna in campos_map.items():
            print(f"{campo} -> {coluna}")
        
        # Verifica se todos os campos necessários foram encontrados
        campos_necessarios = ['produto', 'quantidade', 'historico']
        for campo in campos_necessarios:
            if campo not in campos_map:
                print(f"ERRO: Campo '{campo}' não encontrado!")
                return None
        
        # Ordena por produto e data
        if 'data' in campos_map:
            df_sorted = df.sort_values([campos_map['produto'], campos_map['data']])
        else:
            df_sorted = df.sort_values([campos_map['produto']])
        
        # Dicionário para armazenar saldo por produto
        estoque = {}
        
        print(f"\n=== PROCESSANDO {len(df_sorted)} MOVIMENTAÇÕES ===")
        
        # Mostra alguns exemplos de histórico para entender os padrões
        historicos_unicos = df[campos_map['historico']].dropna().unique()[:20]
        print(f"Exemplos de histórico: {historicos_unicos}")
        
        # Processa cada movimentação
        for idx, row in df_sorted.iterrows():
            produto = row[campos_map['produto']]
            if pd.isna(produto):
                continue
                
            produto = str(produto).strip()
            historico = str(row[campos_map['historico']]).upper() if pd.notna(row[campos_map['historico']]) else ''
            quantidade = float(row[campos_map['quantidade']]) if pd.notna(row[campos_map['quantidade']]) else 0
            
            # Tenta identificar movimentação se existe o campo
            movimentacao = ''
            if 'movimentacao' in campos_map:
                movimentacao = str(row[campos_map['movimentacao']]).upper() if pd.notna(row[campos_map['movimentacao']]) else ''
            
            # Se for SALDO INICIAL, zera o estoque e define novo saldo
            if 'SALDO INICIAL' in historico:
                estoque[produto] = quantidade
                if len(estoque) <= 10:  # Mostra apenas os primeiros para não poluir o log
                    print(f"SALDO INICIAL - {produto}: {quantidade}")
            else:
                # Inicializa produto se não existir
                if produto not in estoque:
                    estoque[produto] = 0
                
                # Lógica para determinar se é entrada ou saída
                if 'movimentacao' in campos_map and movimentacao:
                    if 'ENTRADA' in movimentacao or 'E' == movimentacao:
                        estoque[produto] += quantidade
                    elif 'SAIDA' in movimentacao or 'SAÍDA' in movimentacao or 'S' == movimentacao:
                        estoque[produto] -= quantidade
                    else:
                        # Analisa pelo histórico
                        if any(termo in historico for termo in ['COMPRA', 'ENTRADA', 'DEVOLUCAO']):
                            estoque[produto] += quantidade
                        elif any(termo in historico for termo in ['VENDA', 'SAIDA', 'SAÍDA']):
                            estoque[produto] -= quantidade
                        else:
                            # Assume que quantidade positiva é entrada e negativa é saída
                            estoque[produto] += quantidade
                else:
                    # Sem campo movimentação, analisa pelo histórico e quantidade
                    if any(termo in historico for termo in ['COMPRA', 'ENTRADA', 'DEVOLUCAO']):
                        estoque[produto] += quantidade
                    elif any(termo in historico for termo in ['VENDA', 'SAIDA', 'SAÍDA']):
                        estoque[produto] -= quantidade
                    else:
                        # Assume que quantidade positiva é entrada e negativa é saída
                        estoque[produto] += quantidade
        
        # Cria DataFrame com o resultado
        resultado = pd.DataFrame([
            {'produto': produto, 'saldo_01_01_2025': saldo}
            for produto, saldo in estoque.items()
        ])
        
        # Ordena por produto
        resultado = resultado.sort_values('produto')
        
        # Salva em CSV
        nome_arquivo = f'estoque_01_01_2025_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
        resultado.to_csv(nome_arquivo, index=False, encoding='utf-8-sig')
        
        print(f"\n=== RELATÓRIO GERADO ===")
        print(f"Arquivo: {nome_arquivo}")
        print(f"Total de produtos: {len(resultado)}")
        print(f"Produtos com estoque positivo: {len(resultado[resultado['saldo_01_01_2025'] > 0])}")
        print(f"Produtos com estoque negativo: {len(resultado[resultado['saldo_01_01_2025'] < 0])}")
        print(f"Produtos com estoque zero: {len(resultado[resultado['saldo_01_01_2025'] == 0])}")
        
        print(f"\nPrimeiros 10 produtos:")
        print(resultado.head(10))
        
        print(f"\nProdutos com maior estoque:")
        print(resultado.nlargest(5, 'saldo_01_01_2025'))
        
        return nome_arquivo
        
    except Exception as e:
        print(f"Erro ao processar estoque: {e}")
        import traceback
        traceback.print_exc()
        return None

def processar_estoque_completo(nome_tabela):
    """Processa o estoque completo com a lógica de saldo inicial"""
    conn = conectar_access()
    if not conn:
        return
    
    try:
        cursor = conn.cursor()
        
        # Busca todas as movimentações até 01/01/2025
        data_corte = datetime(2025, 1, 1)
        
        query = f"""
        SELECT * FROM [{nome_tabela}]
        WHERE data <= ?
        ORDER BY produto, data
        """
        
        cursor.execute(query, data_corte)
        movimentacoes = cursor.fetchall()
        columns = [column[0] for column in cursor.description]
        
        df = pd.DataFrame(movimentacoes, columns=columns)
        
        # Dicionário para armazenar saldo por produto
        estoque = {}
        
        # Processa cada movimentação
        for _, row in df.iterrows():
            produto = row['produto']  # Ajustar nome do campo conforme necessário
            historico = str(row['historico']).upper() if pd.notna(row['historico']) else ''
            quantidade = float(row['quantidade']) if pd.notna(row['quantidade']) else 0
            movimentacao = str(row['movimentacao']).upper() if pd.notna(row['movimentacao']) else ''
            
            # Se for SALDO INICIAL, zera o estoque e define novo saldo
            if 'SALDO INICIAL' in historico:
                estoque[produto] = quantidade
                print(f"SALDO INICIAL - {produto}: {quantidade}")
            else:
                # Inicializa produto se não existir
                if produto not in estoque:
                    estoque[produto] = 0
                
                # Processa entrada ou saída
                if 'ENTRADA' in movimentacao or 'E' == movimentacao:
                    estoque[produto] += quantidade
                elif 'SAIDA' in movimentacao or 'SAÍDA' in movimentacao or 'S' == movimentacao:
                    estoque[produto] -= quantidade
                else:
                    # Se não especificado, considera a quantidade como está
                    if quantidade > 0:
                        estoque[produto] += quantidade
                    else:
                        estoque[produto] += quantidade  # Pode ser negativo
        
        # Cria DataFrame com o resultado
        resultado = pd.DataFrame([
            {'produto': produto, 'saldo_01_01_2025': saldo}
            for produto, saldo in estoque.items()
        ])
        
        # Ordena por produto
        resultado = resultado.sort_values('produto')
        
        # Salva em CSV
        nome_arquivo = f'estoque_01_01_2025_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
        resultado.to_csv(nome_arquivo, index=False, encoding='utf-8-sig')
        
        print(f"\n=== RELATÓRIO GERADO ===")
        print(f"Arquivo: {nome_arquivo}")
        print(f"Total de produtos: {len(resultado)}")
        print(f"\nResumo do estoque:")
        print(resultado.head(10))
        
        return nome_arquivo
        
    except Exception as e:
        print(f"Erro ao processar estoque: {e}")
        return None
    
    finally:
        conn.close()

if __name__ == "__main__":
    print("=== ANÁLISE DE ESTOQUE - NOTAS FISCAIS ===")
    print("Analisando estrutura do banco de dados...")
    
    # Primeiro analisa a estrutura
    analisar_estrutura_tabela()
    
    print("\n" + "="*50)
    print("Gerando relatório de estoque...")
    
    # Gera o relatório
    gerar_relatorio_estoque()
