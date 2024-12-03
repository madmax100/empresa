# -*- coding: utf-8 -*-
"""
Created on Wed Nov 13 19:56:50 2024

@author: Cirilo
"""
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

def verificar_tabela_contratos_access(access_conn):
    try:
        cursor_access = access_conn.cursor()
        
        print("\nVerificando a estrutura da tabela Contratos no Access...")
        
        # Obter informações sobre as colunas da tabela Contratos
        cursor_access.execute("SELECT * FROM Contratos WHERE 1=0")
        colunas_contratos = [column[0] for column in cursor_access.description]
        
        print("Colunas da tabela Contratos no Access:")
        for coluna in colunas_contratos:
            print(coluna)
        
        return colunas_contratos
        
    except Exception as e:
        print(f"Erro ao verificar a tabela Contratos no Access: {str(e)}")
        raise
    
def corrigir_tabela_contratos_locacao(pg_conn, colunas_contratos):
    try:
        cursor = pg_conn.cursor()
        
        print("\nCorrigindo a tabela contratos_locacao...")
        
        # Verificar se a coluna "status" existe e adicioná-la caso não exista
        cursor.execute("SELECT column_name FROM information_schema.columns WHERE table_name = 'contratos_locacao' AND column_name = 'status'")
        resultado = cursor.fetchone()
        if resultado is None:
            cursor.execute("ALTER TABLE contratos_locacao ADD COLUMN status VARCHAR(20)")
            print("Coluna 'status' adicionada à tabela contratos_locacao.")
        
        # Verificar se as outras colunas existem e adicionar as que estão faltando
        colunas_existentes = []
        cursor.execute("SELECT column_name FROM information_schema.columns WHERE table_name = 'contratos_locacao'")
        for row in cursor.fetchall():
            colunas_existentes.append(row[0])
        
        for coluna in colunas_contratos:
            if coluna.lower() not in colunas_existentes:
                if coluna == 'ValorContrato':
                    cursor.execute(f"ALTER TABLE contratos_locacao ADD COLUMN {coluna.lower()} NUMERIC(10,2)")
                elif coluna == 'Obs':
                    cursor.execute(f"ALTER TABLE contratos_locacao ADD COLUMN {coluna.lower()} VARCHAR(255)")
                elif coluna == 'TipoContrato':
                    cursor.execute(f"ALTER TABLE contratos_locacao ADD COLUMN {coluna.lower()} VARCHAR(20)")
                else:
                    cursor.execute(f"ALTER TABLE contratos_locacao ADD COLUMN {coluna.lower()} VARCHAR(100)")
                print(f"Coluna {coluna} adicionada à tabela contratos_locacao.")
        
        # Remover colunas que não existem mais na tabela Contratos do Access, exceto as colunas com restrições de chave estrangeira
        for coluna in colunas_existentes:
            if coluna not in [c.lower() for c in colunas_contratos]:
                if coluna not in ['id', 'cliente_id']:  # Adicionar outras colunas com restrições de chave estrangeira, se necessário
                    cursor.execute(f"ALTER TABLE contratos_locacao DROP COLUMN {coluna}")
                    print(f"Coluna {coluna} removida da tabela contratos_locacao.")
                else:
                    print(f"A coluna {coluna} não pode ser removida devido a restrições de chave estrangeira.")
        
        pg_conn.commit()
        print("Correções na tabela contratos_locacao concluídas!")
        
    except Exception as e:
        print(f"Erro ao corrigir a tabela contratos_locacao: {str(e)}")
        pg_conn.rollback()
        
def migrar_contratos(access_conn, pg_conn):
    try:
        cursor_access = access_conn.cursor()
        cursor_pg = pg_conn.cursor()
        
        print("\nIniciando migração de contratos...")
        
        # Verificar clientes existentes no PostgreSQL
        cursor_pg.execute("SELECT id FROM clientes")
        clientes_existentes = {str(row[0]) for row in cursor_pg.fetchall()}
        
        # Obter lista de colunas da tabela Contratos do Access
        cursor_access.execute("SELECT * FROM Contratos WHERE 1=0")
        colunas_contratos = [column[0] for column in cursor_access.description]
        
        # Montar a consulta SELECT com todas as colunas
        select_query = "SELECT " + ", ".join(colunas_contratos) + " FROM Contratos ORDER BY Contrato"
        
        # Selecionar contratos do Access
        cursor_access.execute(select_query)
        
        contratos = cursor_access.fetchall()
        print(f"Total de contratos encontrados no Access: {len(contratos)}")
        contratos_migrados = 0
        
        for contrato in contratos:
            pg_conn.rollback()  # Desfazer transações anteriores em caso de erro
            try:
                dados_contrato = {}
                for i, coluna in enumerate(colunas_contratos):
                    if coluna == 'Cliente':
                        cliente_id = str(contrato[i])
                        # Verificar se o cliente existe no PostgreSQL
                        if cliente_id not in clientes_existentes:
                            print(f"Cliente {cliente_id} não encontrado para o contrato {contrato[0]}. Pulando...")
                            break
                        dados_contrato['cliente_id'] = cliente_id
                    elif coluna == 'ValorContrato':
                        dados_contrato['valorcontrato'] = float(contrato[i]) if contrato[i] else 0.0
                    elif coluna == 'Obs':
                        dados_contrato['obs'] = contrato[i]
                    elif coluna == 'TipoContrato':
                        dados_contrato['tipocontrato'] = contrato[i]
                    else:
                        dados_contrato[coluna.lower()] = contrato[i]
                else:
                    # Converter número do contrato para ID (removendo o 'C')
                    try:
                        id_contrato = int(dados_contrato['contrato'].replace('C', ''))
                        dados_contrato['id'] = id_contrato
                    except ValueError:
                        print(f"Erro ao converter número do contrato: {dados_contrato['contrato']}")
                        continue
                    
                    print(f"\nProcessando contrato: {dados_contrato['contrato']}")
                    print(f"ID Contrato: {dados_contrato['id']}")
                    print(f"Cliente ID: {dados_contrato['cliente_id']}")
                    
                    # Remover a coluna "status" dos dados do contrato
                    dados_contrato.pop('status', None)
                    
                    # Montar a consulta INSERT com as colunas e valores
                    colunas = ", ".join(dados_contrato.keys())
                    valores = tuple(dados_contrato.values())
                    placeholders = ", ".join(["%s"] * len(dados_contrato))
                    insert_query = f"INSERT INTO contratos_locacao ({colunas}) VALUES ({placeholders})"
                    
                    # Inserir contrato
                    cursor_pg.execute(insert_query, valores)
                    pg_conn.commit()  # Confirmar a transação para cada contrato
                    
                    contratos_migrados += 1
                    
                    if contratos_migrados % 100 == 0:
                        print(f"Migrados {contratos_migrados} contratos...")
                    
                    print(f"Contrato {dados_contrato['contrato']} migrado com sucesso.")
                    
            except Exception as e:
                print(f"Erro ao migrar contrato {contrato[0]}:")
                print(f"Dados do contrato: {contrato}")
                print(f"Erro: {str(e)}")
                print("Tentando próximo contrato...")
                continue
        
        print(f"\nMigração de contratos concluída!")
        print(f"Total de contratos migrados: {contratos_migrados}")
        
    except Exception as e:
        print(f"Erro durante a migração de contratos: {str(e)}")
        pg_conn.rollback()
        raise

def migrar_itens_contrato(access_conn, pg_conn):
    try:
        cursor_access = access_conn.cursor()
        cursor_pg = pg_conn.cursor()
        
        print("\nIniciando migração de itens do contrato...")
        
        # Selecionar itens do contrato do Access
        cursor_access.execute("""
            SELECT Contrato, Serie, Modelo, Categoria
            FROM [Itens dos Contratos]
            ORDER BY Contrato
        """)
        
        itens_contrato = cursor_access.fetchall()
        print(f"Total de itens do contrato encontrados no Access: {len(itens_contrato)}")
        itens_migrados = 0
        
        for item in itens_contrato:
            pg_conn.rollback()  # Desfazer transações anteriores em caso de erro
            try:
                contrato_codigo = str(item[0])
                serie = str(item[1])
                modelo = str(item[2])
                codigo = str(item[3])
                
                # Verificar se o contrato existe no PostgreSQL com base no código do cliente
                cursor_pg.execute("""
                    SELECT id
                    FROM contratos_locacao 
                    WHERE contrato = %s
                """, (contrato_codigo,))
                resultado = cursor_pg.fetchone()
                
                if resultado:
                    contrato_id = str(resultado[0])
                else:
                    print(f"Contra     to com código de cliente {contrato_codigo} não encontrado. Pulando...")
                    continue
                
                # Verificar se a categoria existe no PostgreSQL
                cursor_pg.execute("SELECT id FROM categorias WHERE codigo = %s", (codigo,))
                resultado = cursor_pg.fetchone()
                
                if resultado:
                    categoria_id = str(resultado[0])
                else:
                    print(f"Categoria {modelo} não encontrada para o item do contrato. Pulando...")
                    continue
                
                # Montar a consulta INSERT com as colunas e valores
                insert_query = """
                    INSERT INTO itens_contrato_locacao (contrato_id, numeroserie, categoria_id)
                    VALUES (%s, %s, %s)
                """
                valores = (contrato_id, serie, categoria_id)
                
                # Inserir item do contrato
                cursor_pg.execute(insert_query, valores)
                pg_conn.commit()  # Confirmar a transação para cada item do contrato
                
                itens_migrados += 1
                
                if itens_migrados % 100 == 0:
                    print(f"Migrados {itens_migrados} itens do contrato...")
                
                print(f"Item do contrato migrado com sucesso.")
                
            except Exception as e:
                print(f"Erro ao migrar item do contrato:")
                print(f"Dados do item: {item}")
                print(f"Erro: {str(e)}")
                print("Tentando próximo item...")
                continue
        
        print(f"\nMigração de itens do contrato concluída!")
        print(f"Total de itens migrados: {itens_migrados}")
        
    except Exception as e:
        print(f"Erro durante a migração de itens do contrato: {str(e)}")
        pg_conn.rollback()
        raise
        
movimentos_path = r"C:\Users\Cirilo\Documents\empresa\Bancos\Cadastros\Cadastros.mdb"
access_conn = conectar_access(movimentos_path)
pg_conn = conectar_postgresql()
        
#colunas_contratos = verificar_tabela_contratos_access(access_conn)
#corrigir_tabela_contratos_locacao(pg_conn, colunas_contratos)
#migrar_contratos(access_conn, pg_conn)
migrar_itens_contrato(access_conn, pg_conn)
