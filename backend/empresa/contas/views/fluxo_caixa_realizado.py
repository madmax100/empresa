# empresa/contas/views/fluxo_caixa_realizado.py
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q, Sum, Count
from django.db.models.functions import TruncMonth, TruncDay
from datetime import datetime, date
from decimal import Decimal
import time

from ..models.access import ContasPagar, ContasReceber


class FluxoCaixaRealizadoViewSet(viewsets.ViewSet):
    """
    ViewSet para consulta do fluxo de caixa realizado (apenas movimentações efetivadas)
    """

    def parse_date(self, date_str):
        """
        Converte string de data ISO para objeto date
        """
        if not date_str:
            return None
        try:
            date_str = date_str.split('T')[0]
            return date(*time.strptime(date_str, '%Y-%m-%d')[:3])
        except (ValueError, IndexError):
            return None

    @action(detail=False, methods=['get'])
    def movimentacoes_realizadas(self, request):
        """
        Retorna todas as movimentações realizadas (pagas/recebidas) no período
        """
        data_inicio = self.parse_date(request.query_params.get('data_inicio'))
        data_fim = self.parse_date(request.query_params.get('data_fim'))
        
        if not data_inicio or not data_fim:
            return Response(
                {'error': 'Parâmetros data_inicio e data_fim são obrigatórios (formato: YYYY-MM-DD)'}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        # Helper classificação de custo (FIXO/VARIÁVEL)
        def classificar_tipo_custo(especificacao: str | None):
            custos_fixos = {
                'SALARIOS', 'PRO-LABORE', 'HONOR. CONTABEIS', 'LUZ', 'AGUA', 'TELEFONE',
                'IMPOSTOS', 'ENCARGOS', 'REFEICAO', 'BENEFICIOS', 'OUTRAS DESPESAS',
                'MAT. DE ESCRITORIO', 'PAGTO SERVICOS', 'EMPRESTIMO', 'DESP. FINANCEIRAS'
            }
            custos_variaveis = {
                'FORNECEDORES', 'FRETE', 'COMISSOES', 'DESP. VEICULOS'
            }
            if not especificacao:
                return 'NÃO CLASSIFICADO'
            e = especificacao.upper()
            if e in custos_fixos:
                return 'FIXO'
            if e in custos_variaveis:
                return 'VARIÁVEL'
            return 'NÃO CLASSIFICADO'

        # Buscar contas a pagar realizadas
        contas_pagar = ContasPagar.objects.filter(
            data_pagamento__isnull=False,
            data_pagamento__date__gte=data_inicio,
            data_pagamento__date__lte=data_fim,
            status='P'  # Status pago
        ).select_related('fornecedor').values(
            'id',
            'data_pagamento',
            'valor_pago',
            'fornecedor__nome',
            'fornecedor__especificacao',
            'historico',
            'forma_pagamento'
        )

        # Buscar contas a receber realizadas
        contas_receber = ContasReceber.objects.filter(
            data_pagamento__isnull=False,
            data_pagamento__date__gte=data_inicio,
            data_pagamento__date__lte=data_fim,
            status='P'  # Status pago
        ).select_related('cliente').values(
            'id',
            'data_pagamento',
            'recebido',
            'cliente__id',
            'cliente__nome',
            'historico',
            'forma_pagamento'
        )

        # Consolidar dados
        movimentacoes = []
        
        # Adicionar saídas (contas a pagar)
        for conta in contas_pagar:
            tipo_custo = classificar_tipo_custo(conta.get('fornecedor__especificacao'))
            movimentacoes.append({
                'id': f"cp_{conta['id']}",
                'tipo': 'saida',
                'data_pagamento': conta['data_pagamento'],
                'valor': float(conta['valor_pago'] or 0),
                'contraparte': conta['fornecedor__nome'] or 'Fornecedor não informado',
                'historico': conta['historico'] or '',
                'forma_pagamento': conta['forma_pagamento'] or '',
                'origem': 'contas_pagar',
                'tipo_custo': tipo_custo
            })

        # Adicionar entradas (contas a receber)
        for conta in contas_receber:
            movimentacoes.append({
                'id': f"cr_{conta['id']}",
                'tipo': 'entrada',
                'data_pagamento': conta['data_pagamento'],
                'valor': float(conta['recebido'] or 0),
                'contraparte': conta['cliente__nome'] or 'Cliente não informado',
                'historico': conta['historico'] or '',
                'forma_pagamento': conta['forma_pagamento'] or '',
                'origem': 'contas_receber',
                'cliente_id': conta.get('cliente__id')
            })

        # Ordenar por data
        movimentacoes.sort(key=lambda x: x['data_pagamento'], reverse=True)

        # Calcular totais
        total_entradas = sum(m['valor'] for m in movimentacoes if m['tipo'] == 'entrada')
        total_saidas = sum(m['valor'] for m in movimentacoes if m['tipo'] == 'saida')
        saldo_liquido = total_entradas - total_saidas

        return Response({
            'periodo': {
                'data_inicio': data_inicio.strftime('%Y-%m-%d'),
                'data_fim': data_fim.strftime('%Y-%m-%d')
            },
            'resumo': {
                'total_entradas': total_entradas,
                'total_saidas': total_saidas,
                'saldo_liquido': saldo_liquido,
                'total_movimentacoes': len(movimentacoes)
            },
            'movimentacoes': movimentacoes
        })

    @action(detail=False, methods=['get'])
    def resumo_mensal(self, request):
        """
        Retorna resumo do fluxo de caixa realizado agrupado por mês
        """
        data_inicio = self.parse_date(request.query_params.get('data_inicio'))
        data_fim = self.parse_date(request.query_params.get('data_fim'))
        
        if not data_inicio or not data_fim:
            return Response(
                {'error': 'Parâmetros data_inicio e data_fim são obrigatórios (formato: YYYY-MM-DD)'}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        # Agrupar contas a pagar por mês
        pagar_mensal = ContasPagar.objects.filter(
            data_pagamento__isnull=False,
            data_pagamento__date__gte=data_inicio,
            data_pagamento__date__lte=data_fim,
            status='P'
        ).annotate(
            mes=TruncMonth('data_pagamento')
        ).values('mes').annotate(
            total_pago=Sum('valor_pago'),
            quantidade=Count('id')
        ).order_by('mes')

        # Agrupar contas a receber por mês
        receber_mensal = ContasReceber.objects.filter(
            data_pagamento__isnull=False,
            data_pagamento__date__gte=data_inicio,
            data_pagamento__date__lte=data_fim,
            status='P'
        ).annotate(
            mes=TruncMonth('data_pagamento')
        ).values('mes').annotate(
            total_recebido=Sum('recebido'),
            quantidade=Count('id')
        ).order_by('mes')

        # Consolidar dados por mês
        meses_dict = {}
        
        for item in pagar_mensal:
            mes = item['mes']
            if mes not in meses_dict:
                meses_dict[mes] = {
                    'mes': mes,
                    'entradas': 0,
                    'saidas': 0,
                    'saldo_liquido': 0,
                    'qtd_entradas': 0,
                    'qtd_saidas': 0
                }
            meses_dict[mes]['saidas'] = float(item['total_pago'] or 0)
            meses_dict[mes]['qtd_saidas'] = item['quantidade']

        for item in receber_mensal:
            mes = item['mes']
            if mes not in meses_dict:
                meses_dict[mes] = {
                    'mes': mes,
                    'entradas': 0,
                    'saidas': 0,
                    'saldo_liquido': 0,
                    'qtd_entradas': 0,
                    'qtd_saidas': 0
                }
            meses_dict[mes]['entradas'] = float(item['total_recebido'] or 0)
            meses_dict[mes]['qtd_entradas'] = item['quantidade']

        # Calcular saldo líquido para cada mês
        for mes_data in meses_dict.values():
            mes_data['saldo_liquido'] = mes_data['entradas'] - mes_data['saidas']

        # Converter para lista e ordenar
        resumo_mensal = list(meses_dict.values())
        resumo_mensal.sort(key=lambda x: x['mes'])

        # Calcular totais gerais
        total_entradas = sum(m['entradas'] for m in resumo_mensal)
        total_saidas = sum(m['saidas'] for m in resumo_mensal)
        total_saldo = total_entradas - total_saidas

        return Response({
            'periodo': {
                'data_inicio': data_inicio.strftime('%Y-%m-%d'),
                'data_fim': data_fim.strftime('%Y-%m-%d')
            },
            'totais': {
                'total_entradas': total_entradas,
                'total_saidas': total_saidas,
                'saldo_liquido': total_saldo
            },
            'resumo_mensal': resumo_mensal
        })

    @action(detail=False, methods=['get'])
    def resumo_diario(self, request):
        """
        Retorna resumo do fluxo de caixa realizado agrupado por dia
        """
        data_inicio = self.parse_date(request.query_params.get('data_inicio'))
        data_fim = self.parse_date(request.query_params.get('data_fim'))
        
        if not data_inicio or not data_fim:
            return Response(
                {'error': 'Parâmetros data_inicio e data_fim são obrigatórios (formato: YYYY-MM-DD)'}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        # Agrupar contas a pagar por dia
        pagar_diario = ContasPagar.objects.filter(
            data_pagamento__isnull=False,
            data_pagamento__date__gte=data_inicio,
            data_pagamento__date__lte=data_fim,
            status='P'
        ).annotate(
            dia=TruncDay('data_pagamento')
        ).values('dia').annotate(
            total_pago=Sum('valor_pago'),
            quantidade=Count('id')
        ).order_by('dia')

        # Agrupar contas a receber por dia
        receber_diario = ContasReceber.objects.filter(
            data_pagamento__isnull=False,
            data_pagamento__date__gte=data_inicio,
            data_pagamento__date__lte=data_fim,
            status='P'
        ).annotate(
            dia=TruncDay('data_pagamento')
        ).values('dia').annotate(
            total_recebido=Sum('recebido'),
            quantidade=Count('id')
        ).order_by('dia')

        # Consolidar dados por dia
        dias_dict = {}
        
        for item in pagar_diario:
            dia = item['dia']
            if dia not in dias_dict:
                dias_dict[dia] = {
                    'data': dia,
                    'entradas': 0,
                    'saidas': 0,
                    'saldo_liquido': 0,
                    'qtd_entradas': 0,
                    'qtd_saidas': 0
                }
            dias_dict[dia]['saidas'] = float(item['total_pago'] or 0)
            dias_dict[dia]['qtd_saidas'] = item['quantidade']

        for item in receber_diario:
            dia = item['dia']
            if dia not in dias_dict:
                dias_dict[dia] = {
                    'data': dia,
                    'entradas': 0,
                    'saidas': 0,
                    'saldo_liquido': 0,
                    'qtd_entradas': 0,
                    'qtd_saidas': 0
                }
            dias_dict[dia]['entradas'] = float(item['total_recebido'] or 0)
            dias_dict[dia]['qtd_entradas'] = item['quantidade']

        # Calcular saldo líquido para cada dia
        for dia_data in dias_dict.values():
            dia_data['saldo_liquido'] = dia_data['entradas'] - dia_data['saidas']

        # Converter para lista e ordenar
        resumo_diario = list(dias_dict.values())
        resumo_diario.sort(key=lambda x: x['data'])

        # Calcular totais gerais
        total_entradas = sum(d['entradas'] for d in resumo_diario)
        total_saidas = sum(d['saidas'] for d in resumo_diario)
        total_saldo = total_entradas - total_saidas

        return Response({
            'periodo': {
                'data_inicio': data_inicio.strftime('%Y-%m-%d'),
                'data_fim': data_fim.strftime('%Y-%m-%d')
            },
            'totais': {
                'total_entradas': total_entradas,
                'total_saidas': total_saidas,
                'saldo_liquido': total_saldo
            },
            'resumo_diario': resumo_diario
        })

    @action(detail=False, methods=['get'])
    def movimentacoes_vencimento_aberto(self, request):
        """
        Retorna movimentações com data de vencimento no período que estão em aberto (não pagas/recebidas)
        """
        data_inicio = self.parse_date(request.query_params.get('data_inicio'))
        data_fim = self.parse_date(request.query_params.get('data_fim'))
        
        if not data_inicio or not data_fim:
            return Response(
                {'error': 'Parâmetros data_inicio e data_fim são obrigatórios (formato: YYYY-MM-DD)'}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        # Helper classificação de custo (FIXO/VARIÁVEL)
        def classificar_tipo_custo(especificacao: str | None):
            custos_fixos = {
                'SALARIOS', 'PRO-LABORE', 'HONOR. CONTABEIS', 'LUZ', 'AGUA', 'TELEFONE',
                'IMPOSTOS', 'ENCARGOS', 'REFEICAO', 'BENEFICIOS', 'OUTRAS DESPESAS',
                'MAT. DE ESCRITORIO', 'PAGTO SERVICOS', 'EMPRESTIMO', 'DESP. FINANCEIRAS'
            }
            custos_variaveis = {
                'FORNECEDORES', 'FRETE', 'COMISSOES', 'DESP. VEICULOS'
            }
            if not especificacao:
                return 'NÃO CLASSIFICADO'
            e = especificacao.upper()
            if e in custos_fixos:
                return 'FIXO'
            if e in custos_variaveis:
                return 'VARIÁVEL'
            return 'NÃO CLASSIFICADO'

        # Buscar contas a pagar com vencimento no período e status aberto
        contas_pagar_aberto = ContasPagar.objects.filter(
            vencimento__date__gte=data_inicio,
            vencimento__date__lte=data_fim,
            status='A',  # Status aberto
            data_pagamento__isnull=True
        ).select_related('fornecedor').values(
            'id',
            'vencimento',
            'valor',
            'fornecedor__nome',
            'fornecedor__especificacao',
            'historico',
            'forma_pagamento',
            'data'
        )

        # Buscar contas a receber com vencimento no período e status aberto
        contas_receber_aberto = ContasReceber.objects.filter(
            vencimento__date__gte=data_inicio,
            vencimento__date__lte=data_fim,
            status='A',  # Status aberto
            data_pagamento__isnull=True
        ).select_related('cliente').values(
            'id',
            'vencimento',
            'valor',
            'cliente__id',
            'cliente__nome',
            'historico',
            'forma_pagamento',
            'data'
        )

        # Consolidar dados
        movimentacoes_abertas = []
        
        # Adicionar saídas pendentes (contas a pagar)
        for conta in contas_pagar_aberto:
            # Calcular dias para vencimento/atraso
            hoje = date.today()
            vencimento_date = conta['vencimento'].date() if conta['vencimento'] else None
            dias_vencimento = 0
            status_vencimento = 'no_prazo'
            
            if vencimento_date:
                diferenca = (vencimento_date - hoje).days
                dias_vencimento = diferenca
                if diferenca < 0:
                    status_vencimento = 'vencido'
                elif diferenca <= 3:
                    status_vencimento = 'vence_em_breve'
            
            tipo_custo = classificar_tipo_custo(conta.get('fornecedor__especificacao'))
            movimentacoes_abertas.append({
                'id': f"cp_{conta['id']}",
                'tipo': 'saida_pendente',
                'data_emissao': conta['data'],
                'data_vencimento': conta['vencimento'],
                'valor': float(conta['valor'] or 0),
                'contraparte': conta['fornecedor__nome'] or 'Fornecedor não informado',
                'historico': conta['historico'] or '',
                'forma_pagamento': conta['forma_pagamento'] or '',
                'origem': 'contas_pagar',
                'dias_vencimento': dias_vencimento,
                'status_vencimento': status_vencimento,
                'tipo_custo': tipo_custo
            })

        # Adicionar entradas pendentes (contas a receber)
        for conta in contas_receber_aberto:
            # Calcular dias para vencimento/atraso
            hoje = date.today()
            vencimento_date = conta['vencimento'].date() if conta['vencimento'] else None
            dias_vencimento = 0
            status_vencimento = 'no_prazo'
            
            if vencimento_date:
                diferenca = (vencimento_date - hoje).days
                dias_vencimento = diferenca
                if diferenca < 0:
                    status_vencimento = 'vencido'
                elif diferenca <= 3:
                    status_vencimento = 'vence_em_breve'
            
            movimentacoes_abertas.append({
                'id': f"cr_{conta['id']}",
                'tipo': 'entrada_pendente',
                'data_emissao': conta['data'],
                'data_vencimento': conta['vencimento'],
                'valor': float(conta['valor'] or 0),
                'contraparte': conta['cliente__nome'] or 'Cliente não informado',
                'historico': conta['historico'] or '',
                'forma_pagamento': conta['forma_pagamento'] or '',
                'origem': 'contas_receber',
                'dias_vencimento': dias_vencimento,
                'status_vencimento': status_vencimento,
                'cliente_id': conta.get('cliente__id')
            })

        # Ordenar por data de vencimento
        movimentacoes_abertas.sort(key=lambda x: x['data_vencimento'] if x['data_vencimento'] else date.min)

        # Calcular totais
        total_entradas_pendentes = sum(m['valor'] for m in movimentacoes_abertas if m['tipo'] == 'entrada_pendente')
        total_saidas_pendentes = sum(m['valor'] for m in movimentacoes_abertas if m['tipo'] == 'saida_pendente')
        saldo_pendente = total_entradas_pendentes - total_saidas_pendentes

        # Estatísticas por status de vencimento
        stats_vencimento = {
            'no_prazo': {'entradas': 0, 'saidas': 0, 'qtd_entradas': 0, 'qtd_saidas': 0},
            'vence_em_breve': {'entradas': 0, 'saidas': 0, 'qtd_entradas': 0, 'qtd_saidas': 0},
            'vencido': {'entradas': 0, 'saidas': 0, 'qtd_entradas': 0, 'qtd_saidas': 0}
        }

        for mov in movimentacoes_abertas:
            status_key = mov['status_vencimento']
            if mov['tipo'] == 'entrada_pendente':
                stats_vencimento[status_key]['entradas'] += mov['valor']
                stats_vencimento[status_key]['qtd_entradas'] += 1
            else:
                stats_vencimento[status_key]['saidas'] += mov['valor']
                stats_vencimento[status_key]['qtd_saidas'] += 1

        return Response({
            'periodo': {
                'data_inicio': data_inicio.strftime('%Y-%m-%d'),
                'data_fim': data_fim.strftime('%Y-%m-%d')
            },
            'resumo': {
                'total_entradas_pendentes': total_entradas_pendentes,
                'total_saidas_pendentes': total_saidas_pendentes,
                'saldo_liquido_pendente': saldo_pendente,
                'total_movimentacoes': len(movimentacoes_abertas)
            },
            'estatisticas_vencimento': stats_vencimento,
            'movimentacoes_abertas': movimentacoes_abertas
        })
