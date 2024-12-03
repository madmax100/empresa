import pyodbc
import psycopg2
from datetime import datetime
from decimal import Decimal
import re

def clean_string(value):
    if value is None:
        return None
    return str(value).strip()

def clean_decimal(value):
    if value is None:
        return Decimal('0.00')
    try:
        clean_value = re.sub(r'[^\d.,\-]', '', str(value))
        clean_value = clean_value.replace(',', '.')
        return Decimal(clean_value).quantize(Decimal('0.01'))
    except:
        return Decimal('0.00')

def clean_boolean(value):
    if value is None:
        return False
    return bool(value)

def determinar_status(row):
    """Determina o status com base nos valores"""
    if row[19]:  # Status do Access
        status_atual = clean_string(row[19]).upper()
        if status_atual == 'BAIXADO':
            return 'P'
        elif status_atual == 'CANCELADO':
            return 'C'
    if not row[15]:  # Sem data de pagamento
        return 'A'
    valor_recebido = clean_decimal(row[14])
    if valor_recebido >= clean_decimal(row[3]):
        return 'P'
    return 'A'

def limpar_tabelas(pg_conn):
    try:
        cursor = pg_conn.cursor()
        
        print("\nIniciando limpeza das tabelas...")
        cursor.execute("SET session_replication_role = 'replica';")
        
        tabelas = [
            'contas_receber'
        ]
        
        for tabela in tabelas:
            try:
                print(f"\nVerificando tabela {tabela}...")
                cursor.execute(f"SELECT COUNT(*) FROM {tabela}")
                qtd_antes = cursor.fetchone()[0]
                print(f"Registros encontrados em {tabela}: {qtd_antes}")
                
                if qtd_antes > 0:
                    print(f"Limpando tabela {tabela}...")
                    cursor.execute(f"TRUNCATE TABLE {tabela} CASCADE")
                    pg_conn.commit()
                    print(f"Tabela {tabela} limpa com sucesso!")
                
            except Exception as e:
                print(f"Erro ao limpar tabela {tabela}: {str(e)}")
                pg_conn.rollback()
                raise
        
        cursor.execute("SET session_replication_role = 'origin';")
        pg_conn.commit()
        
        print("\nLimpeza concluída com sucesso!")
        return True
        
    except Exception as e:
        print(f"Erro durante a limpeza: {str(e)}")
        pg_conn.rollback()
        return False

def carregar_clientes(pg_cursor):
    """Carrega o mapeamento de clientes"""
    pg_cursor.execute("SELECT id FROM clientes")
    ids = {row[0] for row in pg_cursor.fetchall()}
    print(f"Clientes encontrados: {len(ids)}")
    return ids

def carregar_contas(pg_cursor):
    """Carrega o mapeamento de contas bancárias"""
    pg_cursor.execute("SELECT id FROM contas_bancarias")
    ids = {row[0] for row in pg_cursor.fetchall()}
    print(f"Contas bancárias encontradas: {len(ids)}")
    return ids

def migrar_contas_receber():
    pg_config = {
        'dbname': 'c3mcopiasdb2',
        'user': 'cirilomax',
        'password': '226cmm100',
        'host': 'localhost',
        'port': '5432'
    }

    db_path = r"C:\Users\Cirilo\Documents\c3mcopias\Bancos\Contas\Contas.mdb"
    
    try:
        # Conexões
        print("Conectando aos bancos de dados...")
        conn_str = (
            r'Driver={Microsoft Access Driver (*.mdb, *.accdb)};'
            f'DBQ={db_path};'
            'PWD=010182;'
        )
        access_conn = pyodbc.connect(conn_str)
        pg_conn = psycopg2.connect(**pg_config)
        
        if not limpar_tabelas(pg_conn):
            raise Exception("Falha na limpeza das tabelas. Abortando importação.")

        pg_cursor = pg_conn.cursor()
        
        # Carregar mapeamentos
        clientes = carregar_clientes(pg_cursor)
        contas = carregar_contas(pg_cursor)
        
        # Query para buscar dados do Access
        query = """
        SELECT [CodConta a Receber],
               Documento,
               Data,
               Valor,
               Cliente,
               Vencimento,
               ValorTotalPago,
               Historico,
               FormaPagto,
               Condicoes,
               Confirmacao,
               Juros,
               Tarifas,
               NN,
               Recebido,
               DataPagto,
               Local,
               Conta,
               Impresso,
               Status,
               Comanda,
               RepassadoFactory,
               Factory,
               ValorFactory,
               StatusFactory,
               ValorPagoFactory,
               Cartorio,
               Protesto,
               Desconto,
               DataPagtoFactory
        FROM Receber
        ORDER BY [CodConta a Receber]
        """
        
        print("\nBuscando dados do Access...")
        access_cursor = access_conn.cursor()
        access_cursor.execute(query)

        rows = access_cursor.fetchall()
        total_registros = len(rows)
        print(f"Total de registros a processar: {total_registros}")

        # SQL de inserção
        insert_sql = """
            INSERT INTO contas_receber (
                documento,
                data,
                valor,
                cliente_id,
                vencimento,
                valor_total_pago,
                historico,
                forma_pagamento,
                condicoes,
                confirmacao,
                juros,
                tarifas,
                nosso_numero,
                recebido,
                data_pagamento,
                local,
                conta_id,
                impresso,
                status,
                comanda,
                repassado_factory,
                factory,
                valor_factory,
                status_factory,
                valor_pago_factory,
                cartorio,
                protesto,
                desconto,
                data_pagto_factory
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        # Processo de migração
        contador = 0
        erros = 0
        contador_zerados = 0
        clientes_nao_encontrados = set()
        contas_nao_encontradas = set()
        
        print("\nIniciando migração das contas a receber...")

        for row in rows:
            try:
                # Verifica se o registro tem valor
                if clean_decimal(row[3]) == Decimal('0.00'):
                    contador_zerados += 1
                    continue

                # Validar cliente
                cliente_id = None
                if row[4] is not None and str(row[4]).strip() != '0':
                    try:
                        temp_cliente_id = int(row[4])
                        if temp_cliente_id in clientes:
                            cliente_id = temp_cliente_id
                        else:
                            clientes_nao_encontrados.add(temp_cliente_id)
                            if not row[7]:  # Se não tem histórico, pula
                                continue
                    except (ValueError, TypeError):
                        pass

                # Validar conta
                conta_id = None
                if row[17] and str(row[17]).strip() != '0':
                    try:
                        temp_conta_id = int(row[17])
                        if temp_conta_id in contas:
                            conta_id = temp_conta_id
                        else:
                            contas_nao_encontradas.add(temp_conta_id)
                    except (ValueError, TypeError):
                        pass

                dados = (
                    clean_string(row[1]),       # documento
                    row[2],                     # data
                    clean_decimal(row[3]),      # valor
                    cliente_id,                 # cliente_id
                    row[5],                     # vencimento
                    clean_decimal(row[6]),      # valor_total_pago
                    clean_string(row[7]),       # historico
                    clean_string(row[8]),       # forma_pagamento
                    clean_string(row[9]),       # condicoes
                    clean_string(row[10]),      # confirmacao
                    clean_decimal(row[11]),     # juros
                    clean_decimal(row[12]),     # tarifas
                    clean_string(row[13]),      # nosso_numero
                    clean_decimal(row[14]),     # recebido
                    row[15],                    # data_pagamento
                    clean_string(row[16]),      # local
                    conta_id,                   # conta_id
                    clean_boolean(row[18]),     # impresso
                    determinar_status(row),     # status
                    clean_string(row[20]),      # comanda
                    clean_boolean(row[21]),     # repassado_factory
                    clean_string(row[22]),      # factory
                    clean_decimal(row[23]),     # valor_factory
                    clean_string(row[24]),      # status_factory
                    clean_decimal(row[25]),     # valor_pago_factory
                    clean_boolean(row[26]),     # cartorio
                    clean_boolean(row[27]),     # protesto
                    clean_decimal(row[28]),     # desconto
                    row[29]                     # data_pagto_factory
                )
                
                pg_cursor.execute(insert_sql, dados)
                pg_conn.commit()
                contador += 1
                
                if contador % 1000 == 0:
                    percentual = (contador / total_registros) * 100
                    print(f"Progresso: {contador}/{total_registros} ({percentual:.2f}%) contas migradas...")
            
            except Exception as e:
                erros += 1
                print(f"Erro ao migrar conta a receber {row[0]}: {str(e)}")
                print(f"Dados: {row}")
                pg_conn.rollback()
                continue

        # Resultados da migração
        print("\nMigração concluída!")
        print(f"Total de registros processados: {total_registros}")
        print(f"Total de contas migradas com sucesso: {contador}")
        print(f"Total de registros com valor zero: {contador_zerados}")
        print(f"Total de erros: {erros}")
        
        if clientes_nao_encontrados:
            print("\nClientes não encontrados:")
            for c in sorted(clientes_nao_encontrados):
                print(f"- {c}")
                
        if contas_nao_encontradas:
            print("\nContas bancárias não encontradas:")
            for c in sorted(contas_nao_encontradas):
                print(f"- {c}")
        
    except Exception as e:
        print(f"Erro durante a migração: {str(e)}")
        if 'pg_conn' in locals():
            pg_conn.rollback()
    finally:
        if 'access_conn' in locals():
            access_conn.close()
        if 'pg_conn' in locals():
            pg_conn.close()

if __name__ == "__main__":
    print("=== MIGRAÇÃO DE CONTAS A RECEBER ===")
    print("Início:", datetime.now())
    migrar_contas_receber()
    print("Fim:", datetime.now())