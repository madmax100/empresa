#!/usr/bin/env python3
"""
Comparação detalhada entre estoque atual do MS Access e PostgreSQL
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

def comparar_estoques():
    print("=== COMPARAÇÃO ESTOQUE: MS ACCESS vs POSTGRESQL ===\n")
    
    # Conectar ao MS Access
    try:
        conn_access = conectar_access()
        cursor_access = conn_access.cursor()
        
        # Query no MS Access
        cursor_access.execute("""
            SELECT Codigo, Descricao, Custo, Estoque 
            FROM produtos 
            WHERE Estoque > 0 
            ORDER BY Estoque DESC
        """)
        
        produtos_access = {}
        total_access = Decimal('0')
        
        print("PRODUTOS COM ESTOQUE NO MS ACCESS:")
        print("-" * 80)
        print(f"{'Código':<10} {'Descrição':<40} {'Custo':<12} {'Estoque':<10} {'Valor':<15}")
        print("-" * 80)
        
        for row in cursor_access.fetchall():
            codigo = row[0]
            descricao = row[1] or ''
            custo = Decimal(str(row[2] or 0))
            estoque = int(row[3] or 0)
            valor = custo * estoque
            
            produtos_access[codigo] = {
                'descricao': descricao,
                'custo': custo,
                'estoque': estoque,
                'valor': valor
            }
            
            total_access += valor
            
            if len(produtos_access) <= 10:  # Mostrar apenas os primeiros 10
                print(f"{codigo:<10} {descricao[:38]:<40} {custo:<12} {estoque:<10} {valor:<15}")
        
        print(f"\nTotal de produtos com estoque no Access: {len(produtos_access)}")
        print(f"Valor total do estoque no Access: R$ {total_access:,.2f}")
        
    except Exception as e:
        print(f"Erro ao conectar ao MS Access: {e}")
        return
    
    print("\n" + "="*80 + "\n")
    
    # Query no PostgreSQL
    produtos_postgres = Produtos.objects.filter(estoque_atual__gt=0).order_by('-estoque_atual')
    
    total_postgres = Decimal('0')
    produtos_pg_dict = {}
    
    print("PRODUTOS COM ESTOQUE NO POSTGRESQL:")
    print("-" * 80)
    print(f"{'Código':<10} {'Descrição':<40} {'Custo':<12} {'Estoque':<10} {'Valor':<15}")
    print("-" * 80)
    
    count = 0
    for produto in produtos_postgres:
        custo = produto.preco_custo or Decimal('0')
        estoque = produto.estoque_atual or 0
        valor = custo * estoque
        
        produtos_pg_dict[produto.codigo] = {
            'descricao': produto.nome,
            'custo': custo,
            'estoque': estoque,
            'valor': valor
        }
        
        total_postgres += valor
        
        if count < 10:  # Mostrar apenas os primeiros 10
            print(f"{produto.codigo:<10} {produto.nome[:38]:<40} {custo:<12} {estoque:<10} {valor:<15}")
        count += 1
    
    print(f"\nTotal de produtos com estoque no PostgreSQL: {len(produtos_pg_dict)}")
    print(f"Valor total do estoque no PostgreSQL: R$ {total_postgres:,.2f}")
    
    print("\n" + "="*80 + "\n")
    
    # Comparação
    print("COMPARAÇÃO DOS VALORES:")
    print("-" * 50)
    print(f"Access:     R$ {total_access:,.2f}")
    print(f"PostgreSQL: R$ {total_postgres:,.2f}")
    diferenca = total_postgres - total_access
    print(f"Diferença:  R$ {diferenca:,.2f}")
    
    if abs(diferenca) < Decimal('0.01'):
        print("✅ VALORES IGUAIS!")
    else:
        print(f"❌ DIFERENÇA ENCONTRADA: R$ {diferenca:,.2f}")
    
    # Analisar diferenças produto por produto
    print("\n=== ANÁLISE DETALHADA DAS DIFERENÇAS ===\n")
    
    diferencas_encontradas = 0
    
    # Produtos apenas no Access
    apenas_access = set(produtos_access.keys()) - set(produtos_pg_dict.keys())
    if apenas_access:
        print(f"Produtos apenas no Access ({len(apenas_access)}):")
        for codigo in list(apenas_access)[:5]:
            produto = produtos_access[codigo]
            print(f"  {codigo}: {produto['estoque']} unidades (R$ {produto['valor']:,.2f})")
        if len(apenas_access) > 5:
            print(f"  ... e mais {len(apenas_access) - 5} produtos")
        diferencas_encontradas += len(apenas_access)
    
    # Produtos apenas no PostgreSQL
    apenas_postgres = set(produtos_pg_dict.keys()) - set(produtos_access.keys())
    if apenas_postgres:
        print(f"\nProdutos apenas no PostgreSQL ({len(apenas_postgres)}):")
        for codigo in list(apenas_postgres)[:5]:
            produto = produtos_pg_dict[codigo]
            print(f"  {codigo}: {produto['estoque']} unidades (R$ {produto['valor']:,.2f})")
        if len(apenas_postgres) > 5:
            print(f"  ... e mais {len(apenas_postgres) - 5} produtos")
        diferencas_encontradas += len(apenas_postgres)
    
    # Produtos com diferenças de estoque
    produtos_comuns = set(produtos_access.keys()) & set(produtos_pg_dict.keys())
    diferencas_estoque = []
    
    for codigo in produtos_comuns:
        access_prod = produtos_access[codigo]
        pg_prod = produtos_pg_dict[codigo]
        
        if access_prod['estoque'] != pg_prod['estoque']:
            diferencas_estoque.append({
                'codigo': codigo,
                'access_estoque': access_prod['estoque'],
                'pg_estoque': pg_prod['estoque'],
                'diferenca': pg_prod['estoque'] - access_prod['estoque']
            })
    
    if diferencas_estoque:
        print(f"\nProdutos com diferenças de estoque ({len(diferencas_estoque)}):")
        for diff in diferencas_estoque[:10]:
            print(f"  {diff['codigo']}: Access={diff['access_estoque']}, PG={diff['pg_estoque']}, Dif={diff['diferenca']}")
        if len(diferencas_estoque) > 10:
            print(f"  ... e mais {len(diferencas_estoque) - 10} produtos")
        diferencas_encontradas += len(diferencas_estoque)
    
    print(f"\nTotal de diferenças encontradas: {diferencas_encontradas}")
    
    if diferencas_encontradas == 0:
        print("✅ TODAS AS QUANTIDADES ESTÃO SINCRONIZADAS!")
    
    # Fechar conexões
    conn_access.close()

if __name__ == "__main__":
    comparar_estoques()