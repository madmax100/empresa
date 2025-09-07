#!/usr/bin/env python3
"""
Script para corrigir o estoque iniciando em 01/01/2025
ATENÇÃO: Este script modifica dados no banco. Execute com cuidado!
"""

import os
import sys
import django
from datetime import datetime, date
from decimal import Decimal
import json

# Configurar Django
sys.path.append('c:/Users/Cirilo/Documents/c3mcopias/backend/empresa')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'empresa.settings')
django.setup()

from django.db import transaction
from django.utils import timezone
from contas.models import MovimentacoesEstoque, SaldosEstoque, Produtos, TiposMovimentacaoEstoque

class CorretorEstoque:
    def __init__(self):
        self.data_corte = timezone.make_aware(datetime(2025, 1, 1, 0, 0, 0))
        self.backup_file = 'backup_estoque_antes_correcao.json'
        
    def fazer_backup(self):
        """Faz backup dos dados atuais"""
        print("=== FAZENDO BACKUP DOS DADOS ATUAIS ===")
        
        backup_data = {
            'data_backup': datetime.now().isoformat(),
            'movimentacoes': [],
            'saldos': []
        }
        
        # Backup das movimentações
        print("Fazendo backup das movimentações...")
        movimentacoes = MovimentacoesEstoque.objects.all()
        for mov in movimentacoes:
            backup_data['movimentacoes'].append({
                'id': mov.id,
                'data_movimentacao': mov.data_movimentacao.isoformat(),
                'tipo_movimentacao_id': mov.tipo_movimentacao.id if mov.tipo_movimentacao else None,
                'produto_id': mov.produto.id if mov.produto else None,
                'quantidade': str(mov.quantidade),
                'custo_unitario': str(mov.custo_unitario) if mov.custo_unitario else None,
                'valor_total': str(mov.valor_total) if mov.valor_total else None,
                'observacoes': mov.observacoes,
                'documento_referencia': mov.documento_referencia,
            })
        
        # Backup dos saldos
        print("Fazendo backup dos saldos...")
        saldos = SaldosEstoque.objects.all()
        for saldo in saldos:
            backup_data['saldos'].append({
                'id': saldo.id,
                'produto_id': saldo.produto_id.id if saldo.produto_id else None,
                'local_id': saldo.local_id.id if saldo.local_id else None,
                'lote_id': saldo.lote_id.id if saldo.lote_id else None,
                'quantidade': str(saldo.quantidade),
                'quantidade_reservada': str(saldo.quantidade_reservada),
                'custo_medio': str(saldo.custo_medio) if saldo.custo_medio else None,
                'ultima_movimentacao': saldo.ultima_movimentacao.isoformat() if saldo.ultima_movimentacao else None,
            })
        
        # Salvar backup
        with open(self.backup_file, 'w', encoding='utf-8') as f:
            json.dump(backup_data, f, indent=2, ensure_ascii=False)
        
        print(f"Backup salvo em: {self.backup_file}")
        print(f"Movimentações: {len(backup_data['movimentacoes'])}")
        print(f"Saldos: {len(backup_data['saldos'])}")
        
    def obter_saldos_atuais(self):
        """Obtém os saldos atuais de produtos com estoque positivo"""
        print("\n=== OBTENDO SALDOS ATUAIS ===")
        
        saldos_positivos = SaldosEstoque.objects.filter(
            quantidade__gt=0
        ).select_related('produto_id')
        
        saldos_para_manter = []
        for saldo in saldos_positivos:
            if saldo.produto_id:
                saldos_para_manter.append({
                    'produto': saldo.produto_id,
                    'quantidade': saldo.quantidade,
                    'custo_medio': saldo.custo_medio or saldo.produto_id.preco_custo or Decimal('0.00'),
                    'local_id': saldo.local_id,
                    'lote_id': saldo.lote_id
                })
        
        print(f"Produtos com saldo positivo: {len(saldos_para_manter)}")
        return saldos_para_manter
        
    def limpar_movimentacoes_antigas(self):
        """Remove movimentações anteriores a 01/01/2025"""
        print("\n=== LIMPANDO MOVIMENTAÇÕES ANTIGAS ===")
        
        movs_antigas = MovimentacoesEstoque.objects.filter(
            data_movimentacao__lt=self.data_corte
        )
        
        total_antigas = movs_antigas.count()
        print(f"Movimentações a serem removidas: {total_antigas}")
        
        if total_antigas > 0:
            confirm = input("Confirma a remoção das movimentações antigas? (S/N): ")
            if confirm.upper() == 'S':
                movs_antigas.delete()
                print(f"Removidas {total_antigas} movimentações antigas")
            else:
                print("Operação cancelada")
                return False
        
        return True
    
    def criar_tipo_estoque_inicial(self):
        """Cria tipo de movimentação para estoque inicial se não existir"""
        print("\n=== VERIFICANDO TIPO DE MOVIMENTAÇÃO ===")
        
        tipo_inicial, created = TiposMovimentacaoEstoque.objects.get_or_create(
            codigo='EST_INI',
            defaults={
                'descricao': 'Estoque Inicial',
                'tipo': 'E',
                'movimenta_custo': True,
                'ativo': True
            }
        )
        
        if created:
            print("Criado tipo 'Estoque Inicial'")
        else:
            print("Tipo 'Estoque Inicial' já existe")
            
        return tipo_inicial
    
    def criar_movimentacoes_iniciais(self, saldos_para_manter, tipo_movimentacao):
        """Cria movimentações de estoque inicial para 01/01/2025"""
        print("\n=== CRIANDO MOVIMENTAÇÕES INICIAIS ===")
        
        movimentacoes_criadas = 0
        total_produtos = len(saldos_para_manter)
        
        for i, saldo_info in enumerate(saldos_para_manter):
            if i % 50 == 0:
                print(f"Processando produto {i+1} de {total_produtos}")
            
            # Criar movimentação de entrada
            MovimentacoesEstoque.objects.create(
                data_movimentacao=self.data_corte,
                tipo_movimentacao=tipo_movimentacao,
                produto=saldo_info['produto'],
                lote_id=saldo_info['lote_id'],
                local_origem_id=None,
                local_destino_id=saldo_info['local_id'],
                quantidade=saldo_info['quantidade'],
                custo_unitario=saldo_info['custo_medio'],
                valor_total=saldo_info['quantidade'] * saldo_info['custo_medio'],
                observacoes='Estoque inicial - Migração para 01/01/2025',
                documento_referencia='EST_INICIAL_2025',
                usuario_id=1
            )
            
            movimentacoes_criadas += 1
        
        print(f"Criadas {movimentacoes_criadas} movimentações de estoque inicial")
        return movimentacoes_criadas
    
    def limpar_saldos_antigos(self):
        """Remove todos os saldos antigos para recalculo"""
        print("\n=== LIMPANDO SALDOS ANTIGOS ===")
        
        total_saldos = SaldosEstoque.objects.count()
        print(f"Saldos a serem removidos: {total_saldos}")
        
        if total_saldos > 0:
            SaldosEstoque.objects.all().delete()
            print(f"Removidos {total_saldos} saldos antigos")
    
    def recalcular_saldos(self):
        """Recalcula saldos baseado nas novas movimentações"""
        print("\n=== RECALCULANDO SALDOS ===")
        
        from django.db.models import Sum, Case, When, F
        
        # Buscar todas as movimentações de 2025 em diante
        movimentacoes = MovimentacoesEstoque.objects.filter(
            data_movimentacao__gte=self.data_corte
        ).select_related('produto', 'tipo_movimentacao')
        
        print(f"Movimentações para recálculo: {movimentacoes.count()}")
        
        # Agrupar por produto
        produtos_movimentados = {}
        for mov in movimentacoes:
            if not mov.produto:
                continue
                
            produto_id = mov.produto.id
            if produto_id not in produtos_movimentados:
                produtos_movimentados[produto_id] = {
                    'produto': mov.produto,
                    'entradas': Decimal('0'),
                    'saidas': Decimal('0'),
                    'valor_entradas': Decimal('0'),
                    'valor_saidas': Decimal('0'),
                    'local_id': None,
                    'lote_id': None,
                    'ultima_movimentacao': mov.data_movimentacao
                }
            
            info = produtos_movimentados[produto_id]
            
            if mov.tipo_movimentacao and mov.tipo_movimentacao.tipo == 'E':
                info['entradas'] += mov.quantidade
                if mov.valor_total:
                    info['valor_entradas'] += mov.valor_total
            elif mov.tipo_movimentacao and mov.tipo_movimentacao.tipo == 'S':
                info['saidas'] += mov.quantidade
                if mov.valor_total:
                    info['valor_saidas'] += mov.valor_total
            
            # Atualizar informações do local e lote
            if mov.local_destino_id:
                info['local_id'] = mov.local_destino_id
            if mov.lote_id:
                info['lote_id'] = mov.lote_id
            
            # Atualizar última movimentação
            if mov.data_movimentacao > info['ultima_movimentacao']:
                info['ultima_movimentacao'] = mov.data_movimentacao
        
        # Criar novos saldos
        saldos_criados = 0
        for produto_id, info in produtos_movimentados.items():
            saldo_final = info['entradas'] - info['saidas']
            
            if saldo_final != 0:  # Só criar saldo se diferente de zero
                # Calcular custo médio
                custo_medio = Decimal('0')
                if info['entradas'] > 0 and info['valor_entradas'] > 0:
                    custo_medio = info['valor_entradas'] / info['entradas']
                elif info['produto'].preco_custo:
                    custo_medio = info['produto'].preco_custo
                
                SaldosEstoque.objects.create(
                    produto_id=info['produto'],
                    local_id=info['local_id'],
                    lote_id=info['lote_id'],
                    quantidade=saldo_final,
                    quantidade_reservada=Decimal('0'),
                    custo_medio=custo_medio,
                    ultima_movimentacao=info['ultima_movimentacao']
                )
                
                saldos_criados += 1
        
        print(f"Criados {saldos_criados} novos saldos")
        return saldos_criados
    
    def validar_resultado(self, saldos_originais):
        """Valida se a correção foi bem-sucedida"""
        print("\n=== VALIDANDO RESULTADO ===")
        
        # Verificar se não há movimentações antes de 2025
        movs_antigas = MovimentacoesEstoque.objects.filter(
            data_movimentacao__lt=self.data_corte
        ).count()
        
        print(f"Movimentações antes de 01/01/2025: {movs_antigas}")
        
        # Verificar movimentações de 2025
        movs_2025 = MovimentacoesEstoque.objects.filter(
            data_movimentacao__gte=self.data_corte
        ).count()
        
        print(f"Movimentações de 01/01/2025 em diante: {movs_2025}")
        
        # Verificar saldos
        saldos_atuais = SaldosEstoque.objects.count()
        saldos_positivos = SaldosEstoque.objects.filter(quantidade__gt=0).count()
        
        print(f"Total de saldos: {saldos_atuais}")
        print(f"Saldos positivos: {saldos_positivos}")
        print(f"Saldos originais positivos: {len(saldos_originais)}")
        
        # Verificar valor total do estoque
        valor_total = sum(
            saldo.quantidade * (saldo.custo_medio or Decimal('0'))
            for saldo in SaldosEstoque.objects.filter(quantidade__gt=0)
        )
        
        print(f"Valor total do estoque: R$ {valor_total:,.2f}")
        
        sucesso = (movs_antigas == 0 and saldos_positivos > 0)
        print(f"\nValidação: {'SUCESSO' if sucesso else 'FALHA'}")
        
        return sucesso
    
    def executar_correcao(self):
        """Executa todo o processo de correção"""
        print("=== CORREÇÃO DO ESTOQUE PARA 01/01/2025 ===")
        print("ATENÇÃO: Esta operação modificará dados no banco!")
        print("Certifique-se de ter um backup completo do banco antes de continuar.")
        
        confirm = input("\nDeseja continuar com a correção? (S/N): ")
        if confirm.upper() != 'S':
            print("Operação cancelada pelo usuário")
            return False
        
        try:
            with transaction.atomic():
                # 1. Fazer backup
                self.fazer_backup()
                
                # 2. Obter saldos atuais
                saldos_originais = self.obter_saldos_atuais()
                
                if not saldos_originais:
                    print("ERRO: Nenhum saldo positivo encontrado!")
                    return False
                
                # 3. Limpar movimentações antigas
                if not self.limpar_movimentacoes_antigas():
                    return False
                
                # 4. Criar tipo de movimentação
                tipo_inicial = self.criar_tipo_estoque_inicial()
                
                # 5. Criar movimentações iniciais
                self.criar_movimentacoes_iniciais(saldos_originais, tipo_inicial)
                
                # 6. Limpar saldos antigos
                self.limpar_saldos_antigos()
                
                # 7. Recalcular saldos
                self.recalcular_saldos()
                
                # 8. Validar resultado
                sucesso = self.validar_resultado(saldos_originais)
                
                if not sucesso:
                    raise Exception("Validação falhou - transação será revertida")
                
                # Confirmar transação
                print("\nTodos os passos executados com sucesso!")
                confirmar_final = input("Confirma a aplicação das mudanças? (S/N): ")
                
                if confirmar_final.upper() != 'S':
                    raise Exception("Operação cancelada pelo usuário")
                
                print("✅ Correção do estoque concluída com sucesso!")
                return True
                
        except Exception as e:
            print(f"❌ ERRO durante a correção: {e}")
            print("Todas as mudanças foram revertidas")
            return False

if __name__ == '__main__':
    corretor = CorretorEstoque()
    corretor.executar_correcao()
