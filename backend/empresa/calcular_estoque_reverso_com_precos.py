import psycopg2
import pandas as pd
from datetime import datetime, date
import os
from decimal import Decimal
import locale

def formatar_numero_brasileiro(numero):
    """Formata número com vírgula como separador decimal"""
    if isinstance(numero, (int, float)):
        return str(numero).replace('.', ',')
    return str(numero)

def conectar_postgresql():
    """Conecta ao banco PostgreSQL"""
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

def calcular_estoque_reverso_com_precos():
    """Calcula estoque em 31/12/2024 de forma reversa incluindo preços"""
    conn = conectar_postgresql()
    if not conn:
        return
    
    try:
        cursor = conn.cursor()
        
        print("=== CÁLCULO DE ESTOQUE REVERSO COM PREÇOS - 31/12/2024 ===")
        print("="*60)
        
        # Data de referência
        data_referencia = date(2024, 12, 31)
        
        # 1. Busca estoque atual de todos os produtos com preços
        print(f"\n1. BUSCANDO ESTOQUE ATUAL DOS PRODUTOS COM PREÇOS...")
        
        cursor.execute("""
            SELECT p.id, p.codigo, p.referencia, p.nome, p.estoque_atual, p.preco_custo, 
                   COALESCE(g.nome, 'Sem Grupo') as grupo_nome
            FROM produtos p
            LEFT JOIN grupos g ON p.grupo_id = g.id
            WHERE p.ativo = true
            ORDER BY p.codigo
        """)
        
        produtos = cursor.fetchall()
        print(f"Produtos encontrados: {len(produtos)}")
        
        if len(produtos) > 0:
            print("Primeiros 5 produtos:")
            for i, (id_prod, codigo, referencia, nome, estoque, preco_custo, grupo) in enumerate(produtos[:5]):
                valor_atual = float(estoque or 0) * float(preco_custo or 0)
                print(f"  {codigo}: {nome} (Ref: {referencia}) - Grupo: {grupo}")
                print(f"    Estoque atual: {estoque} - Preço custo: R$ {preco_custo} - Valor total: R$ {valor_atual:.2f}")
        else:
            print("Nenhum produto encontrado")
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
        print(f"\n3. PROCESSANDO CÁLCULO REVERSO COM VALORES...")
        
        resultado = []
        produtos_processados = 0
        
        # Para cada produto, parte do estoque atual e retrocede
        for id_prod, codigo, referencia, nome, estoque_atual, preco_custo, grupo in produtos:
            estoque_calculado = float(estoque_atual) if estoque_atual else 0.0
            preco_unitario = float(preco_custo) if preco_custo else 0.0
            
            # Busca movimentações deste produto após 31/12/2024
            movs_produto = [mov for mov in movimentacoes if mov[0] == id_prod]
            
            saldos_redefinidos = 0
            movimentacoes_revertidas = 0
            
            # Processa movimentações em ordem reversa (mais recente para mais antiga)
            for produto_id, data_mov, tipo_mov, quantidade, doc_ref, obs in movs_produto:
                movimentacoes_revertidas += 1
                
                # Se for documento 000000, é uma redefinição de saldo
                if doc_ref == '000000':
                    saldos_redefinidos += 1
                    # Para redefinições, precisamos considerar que o estoque foi zerado
                    # e definido com essa quantidade
                    if tipo_mov == 'E':  # Entrada
                        estoque_calculado -= float(quantidade)
                    else:  # Saída
                        estoque_calculado += float(quantidade)
                else:
                    # Movimentação normal - inverte o efeito
                    if tipo_mov == 'E':  # Era entrada, então reduz do estoque calculado
                        estoque_calculado -= float(quantidade)
                    else:  # Era saída, então adiciona ao estoque calculado
                        estoque_calculado += float(quantidade)
            
            # Calcula valores monetários
            estoque_31_12 = estoque_calculado
            estoque_atual_float = float(estoque_atual) if estoque_atual else 0.0
            diferenca = estoque_atual_float - estoque_31_12
            
            # Valores numéricos para cálculos
            valor_total_31_12 = estoque_31_12 * preco_unitario
            valor_total_atual = estoque_atual_float * preco_unitario
            diferenca_valor = valor_total_atual - valor_total_31_12
            
            resultado.append({
                'codigo': codigo,
                'referencia': referencia,
                'nome': nome,
                'grupo': grupo,
                'estoque_31_12_2024': formatar_numero_brasileiro(round(estoque_31_12, 3)),
                'estoque_atual': formatar_numero_brasileiro(round(estoque_atual_float, 3)),
                'diferenca_quantidade': formatar_numero_brasileiro(round(diferenca, 3)),
                'preco_custo': formatar_numero_brasileiro(round(preco_unitario, 2)),
                'valor_total_31_12_2024': formatar_numero_brasileiro(round(valor_total_31_12, 2)),
                'valor_total_atual': formatar_numero_brasileiro(round(valor_total_atual, 2)),
                'diferenca_valor': formatar_numero_brasileiro(round(diferenca_valor, 2)),
                'movimentacoes_revertidas': movimentacoes_revertidas,
                'saldos_redefinidos': saldos_redefinidos,
                # Valores numéricos para cálculos (não aparecem no CSV)
                '_valor_total_31_12_num': round(valor_total_31_12, 2),
                '_valor_total_atual_num': round(valor_total_atual, 2),
                '_diferenca_valor_num': round(diferenca_valor, 2),
                '_estoque_31_12_num': round(estoque_31_12, 3),
                '_estoque_atual_num': round(estoque_atual_float, 3)
            })
            
            produtos_processados += 1
            if produtos_processados % 500 == 0:
                print(f"    Processados {produtos_processados} produtos...")
        
        print(f"Total de produtos processados: {produtos_processados}")
        
        # 4. Gera arquivo CSV com timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        nome_arquivo = f"estoque_31_12_2024_com_precos_{timestamp}.csv"
        
        df_resultado = pd.DataFrame(resultado)
        df_resultado = df_resultado.sort_values('codigo')
        
        # Remove colunas auxiliares antes de salvar o CSV
        colunas_csv = [col for col in df_resultado.columns if not col.startswith('_')]
        df_csv = df_resultado[colunas_csv]
        df_csv.to_csv(nome_arquivo, index=False, encoding='utf-8-sig', sep=';')
        
        print(f"\n=== RELATÓRIO GERADO COM PREÇOS ===")
        print(f"Arquivo: {nome_arquivo}")
        print(f"Total de produtos: {len(df_resultado)}")
        
        # Cálculos de resumo usando valores numéricos
        total_valor_31_12 = df_resultado['_valor_total_31_12_num'].sum()
        total_valor_atual = df_resultado['_valor_total_atual_num'].sum()
        diferenca_total_valor = df_resultado['_diferenca_valor_num'].sum()
        
        print(f"\nResumo de valores:")
        print(f"- Valor total do estoque em 31/12/2024: R$ {total_valor_31_12:,.2f}".replace('.', 'TEMP').replace(',', '.').replace('TEMP', ','))
        print(f"- Valor total do estoque atual: R$ {total_valor_atual:,.2f}".replace('.', 'TEMP').replace(',', '.').replace('TEMP', ','))
        print(f"- Diferença de valor: R$ {diferenca_total_valor:,.2f}".replace('.', 'TEMP').replace(',', '.').replace('TEMP', ','))
        
        print(f"\nPrimeiros 10 produtos:")
        colunas_exibir = ['codigo', 'referencia', 'nome', 'grupo', 'estoque_31_12_2024', 'estoque_atual', 'preco_custo', 'valor_total_31_12_2024', 'valor_total_atual']
        print(df_csv.head(10)[colunas_exibir].to_string(index=False))
        
        print(f"\nEstatísticas do estoque em 31/12/2024:")
        produtos_com_estoque = len(df_resultado[df_resultado['_estoque_31_12_num'] > 0])
        produtos_sem_estoque = len(df_resultado[df_resultado['_estoque_31_12_num'] == 0])
        produtos_negativo = len(df_resultado[df_resultado['_estoque_31_12_num'] < 0])
        
        print(f"- Produtos com estoque > 0: {produtos_com_estoque}")
        print(f"- Produtos com estoque = 0: {produtos_sem_estoque}")
        print(f"- Produtos com estoque < 0: {produtos_negativo}")
        
        print(f"\nTotal de movimentações revertidas: {df_resultado['movimentacoes_revertidas'].sum()}")
        print(f"Total de saldos redefinidos (doc 000000): {df_resultado['saldos_redefinidos'].sum()}")
        
        # Produtos com maior diferença de valor
        print(f"\nProdutos com maior diferença de valor (atual - 31/12/2024):")
        maiores_diferencas = df_resultado.nlargest(5, '_diferenca_valor_num')
        colunas_diferenca = ['codigo', 'referencia', 'nome', 'grupo', 'diferenca_quantidade', 'preco_custo', 'diferenca_valor']
        print(df_csv.loc[maiores_diferencas.index][colunas_diferenca].to_string(index=False))
        
        return nome_arquivo
        
    except Exception as e:
        print(f"Erro no cálculo reverso: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        conn.close()

def main():
    """Função principal"""
    print("=== CÁLCULO DE ESTOQUE REVERSO COM PREÇOS - PostgreSQL ===")
    print("Data de referência: 31/12/2024")
    print("Método: Reverso (do estoque atual para trás)")
    print("Inclui: Preço de custo e valores totais")
    print("="*60)
    
    # Calcula o estoque com preços
    calcular_estoque_reverso_com_precos()

if __name__ == "__main__":
    main()
