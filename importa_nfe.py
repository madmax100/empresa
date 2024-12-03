import pyodbc
import psycopg2
from datetime import datetime
from collections import defaultdict

def conectar_access(movimentos_path):
    try:
        conn_str = (
            r'Driver={Microsoft Access Driver (*.mdb, *.accdb)};'
            f'DBQ={movimentos_path};'
            'PWD=010182;'
        )
        return pyodbc.connect(conn_str)
    except Exception as e:
        print(f"Erro ao conectar ao Access: {str(e)}")
        return None

def conectar_postgresql():
    try:
        pg_config = {
            'dbname': 'c3mcopiasdb',
            'user': 'cirilomax',
            'password': '226cmm100',
            'host': 'localhost',
            'port': '5432'
        }
        return psycopg2.connect(**pg_config)
    except Exception as e:
        print(f"Erro ao conectar ao PostgreSQL: {str(e)}")
        return None



def analisar_estrutura_nfe(access_conn, pg_conn):
    try:
        cursor_access = access_conn.cursor()
        cursor_pg = pg_conn.cursor()
        
        # Análise de fornecedores únicos
        print("\nAnalisando fornecedores únicos...")
        cursor_access.execute("SELECT DISTINCT Fornecedor FROM NFE ORDER BY Fornecedor")
        fornecedores = cursor_access.fetchall()
        total_fornecedores = len(fornecedores)
        print(f"Total de fornecedores distintos: {total_fornecedores}")
        print("Amostra de fornecedores (primeiros 5):")
        for fornecedor in fornecedores[:5]:
            print(f"- {fornecedor[0]}")

        # Análise de produtos únicos
        print("\nAnalisando produtos únicos...")
        cursor_access.execute("SELECT DISTINCT Produtos FROM [Itens da NFE] ORDER BY Produtos")
        produtos = cursor_access.fetchall()
        total_produtos = len(produtos)
        print(f"Total de produtos distintos: {total_produtos}")
        print("Amostra de produtos (primeiros 5):")
        for produto in produtos[:5]:
            print(f"- {produto[0]}")
        
        # Estrutura PostgreSQL
        print("\n=== Estrutura no PostgreSQL ===")
        print("\nTabela notas_fiscais_compra:")
        cursor_pg.execute("""
            SELECT 
                column_name, 
                data_type, 
                is_nullable,
                character_maximum_length,
                column_default
            FROM information_schema.columns
            WHERE table_name = 'notas_fiscais_compra'
            ORDER BY ordinal_position;
        """)
        for col in cursor_pg.fetchall():
            print(f"- {col[0]}: {col[1]}" + 
                  (f" ({col[3]} caracteres)" if col[3] else "") +
                  f" (Nullable: {col[2]}, Default: {col[4]})")

        print("\nTabela itens_nf_compra:")
        cursor_pg.execute("""
            SELECT 
                column_name, 
                data_type, 
                is_nullable,
                character_maximum_length,
                column_default
            FROM information_schema.columns
            WHERE table_name = 'itens_nf_compra'
            ORDER BY ordinal_position;
        """)
        for col in cursor_pg.fetchall():
            print(f"- {col[0]}: {col[1]}" + 
                  (f" ({col[3]} caracteres)" if col[3] else "") +
                  f" (Nullable: {col[2]}, Default: {col[4]})")

        # Verificar tabelas relacionadas no PostgreSQL
        print("\n=== Contagens no PostgreSQL ===")
        cursor_pg.execute("SELECT COUNT(*) FROM fornecedores")
        total_fornecedores_pg = cursor_pg.fetchone()[0]
        print(f"Total de Fornecedores no PostgreSQL: {total_fornecedores_pg}")
        
        cursor_pg.execute("SELECT COUNT(*) FROM produtos")
        total_produtos_pg = cursor_pg.fetchone()[0]
        print(f"Total de Produtos no PostgreSQL: {total_produtos_pg}")
        
        # Verificar dependências
        print("\n=== Verificando dependências no PostgreSQL ===")
        cursor_pg.execute("""
            SELECT 
                tc.table_name, tc.constraint_name, 
                kcu.column_name, 
                ccu.table_name AS foreign_table_name,
                ccu.column_name AS foreign_column_name
            FROM information_schema.table_constraints AS tc 
            JOIN information_schema.key_column_usage AS kcu
              ON tc.constraint_name = kcu.constraint_name
              AND tc.table_schema = kcu.table_schema
            JOIN information_schema.constraint_column_usage AS ccu
              ON ccu.constraint_name = tc.constraint_name
              AND ccu.table_schema = tc.table_schema
            WHERE tc.constraint_type = 'FOREIGN KEY' 
              AND (tc.table_name = 'notas_fiscais_compra' 
                   OR tc.table_name = 'itens_nf_compra'
                   OR ccu.table_name = 'notas_fiscais_compra'
                   OR ccu.table_name = 'itens_nf_compra');
        """)
        print("\nChaves estrangeiras encontradas:")
        for dep in cursor_pg.fetchall():
            print(f"Tabela: {dep[0]} -> Campo: {dep[2]} -> Referencia: {dep[3]}.{dep[4]}")
        
        # Verificar registros existentes
        print("\n=== Registros existentes no PostgreSQL ===")
        cursor_pg.execute("SELECT COUNT(*) FROM notas_fiscais_compra")
        total_nfe_pg = cursor_pg.fetchone()[0]
        print(f"Total de Notas Fiscais de Compra: {total_nfe_pg}")
        
        cursor_pg.execute("SELECT COUNT(*) FROM itens_nf_compra")
        total_itens_pg = cursor_pg.fetchone()[0]
        print(f"Total de Itens de NF Compra: {total_itens_pg}")
        
    except Exception as e:
        print(f"Erro durante a análise: {str(e)}")
        import traceback
        print(f"Traceback completo:\n{traceback.format_exc()}")

def limpar_tabelas_nfe(pg_conn):
    try:
        cursor_pg = pg_conn.cursor()
        
        print("\nLimpando tabelas do PostgreSQL...")
        print("Desabilitando triggers...")
        
        # Lista de tabelas para desabilitar triggers
        tabelas = [
            'contas_pagar',
            'lotes',
            'movimentacoes_estoque',
            'fretes',
            'itens_nf_compra',
            'notas_fiscais_compra'
        ]
        
        # Desabilitar triggers
        for tabela in tabelas:
            cursor_pg.execute(f"ALTER TABLE {tabela} DISABLE TRIGGER ALL")
            print(f"Triggers desabilitados para {tabela}")
        
        # Verificar totais antes da limpeza
        print("\nTotais antes da limpeza:")
        for tabela in tabelas:
            cursor_pg.execute(f"SELECT COUNT(*) FROM {tabela}")
            total = cursor_pg.fetchone()[0]
            print(f"{tabela}: {total} registros")
        
        # Limpar tabelas na ordem correta
        print("\nLimpando tabelas...")
        
        print("Limpando contas a pagar vinculadas...")
        cursor_pg.execute("UPDATE contas_pagar SET nota_fiscal_id = NULL WHERE nota_fiscal_id IS NOT NULL")
        
        print("Limpando lotes...")
        cursor_pg.execute("UPDATE lotes SET nota_fiscal_compra_id = NULL WHERE nota_fiscal_compra_id IS NOT NULL")
        
        print("Limpando movimentações de estoque...")
        cursor_pg.execute("UPDATE movimentacoes_estoque SET nota_fiscal_compra_id = NULL WHERE nota_fiscal_compra_id IS NOT NULL")
        
        print("Limpando fretes...")
        cursor_pg.execute("DELETE FROM fretes WHERE nota_fiscal_compra_id IS NOT NULL")
        
        print("Limpando itens de notas fiscais...")
        cursor_pg.execute("DELETE FROM itens_nf_compra")
        
        print("Limpando notas fiscais...")
        cursor_pg.execute("DELETE FROM notas_fiscais_compra")
        
        # Reabilitar triggers
        print("\nReabilitando triggers...")
        for tabela in tabelas:
            cursor_pg.execute(f"ALTER TABLE {tabela} ENABLE TRIGGER ALL")
            print(f"Triggers reabilitados para {tabela}")
        
        pg_conn.commit()
        
        # Verificar totais após limpeza
        print("\nTotais após limpeza:")
        for tabela in tabelas:
            cursor_pg.execute(f"SELECT COUNT(*) FROM {tabela}")
            total = cursor_pg.fetchone()[0]
            print(f"{tabela}: {total} registros")
        
    except Exception as e:
        print(f"Erro ao limpar tabelas: {str(e)}")
        pg_conn.rollback()
        raise

def migrar_nfe(access_conn, pg_conn):
    try:
        cursor_access = access_conn.cursor()
        cursor_pg = pg_conn.cursor()
        
        print("\nBuscando notas fiscais no Access...")
        
        # Teste simples primeiro
        print("Testando consulta básica...")
        cursor_access.execute("SELECT COUNT(*) FROM NFE")
        total = cursor_access.fetchone()[0]
        print(f"Total de notas encontradas: {total}")
        
        # Buscar fornecedores existentes
        cursor_pg.execute("SELECT id FROM fornecedores")
        fornecedores_existentes = {str(row[0]) for row in cursor_pg.fetchall()}
        
        # Migrar notas fiscais - Consulta simplificada
        print("\nBuscando dados das notas...")
        cursor_access.execute("SELECT * FROM NFE ORDER BY CodNFE")
        notas = cursor_access.fetchall()
        colunas = [column[0] for column in cursor_access.description]
        print(f"Colunas encontradas: {', '.join(colunas)}")
        
        print(f"Processando {len(notas)} notas...")
        
        registros_migrados = 0
        notas_ignoradas = 0
        mapeamento_notas = {}
        
        # Encontrar índices das colunas
        idx = {
            'CodNFE': colunas.index('CodNFE'),
            'NumNFE': colunas.index('NumNFE'),
            'Data': colunas.index('Data'),
            'Fornecedor': colunas.index('Fornecedor'),
            'ValorProdutos': colunas.index('ValorProdutos'),
            'ValorFrete': colunas.index('ValorFrete'),
            'TipoFrete': colunas.index('TipoFrete'),
            'Valoricms': colunas.index('Valoricms'),
            'Valoripi': colunas.index('Valoripi'),
            'Valortotalnota': colunas.index('Valortotalnota'),
            'Observação': colunas.index('Observação'),
            'DataEntrada': colunas.index('DataEntrada'),
            'Serie': colunas.index('Serie')
        }
        
        for nota in notas:
            try:
                cod_nfe = nota[idx['CodNFE']]
                num_nfe = nota[idx['NumNFE']]
                fornecedor_id = str(nota[idx['Fornecedor']])
                
                if fornecedor_id not in fornecedores_existentes:
                    print(f"Fornecedor {fornecedor_id} não encontrado. Pulando nota {num_nfe}")
                    notas_ignoradas += 1
                    continue
                
                tipo_frete = nota[idx['TipoFrete']]
                modalidade_frete = 'C' if tipo_frete == 'CIF' else ('F' if tipo_frete == 'FOB' else 'O')
                
                # Data de entrada, se nula usa data de emissão
                data_emissao = nota[idx['Data']]
                data_entrada = nota[idx['DataEntrada']] if nota[idx['DataEntrada']] else data_emissao
                
                cursor_pg.execute("""
                    INSERT INTO notas_fiscais_compra (
                        fornecedor_id,
                        numero_nota,
                        serie_nota,
                        data_emissao,
                        data_entrada,
                        valor_total,
                        valor_icms,
                        valor_ipi,
                        valor_frete,
                        observacoes,
                        modalidade_frete,
                        data_cadastro
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP)
                    RETURNING id
                """, (
                    int(fornecedor_id),
                    str(num_nfe),
                    str(nota[idx['Serie']]) if nota[idx['Serie']] else '1',
                    data_emissao,
                    data_entrada,
                    float(nota[idx['Valortotalnota']]) if nota[idx['Valortotalnota']] else 0.0,
                    float(nota[idx['Valoricms']]) if nota[idx['Valoricms']] else 0.0,
                    float(nota[idx['Valoripi']]) if nota[idx['Valoripi']] else 0.0,
                    float(nota[idx['ValorFrete']]) if nota[idx['ValorFrete']] else 0.0,
                    nota[idx['Observação']],
                    modalidade_frete
                ))
                
                nota_id = cursor_pg.fetchone()[0]
                mapeamento_notas[num_nfe] = nota_id
                registros_migrados += 1
                
                if registros_migrados % 100 == 0:
                    pg_conn.commit()
                    print(f"Migradas {registros_migrados} notas...")
            
            except Exception as e:
                print(f"Erro ao migrar nota {num_nfe}:")
                print(f"Dados da nota: {nota}")
                print(f"Erro: {str(e)}")
                continue
        
        pg_conn.commit()
        print(f"\nMigração de notas concluída.")
        print(f"Total migrado: {registros_migrados}")
        print(f"Total ignorado: {notas_ignoradas}")
        
        # Migrar itens
        print("\nIniciando migração dos itens...")
        
        # Buscar produtos existentes
        cursor_pg.execute("SELECT id FROM produtos")
        produtos_existentes = {str(row[0]) for row in cursor_pg.fetchall()}
        
        # Consulta simplificada para itens
        print("Buscando itens...")
        cursor_access.execute("SELECT * FROM [Itens da NFE] ORDER BY CodItemNFE")
        itens = cursor_access.fetchall()
        colunas_itens = [column[0] for column in cursor_access.description]
        print(f"Colunas dos itens: {', '.join(colunas_itens)}")
        
        # Encontrar índices das colunas dos itens
        idx_item = {
            'CodItemNFE': colunas_itens.index('CodItemNFE'),
            'NumNFE': colunas_itens.index('NumNFE'),
            'Produtos': colunas_itens.index('Produtos'),
            'Qtde': colunas_itens.index('Qtde'),
            'Valor': colunas_itens.index('Valor'),
            'Total': colunas_itens.index('Total'),
            'Aliquota': colunas_itens.index('Aliquota'),
            'PercIpi': colunas_itens.index('PercIpi')
        }
        
        itens_migrados = 0
        itens_ignorados = 0
        
        for item in itens:
            try:
                cod_item = item[idx_item['CodItemNFE']]
                num_nfe = item[idx_item['NumNFE']]
                produto_id = str(item[idx_item['Produtos']])
                
                nota_id = mapeamento_notas.get(num_nfe)
                if nota_id is None:
                    print(f"Nota fiscal {num_nfe} não encontrada para o item {cod_item}")
                    itens_ignorados += 1
                    continue
                    
                if produto_id not in produtos_existentes:
                    print(f"Produto {produto_id} não encontrado. Pulando item da nota {num_nfe}")
                    itens_ignorados += 1
                    continue
                
                valor_total = float(item[idx_item['Total']]) if item[idx_item['Total']] else 0.0
                aliquota = float(item[idx_item['Aliquota']]) if item[idx_item['Aliquota']] else 0.0
                perc_ipi = float(item[idx_item['PercIpi']]) if item[idx_item['PercIpi']] else 0.0
                
                valor_icms = (valor_total * aliquota / 100) if aliquota > 0 else 0.0
                valor_ipi = (valor_total * perc_ipi / 100) if perc_ipi > 0 else 0.0
                
                cursor_pg.execute("""
                    INSERT INTO itens_nf_compra (
                        nota_fiscal_id,
                        produto_id,
                        quantidade,
                        valor_unitario,
                        valor_total,
                        valor_icms,
                        valor_ipi
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, (
                    nota_id,
                    int(produto_id),
                    float(item[idx_item['Qtde']]) if item[idx_item['Qtde']] else 0.0,
                    float(item[idx_item['Valor']]) if item[idx_item['Valor']] else 0.0,
                    valor_total,
                    valor_icms,
                    valor_ipi
                ))
                
                itens_migrados += 1
                if itens_migrados % 100 == 0:
                    pg_conn.commit()
                    print(f"Migrados {itens_migrados} itens...")
            
            except Exception as e:
                print(f"Erro ao migrar item {cod_item}:")
                print(f"Dados do item: {item}")
                print(f"Erro: {str(e)}")
                continue
        
        pg_conn.commit()
        print(f"\nMigração de itens concluída.")
        print(f"Total migrado: {itens_migrados}")
        print(f"Total ignorado: {itens_ignorados}")
        
        # Verificação final
        cursor_pg.execute("SELECT COUNT(*) FROM notas_fiscais_compra")
        total_notas_pg = cursor_pg.fetchone()[0]
        
        cursor_pg.execute("SELECT COUNT(*) FROM itens_nf_compra")
        total_itens_pg = cursor_pg.fetchone()[0]
        
        print(f"\nVerificação final:")
        print(f"Notas fiscais no PostgreSQL: {total_notas_pg}")
        print(f"Itens de notas no PostgreSQL: {total_itens_pg}")
        
    except Exception as e:
        print(f"Erro durante a migração: {str(e)}")
        pg_conn.rollback()
        raise

def main():
    try:
        movimentos_path = r"C:\Users\Cirilo\Documents\empresa\Bancos\Movimentos\Movimentos.mdb"
        access_conn = conectar_access(movimentos_path)
        pg_conn = conectar_postgresql()
        
        if not access_conn or not pg_conn:
            print("Erro ao conectar aos bancos de dados.")
            return
            
        migrar_nfe(access_conn, pg_conn)
        
    except Exception as e:
        print(f"Erro durante o processo: {str(e)}")
    finally:
        if 'access_conn' in locals():
            access_conn.close()
        if 'pg_conn' in locals():
            pg_conn.close()

if __name__ == "__main__":
    main()