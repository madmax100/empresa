import pyodbc
import psycopg2
from datetime import datetime, date
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

def clean_date(value):
    if not value:
        return None
    if isinstance(value, (datetime, date)):
        return value
    try:
        # Remove espaços e caracteres inválidos
        clean_value = str(value).strip()
        if not clean_value:
            return None
            
        # Tenta converter para datetime
        return datetime.strptime(clean_value, '%Y-%m-%d %H:%M:%S').date()
    except:
        try:
            # Tenta outros formatos comuns
            return datetime.strptime(clean_value, '%d/%m/%Y').date()
        except:
            return None

def limpar_tabelas(pg_conn):
    try:
        cursor = pg_conn.cursor()
        
        print("\nIniciando limpeza das tabelas...")
        cursor.execute("SET session_replication_role = 'replica';")
        
        tabelas = [
            'contas_pagar'
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

def carregar_fornecedores(pg_cursor):
    """Carrega o mapeamento de fornecedores"""
    pg_cursor.execute("SELECT id FROM fornecedores")
    ids = {row[0] for row in pg_cursor.fetchall()}
    print(f"Fornecedores encontrados: {len(ids)}")
    return ids

def carregar_contas(pg_cursor):
    """Carrega o mapeamento de contas bancárias"""
    pg_cursor.execute("SELECT id FROM contas_bancarias")
    ids = {row[0] for row in pg_cursor.fetchall()}
    print(f"Contas bancárias encontradas: {len(ids)}")
    return ids

def determinar_status(row):
    """Determina o status com base nos valores"""
    if row[16] and str(row[16]).strip().upper() in ['A', 'P', 'C']:
        return str(row[16]).strip().upper()
    if row[13]:  # Sem data de pagamento
        return 'P'
    valor_pago = clean_decimal(row[14])
    if valor_pago >= clean_decimal(row[2]):
        return 'P'
    return 'A'


def migrar_contas_pagar():
    pg_config = {
        'dbname': 'c3mcopiasdb2',
        'user': 'cirilomax',
        'password': '226cmm100',
        'host': 'localhost',
        'port': '5432'
    }

    db_path = r"C:\Users\Cirilo\Documents\empresa\Bancos\Contas\Contas.mdb"
    
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
        fornecedores = carregar_fornecedores(pg_cursor)
        contas = carregar_contas(pg_cursor)
        
        # Query para buscar dados do Access
        query = """
        SELECT [CodConta a Pagar],
               Data,
               Valor,
               Fornecedor,
               Vencimento,
               ValorTotalPago,
               Historico,
               FormaPagto,
               Condicoes,
               Confirmacao,
               Juros,
               Tarifas,
               NDuplicata,
               DataPagto,
               ValorPago,
               Local,
               Status,
               Conta
        FROM Pagar
        ORDER BY [CodConta a Pagar]
        """
        
        print("\nBuscando dados do Access...")
        access_cursor = access_conn.cursor()
        access_cursor.execute(query)

        # SQL de inserção
        insert_sql = """
            INSERT INTO contas_pagar (
                data,
                valor,
                fornecedor_id,
                vencimento,
                valor_total_pago,
                historico,
                forma_pagamento,
                condicoes,
                confirmacao,
                juros,
                tarifas,
                numero_duplicata,
                data_pagamento,
                valor_pago,
                local,
                status,
                conta_id
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, %s, %s
            )
        """

        # Processo de migração
        contador = 0
        erros = 0
        contador_zerados = 0
        fornecedores_nao_encontrados = set()
        contas_nao_encontradas = set()
        
        print("\nIniciando migração das contas a pagar...")
        
        rows = access_cursor.fetchall()
        total_registros = len(rows)
        print(f"Total de registros a processar: {total_registros}")
        
        for row in rows:
            try:
                # Verifica se o registro tem valor
                if clean_decimal(row[2]) == Decimal('0.00'):
                    contador_zerados += 1
                    continue

                # Validar fornecedor
                fornecedor_id = None
                if row[3] is not None and str(row[3]).strip() != '0':
                    try:
                        temp_fornecedor_id = int(row[3])
                        if temp_fornecedor_id in fornecedores:
                            fornecedor_id = temp_fornecedor_id
                        else:
                            fornecedores_nao_encontrados.add(temp_fornecedor_id)
                            if not row[6]:  # Se não tem histórico, pula
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
                        clean_date(row[1]),           # data
                        clean_decimal(row[2]),        # valor
                        fornecedor_id,                # fornecedor_id 
                        clean_date(row[4]),           # vencimento
                        clean_decimal(row[5]),        # valor_total_pago
                        clean_string(row[6]),         # historico
                        clean_string(row[7]),         # forma_pagamento
                        clean_string(row[8]),         # condicoes
                        clean_string(row[9]),         # confirmacao
                        clean_decimal(row[10]),       # juros
                        clean_decimal(row[11]),       # tarifas
                        clean_string(row[12]),        # numero_duplicata
                        clean_date(row[13]),          # data_pagamento
                        clean_decimal(row[14]),       # valor_pago
                        clean_string(row[15]),        # local
                        determinar_status(row),       # status
                        conta_id                      # conta_id
                    )
                
                pg_cursor.execute(insert_sql, dados)
                pg_conn.commit()
                contador += 1
                
                if contador % 1000 == 0:
                    percentual = (contador / total_registros) * 100
                    print(f"Progresso: {contador}/{total_registros} ({percentual:.2f}%) contas migradas...")
            
            except Exception as e:
                erros += 1
                print(f"Erro ao migrar conta a pagar {row[0]}: {str(e)}")
                print(f"Dados: {row}")
                pg_conn.rollback()
                continue

        print("\nMigração concluída!")
        print(f"Total de registros processados: {total_registros}")
        print(f"Total de contas migradas com sucesso: {contador}")
        print(f"Total de registros com valor zero: {contador_zerados}")
        print(f"Total de erros: {erros}")
        
        if fornecedores_nao_encontrados:
            print("\nFornecedores não encontrados:")
            for f in sorted(fornecedores_nao_encontrados):
                print(f"- {f}")
                
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
    print("=== MIGRAÇÃO DE CONTAS A PAGAR ===")
    print("Início:", datetime.now())
    migrar_contas_pagar()
    print("Fim:", datetime.now())