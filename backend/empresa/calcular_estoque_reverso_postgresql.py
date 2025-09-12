import psycopg2
import pandas as pd
from datetime import datetime, date
import os
from decimal import Decimal

def conectar_postgresql        # 1. Busca estoque atual de todos os produtos
        print(f"1. BUSCANDO ESTOQUE ATUAL DOS PRODUTOS...")
        
        cursor.execute("""
            SELECT id, codigo, nome, estoque_atual, preco_custo 
            FROM produtos 
            WHERE ativo = true
            ORDER BY codigo
        """)
        
        produtos = cursor.fetchall()
        print(f"Produtos encontrados: {len(produtos)}")
        
        if len(produtos) > 0:
            print("Primeiros 5 produtos:")
            for i, (id_prod, codigo, nome, estoque, preco_custo) in enumerate(produtos[:5]):
                print(f"  {codigo}: {nome} - Estoque atual: {estoque} - Preço custo: R$ {preco_custo}")
        else:
            print("Nenhum produto com estoque encontrado")
            returnao banco PostgreSQL"""
    try:
        # Configurações do Django
        conn = psycopg2.connect(
            host="localhost",
            database="c3mcopiasdb2",
            user="cirilomax", 
            password="226cmm100",
            port="5432"
        )
        return conn
    except Exception as e:
        print(f"Erro ao conectar ao PostgreSQL: {e}")
        print("Verifique se o PostgreSQL está rodando e as configurações estão corretas!")
        return None

def analisar_estrutura_tabelas():
    """Analisa a estrutura das tabelas de produtos e movimentações"""
    conn = conectar_postgresql()
    if not conn:
        return
    
    try:
        cursor = conn.cursor()
        
        print("=== ANALISANDO ESTRUTURA DAS TABELAS ===")
        print("="*60)
        
        # Verifica tabela de produtos
        print("\n1. TABELA DE PRODUTOS:")
        cursor.execute("""
            SELECT table_name FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name LIKE '%produto%'
            ORDER BY table_name
        """)
        
        tabelas_produtos = cursor.fetchall()
        
        for (tabela,) in tabelas_produtos:
            print(f"   - {tabela}")
            
            # Mostra estrutura da tabela
            cursor.execute(f"""
                SELECT column_name, data_type 
                FROM information_schema.columns 
                WHERE table_name = '{tabela}'
                ORDER BY ordinal_position
            """)
            
            colunas = cursor.fetchall()
            print("     Colunas:")
            for col, tipo in colunas:
                print(f"       {col} ({tipo})")
            
            # Mostra alguns registros
            cursor.execute(f"SELECT COUNT(*) FROM {tabela}")
            total = cursor.fetchone()[0]
            print(f"     Total de registros: {total}")
            
            if total > 0:
                cursor.execute(f"SELECT * FROM {tabela} LIMIT 3")
                registros = cursor.fetchall()
                columns = [desc[0] for desc in cursor.description]
                
                print("     Exemplos:")
                for i, registro in enumerate(registros):
                    print(f"       {i+1}: {dict(zip(columns, registro))}")
        
        # Verifica tabela de movimentações
        print(f"\n2. TABELA DE MOVIMENTAÇÕES:")
        cursor.execute("""
            SELECT table_name FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND (table_name LIKE '%moviment%' OR table_name LIKE '%estoque%')
            ORDER BY table_name
        """)
        
        tabelas_movimentacoes = cursor.fetchall()
        
        for (tabela,) in tabelas_movimentacoes:
            print(f"   - {tabela}")
            
            # Mostra estrutura da tabela
            cursor.execute(f"""
                SELECT column_name, data_type 
                FROM information_schema.columns 
                WHERE table_name = '{tabela}'
                ORDER BY ordinal_position
            """)
            
            colunas = cursor.fetchall()
            print("     Colunas:")
            for col, tipo in colunas:
                print(f"       {col} ({tipo})")
            
            # Mostra alguns registros
            cursor.execute(f"SELECT COUNT(*) FROM {tabela}")
            total = cursor.fetchone()[0]
            print(f"     Total de registros: {total}")
            
            if total > 0:
                cursor.execute(f"SELECT * FROM {tabela} LIMIT 3")
                registros = cursor.fetchall()
                columns = [desc[0] for desc in cursor.description]
                
                print("     Exemplos:")
                for i, registro in enumerate(registros):
                    print(f"       {i+1}: {dict(zip(columns, registro))}")
        
    except Exception as e:
        print(f"Erro na análise: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        conn.close()

def calcular_estoque_reverso():
    """Calcula estoque em 31/12/2024 de forma reversa"""
    conn = conectar_postgresql()
    if not conn:
        return
    
    try:
        cursor = conn.cursor()
        
        print("=== CALCULANDO ESTOQUE REVERSO PARA 31/12/2024 ===")
        print("="*60)
        
        # Data de referência
        data_referencia = date(2024, 12, 31)
        
        # 1. Busca estoque atual de todos os produtos
        print("\n1. BUSCANDO ESTOQUE ATUAL DOS PRODUTOS...")
        
        cursor.execute("""
            SELECT id, codigo, nome, estoque_atual 
            FROM produtos 
            WHERE estoque_atual IS NOT NULL
            ORDER BY codigo
        """)
        
        produtos = cursor.fetchall()
        print(f"Produtos encontrados: {len(produtos)}")
        
        if len(produtos) > 0:
            print("Primeiros 5 produtos:")
            for i, (id_prod, codigo, nome, estoque) in enumerate(produtos[:5]):
                print(f"  {codigo}: {nome} - Estoque atual: {estoque}")
        else:
            print("Nenhum produto com estoque encontrado")
            return
        
        # 2. Busca movimentações após 31/12/2024
        print(f"\n2. BUSCANDO MOVIMENTAÇÕES APÓS 31/12/2024...")
        
        cursor.execute("""
            SELECT me.produto_id, me.data_movimentacao, tme.tipo, me.quantidade, 
                   me.documento_referencia, me.observacoes
            FROM movimentacoes_estoque me
            JOIN tipos_movimentacao_estoque tme ON me.tipo_movimentacao_id = tme.id
            WHERE DATE(me.data_movimentacao) > %s
            ORDER BY me.produto_id, me.data_movimentacao DESC, me.id DESC
        """, (data_referencia,))
        
        movimentacoes = cursor.fetchall()
        print(f"Movimentações encontradas após 31/12/2024: {len(movimentacoes)}")
        
        if len(movimentacoes) > 0:
            print("Primeiras 5 movimentações:")
            for i, mov in enumerate(movimentacoes[:5]):
                produto_id, data_mov, tipo_mov, quantidade, doc_ref, obs = mov
                print(f"  Produto {produto_id}: {data_mov} - {tipo_mov} - Qtd: {quantidade} - Doc: {doc_ref}")
        
        # 3. Processa o cálculo reverso
        print(f"\n3. PROCESSANDO CÁLCULO REVERSO...")
        
        estoque_31_12_2024 = {}
        produtos_processados = 0
        
        # Para cada produto, parte do estoque atual e retrocede
        for id_prod, codigo, nome, estoque_atual in produtos:
            estoque_calculado = float(estoque_atual) if estoque_atual else 0.0
            estoque_original = estoque_calculado
            
            # Busca movimentações deste produto após 31/12/2024
            movs_produto = [mov for mov in movimentacoes if mov[0] == id_prod]
            
            saldos_redefinidos = 0
            movimentacoes_revertidas = 0
            
            # Processa movimentações em ordem reversa (mais recente para mais antiga)
            for produto_id, data_mov, tipo_mov, quantidade, doc_ref, obs in movs_produto:
                quantidade_val = float(quantidade) if quantidade else 0.0
                
                # Se documento for 000000, ignora movimentações e define novo saldo
                if str(doc_ref) == '000000':
                    estoque_calculado = quantidade_val
                    saldos_redefinidos += 1
                    if produtos_processados < 5:  # Mostra detalhes dos primeiros produtos
                        print(f"    {codigo}: Saldo redefinido em {data_mov} para {quantidade_val}")
                else:
                    # Reverte a movimentação
                    if tipo_mov == 'E':  # Era entrada
                        estoque_calculado -= quantidade_val  # Subtrai para reverter
                        if produtos_processados < 5:
                            print(f"    {codigo}: Revertendo entrada de {quantidade_val} em {data_mov}")
                    elif tipo_mov == 'S':  # Era saída
                        estoque_calculado += quantidade_val  # Soma para reverter
                        if produtos_processados < 5:
                            print(f"    {codigo}: Revertendo saída de {quantidade_val} em {data_mov}")
                    
                    movimentacoes_revertidas += 1
            
            estoque_31_12_2024[codigo] = {
                'id': id_prod,
                'nome': nome,
                'estoque_31_12_2024': estoque_calculado,
                'estoque_atual': estoque_original,
                'movimentacoes_revertidas': movimentacoes_revertidas,
                'saldos_redefinidos': saldos_redefinidos
            }
            
            produtos_processados += 1
            if produtos_processados % 500 == 0:
                print(f"    Processados {produtos_processados} produtos...")
        
        print(f"Total de produtos processados: {produtos_processados}")
        
        # 4. Gera relatório CSV
        nome_arquivo = f'estoque_31_12_2024_reverso_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
        
        resultado = []
        for codigo, dados in estoque_31_12_2024.items():
            resultado.append({
                'codigo': codigo,
                'nome': dados['nome'],
                'estoque_31_12_2024': dados['estoque_31_12_2024'],
                'estoque_atual': dados['estoque_atual'],
                'diferenca': dados['estoque_atual'] - dados['estoque_31_12_2024'],
                'movimentacoes_revertidas': dados['movimentacoes_revertidas'],
                'saldos_redefinidos': dados['saldos_redefinidos']
            })
        
        df_resultado = pd.DataFrame(resultado)
        df_resultado = df_resultado.sort_values('codigo')
        df_resultado.to_csv(nome_arquivo, index=False, encoding='utf-8-sig')
        
        print(f"\n=== RELATÓRIO GERADO ===")
        print(f"Arquivo: {nome_arquivo}")
        print(f"Total de produtos: {len(df_resultado)}")
        
        print(f"\nPrimeiros 10 produtos:")
        print(df_resultado.head(10)[['codigo', 'nome', 'estoque_31_12_2024', 'estoque_atual', 'diferenca']].to_string(index=False))
        
        print(f"\nEstatísticas do estoque em 31/12/2024:")
        print(f"- Produtos com estoque > 0: {len(df_resultado[df_resultado['estoque_31_12_2024'] > 0])}")
        print(f"- Produtos com estoque = 0: {len(df_resultado[df_resultado['estoque_31_12_2024'] == 0])}")
        print(f"- Produtos com estoque < 0: {len(df_resultado[df_resultado['estoque_31_12_2024'] < 0])}")
        
        print(f"\nTotal de movimentações revertidas: {df_resultado['movimentacoes_revertidas'].sum()}")
        print(f"Total de saldos redefinidos (doc 000000): {df_resultado['saldos_redefinidos'].sum()}")
        
        # Produtos com maior diferença
        print(f"\nProdutos com maior diferença (atual - 31/12/2024):")
        maiores_diferencas = df_resultado.nlargest(5, 'diferenca')
        print(maiores_diferencas[['codigo', 'nome', 'estoque_31_12_2024', 'estoque_atual', 'diferenca']].to_string(index=False))
        
        return nome_arquivo
        
    except Exception as e:
        print(f"Erro no cálculo reverso: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        conn.close()

def main():
    """Função principal"""
    print("=== CÁLCULO DE ESTOQUE REVERSO - PostgreSQL ===")
    print("Data de referência: 31/12/2024")
    print("Método: Reverso (do estoque atual para trás)")
    print("="*60)
    
    # Primeiro analisa a estrutura
    analisar_estrutura_tabelas()
    
    print("\n" + "="*60)
    
    # Depois calcula o estoque
    calcular_estoque_reverso()

if __name__ == "__main__":
    main()
