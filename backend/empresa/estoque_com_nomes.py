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

def testar_tabelas_produtos():
    """Testa a tabela Produtos no banco de cadastros"""
    conn = conectar_access_cadastros()
    if not conn:
        return None
    
    try:
        cursor = conn.cursor()
        
        print("=== ANALISANDO TABELA PRODUTOS NO BANCO CADASTROS ===")
        
        try:
            cursor.execute("SELECT TOP 5 * FROM [Produtos]")
            columns = [column[0] for column in cursor.description]
            rows = cursor.fetchall()
            
            print(f"✓ TABELA 'Produtos' ENCONTRADA")
            print(f"Campos: {columns}")
            print("Primeiros registros:")
            for i, row in enumerate(rows):
                print(f"  {i+1}: {dict(zip(columns, row))}")
            
            # Identifica campos de código e nome
            campo_codigo = None
            campo_nome = None
            
            for col in columns:
                col_lower = col.lower()
                if not campo_codigo and (col_lower in ['codigo', 'cod', 'id', 'produto', 'item'] or 'codigo' in col_lower):
                    campo_codigo = col
                if not campo_nome and ('nome' in col_lower or 'desc' in col_lower or 'denominacao' in col_lower):
                    campo_nome = col
            
            print(f"Campo código identificado: {campo_codigo}")
            print(f"Campo nome identificado: {campo_nome}")
            
            if campo_codigo and campo_nome:
                return 'Produtos', campo_codigo, campo_nome
            elif campo_codigo:
                print(f"Apenas campo código encontrado: {campo_codigo}")
                return 'Produtos', campo_codigo, None
                
        except Exception as e:
            print(f"Erro ao acessar tabela Produtos: {e}")
            return None
        
    except Exception as e:
        print(f"Erro ao testar tabela: {e}")
        return None
    finally:
        conn.close()

def gerar_estoque_com_nomes():
    """Gera estoque com nomes dos produtos"""
    # Primeiro testa as tabelas
    info_tabela = testar_tabelas_produtos()
    
    conn_cadastros = conectar_access_cadastros()
    if not conn_cadastros:
        print("Não foi possível conectar ao banco de cadastros")
        return
    
    try:
        cursor = conn_cadastros.cursor()
        
        # Carrega o estoque já calculado do arquivo anterior
        print("\n=== CARREGANDO ESTOQUE ANTERIOR ===")
        try:
            df_estoque = pd.read_csv('estoque_01_01_2025_20250911_041127.csv')
            print(f"Carregado estoque de {len(df_estoque)} produtos")
        except:
            print("Arquivo de estoque anterior não encontrado. Recalculando...")
            return
        
        # Tenta carregar nomes dos produtos
        nomes_produtos = {}
        
        if info_tabela:
            tabela, campo_codigo, campo_nome = info_tabela
            print(f"\n=== CARREGANDO NOMES DA TABELA {tabela} ===")
            
            try:
                if campo_nome:
                    query = f"SELECT [{campo_codigo}], [{campo_nome}] FROM [{tabela}]"
                else:
                    query = f"SELECT [{campo_codigo}] FROM [{tabela}]"
                
                cursor.execute(query)
                produtos = cursor.fetchall()
                
                print(f"Encontrados {len(produtos)} produtos na tabela")
                
                for row in produtos:
                    codigo = str(row[0]).strip() if row[0] else ''
                    nome = str(row[1]).strip() if len(row) > 1 and row[1] else 'Nome não informado'
                    
                    if codigo:
                        nomes_produtos[codigo] = nome
                
                print(f"Carregados {len(nomes_produtos)} nomes de produtos")
                
                # Mostra alguns exemplos
                print("Exemplos de produtos:")
                for i, (cod, nome) in enumerate(list(nomes_produtos.items())[:5]):
                    print(f"  {cod}: {nome}")
                
            except Exception as e:
                print(f"Erro ao carregar nomes: {e}")
        
        # Cria DataFrame final com nomes
        resultado = []
        produtos_com_nome = 0
        
        for _, row in df_estoque.iterrows():
            codigo = str(int(row['produto'])) if not pd.isna(row['produto']) else ''
            quantidade = row['saldo_01_01_2025']
            
            # Tenta encontrar o nome
            nome = nomes_produtos.get(codigo, 'Nome não encontrado')
            if nome != 'Nome não encontrado':
                produtos_com_nome += 1
            
            resultado.append({
                'codigo': codigo,
                'nome': nome,
                'quantidade': quantidade
            })
        
        df_final = pd.DataFrame(resultado)
        df_final = df_final.sort_values('codigo')
        
        # Salva arquivo final
        nome_arquivo = f'estoque_com_nomes_01_01_2025_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
        df_final.to_csv(nome_arquivo, index=False, encoding='utf-8-sig')
        
        print(f"\n=== RELATÓRIO FINAL GERADO ===")
        print(f"Arquivo: {nome_arquivo}")
        print(f"Total de produtos: {len(df_final)}")
        print(f"Produtos com nome encontrado: {produtos_com_nome}")
        print(f"Produtos sem nome: {len(df_final) - produtos_com_nome}")
        
        # Estatísticas
        print(f"\nEstatísticas:")
        print(f"- Produtos com estoque > 0: {len(df_final[df_final['quantidade'] > 0])}")
        print(f"- Produtos com estoque = 0: {len(df_final[df_final['quantidade'] == 0])}")
        print(f"- Produtos com estoque < 0: {len(df_final[df_final['quantidade'] < 0])}")
        
        print(f"\nPrimeiros 10 produtos:")
        print(df_final.head(10).to_string(index=False))
        
        # Produtos com maior estoque
        print(f"\nTop 5 produtos com maior estoque:")
        top_produtos = df_final.nlargest(5, 'quantidade')
        print(top_produtos.to_string(index=False))
        
        return nome_arquivo
        
    except Exception as e:
        print(f"Erro ao gerar estoque com nomes: {e}")
        import traceback
        traceback.print_exc()
        return None
    
    finally:
        conn_cadastros.close()

if __name__ == "__main__":
    print("=== GERAÇÃO DE ESTOQUE COM NOMES DOS PRODUTOS ===")
    gerar_estoque_com_nomes()
