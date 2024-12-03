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

def clean_frete(value):
    """Limpa e formata o número do frete"""
    if value is None:
        return None
    try:
        # Remove caracteres não numéricos
        num = re.sub(r'[^\d]', '', str(value))
        # Retorna None se não houver números
        if not num:
            return None
        return str(int(num)).zfill(6)  # Preenche com zeros à esquerda até 6 dígitos
    except:
        return None

def limpar_tabelas(pg_conn):
    try:
        cursor = pg_conn.cursor()
        
        print("\nIniciando limpeza das tabelas...")
        cursor.execute("SET session_replication_role = 'replica';")
        
        tabelas = [
            'notas_fiscais_entrada'
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

def carregar_fretes(pg_cursor):
    """Carrega o mapeamento de fretes pelo campo formulario"""
    pg_cursor.execute("""
        SELECT DISTINCT id, 
               CASE 
                   WHEN formulario ~ '^[0-9]+$' THEN LPAD(formulario, 6, '0')
                   ELSE formulario 
               END as formulario_padronizado
        FROM fretes 
        WHERE formulario IS NOT NULL
    """)
    fretes = {row[1]: row[0] for row in pg_cursor.fetchall()}
    print(f"Fretes encontrados: {len(fretes)}")
    return fretes

def migrar_nfe():
    pg_config = {
        'dbname': 'c3mcopiasdb2',
        'user': 'cirilomax',
        'password': '226cmm100',
        'host': 'localhost',
        'port': '5432'
    }

    db_path = r"C:\Users\Cirilo\Documents\c3mcopias\Bancos\Movimentos\Movimentos.mdb"
    
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
        fretes = carregar_fretes(pg_cursor)
        
        # Query para buscar dados do Access
        query = """
        SELECT CodNFE,
               NumNFE,
               Data,
               Fornecedor,
               ValorProdutos,
               BaseCalculo,
               Desconto,
               ValorFrete,
               TipoFrete,
               Valoricms,
               Valoripi,
               Valoricmsfonte,
               Valortotalnota,
               FormaPagto,
               Condicoes,
               Comprador,
               Operador,
               Formulario,
               Observação,
               OutrosEncargos,
               Parcelas,
               Operacao,
               CFOP,
               DataEntrada,
               Chave,
               Serie,
               Protocolo,
               Natureza,
               BaseSubstituicao,
               ICMSSubstituicao,
               OutrasDespesas
        FROM NFE 
        ORDER BY CodNFE
        """
        
        print("\nBuscando dados do Access...")
        access_cursor = access_conn.cursor()
        access_cursor.execute(query)

        # SQL de inserção
        insert_sql = """
            INSERT INTO notas_fiscais_entrada (
                id,
                numero_nota,
                data_emissao,
                fornecedor_id,
                valor_produtos,
                base_calculo_icms,
                valor_desconto,
                valor_frete,
                tipo_frete,
                valor_icms,
                valor_ipi,
                valor_icms_st,
                valor_total,
                forma_pagamento,
                condicoes_pagamento,
                comprador,
                operador,
                frete_id,
                observacao,
                outros_encargos,
                parcelas,
                operacao,
                cfop,
                data_entrada,
                chave_nfe,
                serie_nota,
                protocolo,
                natureza_operacao,
                base_calculo_st,
                outras_despesas
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                
            )
        """

        # Processo de migração
        contador = 0
        erros = 0
        fornecedores_nao_encontrados = set()
        fretes_nao_encontrados = set()
        
        print("\nIniciando migração das notas fiscais...")
        
        while True:
            rows = access_cursor.fetchmany(1000)
            if not rows:
                break
            
            for row in rows:
                try:
                    # Validar fornecedor
                    fornecedor_id = int(row[3]) if row[3] is not None else None
                    if fornecedor_id not in fornecedores:
                        fornecedores_nao_encontrados.add(fornecedor_id)
                        continue
                    
                    # Validar e formatar frete
                    formulario_original = clean_string(row[17])
                    formulario = clean_frete(formulario_original)
                    frete_id = None
                    
                    if formulario:
                        frete_id = fretes.get(formulario)
                        print(frete_id)
                        if not frete_id:
                            # Tenta buscar sem os zeros à esquerda
                            try:
                                frete_id = fretes.get(str(int(formulario)))
                            except:
                                pass
                            if not frete_id and formulario_original:
                                fretes_nao_encontrados.add(f"{formulario_original} (Padronizado: {formulario})")
                                pass

                    # Calcula valor total
                    valor_total = (
                        clean_decimal(row[4])    # valor_produtos
                        + clean_decimal(row[7])  # valor_frete
                        + clean_decimal(row[10]) # valor_ipi
                        + clean_decimal(row[11]) # valor_icms_st
                        + clean_decimal(row[30]) # outras_despesas
                        + clean_decimal(row[19]) # outros_encargos
                        - clean_decimal(row[6])  # valor_desconto
                    )

                    dados = (
                        int(row[0]),                # id (CodNFE)
                        clean_string(row[1]),       # numero_nota
                        row[2],                     # data_emissao
                        fornecedor_id,              # fornecedor_id
                        clean_decimal(row[4]),      # valor_produtos
                        clean_decimal(row[5]),      # base_calculo_icms
                        clean_decimal(row[6]),      # valor_desconto
                        clean_decimal(row[7]),      # valor_frete
                        clean_string(row[8]),       # tipo_frete
                        clean_decimal(row[9]),      # valor_icms
                        clean_decimal(row[10]),     # valor_ipi
                        clean_decimal(row[11]),     # valor_icms_st
                        valor_total,                # valor_total
                        clean_string(row[13]),      # forma_pagamento
                        clean_string(row[14]),      # condicoes_pagamento
                        clean_string(row[15]),      # comprador
                        clean_string(row[16]),      # operador
                        frete_id,                   # frete_id
                        clean_string(row[18]),      # observacao
                        clean_decimal(row[19]),     # outros_encargos
                        clean_string(row[20]),      # parcelas
                        clean_string(row[21]),      # operacao
                        clean_string(row[22]),      # cfop
                        row[23],                    # data_entrada
                        clean_string(row[24]),      # chave_nfe
                        clean_string(row[25]),      # serie_nota
                        clean_string(row[26]),      # protocolo
                        clean_string(row[27]),      # natureza_operacao
                        clean_decimal(row[28]),     # base_calculo_st
                        clean_decimal(row[29])      # outras_despesas
                    )
                    
                    pg_cursor.execute(insert_sql, dados)
                    pg_conn.commit()
                    contador += 1
                    
                    if contador % 50 == 0:
                        print(f"Migradas {contador} notas fiscais...")
                
                except Exception as e:
                    erros += 1
                    print(f"Erro ao migrar nota fiscal {row[0]}: {str(e)}")
                    print(f"Dados: {row}")
                    if formulario:
                        #print(f"Formulário original: {formulario_original}")
                        print(f"Formulário padronizado: {formulario}")
                    pg_conn.rollback()
                    continue

        print("\nMigração concluída!")
        print(f"Total de notas fiscais migradas: {contador}")
        print(f"Total de erros: {erros}")
        
        if fornecedores_nao_encontrados:
            print("\nFornecedores não encontrados:")
            for f in sorted(fornecedores_nao_encontrados):
                print(f"- {f}")
                
        if fretes_nao_encontrados:
            print("\nFormulários de frete não encontrados:")
            for f in sorted(fretes_nao_encontrados):
                print(f"- {f}")
        
        # Atualizar sequence
        pg_cursor.execute("""
            SELECT setval('notas_fiscais_entrada_id_seq', 
                         COALESCE((SELECT MAX(id) FROM notas_fiscais_entrada), 1), 
                         true);
        """)
        pg_conn.commit()
        
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
    print("=== MIGRAÇÃO DE NOTAS FISCAIS DE ENTRADA ===")
    print("Início:", datetime.now())
    migrar_nfe()
    print("Fim:", datetime.now())