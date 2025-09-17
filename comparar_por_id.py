#!/usr/bin/env python3
"""
Comparação mais precisa entre estoque atual do MS Access e PostgreSQL usando IDs
"""

import os
import sys
import django
import pyodbc
from decimal import Decimal

# Configurar Django
sys.path.append('backend/empresa')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'empresa.settings')
django.setup()

from contas.models.access import Produtos

def conectar_access():
    """Conecta ao banco MS Access"""
    access_path = r"C:\Users\Cirilo\Documents\Bancos\Cadastros\Cadastros.mdb"
    conn_str = (
        r'DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};'
        f'DBQ={access_path};'
        'PWD=010182;'
    )
    return pyodbc.connect(conn_str)

def comparar_por_id():
    print("=== COMPARAÇÃO POR ID: MS ACCESS vs POSTGRESQL ===\n")
    
    # Conectar ao MS Access
    try:
        conn_access = conectar_access()
        cursor_access = conn_access.cursor()
        
        # Query no MS Access - buscar por ID e Estoque
        cursor_access.execute("""
            SELECT Id, Codigo, Descricao, Custo, Estoque 
            FROM produtos 
            ORDER BY Id
        """)
        
        produtos_access = {}
        total_valor_access = Decimal('0')
        total_produtos_com_estoque_access = 0
        
        for row in cursor_access.fetchall():
            id_produto = int(row[0])
            codigo = row[1]
            descricao = row[2] or ''
            custo = Decimal(str(row[3] or 0))
            estoque = int(row[4] or 0)
            valor = custo * estoque
            
            produtos_access[id_produto] = {
                'codigo': codigo,
                'descricao': descricao,
                'custo': custo,
                'estoque': estoque,
                'valor': valor
            }
            
            if estoque > 0:
                total_valor_access += valor
                total_produtos_com_estoque_access += 1
        
        print(f"Total de produtos no Access: {len(produtos_access)}")
        print(f"Produtos com estoque > 0 no Access: {total_produtos_com_estoque_access}")
        print(f"Valor total do estoque no Access: R$ {total_valor_access:,.2f}")
        
    except Exception as e:
        print(f"Erro ao conectar ao MS Access: {e}")
        return
    
    print("\n" + "="*60 + "\n")
    
    # Query no PostgreSQL
    produtos_postgres = {}
    total_valor_postgres = Decimal('0')
    total_produtos_com_estoque_postgres = 0
    
    for produto in Produtos.objects.all():
        custo = produto.preco_custo or Decimal('0')
        estoque = produto.estoque_atual or 0
        valor = custo * estoque
        
        produtos_postgres[produto.id] = {
            'codigo': produto.codigo,
            'descricao': produto.nome,
            'custo': custo,
            'estoque': estoque,
            'valor': valor
        }
        
        if estoque > 0:
            total_valor_postgres += valor
            total_produtos_com_estoque_postgres += 1
    
    print(f"Total de produtos no PostgreSQL: {len(produtos_postgres)}")
    print(f"Produtos com estoque > 0 no PostgreSQL: {total_produtos_com_estoque_postgres}")
    print(f"Valor total do estoque no PostgreSQL: R$ {total_valor_postgres:,.2f}")
    
    print("\n" + "="*60 + "\n")
    
    # Comparação detalhada
    print("COMPARAÇÃO DETALHADA:")
    print("-" * 60)
    
    ids_comuns = set(produtos_access.keys()) & set(produtos_postgres.keys())
    ids_apenas_access = set(produtos_access.keys()) - set(produtos_postgres.keys())
    ids_apenas_postgres = set(produtos_postgres.keys()) - set(produtos_access.keys())
    
    print(f"IDs comuns: {len(ids_comuns)}")
    print(f"IDs apenas no Access: {len(ids_apenas_access)}")
    print(f"IDs apenas no PostgreSQL: {len(ids_apenas_postgres)}")
    
    # Verificar diferenças nos produtos comuns
    diferencas_estoque = []
    diferencas_custo = []
    produtos_sincronizados = 0
    
    for id_produto in ids_comuns:
        access_prod = produtos_access[id_produto]
        pg_prod = produtos_postgres[id_produto]
        
        # Verificar diferenças de estoque
        if access_prod['estoque'] != pg_prod['estoque']:
            diferencas_estoque.append({
                'id': id_produto,
                'codigo': access_prod['codigo'],
                'access_estoque': access_prod['estoque'],
                'pg_estoque': pg_prod['estoque'],
                'diferenca': pg_prod['estoque'] - access_prod['estoque']
            })
        
        # Verificar diferenças de custo (considerando pequenas diferenças de arredondamento)
        diff_custo = abs(access_prod['custo'] - pg_prod['custo'])
        if diff_custo > Decimal('0.01'):
            diferencas_custo.append({
                'id': id_produto,
                'codigo': access_prod['codigo'],
                'access_custo': access_prod['custo'],
                'pg_custo': pg_prod['custo'],
                'diferenca': pg_prod['custo'] - access_prod['custo']
            })
        
        # Se estoque e custo estão iguais
        if (access_prod['estoque'] == pg_prod['estoque'] and 
            abs(access_prod['custo'] - pg_prod['custo']) <= Decimal('0.01')):
            produtos_sincronizados += 1
    
    print(f"\nProdutos perfeitamente sincronizados: {produtos_sincronizados}")
    print(f"Produtos com diferenças de estoque: {len(diferencas_estoque)}")
    print(f"Produtos com diferenças de custo: {len(diferencas_custo)}")
    
    # Mostrar algumas diferenças de estoque
    if diferencas_estoque:
        print(f"\nPrimeiras 10 diferenças de estoque:")
        for diff in diferencas_estoque[:10]:
            print(f"  ID {diff['id']} ({diff['codigo']}): Access={diff['access_estoque']}, PG={diff['pg_estoque']}")
    
    # Verificar alguns produtos específicos
    print(f"\n=== VERIFICAÇÃO DE PRODUTOS ESPECÍFICOS ===")
    produtos_teste = [2867, 4673, 5288]  # IDs que testamos antes
    
    for id_produto in produtos_teste:
        if id_produto in produtos_access and id_produto in produtos_postgres:
            acc = produtos_access[id_produto]
            pg = produtos_postgres[id_produto]
            
            print(f"\nProduto ID {id_produto} ({acc['codigo']}):")
            print(f"  Access:    Estoque={acc['estoque']}, Custo={acc['custo']}, Valor={acc['valor']}")
            print(f"  PostgreSQL: Estoque={pg['estoque']}, Custo={pg['custo']}, Valor={pg['valor']}")
            
            if acc['estoque'] == pg['estoque'] and abs(acc['custo'] - pg['custo']) <= Decimal('0.01'):
                print(f"  ✅ SINCRONIZADO")
            else:
                print(f"  ❌ DIFERENÇA ENCONTRADA")
    
    # Resumo final
    print(f"\n=== RESUMO FINAL ===")
    print(f"Valor total Access:     R$ {total_valor_access:,.2f}")
    print(f"Valor total PostgreSQL: R$ {total_valor_postgres:,.2f}")
    diferenca_valor = total_valor_postgres - total_valor_access
    print(f"Diferença de valor:     R$ {diferenca_valor:,.2f}")
    
    if abs(diferenca_valor) < Decimal('0.01'):
        print("✅ VALORES TOTAIS PERFEITAMENTE SINCRONIZADOS!")
    else:
        print(f"⚠️  Diferença de valor encontrada: R$ {diferenca_valor:,.2f}")
    
    # Fechar conexões
    conn_access.close()

if __name__ == "__main__":
    comparar_por_id()