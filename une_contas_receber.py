import psycopg2
from datetime import datetime
import re

def converter_data(valor):
    if not valor:
        return None
    try:
        formatos = ['%d/%m/%Y', '%Y-%m-%d', '%d-%m-%Y', '%d.%m.%Y']
        for formato in formatos:
            try:
                return datetime.strptime(str(valor).strip(), formato).date()
            except:
                continue
        return None
    except:
        return None

def converter_decimal(valor):
    if not valor:
        return 0
    try:
        valor = re.sub(r'[^\d.,]', '', str(valor))
        valor = valor.replace(',', '.')
        return float(valor)
    except:
        return 0

def limpar_string(valor):
    if not valor:
        return None
    try:
        if isinstance(valor, bytes):
            return valor.decode('latin1')
        if isinstance(valor, str):
            return valor.strip()
        return str(valor)
    except Exception as e:
        print(f"Erro ao limpar string: {str(e)} - Valor: {valor}")
        return str(valor)

def migrar_contas_receber():
    """Migra Contas a Receber"""
    conn = None
    cur = None
    
    conn_params = {
        'dbname': 'nova_empresa',
        'user': 'cirilomax',
        'password': '226cmm100',
        'host': 'localhost',
        'port': '5432',
        'client_encoding': 'latin1'
    }

    try:
        conn = psycopg2.connect(**conn_params)
        cur = conn.cursor()

        print("\nMigrando Contas a Receber...")
        
        # Query principal para Receber com as colunas corretas
        cur.execute("""
            SELECT 
                r."CodConta_a_Receber",
                r."Data",
                r."Valor",
                r."Cliente",
                r."DataPagto",
                r."Recebido",
                r."Local",
                r."Status",
                r."Conta",
                r."Documento",
                r."Vencimento",
                r."ValorTotalPago",
                r."Historico",
                r."FormaPagto",
                r."Condicoes",
                r."Confirmacao",
                r."Juros",
                r."Tarifas",
                r."Factory",
                r."ValorFactory",
                r."StatusFactory",
                r."DataPagtoFactory",
                r."ValorPagoFactory",
                r."Cartorio",
                r."Protesto",
                r."Desconto"
            FROM "Receber" r
        """)
        
        contas_receber = cur.fetchall()
        total_receber = 0
        erros_receber = 0

        print(f"Encontradas {len(contas_receber)} contas a receber")

        for conta in contas_receber:
            try:
                print(f"\nProcessando conta a receber:")
                print(f"Código: {conta[0]}")
                cliente_nome = limpar_string(conta[3])
                print(f"Cliente: {cliente_nome}")

                # Busca ID do cliente
                cur.execute("""
                    SELECT codcliente FROM clientes 
                    WHERE UPPER(nome) = UPPER(%s)
                """, (cliente_nome,))
                
                cliente_result = cur.fetchone()
                cliente_id = cliente_result[0] if cliente_result else None
                print(f"Cliente ID encontrado: {cliente_id}")

                # Busca ID do factoring se existir
                factoring_id = None
                if conta[18]:  # Factory
                    factoring_nome = limpar_string(conta[18])
                    cur.execute("""
                        SELECT id FROM financeiro_factoring 
                        WHERE UPPER(nome) = UPPER(%s)
                    """, (factoring_nome,))
                    factoring_result = cur.fetchone()
                    factoring_id = factoring_result[0] if factoring_result else None
                    print(f"Factoring ID encontrado: {factoring_id}")

                dados = {
                    'cliente_fornecedor_id': cliente_id,
                    'data_emissao': converter_data(conta[1]),
                    'data_vencimento': converter_data(conta[10]),
                    'data_pagamento': converter_data(conta[4]),
                    'valor_original': converter_decimal(conta[2]),
                    'valor_pago': converter_decimal(conta[5]),  # Recebido
                    'valor_total_pago': converter_decimal(conta[11]),
                    'historico': limpar_string(conta[12]),
                    'numero_documento': limpar_string(conta[0]),
                    'documento': limpar_string(conta[9]),
                    'confirmacao': limpar_string(conta[15]),
                    'status': limpar_string(conta[7]) or 'ABERTO',
                    'conta': limpar_string(conta[8]),
                    'local_pagamento': limpar_string(conta[6]),
                    'tipo': 'RECEBER',
                    'condicoes': limpar_string(conta[14]),
                    'forma_pagamento': limpar_string(conta[13]),
                    'juros': converter_decimal(conta[16]),
                    'tarifas': converter_decimal(conta[17]),
                    'factoring_id': factoring_id,
                    'valor_factoring': converter_decimal(conta[19]),
                    'status_factoring': limpar_string(conta[20]),
                    'data_pago_factoring': converter_data(conta[21]),
                    'valor_pago_factoring': converter_decimal(conta[22]),
                    'cartorio': conta[23] == '1' or conta[23] == 'True',
                    'protesto': conta[24] == '1' or conta[24] == 'True',
                    'descontos': converter_decimal(conta[25])
                }

                # Debug - mostrar dados preparados
                print("Dados preparados para inserção:")
                for k, v in dados.items():
                    if v is not None:  # Mostrar apenas valores não nulos
                        print(f"{k}: {v}")

                # Insert na tabela financeiro_contas
                cur.execute("""
                    INSERT INTO financeiro_contas (
                        cliente_fornecedor_id, data_emissao, data_vencimento,
                        data_pagamento, valor_original, valor_pago,
                        valor_total_pago, historico, numero_documento,
                        documento, confirmacao, status, conta,
                        local_pagamento, tipo, condicoes, forma_pagamento,
                        juros, tarifas, factoring_id, valor_factoring,
                        status_factoring, data_pago_factoring, valor_pago_factoring,
                        cartorio, protesto, descontos,
                        created_at
                    ) VALUES (
                        %(cliente_fornecedor_id)s, %(data_emissao)s, %(data_vencimento)s,
                        %(data_pagamento)s, %(valor_original)s, %(valor_pago)s,
                        %(valor_total_pago)s, %(historico)s, %(numero_documento)s,
                        %(documento)s, %(confirmacao)s, %(status)s, %(conta)s,
                        %(local_pagamento)s, %(tipo)s, %(condicoes)s, %(forma_pagamento)s,
                        %(juros)s, %(tarifas)s, %(factoring_id)s, %(valor_factoring)s,
                        %(status_factoring)s, %(data_pago_factoring)s, %(valor_pago_factoring)s,
                        %(cartorio)s, %(protesto)s, %(descontos)s,
                        CURRENT_TIMESTAMP
                    )
                """, dados)

                total_receber += 1
                print(f"Conta a receber migrada com sucesso")
                
                # Commit a cada registro
                conn.commit()

            except Exception as e:
                erros_receber += 1
                print(f"Erro ao migrar conta a receber: {str(e)}")
                print("Dados do registro com erro:", conta)
                conn.rollback()
                continue

        # Relatório final
        print("\n=== Relatório Final ===")
        print(f"Contas a Receber migradas com sucesso: {total_receber}")
        print(f"Erros em Contas a Receber: {erros_receber}")

        # Atualizar estatísticas
        print("\nAtualizando estatísticas...")
        cur.execute("""
            SELECT tipo, status, COUNT(*), SUM(valor_original)
            FROM financeiro_contas
            GROUP BY tipo, status
            ORDER BY tipo, status
        """)
        
        estatisticas = cur.fetchall()
        print("\nDistribuição de contas:")
        print("Tipo      | Status    | Quantidade | Valor Total")
        print("-" * 50)
        for est in estatisticas:
            print(f"{est[0]:<9} | {est[1]:<9} | {est[2]:<10} | R$ {est[3]:,.2f}")

    except Exception as e:
        print(f"Erro durante a migração: {str(e)}")
        if conn:
            conn.rollback()
        
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()

if __name__ == "__main__":
    print("Iniciando migração das contas a receber...")
    migrar_contas_receber()
    print("\nMigração finalizada!")