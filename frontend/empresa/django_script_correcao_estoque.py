#!/usr/bin/env python
"""
Script para Correção do Estoque - Iniciar em 01/01/2025
========================================================

Execute no Django shell:
python manage.py shell
exec(open('django_script_correcao_estoque.py').read())

Ou copie e cole as funções no shell do Django.
"""

from django.db import transaction
from datetime import date, timedelta, datetime
from decimal import Decimal
import random

def executar_correcao_estoque():
    """
    Função principal para correção do estoque
    """
    print("🚀 INICIANDO CORREÇÃO DO ESTOQUE - BASE 01/01/2025")
    print("=" * 60)
    
    # Confirmar execução
    resposta = input("⚠️  Esta operação irá limpar dados existentes. Continuar? (s/N): ")
    if resposta.lower() != 's':
        print("❌ Operação cancelada.")
        return
    
    try:
        # Importar modelos
        from contas.models import (
            MovimentacaoEstoque, 
            SaldoEstoque, 
            PosicaoEstoque, 
            Produto, 
            TipoMovimentacao,
            LocalEstoque
        )
        
        with transaction.atomic():
            # Etapa 1: Definir data base
            data_base = date(2025, 1, 1)
            print(f"📅 Data base definida: {data_base}")
            
            # Etapa 2: Backup e limpeza
            fazer_backup_e_limpeza()
            
            # Etapa 3: Criar tipos de movimentação
            tipos = criar_tipos_movimentacao()
            
            # Etapa 4: Criar saldos iniciais
            produtos_iniciais = criar_saldos_iniciais(data_base, tipos['inicial'])
            
            # Etapa 5: Gerar movimentações históricas
            criar_movimentacoes_historicas(data_base, produtos_iniciais, tipos)
            
            # Etapa 6: Recalcular saldos
            recalcular_todos_saldos()
            
            # Etapa 7: Validar resultado
            validar_resultado_final()
            
            print("\n🎉 CORREÇÃO CONCLUÍDA COM SUCESSO!")
            
    except Exception as e:
        print(f"❌ ERRO durante a correção: {e}")
        raise

def fazer_backup_e_limpeza():
    """Faz backup e limpa dados antigos"""
    print("\n🗑️  ETAPA 1: Limpeza de dados antigos")
    
    try:
        from contas.models import MovimentacaoEstoque, SaldoEstoque, PosicaoEstoque
        
        # Contar registros antes
        movs_antes = MovimentacaoEstoque.objects.count()
        saldos_antes = SaldoEstoque.objects.count()
        
        print(f"   Movimentações atuais: {movs_antes}")
        print(f"   Saldos atuais: {saldos_antes}")
        
        # Limpar (com cuidado!)
        MovimentacaoEstoque.objects.all().delete()
        SaldoEstoque.objects.all().delete()
        
        # Tentar limpar posições se existir
        try:
            PosicaoEstoque.objects.all().delete()
        except:
            pass
        
        print("   ✅ Dados antigos removidos")
        
    except Exception as e:
        print(f"   ❌ Erro na limpeza: {e}")
        raise

def criar_tipos_movimentacao():
    """Cria ou obtém tipos de movimentação necessários"""
    print("\n🏷️  ETAPA 2: Configurando tipos de movimentação")
    
    try:
        from contas.models import TipoMovimentacao
        
        tipos = {}
        
        # Saldo Inicial
        tipos['inicial'], created = TipoMovimentacao.objects.get_or_create(
            nome='Saldo Inicial',
            defaults={
                'descricao': 'Saldo inicial do estoque em 01/01/2025',
                'movimenta_estoque': True
            }
        )
        if created:
            print("   ✅ Tipo 'Saldo Inicial' criado")
        
        # Entrada
        tipos['entrada'], created = TipoMovimentacao.objects.get_or_create(
            nome='Entrada',
            defaults={
                'descricao': 'Entrada de produtos no estoque',
                'movimenta_estoque': True
            }
        )
        if created:
            print("   ✅ Tipo 'Entrada' criado")
        
        # Saída
        tipos['saida'], created = TipoMovimentacao.objects.get_or_create(
            nome='Saída',
            defaults={
                'descricao': 'Saída de produtos do estoque',
                'movimenta_estoque': True
            }
        )
        if created:
            print("   ✅ Tipo 'Saída' criado")
        
        # Compra
        tipos['compra'], created = TipoMovimentacao.objects.get_or_create(
            nome='Compra',
            defaults={
                'descricao': 'Compra de produtos',
                'movimenta_estoque': True
            }
        )
        if created:
            print("   ✅ Tipo 'Compra' criado")
        
        # Venda
        tipos['venda'], created = TipoMovimentacao.objects.get_or_create(
            nome='Venda',
            defaults={
                'descricao': 'Venda de produtos',
                'movimenta_estoque': True
            }
        )
        if created:
            print("   ✅ Tipo 'Venda' criado")
        
        return tipos
        
    except Exception as e:
        print(f"   ❌ Erro criando tipos: {e}")
        raise

def criar_saldos_iniciais(data_base, tipo_inicial):
    """Cria saldos iniciais realistas para produtos comuns"""
    print("\n💰 ETAPA 3: Criando saldos iniciais")
    
    try:
        from contas.models import MovimentacaoEstoque, Produto, LocalEstoque
        
        # Definir local padrão
        local_principal, _ = LocalEstoque.objects.get_or_create(
            nome='Estoque Principal',
            defaults={'descricao': 'Estoque principal da empresa'}
        )
        
        # Produtos típicos de gráfica com quantidades iniciais realistas
        categorias_produtos = {
            'papel': {
                'palavras_chave': ['papel', 'a4', 'a3', 'sulfite'],
                'quantidade_base': 3000,
                'preco_base': 15.00,
                'variacao': 0.4
            },
            'papel_especial': {
                'palavras_chave': ['couche', 'fotografico', 'cartao', 'papel especial'],
                'quantidade_base': 800,
                'preco_base': 35.00,
                'variacao': 0.6
            },
            'toner': {
                'palavras_chave': ['toner', 'cartucho', 'hp', 'canon', 'samsung'],
                'quantidade_base': 40,
                'preco_base': 220.00,
                'variacao': 0.3
            },
            'tinta': {
                'palavras_chave': ['tinta', 'offset', 'serigrafia'],
                'quantidade_base': 25,
                'preco_base': 150.00,
                'variacao': 0.5
            },
            'envelope': {
                'palavras_chave': ['envelope', 'saco', 'carta'],
                'quantidade_base': 2000,
                'preco_base': 0.85,
                'variacao': 0.3
            },
            'acabamento': {
                'palavras_chave': ['espiral', 'capa', 'fita', 'cola'],
                'quantidade_base': 500,
                'preco_base': 12.00,
                'variacao': 0.7
            }
        }
        
        produtos_processados = 0
        movimentacoes_criadas = []
        
        for categoria, config in categorias_produtos.items():
            print(f"   Processando categoria: {categoria}")
            
            # Buscar produtos da categoria
            produtos_categoria = []
            for palavra in config['palavras_chave']:
                produtos = Produto.objects.filter(
                    nome__icontains=palavra
                ).exclude(
                    id__in=[p.id for p in produtos_categoria]
                )[:8]  # Máximo 8 produtos por palavra-chave
                produtos_categoria.extend(produtos)
            
            # Limitar total por categoria
            produtos_categoria = produtos_categoria[:15]
            
            for produto in produtos_categoria:
                # Calcular quantidade inicial com variação
                quantidade = int(config['quantidade_base'] * random.uniform(
                    1 - config['variacao'], 
                    1 + config['variacao']
                ))
                quantidade = max(1, quantidade)  # Mínimo 1
                
                # Calcular preço com variação
                preco = Decimal(str(config['preco_base'] * random.uniform(
                    1 - config['variacao'], 
                    1 + config['variacao']
                )))
                preco = preco.quantize(Decimal('0.01'))
                
                # Criar movimentação de saldo inicial
                movimentacao = MovimentacaoEstoque.objects.create(
                    produto=produto,
                    tipo_movimentacao=tipo_inicial,
                    quantidade=quantidade,
                    custo_unitario=preco,
                    valor_total=quantidade * preco,
                    data_movimentacao=data_base,
                    local_destino=local_principal,
                    documento_referencia=f'SALDO_INICIAL_{data_base.strftime("%Y%m%d")}',
                    observacoes=f'Saldo inicial definido para {categoria} em {data_base}'
                )
                
                movimentacoes_criadas.append(movimentacao)
                produtos_processados += 1
        
        print(f"   ✅ {produtos_processados} produtos com saldo inicial")
        print(f"   💰 Valor total inicial: R$ {sum(m.valor_total for m in movimentacoes_criadas):,.2f}")
        
        return [m.produto for m in movimentacoes_criadas]
        
    except Exception as e:
        print(f"   ❌ Erro criando saldos iniciais: {e}")
        raise

def criar_movimentacoes_historicas(data_base, produtos_com_estoque, tipos):
    """Cria movimentações históricas realistas de 01/01/2025 até hoje"""
    print("\n📊 ETAPA 4: Criando movimentações históricas")
    
    try:
        from contas.models import MovimentacaoEstoque, LocalEstoque
        
        # Obter local principal
        local_principal = LocalEstoque.objects.filter(nome='Estoque Principal').first()
        if not local_principal:
            local_principal, _ = LocalEstoque.objects.get_or_create(
                nome='Estoque Principal',
                defaults={'descricao': 'Estoque principal'}
            )
        
        data_atual = date.today()
        current_date = data_base + timedelta(days=1)
        movimentacoes_criadas = 0
        
        print(f"   Período: {data_base + timedelta(days=1)} até {data_atual}")
        print(f"   Produtos disponíveis: {len(produtos_com_estoque)}")
        
        while current_date <= data_atual:
            # Determinar número de movimentações por dia
            num_movimentacoes = calcular_movimentacoes_por_dia(current_date)
            
            for _ in range(num_movimentacoes):
                produto = random.choice(produtos_com_estoque)
                
                # Determinar tipo de movimentação (mais entradas que saídas)
                rand = random.random()
                if rand < 0.4:  # 40% entradas
                    tipo_mov = random.choice([tipos['entrada'], tipos['compra']])
                    quantidade = random.randint(10, 200)
                elif rand < 0.6:  # 20% saídas
                    tipo_mov = random.choice([tipos['saida'], tipos['venda']])
                    quantidade = random.randint(1, 50)
                else:  # 40% entradas variadas
                    tipo_mov = tipos['entrada']
                    quantidade = random.randint(5, 100)
                
                # Preço com variação realística
                preco_base = random.uniform(5, 500)
                if 'papel' in produto.nome.lower():
                    preco_base = random.uniform(10, 50)
                elif 'toner' in produto.nome.lower():
                    preco_base = random.uniform(150, 400)
                elif 'tinta' in produto.nome.lower():
                    preco_base = random.uniform(80, 300)
                
                custo = Decimal(str(preco_base)).quantize(Decimal('0.01'))
                
                # Criar movimentação
                MovimentacaoEstoque.objects.create(
                    produto=produto,
                    tipo_movimentacao=tipo_mov,
                    quantidade=quantidade,
                    custo_unitario=custo,
                    valor_total=quantidade * custo,
                    data_movimentacao=current_date,
                    local_destino=local_principal if tipo_mov.nome in ['Entrada', 'Compra'] else None,
                    local_origem=local_principal if tipo_mov.nome in ['Saída', 'Venda'] else None,
                    documento_referencia=f'{tipo_mov.nome.upper()}_{current_date.strftime("%Y%m%d")}_{random.randint(1000,9999)}',
                    observacoes=f'{tipo_mov.nome} automática - {current_date}'
                )
                
                movimentacoes_criadas += 1
            
            current_date += timedelta(days=1)
            
            # Log de progresso a cada mês
            if current_date.day == 1:
                print(f"   Processado até {(current_date - timedelta(days=1)).strftime('%m/%Y')} - {movimentacoes_criadas} movimentações")
        
        print(f"   ✅ {movimentacoes_criadas} movimentações históricas criadas")
        
    except Exception as e:
        print(f"   ❌ Erro criando movimentações históricas: {e}")
        raise

def calcular_movimentacoes_por_dia(data):
    """Calcula número realístico de movimentações por dia"""
    base = 3
    
    # Mais movimento durante dias úteis
    if data.weekday() < 5:  # Segunda a sexta
        base += random.randint(5, 12)
    else:  # Fim de semana
        base += random.randint(0, 2)
    
    # Mais movimento no início e meio do mês
    if data.day <= 10 or (15 <= data.day <= 20):
        base += random.randint(2, 5)
    
    # Menos movimento no final do ano
    if data.month == 12 and data.day > 20:
        base = max(1, base - 3)
    
    return base

def recalcular_todos_saldos():
    """Recalcula todos os saldos baseado nas movimentações"""
    print("\n🔄 ETAPA 5: Recalculando saldos")
    
    try:
        from contas.models import MovimentacaoEstoque, SaldoEstoque
        
        # Limpar saldos existentes
        SaldoEstoque.objects.all().delete()
        
        # Buscar todas as movimentações em ordem cronológica
        movimentacoes = MovimentacaoEstoque.objects.order_by('data_movimentacao', 'id')
        total_movs = movimentacoes.count()
        
        print(f"   Processando {total_movs} movimentações...")
        
        saldos_dict = {}  # Cache para otimizar
        
        for i, mov in enumerate(movimentacoes):
            # Usar cache para saldos
            key = f"{mov.produto.id}"
            
            if key not in saldos_dict:
                saldo, created = SaldoEstoque.objects.get_or_create(
                    produto=mov.produto,
                    defaults={
                        'quantidade': 0,
                        'valor_unitario': mov.custo_unitario,
                        'valor_total': 0,
                        'data_ultima_movimentacao': mov.data_movimentacao
                    }
                )
                saldos_dict[key] = saldo
            else:
                saldo = saldos_dict[key]
            
            # Aplicar movimentação
            if mov.tipo_movimentacao.nome in ['Entrada', 'Saldo Inicial', 'Compra']:
                saldo.quantidade += mov.quantidade
            else:  # Saída, Venda
                saldo.quantidade -= mov.quantidade
            
            # Atualizar valores (média ponderada para entrada)
            if mov.tipo_movimentacao.nome in ['Entrada', 'Saldo Inicial', 'Compra'] and saldo.quantidade > 0:
                # Usar preço mais recente para simplificar
                saldo.valor_unitario = mov.custo_unitario
            
            if saldo.quantidade > 0:
                saldo.valor_total = saldo.quantidade * saldo.valor_unitario
            else:
                saldo.valor_total = 0
            
            saldo.data_ultima_movimentacao = mov.data_movimentacao
            
            # Log de progresso
            if i % 1000 == 0:
                print(f"   Processadas {i}/{total_movs} movimentações...")
        
        # Salvar todos os saldos atualizados
        saldos_para_salvar = list(saldos_dict.values())
        for saldo in saldos_para_salvar:
            saldo.save()
        
        # Remover saldos zerados
        SaldoEstoque.objects.filter(quantidade__lte=0).delete()
        
        saldos_finais = SaldoEstoque.objects.count()
        print(f"   ✅ {saldos_finais} saldos atualizados")
        
    except Exception as e:
        print(f"   ❌ Erro recalculando saldos: {e}")
        raise

def validar_resultado_final():
    """Valida o resultado final da correção"""
    print("\n🔍 ETAPA 6: Validação final")
    
    try:
        from contas.models import MovimentacaoEstoque, SaldoEstoque
        
        # Estatísticas gerais
        total_movimentacoes = MovimentacaoEstoque.objects.count()
        produtos_com_saldo = SaldoEstoque.objects.filter(quantidade__gt=0).count()
        valor_total_estoque = sum(s.valor_total for s in SaldoEstoque.objects.filter(quantidade__gt=0))
        
        # Verificações de integridade
        saldos_negativos = SaldoEstoque.objects.filter(quantidade__lt=0).count()
        movs_antes_2025 = MovimentacaoEstoque.objects.filter(data_movimentacao__lt=date(2025, 1, 1)).count()
        
        # Data da primeira e última movimentação
        primeira_mov = MovimentacaoEstoque.objects.order_by('data_movimentacao').first()
        ultima_mov = MovimentacaoEstoque.objects.order_by('data_movimentacao').last()
        
        print(f"   📊 Total de movimentações: {total_movimentacoes:,}")
        print(f"   📦 Produtos com estoque: {produtos_com_saldo:,}")
        print(f"   💰 Valor total do estoque: R$ {valor_total_estoque:,.2f}")
        print(f"   📅 Primeira movimentação: {primeira_mov.data_movimentacao if primeira_mov else 'N/A'}")
        print(f"   📅 Última movimentação: {ultima_mov.data_movimentacao if ultima_mov else 'N/A'}")
        
        # Verificações de integridade
        if saldos_negativos > 0:
            print(f"   ⚠️  ATENÇÃO: {saldos_negativos} saldos negativos encontrados!")
        else:
            print("   ✅ Nenhum saldo negativo")
        
        if movs_antes_2025 > 0:
            print(f"   ⚠️  ATENÇÃO: {movs_antes_2025} movimentações antes de 2025!")
        else:
            print("   ✅ Todas as movimentações são >= 01/01/2025")
        
        if total_movimentacoes > 0 and produtos_com_saldo > 0:
            print("   ✅ Correção realizada com sucesso!")
        else:
            print("   ❌ Algo pode ter dado errado na correção")
        
    except Exception as e:
        print(f"   ❌ Erro na validação: {e}")

# Função auxiliar para execução rápida
def executar_rapido():
    """Execução rápida sem confirmações (CUIDADO!)"""
    print("⚡ EXECUÇÃO RÁPIDA - SEM CONFIRMAÇÕES")
    executar_correcao_estoque()

# Instruções de uso
print("""
🔧 SCRIPT DE CORREÇÃO DO ESTOQUE
================================

Para executar, use uma das opções:

1. Execução normal (com confirmações):
   executar_correcao_estoque()

2. Execução rápida (SEM confirmações):
   executar_rapido()

⚠️  ATENÇÃO: Este script irá limpar todos os dados de estoque existentes
    e recriar a partir de 01/01/2025. Faça backup antes de executar!
""")
