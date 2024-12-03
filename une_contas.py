import psycopg2
from datetime import datetime
import re

def converter_data(valor):
    """Converte string de data para objeto date"""
    if not valor:
        return None
    try:
        formatos = [
            '%d/%m/%Y',
            '%Y-%m-%d',
            '%d-%m-%Y',
            '%d.%m.%Y'
        ]
        for formato in formatos:
            try:
                return datetime.strptime(str(valor).strip(), formato).date()
            except:
                continue
        return None
    except:
        return None

def converter_decimal(valor):
    """Converte string de valor para decimal"""
    if not valor:
        return 0
    try:
        valor = re.sub(r'[^\d.,]', '', str(valor))
        valor = valor.replace(',', '.')
        return float(valor)
    except:
        return 0

def limpar_string(valor):
    """Limpa strings removendo caracteres especiais e espaços extras"""
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

def migrar_contas():
    """Migra Contas a Pagar e Receber"""
    conn = None
    cur = None
    
    conn_params = {
       'dbname': 'nova_empresa',
       'user': 'cirilomax',
       'password': '226cmm100',
       'host': 'localhost',
       'port': '5432'
    }

    try:
        # Conecta com encoding específico
        conn = psycopg2.connect(**conn_params)
        cur = conn.cursor()

        # 1. Migrar Contas a Pagar
        print("\nMigrando Contas a Pagar...")
        
        try:
            cur.execute('SELECT * FROM "Pagar" LIMIT 1')
            colunas = [desc[0] for desc in cur.description]
            print("Colunas encontradas em Pagar:", colunas)
        except Exception as e:
            print(f"Erro ao listar colunas de Pagar: {str(e)}")
            return

        # Query principal para Pagar
        cur.execute("""
            SELECT 
                p."CodConta_a_Pagar",
                p."Data",
                p."Valor",
                p."Fornecedor",
                p."DataPagto",
                p."ValorPago",
                p."Local",
                p."Status",
                p."Conta",
                p."NDuplicata",
                p."Vencimento",
                p."ValorTotalPago",
                p."Historico",
                p."FormaPagto",
                p."Condicoes",
                p."Confirmacao",
                p."Juros",
                p."Tarifas"
            FROM "Pagar" p
        """)
        
        contas_pagar = cur.fetchall()
        total_pagar = 0
        erros_pagar = 0

        print(f"Encontradas {len(contas_pagar)} contas a pagar")

        for conta in contas_pagar:
            try:
                # Debug - mostrar dados do registro
                print(f"\nProcessando conta a pagar:")
                print(f"Código: {conta[0]}")
                fornecedor_nome = limpar_string(conta[3])
                print(f"Fornecedor: {fornecedor_nome}")

                # Busca ID do fornecedor
                cur.execute("""
                    SELECT id FROM fornecedores 
                    WHERE UPPER(nome) = UPPER(%s)
                """, (fornecedor_nome,))
                
                fornecedor_result = cur.fetchone()
                fornecedor_id = fornecedor_result[0] if fornecedor_result else None
                print(f"Fornecedor ID encontrado: {fornecedor_id}")

                dados = {
                    'cliente_fornecedor_id': fornecedor_id,
                    'data_emissao': converter_data(conta[1]),
                    'data_vencimento': converter_data(conta[10]),
                    'data_pagamento': converter_data(conta[4]),
                    'valor_original': converter_decimal(conta[2]),
                    'valor_pago': converter_decimal(conta[5]),
                    'valor_total_pago': converter_decimal(conta[11]),
                    'historico': limpar_string(conta[12]),
                    'numero_documento': limpar_string(conta[0]),
                    'numero_nota': limpar_string(conta[9]),
                    'confirmacao': limpar_string(conta[15]),
                    'status': limpar_string(conta[7]) or 'ABERTO',
                    'conta': limpar_string(conta[8]),
                    'local_pagamento': limpar_string(conta[6]),
                    'tipo': 'PAGAR',
                    'condicoes': limpar_string(conta[14]),
                    'forma_pagamento': limpar_string(conta[13]),
                    'juros': converter_decimal(conta[16]),
                    'tarifas': converter_decimal(conta[17])
                }

                # Debug - mostrar dados preparados
                print("Dados preparados para inserção:")
                for k, v in dados.items():
                    print(f"{k}: {v}")

                cur.execute("""
                    INSERT INTO financeiro_contas (
                        cliente_fornecedor_id, data_emissao, data_vencimento,
                        data_pagamento, valor_original, valor_pago,
                        valor_total_pago, historico, numero_documento,
                        numero_nota, confirmacao, status, conta,
                        local_pagamento, tipo, condicoes, forma_pagamento,
                        juros, tarifas, created_at
                    ) VALUES (
                        %(cliente_fornecedor_id)s, %(data_emissao)s, %(data_vencimento)s,
                        %(data_pagamento)s, %(valor_original)s, %(valor_pago)s,
                        %(valor_total_pago)s, %(historico)s, %(numero_documento)s,
                        %(numero_nota)s, %(confirmacao)s, %(status)s, %(conta)s,
                        %(local_pagamento)s, %(tipo)s, %(condicoes)s, %(forma_pagamento)s,
                        %(juros)s, %(tarifas)s, CURRENT_TIMESTAMP
                    )
                """, dados)

                total_pagar += 1
                print(f"Conta a pagar migrada com sucesso")
                
                # Commit a cada registro para garantir
                conn.commit()

            except Exception as e:
                erros_pagar += 1
                print(f"Erro ao migrar conta a pagar: {str(e)}")
                print("Dados do registro com erro:", conta)
                conn.rollback()
                continue

        print("\n=== Relatório Parcial ===")
        print(f"Contas a Pagar migradas com sucesso: {total_pagar}")
        print(f"Erros em Contas a Pagar: {erros_pagar}")

        # Criar índices
        indices = [
            "CREATE INDEX IF NOT EXISTS idx_fin_contas_cliente ON financeiro_contas(cliente_fornecedor_id);",
            "CREATE INDEX IF NOT EXISTS idx_fin_contas_data_venc ON financeiro_contas(data_vencimento);",
            "CREATE INDEX IF NOT EXISTS idx_fin_contas_tipo ON financeiro_contas(tipo);",
            "CREATE INDEX IF NOT EXISTS idx_fin_contas_status ON financeiro_contas(status);"
        ]
        
        print("\nCriando índices...")
        for idx in indices:
            try:
                cur.execute(idx)
                print("Índice criado com sucesso")
            except Exception as e:
                print(f"Erro ao criar índice: {str(e)}")

        conn.commit()

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
    print("Iniciando migração das contas...")
    migrar_contas()
    print("\nMigração finalizada!")