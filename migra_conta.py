# -*- coding: utf-8 -*-
"""
Created on Fri Nov 15 08:33:05 2024

@author: Cirilo
"""

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




def analisar_estrutura_contas(access_conn, pg_conn):
    try:
        cursor_access = access_conn.cursor()
        cursor_pg = pg_conn.cursor()
        
        print("\nAnalisando estruturas das tabelas de contas...\n")
        
        # Analisar estrutura Contas a Pagar no Access
        print("=== Tabela de Contas a Pagar (Access) ===")
        cursor_access.execute("SELECT TOP 1 * FROM [Pagar]")
        colunas_pagar = cursor_access.description
        print("\nEstrutura da tabela Contas a Pagar:")
        for col in colunas_pagar:
            print(f"- {col[0]}: {str(col[1])} (Nullable: {col[6]})")
        
        # Exemplo de conta a pagar
        print("\n=== Exemplo de Conta a Pagar ===")
        cursor_access.execute("SELECT TOP 1 * FROM [Pagar] ORDER BY [CodConta a Pagar] DESC")
        exemplo_pagar = cursor_access.fetchone()
        if exemplo_pagar:
            for i, col in enumerate(colunas_pagar):
                print(f"{col[0]}: {exemplo_pagar[i]}")
        
        # Analisar estrutura Contas a Receber no Access
        print("\n=== Tabela de Contas a Receber (Access) ===")
        cursor_access.execute("SELECT TOP 1 * FROM [Receber]")
        colunas_receber = cursor_access.description
        print("\nEstrutura da tabela Contas a Receber:")
        for col in colunas_receber:
            print(f"- {col[0]}: {str(col[1])} (Nullable: {col[6]})")
        
        # Exemplo de conta a receber
        print("\n=== Exemplo de Conta a Receber ===")
        cursor_access.execute("SELECT TOP 1 * FROM [Receber] ORDER BY [CodConta a Receber] DESC")
        exemplo_receber = cursor_access.fetchone()
        if exemplo_receber:
            for i, col in enumerate(colunas_receber):
                print(f"{col[0]}: {exemplo_receber[i]}")
        
        # Estatísticas
        print("\n=== Estatísticas das Contas ===")
        cursor_access.execute("SELECT COUNT(*) FROM [Pagar]")
        total_pagar = cursor_access.fetchone()[0]
        print(f"Total de Contas a Pagar no Access: {total_pagar}")
        
        cursor_access.execute("SELECT COUNT(*) FROM [Receber]")
        total_receber = cursor_access.fetchone()[0]
        print(f"Total de Contas a Receber no Access: {total_receber}")
        
        # Estrutura PostgreSQL
        print("\n=== Estrutura no PostgreSQL ===")
        print("\nTabela contas_pagar:")
        cursor_pg.execute("""
            SELECT 
                column_name, 
                data_type, 
                is_nullable,
                character_maximum_length,
                column_default
            FROM information_schema.columns
            WHERE table_name = 'contas_pagar'
            ORDER BY ordinal_position;
        """)
        for col in cursor_pg.fetchall():
            print(f"- {col[0]}: {col[1]}" + 
                  (f" ({col[3]} caracteres)" if col[3] else "") +
                  f" (Nullable: {col[2]}, Default: {col[4]})")

        print("\nTabela contas_receber:")
        cursor_pg.execute("""
            SELECT 
                column_name, 
                data_type, 
                is_nullable,
                character_maximum_length,
                column_default
            FROM information_schema.columns
            WHERE table_name = 'contas_receber'
            ORDER BY ordinal_position;
        """)
        for col in cursor_pg.fetchall():
            print(f"- {col[0]}: {col[1]}" + 
                  (f" ({col[3]} caracteres)" if col[3] else "") +
                  f" (Nullable: {col[2]}, Default: {col[4]})")
        
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
              AND (tc.table_name = 'contas_pagar' 
                   OR tc.table_name = 'contas_receber');
        """)
        print("\nChaves estrangeiras encontradas:")
        for dep in cursor_pg.fetchall():
            print(f"Tabela: {dep[0]} -> Campo: {dep[2]} -> Referencia: {dep[3]}.{dep[4]}")
        
        # Verificar registros existentes
        print("\n=== Contagens no PostgreSQL ===")
        cursor_pg.execute("SELECT COUNT(*) FROM contas_pagar")
        total_pagar_pg = cursor_pg.fetchone()[0]
        print(f"Total de Contas a Pagar: {total_pagar_pg}")
        
        cursor_pg.execute("SELECT COUNT(*) FROM contas_receber")
        total_receber_pg = cursor_pg.fetchone()[0]
        print(f"Total de Contas a Receber: {total_receber_pg}")
        
        # Verificar totais de entidades relacionadas
        print("\n=== Totais de Entidades Relacionadas ===")
        cursor_pg.execute("SELECT COUNT(*) FROM fornecedores")
        total_fornecedores = cursor_pg.fetchone()[0]
        print(f"Total de Fornecedores: {total_fornecedores}")
        
        cursor_pg.execute("SELECT COUNT(*) FROM clientes")
        total_clientes = cursor_pg.fetchone()[0]
        print(f"Total de Clientes: {total_clientes}")
        
        cursor_pg.execute("SELECT COUNT(*) FROM contratos")
        total_contratos = cursor_pg.fetchone()[0]
        print(f"Total de Contratos: {total_contratos}")
        
    except Exception as e:
        print(f"Erro durante a análise: {str(e)}")
        import traceback
        print(f"Traceback completo:\n{traceback.format_exc()}")

def limpar_tabelas_contas(pg_conn):
    try:
        cursor_pg = pg_conn.cursor()
        
        print("\nLimpando tabelas do PostgreSQL...")
        print("Desabilitando triggers...")
        
        # Lista de tabelas para desabilitar triggers
        tabelas = [
            'contas_pagar',
            'contas_receber'
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
        
        # Limpar tabelas
        print("\nLimpando tabelas...")
        for tabela in tabelas:
            cursor_pg.execute(f"TRUNCATE TABLE {tabela}")
            print(f"Tabela {tabela} limpa")
        
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

def get_descricao_padrao(historico, documento, tipo_conta='pagar'):
    """Retorna uma descrição padrão para a conta quando o histórico é nulo"""
    if historico:
        return historico
    elif documento:
        return f"Documento: {documento}"
    else:
        return f"Conta a {tipo_conta}" 

def get_status_padrao(status_original, tipo_conta='pagar'):
    """Retorna um status válido baseado no status original"""
    if status_original == 'P':
        return 'PAGO' if tipo_conta == 'pagar' else 'RECEBIDO'
    elif status_original == 'B':
        return 'BAIXADO'
    else:
        return 'ABERTO'

def get_status_conta(status_original, data_pagamento=None):
    """
    Determina o status correto da conta baseado no status original e data de pagamento
    """
    if status_original == 'P' or data_pagamento:
        return 'PAGO'
    elif status_original == 'B':
        return 'BAIXADO'
    elif status_original == 'C':
        return 'CANCELADO'
    else:
        return 'EM_ABERTO'  # Mudando de ABERTO para EM_ABERTO

def migrar_contas_pagar(access_conn, pg_conn):
    try:
        cursor_access = access_conn.cursor()
        cursor_pg = pg_conn.cursor()
        
        print("\nMigrando contas a pagar...")
        
        # Buscar fornecedores existentes
        cursor_pg.execute("SELECT id FROM fornecedores")
        fornecedores_existentes = {str(row[0]) for row in cursor_pg.fetchall()}
        
        # Migrar contas a pagar
        cursor_access.execute("SELECT * FROM [Pagar] ORDER BY [CodConta a Pagar]")
        contas_pagar = cursor_access.fetchall()
        colunas_pagar = [column[0] for column in cursor_access.description]
        
        idx_pagar = {
            'CodConta a Pagar': colunas_pagar.index('CodConta a Pagar'),
            'Data': colunas_pagar.index('Data'),
            'Valor': colunas_pagar.index('Valor'),
            'Fornecedor': colunas_pagar.index('Fornecedor'),
            'Vencimento': colunas_pagar.index('Vencimento'),
            'ValorTotalPago': colunas_pagar.index('ValorTotalPago'),
            'Historico': colunas_pagar.index('Historico'),
            'FormaPagto': colunas_pagar.index('FormaPagto'),
            'DataPagto': colunas_pagar.index('DataPagto'),
            'ValorPago': colunas_pagar.index('ValorPago'),
            'Juros': colunas_pagar.index('Juros'),
            'Status': colunas_pagar.index('Status'),
            'NDuplicata': colunas_pagar.index('NDuplicata')
        }
        
        total_pagar = len(contas_pagar)
        print(f"Total de contas a pagar encontradas: {total_pagar}")
        
        pagar_migradas = 0
        pagar_ignoradas = 0
        lote_atual = []
        
        for conta in contas_pagar:
            try:
                cod_conta = conta[idx_pagar['CodConta a Pagar']]
                fornecedor_id = str(conta[idx_pagar['Fornecedor']]) if conta[idx_pagar['Fornecedor']] else None
                
                # Valores
                valor = float(conta[idx_pagar['Valor']]) if conta[idx_pagar['Valor']] else 0.0
                valor_pago = float(conta[idx_pagar['ValorPago']]) if conta[idx_pagar['ValorPago']] else 0.0
                juros = float(conta[idx_pagar['Juros']]) if conta[idx_pagar['Juros']] else 0.0
                
                # Status
                # Status - Atualizado
                status_original = conta[idx_pagar['Status']]
                data_pagamento = conta[idx_pagar['DataPagto']]
                status = get_status_conta(status_original, data_pagamento)
                
                # Descrição
                historico = conta[idx_pagar['Historico']]
                nduplicata = conta[idx_pagar['NDuplicata']]
                descricao = historico if historico else (f"Documento: {nduplicata}" if nduplicata else "Conta a pagar")
                
                # Datas
                data_cadastro = conta[idx_pagar['Data']] if conta[idx_pagar['Data']] else datetime.now()
                data_vencimento = conta[idx_pagar['Vencimento']] if conta[idx_pagar['Vencimento']] else data_cadastro
                
                # Preparar dados para inserção
                dados_conta = (
                    int(fornecedor_id) if fornecedor_id in fornecedores_existentes else None,
                    descricao,
                    valor,
                    data_vencimento,
                    conta[idx_pagar['DataPagto']],
                    valor_pago,
                    juros,
                    status,  # Status atualizado
                    conta[idx_pagar['FormaPagto']],
                    data_cadastro
                )
                
                lote_atual.append(dados_conta)
                
                # Commit a cada 100 registros
                if len(lote_atual) >= 100:
                    try:
                        # Criar nova transação
                        with pg_conn.cursor() as cursor_lote:
                            for dados in lote_atual:
                                cursor_lote.execute("""
                                    INSERT INTO contas_pagar (
                                        fornecedor_id,
                                        descricao,
                                        valor,
                                        data_vencimento,
                                        data_pagamento,
                                        valor_pago,
                                        juros,
                                        status,
                                        forma_pagamento,
                                        data_cadastro
                                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                                """, dados)
                            
                        pg_conn.commit()
                        pagar_migradas += len(lote_atual)
                        print(f"Migradas {pagar_migradas} contas a pagar...")
                        lote_atual = []
                        
                    except Exception as e:
                        print(f"Erro ao migrar lote de contas a pagar:")
                        print(f"Erro: {str(e)}")
                        pg_conn.rollback()
                        lote_atual = []
                        continue
            
            except Exception as e:
                print(f"Erro ao preparar conta a pagar {cod_conta}:")
                print(f"Dados da conta: {conta}")
                print(f"Erro: {str(e)}")
                continue
        
        # Migrar último lote
        if lote_atual:
            try:
                with pg_conn.cursor() as cursor_lote:
                    for dados in lote_atual:
                        cursor_lote.execute("""
                            INSERT INTO contas_pagar (
                                fornecedor_id,
                                descricao,
                                valor,
                                data_vencimento,
                                data_pagamento,
                                valor_pago,
                                juros,
                                status,
                                forma_pagamento,
                                data_cadastro
                            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        """, dados)
                        
                pg_conn.commit()
                pagar_migradas += len(lote_atual)
                
            except Exception as e:
                print(f"Erro ao migrar último lote de contas a pagar:")
                print(f"Erro: {str(e)}")
                pg_conn.rollback()
        
        print(f"\nMigração de contas a pagar concluída.")
        print(f"Total migrado: {pagar_migradas}")
        
        return True
        
    except Exception as e:
        print(f"Erro durante a migração de contas a pagar: {str(e)}")
        pg_conn.rollback()
        return False

def migrar_contas_receber(access_conn, pg_conn):
    try:
        cursor_access = access_conn.cursor()
        cursor_pg = pg_conn.cursor()
        
        print("\nMigrando contas a receber...")
        
        # Buscar clientes existentes
        cursor_pg.execute("SELECT id FROM clientes")
        clientes_existentes = {str(row[0]) for row in cursor_pg.fetchall()}
        
        cursor_access.execute("SELECT * FROM [Receber] ORDER BY [CodConta a Receber]")
        contas_receber = cursor_access.fetchall()
        colunas_receber = [column[0] for column in cursor_access.description]
        
        idx_receber = {
            'CodConta a Receber': colunas_receber.index('CodConta a Receber'),
            'Documento': colunas_receber.index('Documento'),
            'Data': colunas_receber.index('Data'),
            'Valor': colunas_receber.index('Valor'),
            'Cliente': colunas_receber.index('Cliente'),
            'Vencimento': colunas_receber.index('Vencimento'),
            'Historico': colunas_receber.index('Historico'),
            'FormaPagto': colunas_receber.index('FormaPagto'),
            'Recebido': colunas_receber.index('Recebido'),
            'DataPagto': colunas_receber.index('DataPagto'),
            'Juros': colunas_receber.index('Juros'),
            'Status': colunas_receber.index('Status'),
            'Desconto': colunas_receber.index('Desconto')
        }
        
        total_receber = len(contas_receber)
        print(f"Total de contas a receber encontradas: {total_receber}")
        
        receber_migradas = 0
        receber_ignoradas = 0
        lote_atual = []
        
        for conta in contas_receber:
            try:
                cod_conta = conta[idx_receber['CodConta a Receber']]
                cliente_id = str(conta[idx_receber['Cliente']]) if conta[idx_receber['Cliente']] else None
                
                # Valores
                valor = float(conta[idx_receber['Valor']]) if conta[idx_receber['Valor']] else 0.0
                valor_recebido = float(conta[idx_receber['Recebido']]) if conta[idx_receber['Recebido']] else 0.0
                juros = float(conta[idx_receber['Juros']]) if conta[idx_receber['Juros']] else 0.0
                desconto = float(conta[idx_receber['Desconto']]) if conta[idx_receber['Desconto']] else 0.0
                
                # Status
               # Status - Atualizado
                status_original = conta[idx_receber['Status']]
                data_recebimento = conta[idx_receber['DataPagto']]
                status = get_status_conta(status_original, data_recebimento)
                
                
                # Descrição
                historico = conta[idx_receber['Historico']]
                documento = conta[idx_receber['Documento']]
                descricao = historico if historico else (f"Documento: {documento}" if documento else "Conta a receber")
                
                # Datas
                data_cadastro = conta[idx_receber['Data']] if conta[idx_receber['Data']] else datetime.now()
                data_vencimento = conta[idx_receber['Vencimento']] if conta[idx_receber['Vencimento']] else data_cadastro
                
                # Preparar dados para inserção
                dados_conta = (
                    int(cliente_id) if cliente_id in clientes_existentes else None,
                    descricao,
                    valor,
                    data_vencimento,
                    conta[idx_receber['DataPagto']],
                    valor_recebido,
                    juros,
                    desconto,
                    status,  # Status atualizado
                    conta[idx_receber['FormaPagto']],
                    documento,
                    data_cadastro
                )
                
                lote_atual.append(dados_conta)
                
                # Commit a cada 100 registros
                if len(lote_atual) >= 100:
                    try:
                        with pg_conn.cursor() as cursor_lote:
                            for dados in lote_atual:
                                cursor_lote.execute("""
                                    INSERT INTO contas_receber (
                                        cliente_id,
                                        descricao,
                                        valor,
                                        data_vencimento,
                                        data_recebimento,
                                        valor_recebido,
                                        juros,
                                        desconto,
                                        status,
                                        forma_recebimento,
                                        observacoes,
                                        data_cadastro
                                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                                """, dados)
                            
                        pg_conn.commit()
                        receber_migradas += len(lote_atual)
                        print(f"Migradas {receber_migradas} contas a receber...")
                        lote_atual = []
                        
                    except Exception as e:
                        print(f"Erro ao migrar lote de contas a receber:")
                        print(f"Erro: {str(e)}")
                        pg_conn.rollback()
                        lote_atual = []
                        continue
            
            except Exception as e:
                print(f"Erro ao preparar conta a receber {cod_conta}:")
                print(f"Dados da conta: {conta}")
                print(f"Erro: {str(e)}")
                continue
        
        # Migrar último lote
        if lote_atual:
            try:
                with pg_conn.cursor() as cursor_lote:
                    for dados in lote_atual:
                        cursor_lote.execute("""
                            INSERT INTO contas_receber (
                                cliente_id,
                                descricao,
                                valor,
                                data_vencimento,
                                data_recebimento,
                                valor_recebido,
                                juros,
                                desconto,
                                status,
                                forma_recebimento,
                                observacoes,
                                data_cadastro
                            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        """, dados)
                        
                pg_conn.commit()
                receber_migradas += len(lote_atual)
                
            except Exception as e:
                print(f"Erro ao migrar último lote de contas a receber:")
                print(f"Erro: {str(e)}")
                pg_conn.rollback()
        
        print(f"\nMigração de contas a receber concluída.")
        print(f"Total migrado: {receber_migradas}")
        
        return True
        
    except Exception as e:
        print(f"Erro durante a migração de contas a receber: {str(e)}")
        pg_conn.rollback()
        return False
# Resto do código permanece igual...

def main():
    try:
        movimentos_path = r"C:\Users\Cirilo\Documents\empresa\Bancos\contas\contas.mdb"
        access_conn = conectar_access(movimentos_path)
        pg_conn = conectar_postgresql()
        
        if not access_conn or not pg_conn:
            print("Erro ao conectar aos bancos de dados.")
            return
        
        # Limpar tabelas primeiro
        limpar_tabelas_contas(pg_conn)
        
        # Migrar contas a pagar
        if migrar_contas_pagar(access_conn, pg_conn):
            # Se contas a pagar ok, migrar contas a receber
            migrar_contas_receber(access_conn, pg_conn)
        
        # Verificação final
        cursor_pg = pg_conn.cursor()
        cursor_pg.execute("SELECT COUNT(*) FROM contas_pagar")
        total_pagar = cursor_pg.fetchone()[0]
        
        cursor_pg.execute("SELECT COUNT(*) FROM contas_receber")
        total_receber = cursor_pg.fetchone()[0]
        
        print(f"\nVerificação final:")
        print(f"Contas a pagar no PostgreSQL: {total_pagar}")
        print(f"Contas a receber no PostgreSQL: {total_receber}")
        
    except Exception as e:
        print(f"Erro durante o processo: {str(e)}")
    finally:
        if 'access_conn' in locals():
            access_conn.close()
        if 'pg_conn' in locals():
            pg_conn.close()

if __name__ == "__main__":
    main()