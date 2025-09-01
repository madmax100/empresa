import pyodbc
import psycopg2
from datetime import datetime

def reimport_nfs():
    # Conectar ao MS Access
    access_conn = pyodbc.connect(r'DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};DBQ=C:\Users\Cirilo\Documents\c3mcopias\backend\c3mcopia.mdb;')
    access_cursor = access_conn.cursor()

    # Conectar ao PostgreSQL
    pg_conn = psycopg2.connect(
        dbname='c3mcopiasdb2',
        user='cirilomax', 
        password='226cmm100',
        host='localhost',
        port='5432'
    )
    pg_cursor = pg_conn.cursor()

    # Buscar notas fiscais de venda do MS Access a partir da 41009
    access_cursor.execute("""
        SELECT NFNumero, NFCodCliente, NFNomeCliente, NFData, NFValor, 
               NFDesconto, NFObservacoes, NFEnderecoEntrega, 
               NFCNPJ, NFInscricaoEstadual, NFReferencia,
               NFDataVencimento, NFCodigoTransportadora, 
               NFNomeTransportadora, NFTelefoneTransportadora,
               NFCNPJTransportadora, NFPlacaVeiculo, NFUFVeiculo,
               NFPesoBruto, NFPesoLiquido, NFQtdVolumes, 
               NFEspecieVolumes, NFMarcaVolumes, NFNumeroVolumes
        FROM NFS
        WHERE NFNumero >= 41009 AND YEAR(NFData) >= 2024
        ORDER BY NFNumero
    """)

    nfs_data = access_cursor.fetchall()
    print(f'Encontradas {len(nfs_data)} notas a partir da 41009')

    # Inserir no PostgreSQL
    inserted_count = 0
    for row in nfs_data:
        try:
            pg_cursor.execute("""
                INSERT INTO notas_fiscais_saida (
                    numero, codigo_cliente, nome_cliente, data_emissao, valor,
                    desconto, observacoes, endereco_entrega, cnpj_cliente,
                    inscricao_estadual, nf_referencia, data_vencimento,
                    codigo_transportadora, nome_transportadora, 
                    telefone_transportadora, cnpj_transportadora,
                    placa_veiculo, uf_veiculo, peso_bruto, peso_liquido,
                    qtd_volumes, especie_volumes, marca_volumes, numero_volumes
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (numero) DO NOTHING
            """, row)
            inserted_count += 1
            if inserted_count % 50 == 0:
                print(f'Processadas {inserted_count} notas...')
        except Exception as e:
            print(f'Erro na nota {row[0]}: {e}')
            
    pg_conn.commit()
    print(f'Total de notas inseridas: {inserted_count}')

    # Verificar se a nota 41440 foi inserida
    pg_cursor.execute('SELECT COUNT(*) FROM notas_fiscais_saida WHERE numero = 41440')
    count = pg_cursor.fetchone()[0]
    print(f'Nota 41440 existe no PostgreSQL: {count > 0}')

    # Contar total de notas no PostgreSQL
    pg_cursor.execute('SELECT COUNT(*) FROM notas_fiscais_saida')
    total_pg = pg_cursor.fetchone()[0]
    print(f'Total de notas no PostgreSQL: {total_pg}')

    pg_conn.close()
    access_conn.close()

if __name__ == "__main__":
    reimport_nfs()
