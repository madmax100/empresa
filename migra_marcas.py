import pyodbc
import psycopg2
from datetime import datetime

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
        cursor = pg_conn.cursor()
        
        print("\nLimpando tabelas existentes...")
        
        # Primeiro limpar itens_contrato_locacao devido à chave estrangeira
        cursor.execute("DELETE FROM itens_contrato_locacao")
        print("Tabela itens_contrato_locacao limpa")
        
        # Depois limpar contratos_locacao
        cursor.execute("DELETE FROM contratos_locacao")
        print("Tabela contratos_locacao limpa")
        
        pg_conn.commit()
    except Exception as e:
        print(f"Erro ao limpar tabelas: {str(e)}")
        pg_conn.rollback()
        raise

def migrar_contratos(access_conn, pg_conn):
    try:
        cursor_access = access_conn.cursor()
        cursor_pg = pg_conn.cursor()
        
        print("\nIniciando migração de contratos...")
        
        # Selecionar contratos do Access
        cursor_access.execute("""
            SELECT 
                Contrato,
                Cliente,
                Data,
                Incio,
                Fim,
                ValorContrato,
                Obs,
                TipoContrato
            FROM Contratos
            ORDER BY Contrato
        """)
        
        contratos = cursor_access.fetchall()
        print(f"Total de contratos encontrados no Access: {len(contratos)}")
        contratos_migrados = 0
        mapeamento_ids = {}
        
        for contrato in contratos:
            try:
                contrato_numero = contrato[0]  # Ex: 'C1601'
                cliente_id = contrato[1]
                data_cadastro = contrato[2] if contrato[2] else datetime.now()
                data_inicio = contrato[3] if contrato[3] else data_cadastro
                data_fim = contrato[4] if contrato[4] else None
                valor_total = float(contrato[5]) if contrato[5] else 0.0
                observacoes = contrato[6]
                tipo_contrato = contrato[7]
                
                # Converter número do contrato para ID (removendo o 'C')
                try:
                    id_contrato = int(contrato_numero.replace('C', ''))
                except ValueError:
                    print(f"Erro ao converter número do contrato: {contrato_numero}")
                    continue
                
                print(f"\nProcessando contrato: {contrato_numero}")
                print(f"ID Contrato: {id_contrato}")
                print(f"Cliente ID: {cliente_id}")
                print(f"Data Início: {data_inicio}")
                print(f"Data Fim: {data_fim}")
                print(f"Valor Total: {valor_total}")
                
                # Definir status com base no tipo de contrato
                if tipo_contrato is None:
                    status = 'ATIVO'
                else:
                    status = 'ATIVO'  # Você pode ajustar essa lógica conforme necessário
                
                # Inserir contrato
                cursor_pg.execute("""
                    INSERT INTO contratos_locacao (
                        id,
                        cliente_id,
                        data_inicio,
                        data_fim,
                        valor_total,
                        status,
                        observacoes,
                        data_cadastro
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    RETURNING id
                """, (
                    id_contrato,
                    cliente_id,
                    data_inicio,
                    data_fim,
                    valor_total,
                    status,
                    observacoes,
                    data_cadastro
                ))
                
                novo_id = cursor_pg.fetchone()[0]
                mapeamento_ids[contrato_numero] = novo_id
                contratos_migrados += 1
                
                if contratos_migrados % 100 == 0:
                    pg_conn.commit()
                    print(f"Migrados {contratos_migrados} contratos...")
                
                print(f"Contrato {contrato_numero} migrado com sucesso. ID: {novo_id}")
                
            except Exception as e:
                print(f"Erro ao migrar contrato {contrato_numero}:")
                print(f"Dados do contrato: {contrato}")
                print(f"Erro: {str(e)}")
                print("Tentando próximo contrato...")
                continue
        
        pg_conn.commit()
        print(f"\nMigração de contratos concluída!")
        print(f"Total de contratos migrados: {contratos_migrados}")
        print(f"Total de mapeamentos criados: {len(mapeamento_ids)}")
        
        # Mostrar alguns exemplos do mapeamento
        print("\nExemplos de mapeamento:")
        for k, v in list(mapeamento_ids.items())[:5]:
            print(f"Contrato {k} -> ID {v}")
        
        return mapeamento_ids
        
    except Exception as e:
        print(f"Erro durante a migração de contratos: {str(e)}")
        pg_conn.rollback()
        raise

def migrar_itens_contrato(access_conn, pg_conn, mapeamento_ids):
    try:
        cursor_access = access_conn.cursor()
        cursor_pg = pg_conn.cursor()
        
        print("\nIniciando migração de itens dos contratos...")
        
        cursor_access.execute("""
            SELECT 
                Codigo,
                Contrato,
                Serie,
                Inicio,
                Fim
            FROM [Itens dos Contratos]
            ORDER BY Codigo
        """)
        
        itens = cursor_access.fetchall()
        print(f"Total de itens encontrados: {len(itens)}")
        itens_migrados = 0
        
        for item in itens:
            try:
                codigo = item[0]
                contrato_antigo = item[1]
                numero_serie = str(item[2]).strip() if item[2] else None
                data_inicio = item[3]
                data_fim = item[4]
                
                print(f"\nProcessando item {codigo} do contrato {contrato_antigo}")
                
                # Obter ID do contrato
                contrato_id = mapeamento_ids.get(contrato_antigo)
                if not contrato_id:
                    print(f"Contrato {contrato_antigo} não encontrado. Pulando item.")
                    continue
                
                # Buscar produto pelo número de série
                if numero_serie:
                    cursor_pg.execute(
                        "SELECT id FROM produtos WHERE codigo = %s",
                        (numero_serie,)
                    )
                    resultado = cursor_pg.fetchone()
                    
                    if resultado:
                        produto_id = resultado[0]
                        
                        # Calcular dias de locação
                        if data_inicio and data_fim:
                            dias_locacao = (data_fim - data_inicio).days
                        else:
                            dias_locacao = 30  # valor padrão
                        
                        # Inserir item do contrato
                        cursor_pg.execute("""
                            INSERT INTO itens_contrato_locacao (
                                contrato_id, produto_id, quantidade,
                                dias_locacao, valor_diaria, valor_total
                            ) VALUES (%s, %s, %s, %s, %s, %s)
                        """, (
                            contrato_id,
                            produto_id,
                            1,  # quantidade padrão
                            dias_locacao,
                            0.0,  # valor_diaria padrão
                            0.0   # valor_total padrão
                        ))
                        
                        itens_migrados += 1
                        print(f"Item migrado com sucesso!")
                    else:
                        print(f"Produto com número de série {numero_serie} não encontrado. Pulando item.")
                        continue
                else:
                    print("Número de série não encontrado. Pulando item.")
                    continue
                
                if itens_migrados % 100 == 0:
                    pg_conn.commit()
                    print(f"Migrados {itens_migrados} itens...")
                
            except Exception as e:
                print(f"Erro ao migrar item {codigo}:")
                print(f"Erro: {str(e)}")
                continue
        
        pg_conn.commit()
        print(f"\nMigração de itens concluída! Total migrado: {itens_migrados}")
        
    except Exception as e:
        print(f"Erro durante a migração de itens: {str(e)}")
        pg_conn.rollback()
        raise

def verificar_clientes(access_conn, pg_conn):
    try:
        cursor_access = access_conn.cursor()
        cursor_pg = pg_conn.cursor()
        
        # Verificar clientes no Access
        print("\nVerificando clientes no Access...")
        cursor_access.execute("""
            SELECT DISTINCT Cliente 
            FROM Contratos 
            WHERE Cliente IS NOT NULL
            ORDER BY Cliente
        """)
        
        clientes_access = cursor_access.fetchall()
        clientes_access_set = {row[0] for row in clientes_access}
        
        # Verificar clientes no PostgreSQL
        print("\nVerificando clientes no PostgreSQL...")
        cursor_pg.execute("SELECT id FROM clientes ORDER BY id")
        clientes_pg = cursor_pg.fetchall()
        clientes_pg_set = {row[0] for row in clientes_pg}
        
        # Análise
        print(f"\nTotal de clientes únicos no Access: {len(clientes_access_set)}")
        print(f"Total de clientes no PostgreSQL: {len(clientes_pg_set)}")
        
        # Encontrar clientes que estão no Access mas não no PostgreSQL
        clientes_faltando = clientes_access_set - clientes_pg_set
        
        print("\nPrimeiros 20 clientes do Access que não existem no PostgreSQL:")
        for cliente_id in sorted(list(clientes_faltando))[:20]:
            print(f"Cliente ID: {cliente_id}")
        
        return clientes_access_set, clientes_pg_set
        
    except Exception as e:
        print(f"Erro durante a verificação: {str(e)}")
        raise

def main():
    try:
        movimentos_path = r"C:\Users\Cirilo\Documents\empresa\Bancos\Cadastros\Cadastros.mdb"
        access_conn = conectar_access(movimentos_path)
        pg_conn = conectar_postgresql()
        
        if not access_conn or not pg_conn:
            print("Erro ao conectar aos bancos de dados.")
            return
        
        # Verificar clientes antes de tentar migrar
        clientes_access, clientes_pg = verificar_clientes(access_conn, pg_conn)
        
        print("\nDeseja prosseguir com a migração? (s/n)")
        resposta = input().lower()
        
        if resposta == 's':
            # Limpar tabelas existentes
            limpar_tabelas(pg_conn)
            
            # Migrar contratos
            mapeamento_ids = migrar_contratos(access_conn, pg_conn)
            
            # Verificar total de contratos migrados
            cursor_pg = pg_conn.cursor()
            cursor_pg.execute("SELECT COUNT(*) FROM contratos_locacao")
            total_contratos = cursor_pg.fetchone()[0]
            print(f"\nTotal de contratos no PostgreSQL após migração: {total_contratos}")
            
            if total_contratos > 0:
                print("\nDeseja prosseguir com a migração dos itens? (s/n)")
                resposta = input().lower()
                if resposta == 's':
                    migrar_itens_contrato(access_conn, pg_conn, mapeamento_ids)
        
    except Exception as e:
        print(f"Erro durante o processo: {str(e)}")
    finally:
        if 'access_conn' in locals():
            access_conn.close()
        if 'pg_conn' in locals():
            pg_conn.close()

if __name__ == "__main__":
    main()