#!/usr/bin/env python3
"""
Comparação por código entre estoque atual do MS Access e PostgreSQL
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

def comparar_por_codigo():
    print("=== COMPARAÇÃO POR CÓDIGO: MS ACCESS vs POSTGRESQL ===\n")
    
    # Conectar ao MS Access
    try:
        conn_access = conectar_access()
        cursor_access = conn_access.cursor()
        
        # Query no MS Access
        cursor_access.execute("""
            SELECT Codigo, Descricao, Custo, Estoque 
            FROM produtos 
            ORDER BY Codigo
        """)
        
        produtos_access = {}
        total_valor_access = Decimal('0')
        total_produtos_com_estoque_access = 0
        
        for row in cursor_access.fetchall():
            codigo = str(row[0]).strip() if row[0] else ''
            descricao = str(row[1]).strip() if row[1] else ''
            custo = Decimal(str(row[2] or 0))
            estoque = int(row[3] or 0)
            valor = custo * estoque
            
            produtos_access[codigo] = {
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
    
    for produto in Produtos.objects.all().order_by('codigo'):
        codigo = str(produto.codigo).strip() if produto.codigo else ''
        custo = produto.preco_custo or Decimal('0')
        estoque = produto.estoque_atual or 0
        valor = custo * estoque
        
        produtos_postgres[codigo] = {
            'id': produto.id,
            'descricao': produto.nome or '',
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
    
    codigos_comuns = set(produtos_access.keys()) & set(produtos_postgres.keys())
    codigos_apenas_access = set(produtos_access.keys()) - set(produtos_postgres.keys())
    codigos_apenas_postgres = set(produtos_postgres.keys()) - set(produtos_access.keys())
    
    print(f"Códigos comuns: {len(codigos_comuns)}")
    print(f"Códigos apenas no Access: {len(codigos_apenas_access)}")
    print(f"Códigos apenas no PostgreSQL: {len(codigos_apenas_postgres)}")
    
    # Verificar diferenças nos produtos comuns
    diferencas_estoque = []
    diferencas_custo = []
    produtos_sincronizados = 0
    
    for codigo in codigos_comuns:
        if not codigo:  # Pular códigos vazios
            continue
            
        access_prod = produtos_access[codigo]
        pg_prod = produtos_postgres[codigo]
        
        # Verificar diferenças de estoque
        if access_prod['estoque'] != pg_prod['estoque']:
            diferencas_estoque.append({
                'codigo': codigo,
                'access_estoque': access_prod['estoque'],
                'pg_estoque': pg_prod['estoque'],
                'diferenca': pg_prod['estoque'] - access_prod['estoque'],
                'pg_id': pg_prod['id']
            })
        
        # Verificar diferenças de custo (considerando pequenas diferenças de arredondamento)
        diff_custo = abs(access_prod['custo'] - pg_prod['custo'])
        if diff_custo > Decimal('0.01'):
            diferencas_custo.append({
                'codigo': codigo,
                'access_custo': access_prod['custo'],
                'pg_custo': pg_prod['custo'],
                'diferenca': pg_prod['custo'] - access_prod['custo'],
                'pg_id': pg_prod['id']
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
            print(f"  {diff['codigo']} (ID {diff['pg_id']}): Access={diff['access_estoque']}, PG={diff['pg_estoque']}, Dif={diff['diferenca']}")
    
    if diferencas_custo:
        print(f"\nPrimeiras 10 diferenças de custo:")
        for diff in diferencas_custo[:10]:
            print(f"  {diff['codigo']} (ID {diff['pg_id']}): Access=R$ {diff['access_custo']}, PG=R$ {diff['pg_custo']}")
    
    # Verificar alguns produtos específicos que testamos antes
    print(f"\n=== VERIFICAÇÃO DE PRODUTOS ESPECÍFICOS ===")
    produtos_teste = ['2867', '4673', '5288']  # Códigos que testamos antes
    
    for codigo in produtos_teste:
        if codigo in produtos_access and codigo in produtos_postgres:
            acc = produtos_access[codigo]
            pg = produtos_postgres[codigo]
            
            print(f"\nProduto {codigo} (ID {pg['id']}):")
            print(f"  Access:     Estoque={acc['estoque']}, Custo=R$ {acc['custo']}, Valor=R$ {acc['valor']}")
            print(f"  PostgreSQL: Estoque={pg['estoque']}, Custo=R$ {pg['custo']}, Valor=R$ {pg['valor']}")
            
            if acc['estoque'] == pg['estoque'] and abs(acc['custo'] - pg['custo']) <= Decimal('0.01'):
                print(f"  ✅ SINCRONIZADO")
            else:
                print(f"  ❌ DIFERENÇA ENCONTRADA")
                if acc['estoque'] != pg['estoque']:
                    print(f"     Diferença estoque: {pg['estoque'] - acc['estoque']}")
                if abs(acc['custo'] - pg['custo']) > Decimal('0.01'):
                    print(f"     Diferença custo: R$ {pg['custo'] - acc['custo']}")
        else:
            print(f"\nProduto {codigo}: Não encontrado em um dos sistemas")
    
    # Verificar produtos apenas em um dos sistemas
    if codigos_apenas_access:
        print(f"\n=== PRODUTOS APENAS NO ACCESS ({len(codigos_apenas_access)}) ===")
        valor_apenas_access = Decimal('0')
        for codigo in list(codigos_apenas_access)[:10]:
            if codigo:  # Pular códigos vazios
                prod = produtos_access[codigo]
                valor_apenas_access += prod['valor']
                print(f"  {codigo}: Estoque={prod['estoque']}, Valor=R$ {prod['valor']}")
        if len(codigos_apenas_access) > 10:
            print(f"  ... e mais {len(codigos_apenas_access) - 10} produtos")
    
    if codigos_apenas_postgres:
        print(f"\n=== PRODUTOS APENAS NO POSTGRESQL ({len(codigos_apenas_postgres)}) ===")
        valor_apenas_postgres = Decimal('0')
        for codigo in list(codigos_apenas_postgres)[:10]:
            if codigo:  # Pular códigos vazios
                prod = produtos_postgres[codigo]
                valor_apenas_postgres += prod['valor']
                print(f"  {codigo} (ID {prod['id']}): Estoque={prod['estoque']}, Valor=R$ {prod['valor']}")
        if len(codigos_apenas_postgres) > 10:
            print(f"  ... e mais {len(codigos_apenas_postgres) - 10} produtos")
    
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
    
    sincronizacao_percentual = (produtos_sincronizados / len(codigos_comuns)) * 100 if codigos_comuns else 0
    print(f"Taxa de sincronização: {sincronizacao_percentual:.1f}% ({produtos_sincronizados}/{len(codigos_comuns)})")
    
    # Fechar conexões
    conn_access.close()

if __name__ == "__main__":
    comparar_por_codigo()