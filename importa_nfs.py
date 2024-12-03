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

def limpar_tabelas(pg_conn):
    try:
        cursor_pg = pg_conn.cursor()
        
        print("\nLimpando tabelas do PostgreSQL...")
        
        # Verificar total de registros antes da limpeza
        cursor_pg.execute("SELECT COUNT(*) FROM itens_nf_venda")
        total_itens_antes = cursor_pg.fetchone()[0]
        
        cursor_pg.execute("SELECT COUNT(*) FROM notas_fiscais_venda")
        total_notas_antes = cursor_pg.fetchone()[0]
        
        cursor_pg.execute("SELECT COUNT(*) FROM contas_receber")
        total_contas_antes = cursor_pg.fetchone()[0]
        
        print(f"\nTotal de registros antes da limpeza:")
        print(f"Itens NF Venda: {total_itens_antes}")
        print(f"Notas Fiscais: {total_notas_antes}")
        print(f"Contas a Receber: {total_contas_antes}")
        
        print("\nIniciando processo de limpeza...")
        
        # Desabilitar triggers temporariamente
        cursor_pg.execute("ALTER TABLE contas_receber DISABLE TRIGGER ALL")
        cursor_pg.execute("ALTER TABLE notas_fiscais_venda DISABLE TRIGGER ALL")
        cursor_pg.execute("ALTER TABLE itens_nf_venda DISABLE TRIGGER ALL")
        
        # Limpar as tabelas em ordem
        print("Excluindo contas a receber...")
        cursor_pg.execute("DELETE FROM contas_receber WHERE nota_fiscal_id IS NOT NULL")
        
        print("Excluindo itens de notas fiscais...")
        cursor_pg.execute("DELETE FROM itens_nf_venda")
        
        print("Excluindo notas fiscais...")
        cursor_pg.execute("DELETE FROM notas_fiscais_venda")
        
        # Reabilitar triggers
        cursor_pg.execute("ALTER TABLE contas_receber ENABLE TRIGGER ALL")
        cursor_pg.execute("ALTER TABLE notas_fiscais_venda ENABLE TRIGGER ALL")
        cursor_pg.execute("ALTER TABLE itens_nf_venda ENABLE TRIGGER ALL")
        
        pg_conn.commit()
        print("Tabelas limpas com sucesso!")
        
        # Verificar se as tabelas estão vazias
        cursor_pg.execute("SELECT COUNT(*) FROM itens_nf_venda")
        total_itens = cursor_pg.fetchone()[0]
        
        cursor_pg.execute("SELECT COUNT(*) FROM notas_fiscais_venda")
        total_notas = cursor_pg.fetchone()[0]
        
        cursor_pg.execute("SELECT COUNT(*) FROM contas_receber WHERE nota_fiscal_id IS NOT NULL")
        total_contas = cursor_pg.fetchone()[0]
        
        print(f"\nVerificação após limpeza:")
        print(f"Itens NF Venda: {total_itens}")
        print(f"Notas Fiscais: {total_notas}")
        print(f"Contas a Receber vinculadas a NF: {total_contas}")
        
    except Exception as e:
        print(f"Erro ao limpar tabelas: {str(e)}")
        pg_conn.rollback()
        raise

# O resto do código permanece o mesmo...
def migrar_nfs(access_conn, pg_conn):
    try:
        cursor_access = access_conn.cursor()
        cursor_pg = pg_conn.cursor()
        
        # Primeiro limpar as tabelas
        limpar_tabelas(pg_conn)
        
        print("\nIniciando migração de notas fiscais de venda...")
        
        # Buscar clientes existentes
        cursor_pg.execute("SELECT id FROM clientes")
        clientes_existentes = {str(row[0]) for row in cursor_pg.fetchall()}
        
        # Buscar produtos existentes
        cursor_pg.execute("SELECT id FROM produtos")
        produtos_existentes = {str(row[0]) for row in cursor_pg.fetchall()}
        
        # Migrar notas fiscais
        cursor_access.execute("""
            SELECT 
                NumNFS,
                Data,
                Cliente,
                ValorProdutos,
                ValorFrete,
                TipoFrete,
                Valoricms,
                Valoripi,
                Valortotalnota,
                Transportadora,
                Peso,
                Volume,
                Obs
            FROM NFS
            ORDER BY NumNFS
        """)
        
        notas = cursor_access.fetchall()
        print(f"Total de notas fiscais encontradas: {len(notas)}")
        
        registros_migrados = 0
        notas_ignoradas = 0
        mapeamento_notas = {}
        
        for nota in notas:
            try:
                num_nfs = str(nota[0])
                cliente_id = str(nota[2])
                
                if cliente_id not in clientes_existentes:
                    print(f"Cliente {cliente_id} não encontrado. Pulando nota {num_nfs}")
                    notas_ignoradas += 1
                    continue
                
                tipo_frete = nota[5]
                modalidade_frete = 'C' if tipo_frete == 'CIF' else ('F' if tipo_frete == 'FOB' else 'O')
                
                try:
                    peso = float(nota[10]) if nota[10] else 0.0
                except (ValueError, TypeError):
                    peso = 0.0
                    
                try:
                    volumes = int(float(nota[11])) if nota[11] else 0
                except (ValueError, TypeError):
                    volumes = 0
                
                cursor_pg.execute("""
                    INSERT INTO notas_fiscais_venda (
                        cliente_id,
                        numero_nota,
                        data_emissao,
                        data_saida,
                        valor_total,
                        valor_icms,
                        valor_ipi,
                        valor_frete,
                        observacoes,
                        modalidade_frete,
                        peso_total,
                        volumes,
                        data_cadastro
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    RETURNING id
                """, (
                    int(cliente_id),
                    num_nfs,
                    nota[1],  # Data
                    nota[1],  # Data
                    float(nota[8]) if nota[8] else 0.0,  # Valortotalnota
                    float(nota[6]) if nota[6] else 0.0,  # Valoricms
                    float(nota[7]) if nota[7] else 0.0,  # Valoripi
                    float(nota[4]) if nota[4] else 0.0,  # ValorFrete
                    nota[12],  # Obs
                    modalidade_frete,
                    peso,
                    volumes,
                    datetime.now()
                ))
                
                nota_id = cursor_pg.fetchone()[0]
                mapeamento_notas[num_nfs] = nota_id
                registros_migrados += 1
                
                if registros_migrados % 100 == 0:
                    pg_conn.commit()
                    print(f"Migradas {registros_migrados} notas...")
            
            except Exception as e:
                print(f"Erro ao migrar nota {num_nfs}:")
                print(f"Dados da nota: {nota}")
                print(f"Erro: {str(e)}")
                pg_conn.rollback()
                continue
        
        pg_conn.commit()
        print(f"\nMigração de notas concluída.")
        print(f"Total migrado: {registros_migrados}")
        print(f"Total ignorado: {notas_ignoradas}")
        
        # Migrar itens
        print("\nIniciando migração dos itens...")
        
        cursor_access.execute("""
            SELECT 
                NumNFS,
                Produtos,
                Qtde,
                Valor,
                Total,
                Aliquota,
                PercIpi
            FROM [Itens da NFS]
            ORDER BY CodItemNFS
        """)
        
        itens = cursor_access.fetchall()
        print(f"Total de itens encontrados: {len(itens)}")
        
        itens_migrados = 0
        itens_ignorados = 0
        
        for item in itens:
            try:
                num_nfs = str(item[0])
                produto_id = str(item[1])
                nota_id = mapeamento_notas.get(num_nfs)
                
                if not nota_id:
                    itens_ignorados += 1
                    continue
                    
                if produto_id not in produtos_existentes:
                    print(f"Produto {produto_id} não encontrado. Pulando item da nota {num_nfs}")
                    itens_ignorados += 1
                    continue
                
                valor_total = float(item[4]) if item[4] else 0.0
                aliquota = float(item[5]) if item[5] else 0.0
                perc_ipi = float(item[6]) if item[6] else 0.0
                
                valor_icms = (valor_total * aliquota / 100) if aliquota > 0 else 0.0
                valor_ipi = (valor_total * perc_ipi / 100) if perc_ipi > 0 else 0.0
                
                cursor_pg.execute("""
                    INSERT INTO itens_nf_venda (
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
                    float(item[2]) if item[2] else 0.0,  # Qtde
                    float(item[3]) if item[3] else 0.0,  # Valor
                    valor_total,
                    valor_icms,
                    valor_ipi
                ))
                
                itens_migrados += 1
                if itens_migrados % 100 == 0:
                    pg_conn.commit()
                    print(f"Migrados {itens_migrados} itens...")
            
            except Exception as e:
                print(f"Erro ao migrar item da nota {num_nfs}:")
                print(f"Dados do item: {item}")
                print(f"Erro: {str(e)}")
                pg_conn.rollback()
                continue
        
        pg_conn.commit()
        print(f"\nMigração de itens concluída.")
        print(f"Total migrado: {itens_migrados}")
        print(f"Total ignorado: {itens_ignorados}")
        
        # Verificação final
        cursor_pg.execute("SELECT COUNT(*) FROM notas_fiscais_venda")
        total_notas_pg = cursor_pg.fetchone()[0]
        
        cursor_pg.execute("SELECT COUNT(*) FROM itens_nf_venda")
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
            
        migrar_nfs(access_conn, pg_conn)
        
    except Exception as e:
        print(f"Erro durante o processo: {str(e)}")
    finally:
        if 'access_conn' in locals():
            access_conn.close()
        if 'pg_conn' in locals():
            pg_conn.close()

if __name__ == "__main__":
    main()