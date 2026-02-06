
import psycopg2
from config import PG_CONFIG

def check_link():
    try:
        conn = psycopg2.connect(**PG_CONFIG)
        cur = conn.cursor()

        # Find 5 recent NFS "A Vista"
        cur.execute("""
            SELECT n.id, n.numero_nota, n.data, n.valor_total_nota, c.nome, n.condicoes, n.operacao, n.cfop
            FROM notas_fiscais_saida n
            JOIN clientes c ON n.cliente_id = c.id
            WHERE n.condicoes ILIKE '%VISTA%'
            ORDER BY n.data DESC
            LIMIT 5
        """)
        nfs_list = cur.fetchall()

        for nf in nfs_list:
            nf_id, numero, data, valor, cliente, condicoes, nat_op, cfop = nf
            print("-" * 50)
            print(f"NFS {numero} ({data})")
            print(f"Valor: R$ {valor}")
            print(f"Cliente: {cliente}")
            print(f"Condicoes: {repr(condicoes)}")
            print(f"Operacao: {repr(nat_op)}")
            print(f"CFOP: {repr(cfop)}")
            
            # Check CR
            # Look for CR with same value and client around that date
            cur.execute("""
                SELECT id, data_pagamento, valor, historico
                FROM contas_receber
                WHERE cliente_id = (SELECT id FROM clientes WHERE nome = %s)
                AND valor = %s
                AND (data_pagamento = %s::date OR vencimento = %s::date)
            """, (cliente, valor, data, data))
            
            crs = cur.fetchall()
            if crs:
                print(f"  -> FOUND {len(crs)} Contas Receber match(es):")
                for cr in crs:
                    print(f"     CR {cr[0]}: {cr[1]} - R$ {cr[2]} - {cr[3]}")
            else:
                print("  -> NO MATCH in ContasReceber!")

        conn.close()

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_link()
