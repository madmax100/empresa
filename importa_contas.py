# -*- coding: utf-8 -*-
"""
Created on Wed Nov 13 22:15:37 2024

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
def migrar_contas_pagar(access_conn, pg_conn):
    try:
        cursor_access = access_conn.cursor()
        cursor_pg = pg_conn.cursor()
        
        print("\nIniciando migração de contas a pagar...")
        
        # Limpar tabela destino
        cursor_pg.execute("DELETE FROM contas_pagar")
        pg_conn.commit()
        
        # Buscar contas a pagar
        cursor_access.execute("""
            SELECT 
                [CodConta a Pagar],
                Data,
                Valor,
                Fornecedor,
                Vencimento,
                ValorTotalPago,
                Historico,
                FormaPagto,
                Juros,
                DataPagto,
                ValorPago,
                Status,
                NDuplicata
            FROM Pagar
            ORDER BY [CodConta a Pagar]
        """)
        
        contas = cursor_access.fetchall()
        print(f"Total de contas a pagar encontradas: {len(contas)}")
        
        # Buscar todos os fornecedores existentes
        cursor_pg.execute("SELECT id FROM fornecedores")
        fornecedores_existentes = {row[0] for row in cursor_pg.fetchall()}
        print(f"Total de fornecedores encontrados: {len(fornecedores_existentes)}")
        
        registros_migrados = 0
        
        for conta in contas:
            try:
                id_conta = conta[0]
                data_cadastro = conta[1] if conta[1] else datetime.now()
                valor = float(conta[2]) if conta[2] else 0.0
                fornecedor_id = conta[3]
                data_vencimento = conta[4] if conta[4] else None
                valor_total = float(conta[5]) if conta[5] else 0.0
                descricao = conta[6]
                forma_pagamento = conta[7]
                juros = float(conta[8]) if conta[8] else 0.0
                data_pagamento = conta[9]
                valor_pago = float(conta[10]) if conta[10] else 0.0
                status = conta[11]
                nota_fiscal = conta[12]
                
                # Converter status
                if status == 'P':
                    status = 'PAGO'
                elif status == 'A':
                    status = 'ABERTO'
                else:
                    status = 'PENDENTE'
                
                # Verificar se fornecedor existe
                if fornecedor_id and fornecedor_id not in fornecedores_existentes:
                    print(f"Fornecedor {fornecedor_id} não encontrado. Pulando conta {id_conta}")
                    continue
                
                print(f"\nMigrando conta a pagar: {id_conta}")
                print(f"Fornecedor: {fornecedor_id}")
                print(f"Valor: {valor}")
                print(f"Status: {status}")
                
                # Criar nova conexão para esta transação
                pg_conn_local = conectar_postgresql()
                try:
                    with pg_conn_local.cursor() as cur:
                        cur.execute("""
                            INSERT INTO contas_pagar (
                                id,
                                fornecedor_id,
                                descricao,
                                valor,
                                data_vencimento,
                                data_pagamento,
                                valor_pago,
                                juros,
                                status,
                                forma_pagamento,
                                data_cadastro,
                                observacoes
                            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        """, (
                            id_conta,
                            fornecedor_id,
                            descricao[:200] if descricao else None,  # Limitando a 200 caracteres
                            valor,
                            data_vencimento,
                            data_pagamento,
                            valor_pago,
                            juros,
                            status[:20] if status else None,  # Limitando a 20 caracteres
                            forma_pagamento[:50] if forma_pagamento else None,  # Limitando a 50 caracteres
                            data_cadastro,
                            nota_fiscal
                        ))
                        pg_conn_local.commit()
                        registros_migrados += 1
                        
                        if registros_migrados % 100 == 0:
                            print(f"Migrados {registros_migrados} registros...")
                            
                finally:
                    pg_conn_local.close()
                
            except Exception as e:
                print(f"Erro ao migrar conta a pagar {id_conta}:")
                print(f"Dados da conta: {conta}")
                print(f"Erro: {str(e)}")
                continue
        
        print(f"\nMigração de contas a pagar concluída!")
        print(f"Total migrado: {registros_migrados}")
        
    except Exception as e:
        print(f"Erro durante a migração de contas a pagar: {str(e)}")
        raise

def verificar_status_permitidos(pg_conn):
    try:
        with pg_conn.cursor() as cur:
            # Verificar a restrição da coluna status
            cur.execute("""
                SELECT pg_get_constraintdef(con.oid) as check_clause
                FROM pg_constraint con 
                    INNER JOIN pg_class rel ON rel.oid = con.conrelid
                WHERE conname = 'contas_receber_status_check'
            """)
            resultado = cur.fetchone()
            if resultado:
                print(f"Restrição de status: {resultado[0]}")
                return resultado[0]
    except Exception as e:
        print(f"Erro ao verificar status permitidos: {str(e)}")
        return None

def migrar_contas_receber(access_conn, pg_conn):
    try:
        # Primeiro verificar os status permitidos
        restricao_status = verificar_status_permitidos(pg_conn)
        print(f"\nRestrição de status encontrada: {restricao_status}")
        
        cursor_access = access_conn.cursor()
        
        print("\nIniciando migração de contas a receber...")
        
        # Primeiro, vamos analisar os dados
        cursor_access.execute("""
            SELECT MIN([CodConta a Receber]), MAX([CodConta a Receber]), COUNT(*)
            FROM Receber
        """)
        min_id, max_id, total = cursor_access.fetchone()
        print(f"Range de IDs: {min_id} até {max_id}")
        print(f"Total de registros: {total}")
        
        # Verificar status existentes no Access
        cursor_access.execute("SELECT DISTINCT Status FROM Receber")
        status_access = cursor_access.fetchall()
        print("\nStatus existentes no Access:")
        for status in status_access:
            print(f"- {status[0]}")
            
        # Limpar tabela
        pg_conn_clean = conectar_postgresql()
        try:
            with pg_conn_clean.cursor() as cur:
                cur.execute("DELETE FROM contas_receber")
                pg_conn_clean.commit()
                print("\nTabela limpa com sucesso")
        finally:
            pg_conn_clean.close()
        
        # Função para converter status
        def converter_status(status_original):
            if not status_original:
                return 'PENDENTE'
            
            status_map = {
                'P': 'RECEBIDO',    # Em vez de 'PAGO'
                'A': 'PENDENTE',    # Em vez de 'ABERTO'
                'C': 'CANCELADO'
            }
            return status_map.get(status_original.upper(), 'PENDENTE')
        
        # Processar registros
        tamanho_lote = 1000
        registros_migrados = 0
        erros = 0
        
        for offset in range(min_id, max_id + 1, tamanho_lote):
            cursor_access.execute("""
                SELECT 
                    [CodConta a Receber],
                    Documento,
                    Data,
                    Valor,
                    Cliente,
                    Vencimento,
                    Historico,
                    FormaPagto,
                    Juros,
                    DataPagto,
                    ValorTotalPago,
                    Status,
                    Desconto
                FROM Receber
                WHERE [CodConta a Receber] BETWEEN ? AND ?
                ORDER BY [CodConta a Receber]
            """, (offset, offset + tamanho_lote - 1))
            
            lote = cursor_access.fetchall()
            print(f"\nProcessando lote de {offset} a {offset + tamanho_lote - 1}")
            print(f"Registros no lote: {len(lote)}")
            
            for conta in lote:
                try:
                    id_conta = conta[0]
                    documento = str(conta[1])[:50] if conta[1] else None
                    data_cadastro = conta[2] if conta[2] else datetime.now()
                    valor = float(conta[3]) if conta[3] else 0.0
                    cliente_id = conta[4]
                    data_vencimento = conta[5] if conta[5] else None
                    descricao = str(conta[6])[:200] if conta[6] else None
                    forma_recebimento = str(conta[7])[:50] if conta[7] else None
                    juros = float(conta[8]) if conta[8] else 0.0
                    data_recebimento = conta[9]
                    valor_recebido = float(conta[10]) if conta[10] else 0.0
                    status = converter_status(conta[11])
                    desconto = float(conta[12]) if conta[12] else 0.0
                    
                    print(f"\nMigrando conta {id_conta}:")
                    print(f"Cliente: {cliente_id}")
                    print(f"Valor: {valor}")
                    print(f"Status original: {conta[11]}")
                    print(f"Status convertido: {status}")
                    
                    # Nova conexão para cada inserção
                    pg_conn_insert = conectar_postgresql()
                    try:
                        with pg_conn_insert.cursor() as cur:
                            cur.execute("""
                                INSERT INTO contas_receber (
                                    id,
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
                                    data_cadastro,
                                    observacoes
                                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                            """, (
                                id_conta,
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
                                data_cadastro,
                                documento
                            ))
                            pg_conn_insert.commit()
                            registros_migrados += 1
                    except Exception as e:
                        print(f"Erro na inserção: {str(e)}")
                        continue
                    finally:
                        pg_conn_insert.close()
                    
                except Exception as e:
                    print(f"Erro ao preparar dados da conta {id_conta}:")
                    print(f"Dados: {conta}")
                    print(f"Erro: {str(e)}")
                    erros += 1
                    continue
                
            print(f"Lote processado. Migrados até agora: {registros_migrados}")
        
        print("\nMigração concluída!")
        print(f"Total de registros migrados: {registros_migrados}")
        print(f"Total de erros: {erros}")
        
        # Verificar resultado final
        pg_conn_check = conectar_postgresql()
        try:
            with pg_conn_check.cursor() as cur:
                cur.execute("SELECT COUNT(*) FROM contas_receber")
                total_final = cur.fetchone()[0]
                print(f"Total de registros na tabela: {total_final}")
        finally:
            pg_conn_check.close()
        
    except Exception as e:
        print(f"Erro durante a migração: {str(e)}")
        print("Traceback completo:")
        import traceback
        print(traceback.format_exc())
        raise

# Resto do código permanece o mesmo...

def main():
    try:
        movimentos_path = r"C:\Users\Cirilo\Documents\empresa\Bancos\Contas\Contas.mdb"
        access_conn = conectar_access(movimentos_path)
        pg_conn = conectar_postgresql()
        
        if not access_conn or not pg_conn:
            print("Erro ao conectar aos bancos de dados.")
            return
        
        print("\n=== Migração de Contas a Receber ===")
        migrar_contas_receber(access_conn, pg_conn)
        
    except Exception as e:
        print(f"Erro durante o processo: {str(e)}")
    finally:
        if 'access_conn' in locals():
            access_conn.close()
        if 'pg_conn' in locals():
            pg_conn.close()

if __name__ == "__main__":
    main()