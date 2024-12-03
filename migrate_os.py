# migrate_os.py
import pyodbc
import psycopg2
from datetime import datetime
from decimal import Decimal

def check_duplicates(access_cursor):
    """Verifica e retorna informações sobre OS duplicadas"""
    print("\nVerificando duplicidades...")
    access_cursor.execute("""
        SELECT Ordem, COUNT(*) as total
        FROM [Ordem de Servico]
        GROUP BY Ordem
        HAVING COUNT(*) > 1
    """)
    
    duplicates = access_cursor.fetchall()
    if duplicates:
        print("\nOrdens de Serviço duplicadas encontradas:")
        print("Número OS | Quantidade | Detalhes")
        print("-" * 60)
        for dup in duplicates:
            # Busca detalhes de cada OS duplicada
            access_cursor.execute("""
                SELECT 
                    Ordem, DataEntrada, Cliente, ValorTotal, 
                    Tecnico, Marca, Modelo, Serie, Observacoes
                FROM [Ordem de Servico]
                WHERE Ordem = ?
                ORDER BY DataEntrada
            """, (dup[0],))
            
            details = access_cursor.fetchall()
            print(f"\nOS: {dup[0]}, Total de duplicatas: {dup[1]}")
            print("Data       | Cliente | Técnico | Valor    | Equipamento")
            print("-" * 70)
            for d in details:
                data = d[1].strftime('%d/%m/%Y') if d[1] else 'Sem data'
                valor = f"R$ {d[3]:,.2f}" if d[3] else 'Sem valor'
                equip = f"{d[5]} {d[6]} ({d[7]})" if d[5] and d[6] else 'Não informado'
                print(f"{data} | {str(d[2]):7} | {str(d[4]):7} | {valor:>9} | {equip[:30]}")
                if d[8]:  # Se tem observações
                    print(f"Obs: {d[8][:100]}")
            print()
    
    return duplicates

def create_os_tables(pg_cursor):
    """Cria as tabelas necessárias para Ordens de Serviço"""
    tables = [
        """
        CREATE TABLE IF NOT EXISTS ordens_servico (
            id SERIAL PRIMARY KEY,
            numero VARCHAR(20),
            data_entrada DATE,
            data_saida DATE,
            data_chamado DATE,
            cliente_id INTEGER,
            valor_servicos DECIMAL(15,2),
            valor_pecas DECIMAL(15,2),
            valor_total DECIMAL(15,2),
            tipo_atendimento VARCHAR(50),
            contrato VARCHAR(50),
            data_inicio_contrato DATE,
            data_fim_contrato DATE,
            tipo_contrato VARCHAR(50),
            equipamento_id INTEGER,
            serie_equipamento VARCHAR(50),
            tecnico VARCHAR(50),
            marca VARCHAR(50),
            modelo VARCHAR(50),
            chamado_por VARCHAR(100),
            hora_chegada TIME,
            tempo_permanencia VARCHAR(50),
            retornar BOOLEAN,
            contadores_copias INTEGER,
            contadores_impressoes INTEGER,
            contadores_color INTEGER,
            insumos_toner BOOLEAN,
            insumos_revelador BOOLEAN,
            insumos_cilindro BOOLEAN,
            insumos_tinta BOOLEAN,
            insumos_master BOOLEAN,
            comentario_tecnico TEXT,
            defeito_reclamado TEXT,
            status VARCHAR(20),
            operador VARCHAR(50),
            observacoes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            CONSTRAINT uk_ordem_servico UNIQUE (numero)
        )""",
        """
        CREATE TABLE IF NOT EXISTS itens_os (
            id SERIAL PRIMARY KEY,
            ordem_servico_id INTEGER REFERENCES ordens_servico(id),
            tipo VARCHAR(10),  -- PEÇA ou SERVIÇO
            produto_id INTEGER,
            descricao VARCHAR(200),
            quantidade DECIMAL(15,3),
            valor_unitario DECIMAL(15,2),
            valor_total DECIMAL(15,2),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )""",
        """
        CREATE INDEX IF NOT EXISTS idx_os_data ON ordens_servico(data_entrada);
        CREATE INDEX IF NOT EXISTS idx_os_cliente ON ordens_servico(cliente_id);
        CREATE INDEX IF NOT EXISTS idx_os_tecnico ON ordens_servico(tecnico);
        CREATE INDEX IF NOT EXISTS idx_os_equipamento ON ordens_servico(equipamento_id);
        """
    ]
    
    for query in tables:
        try:
            pg_cursor.execute(query)
            print(f"Estrutura criada com sucesso!")
        except Exception as e:
            print(f"Erro ao criar estrutura: {str(e)}")
            raise

def clean_value(val):
    """Limpa e converte valores numéricos"""
    if val is None:
        return Decimal('0.00')
    if isinstance(val, str):
        val = val.strip().replace('R$', '').replace(',', '.')
    try:
        return Decimal(str(val))
    except:
        return Decimal('0.00')

def clean_date(val):
    """Limpa e converte datas"""
    if val is None:
        return None
    if isinstance(val, datetime):
        return val.date()
    return val

def clean_string(val, max_length=None):
    """Limpa e trunca strings"""
    if val is None:
        return None
    result = str(val).strip()
    if max_length and len(result) > max_length:
        return result[:max_length]
    return result

def clean_bool(val):
    """Converte valor para boolean"""
    if isinstance(val, bool):
        return val
    if isinstance(val, (int, float)):
        return bool(val)
    if isinstance(val, str):
        return val.lower() in ('sim', 'yes', 'true', '1', 'x', 'checked')
    return False

def migrate_os():
    """Migra as Ordens de Serviço"""
    pg_config = {
        'dbname': 'nova_empresa',
        'user': 'cirilomax',
        'password': '226cmm100',
        'host': 'localhost',
        'port': '5432'
    }
    
    movimentos_path = r"C:\Users\Cirilo\Documents\empresa\Bancos\movimentos\Movimentos.mdb"
    
    try:
        # Conexão PostgreSQL
        print("Conectando ao PostgreSQL...")
        pg_conn = psycopg2.connect(**pg_config)
        pg_cursor = pg_conn.cursor()

        # Cria/atualiza estrutura
        print("\nCriando/atualizando estrutura das tabelas...")
        create_os_tables(pg_cursor)
        pg_conn.commit()

        # Limpa dados existentes
        print("\nLimpando dados existentes...")
        pg_cursor.execute("DELETE FROM itens_os")
        pg_cursor.execute("DELETE FROM ordens_servico")
        pg_conn.commit()

        # Conecta ao Access
        print("\nConectando ao Movimentos.mdb...")
        conn_str = (
            r'Driver={Microsoft Access Driver (*.mdb, *.accdb)};'
            f'DBQ={movimentos_path};'
            'PWD=010182;'
        )
        access_conn = pyodbc.connect(conn_str)
        access_cursor = access_conn.cursor()
        
        duplicates = check_duplicates(access_cursor)
        if duplicates:
            print("\nEncontradas OS duplicadas. Como deseja proceder?")
            print("1. Manter apenas o registro mais recente")
            print("2. Manter apenas o registro mais antigo")
            print("3. Concatenar observações e manter o mais recente")
            print("4. Cancelar migração")
            
            option = input("\nEscolha uma opção (1/2/3/4): ")
            if option == '4':
                print("Migração cancelada pelo usuário.")
                return
                
            if option in ['1', '2', '3']:
                order_by = "DESC" if option in ['1', '3'] else "ASC"
                
                if option == '3':
                    # Cria CTE que agrupa observações
                    main_query = f"""
                        WITH DuplicateOS AS (
                            SELECT 
                                Ordem,
                                ROW_NUMBER() OVER(PARTITION BY Ordem ORDER BY DataEntrada {order_by}) as rn,
                                First(Observacoes) & ' | ' & String(GROUP_CONCAT(Observacoes)) as AllObs,
                                *
                            FROM [Ordem de Servico]
                            GROUP BY Ordem
                        )
                        SELECT * FROM DuplicateOS WHERE rn = 1
                    """
                else:
                    # Cria CTE que seleciona apenas uma versão
                    main_query = f"""
                        WITH RankedOS AS (
                            SELECT *,
                                ROW_NUMBER() OVER(PARTITION BY Ordem 
                                                ORDER BY DataEntrada {order_by}) as rn
                            FROM [Ordem de Servico]
                        )
                        SELECT * FROM RankedOS WHERE rn = 1
                    """
            else:
                main_query = "SELECT * FROM [Ordem de Servico]"
        else:
            main_query = "SELECT * FROM [Ordem de Servico]"

        # Conta total de OS
        access_cursor.execute("SELECT COUNT(*) FROM [Ordem de Servico]")
        total_os = access_cursor.fetchone()[0]
        print(f"\nTotal de Ordens de Serviço a migrar: {total_os}")

        # Migra as OS
        print("\nIniciando migração...")
        processed = 0
        errors = 0
        
        # Processa em lotes
        batch_size = 100
        offset = 0
        
        while True:
            access_cursor.execute(f"""
                SELECT * FROM [Ordem de Servico]
                ORDER BY DataEntrada, Ordem
            """)
            
            rows = access_cursor.fetchmany(batch_size)
            if not rows:
                break
                
            for row in rows:
                try:
                    # Insere OS
                    pg_cursor.execute("""
                        INSERT INTO ordens_servico (
                            numero, data_entrada, data_saida, data_chamado,
                            cliente_id, valor_servicos, valor_pecas, valor_total,
                            tipo_atendimento, contrato, data_inicio_contrato,
                            data_fim_contrato, tipo_contrato, serie_equipamento,
                            tecnico, marca, modelo, chamado_por, hora_chegada,
                            tempo_permanencia, retornar, contadores_copias,
                            contadores_impressoes, contadores_color,
                            insumos_toner, insumos_revelador, insumos_cilindro,
                            insumos_tinta, insumos_master, comentario_tecnico,
                            defeito_reclamado, operador, observacoes
                        )
                        VALUES (
                            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                            %s, %s, %s, %s, %s, %s, %s
                        )
                        RETURNING id
                    """, (
                        clean_string(row.Ordem, 20),
                        clean_date(row.DataEntrada),
                        clean_date(row.DataSaida),
                        clean_date(row.DataChamado),
                        row.Cliente,
                        clean_value(row.ValorServicos),
                        clean_value(row.ValorPecas),
                        clean_value(row.ValorTotal),
                        clean_string(row.Atendimento, 50),
                        clean_string(row.Contrato, 50),
                        clean_date(row.DataInicioContrato),
                        clean_date(row.DataFimContrato),
                        clean_string(row.TipoContrato, 50),
                        clean_string(row.Serie, 50),
                        clean_string(row.Tecnico, 50),
                        clean_string(row.Marca, 50),
                        clean_string(row.Modelo, 50),
                        clean_string(row.ChamadoPor, 100),
                        row.HoraChegada,
                        clean_string(row.Permanencia, 50),
                        clean_bool(row.Retornar),
                        int(clean_value(row.Copias)) if row.Copias else 0,
                        int(clean_value(row.Impressoes)) if row.Impressoes else 0,
                        int(clean_value(row.Fullcolor)) if row.Fullcolor else 0,
                        clean_bool(row.Toner),
                        clean_bool(row.Revelador),
                        clean_bool(row.Cilindro),
                        clean_bool(row.Tinta),
                        clean_bool(row.Master),
                        clean_string(row.ComentarioTecnico),
                        clean_string(row.Defeito),
                        clean_string(row.Operador, 50),
                        clean_string(row.Observacoes)
                    ))
                    
                    os_id = pg_cursor.fetchone()[0]

                    # Processa peças da OS
                    access_cursor2 = access_conn.cursor()
                    access_cursor2.execute("""
                        SELECT * FROM [Pecas da Ordem]
                        WHERE Ordem = ?
                    """, (row.Ordem,))
                    
                    for item in access_cursor2.fetchall():
                        pg_cursor.execute("""
                            INSERT INTO itens_os (
                                ordem_servico_id, tipo, produto_id,
                                descricao, quantidade, valor_unitario,
                                valor_total
                            )
                            VALUES (%s, %s, %s, %s, %s, %s, %s)
                        """, (
                            os_id,
                            'PECA',
                            item.Produto,
                            clean_string(item.Produto, 200),
                            clean_value(item.Qtde),
                            clean_value(item.Valor),
                            clean_value(item.ValorTotal)
                        ))
                    
                    access_cursor2.close()
                    
                    processed += 1
                    if processed % 100 == 0:
                        pg_conn.commit()
                        print(f"Processadas {processed} de {total_os} OS...")
                        
                except Exception as e:
                    print(f"Erro ao processar OS {row.Ordem}: {str(e)}")
                    pg_conn.rollback()
                    errors += 1
                    continue

            pg_conn.commit()

        # Relatório final
        print("\n=== Relatório da Migração ===")
        print(f"Total de OS processadas: {processed}")
        print(f"Erros encontrados: {errors}")
        
        # Verifica totais
        pg_cursor.execute("""
            SELECT 
                COUNT(*) as total_os,
                COUNT(DISTINCT cliente_id) as total_clientes,
                COUNT(DISTINCT tecnico) as total_tecnicos,
                SUM(valor_servicos) as total_servicos,
                SUM(valor_pecas) as total_pecas,
                SUM(valor_total) as valor_total,
                MIN(data_entrada) as data_inicial,
                MAX(data_entrada) as data_final
            FROM ordens_servico
        """)
        
        result = pg_cursor.fetchone()
        print(f"\nTotais no PostgreSQL:")
        print(f"OS migradas: {result[0]}")
        print(f"Total de clientes: {result[1]}")
        print(f"Total de técnicos: {result[2]}")
        print(f"Total serviços: R$ {result[3]:,.2f}")
        print(f"Total peças: R$ {result[4]:,.2f}")
        print(f"Valor total: R$ {result[5]:,.2f}")
        print(f"Período: {result[6]} a {result[7]}")

        # Distribuição por ano
        pg_cursor.execute("""
            SELECT 
                EXTRACT(YEAR FROM data_entrada) as ano,
                COUNT(*) as total,
                SUM(valor_servicos) as servicos,
                SUM(valor_pecas) as pecas,
                SUM(valor_total) as total_valor
            FROM ordens_servico
            WHERE data_entrada IS NOT NULL
            GROUP BY EXTRACT(YEAR FROM data_entrada)
            ORDER BY ano
        """)
        
        print("\nDistribuição por ano:")
        print("Ano    | Qtde OS | Serviços          | Peças             | Total")
        print("-" * 75)
        
        for row in pg_cursor.fetchall():
            if row[0]:  # se ano não é nulo
                print(f"{int(row[0]):4d}  | {row[1]:>7} | R$ {row[2]:>13,.2f} | R$ {row[3]:>13,.2f} | R$ {row[4]:>13,.2f}")

    except Exception as e:
        print(f"Erro durante a migração: {str(e)}")
        if 'pg_conn' in locals():
            pg_conn.rollback()
        raise
    finally:
        if 'access_cursor' in locals():
            access_cursor.close()
        if 'access_conn' in locals():
            access_conn.close()
        if 'pg_cursor' in locals():
            pg_cursor.close()
        if 'pg_conn' in locals():
            pg_conn.close()

if __name__ == "__main__":
    print("Iniciando migração das Ordens de Serviço...")
    print("Data e hora início:", datetime.now())
    migrate_os()
    print("\nData e hora fim:", datetime.now())
