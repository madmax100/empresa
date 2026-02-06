# empresa/contas/views/fluxo_caixa_realizado.py
"""
ViewSet para consulta do fluxo de caixa.
- Utiliza APENAS ContasPagar e ContasReceber.
- Passado (< hoje): data_pagamento (status='P')
- Futuro (>= hoje): vencimento (status='A')
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Sum, Count, Q
from django.db.models.functions import TruncMonth, TruncDay
from datetime import datetime, date
import time

from ..models.access import ContasPagar, ContasReceber, ContratosLocacao


class FluxoCaixaRealizadoViewSet(viewsets.ViewSet):

    def parse_date(self, date_str):
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
        Movimentações efetivadas (pagas/recebidas) no período.
        """
        data_inicio = self.parse_date(request.query_params.get('data_inicio'))
        data_fim = self.parse_date(request.query_params.get('data_fim'))
        
        spec_pagar_raw = request.query_params.get('especificacao_pagar')
        spec_receber_raw = request.query_params.get('especificacao_receber')
        origem_receita_raw = request.query_params.get('origem_receita')
        
        specs_pagar = spec_pagar_raw.split(',') if spec_pagar_raw else []
        specs_receber = spec_receber_raw.split(',') if spec_receber_raw else []
        origem_receita = origem_receita_raw.split(',') if origem_receita_raw else []

        if not data_inicio or not data_fim:
            return Response({'error': 'Parâmetros data inválidos'}, status=400)

        # Filtros Base CP
        filters_cp = {
            'data_pagamento__isnull': False,
            'data_pagamento__date__gte': data_inicio,
            'data_pagamento__date__lte': data_fim,
            'status': 'P'
        }
        
        if specs_pagar:
            filters_cp['fornecedor__especificacao__in'] = specs_pagar

        # Contas a Pagar (Saídas realizadas)
        contas_pagar = ContasPagar.objects.filter(
            **filters_cp
        ).select_related('fornecedor').values(
            'id', 'data_pagamento', 'valor_pago', 
            'fornecedor__nome', 'historico', 'forma_pagamento', 'fornecedor__especificacao'
        )

        # Filtros Base CR
        filters_cr = {
            'data_pagamento__isnull': False,
            'data_pagamento__date__gte': data_inicio,
            'data_pagamento__date__lte': data_fim,
            'status': 'P'
        }
        
        if specs_receber:
            filters_cr['cliente__especificacao__in'] = specs_receber

        # Filtro de Origem (Contrato vs Venda)
        if origem_receita:
            # IDs de clientes com contratos ativos (fim >= hoje ou indefinido?)
            hoje = date.today()
            clientes_com_contrato = ContratosLocacao.objects.filter(
                fim__gte=hoje
            ).values_list('cliente_id', flat=True).distinct()
            
            q_origem = Q()
            if 'CONTRATO' in origem_receita:
                q_origem |= Q(cliente_id__in=clientes_com_contrato)
            if 'VENDA' in origem_receita:
                q_origem |= Q(~Q(cliente_id__in=clientes_com_contrato))
                
        qs_receber = ContasReceber.objects.filter(**filters_cr)
        
        if origem_receita:
            qs_receber = qs_receber.filter(q_origem)

        # Contas a Receber (Entradas realizadas)
        contas_receber = qs_receber.select_related('cliente').values(
            'id', 'data_pagamento', 'recebido',
            'cliente__nome', 'historico', 'forma_pagamento', 'cliente__especificacao'
        )

        movimentacoes = []

        for conta in contas_pagar:
            movimentacoes.append({
                'id': f"cp_{conta['id']}",
                'tipo': 'saida',
                'data': conta['data_pagamento'],
                'valor': float(conta['valor_pago'] or 0),
                'contraparte': conta['fornecedor__nome'] or 'Fornecedor não informado',
                'historico': conta['historico'] or '',
                'forma_pagamento': conta['forma_pagamento'] or '',
                'origem': 'contas_pagar'
            })

        for conta in contas_receber:
            movimentacoes.append({
                'id': f"cr_{conta['id']}",
                'tipo': 'entrada',
                'data': conta['data_pagamento'],
                'valor': float(conta['recebido'] or 0),
                'contraparte': conta['cliente__nome'] or 'Cliente não informado',
                'historico': conta['historico'] or '',
                'forma_pagamento': conta['forma_pagamento'] or '',
                'origem': 'contas_receber'
            })

        movimentacoes.sort(key=lambda x: x['data'] if x['data'] else datetime.min, reverse=True)

        total_entradas = sum(m['valor'] for m in movimentacoes if m['tipo'] == 'entrada')
        total_saidas = sum(m['valor'] for m in movimentacoes if m['tipo'] == 'saida')
        total_count = len(movimentacoes)

        # Paginação
        page = int(request.query_params.get('page', 1))
        page_size = int(request.query_params.get('page_size', 50))
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        paginated = movimentacoes[start_idx:end_idx]
        total_pages = (total_count + page_size - 1) // page_size if page_size > 0 else 1

        return Response({
            'periodo': {'data_inicio': str(data_inicio), 'data_fim': str(data_fim)},
            'resumo': {
                'total_entradas': total_entradas,
                'total_saidas': total_saidas,
                'saldo_liquido': total_entradas - total_saidas,
                'total_movimentacoes': total_count
            },
            'paginacao': {
                'page': page,
                'page_size': page_size,
                'total_pages': total_pages,
                'total_count': total_count
            },
            'movimentacoes': paginated
        })

    @action(detail=False, methods=['get'])
    def filtros(self, request):
        """
        Retorna listas para filtros (ex: especificações de fornecedores e clientes).
        """
        from ..models.access import Fornecedores, Clientes
        
        especificacoes_pagar = Fornecedores.objects.exclude(
            especificacao__isnull=True
        ).exclude(
            especificacao=''
        ).values_list('especificacao', flat=True).distinct().order_by('especificacao')

        especificacoes_receber = Clientes.objects.exclude(
            especificacao__isnull=True
        ).exclude(
            especificacao=''
        ).values_list('especificacao', flat=True).distinct().order_by('especificacao')
        
        return Response({
            'especificacoes_pagar': list(especificacoes_pagar),
            'especificacoes_receber': list(especificacoes_receber)
        })

    @action(detail=False, methods=['get'])
    def movimentacoes_previstas(self, request):
        """
        Movimentações previstas (pendentes) com vencimento no período.
        """
        data_inicio = self.parse_date(request.query_params.get('data_inicio'))
        data_fim = self.parse_date(request.query_params.get('data_fim'))
        
        # Get lists from query params (e.g. ?especificacao_pagar=A,B&especificacao_receber=C)
        # Note: DRF request.query_params.getlist might be needed if format is ?key=val&key=val2
        # If user sends comma separated (key=val1,val2), we split.
        
        spec_pagar_raw = request.query_params.get('especificacao_pagar')
        spec_receber_raw = request.query_params.get('especificacao_receber')
        origem_receita_raw = request.query_params.get('origem_receita')
        
        specs_pagar = spec_pagar_raw.split(',') if spec_pagar_raw else []
        specs_receber = spec_receber_raw.split(',') if spec_receber_raw else []
        origem_receita = origem_receita_raw.split(',') if origem_receita_raw else []
        
        if not data_inicio or not data_fim:
            return Response({'error': 'Parâmetros data inválidos'}, status=400)

        # Base filter CP
        filters_cp = {
            'vencimento__date__gte': data_inicio,
            'vencimento__date__lte': data_fim,
            'status': 'A'
        }
        
        if specs_pagar:
            filters_cp['fornecedor__especificacao__in'] = specs_pagar

        # Contas a Pagar pendentes
        contas_pagar = ContasPagar.objects.filter(
            **filters_cp
        ).select_related('fornecedor').values(
            'id', 'vencimento', 'valor',
            'fornecedor__nome', 'historico', 'fornecedor__especificacao'
        )

        # Base filter CR
        filters_cr = {
            'vencimento__date__gte': data_inicio,
            'vencimento__date__lte': data_fim,
            'status': 'A'
        }
        
        if specs_receber:
            filters_cr['cliente__especificacao__in'] = specs_receber
            
        # Filtro de Origem (Contrato vs Venda)
        if origem_receita:
            from ..models.access import ContratosLocacao
            # from datetime import date # Removed shadowed import
            
            # IDs de clientes com contratos ativos (fim >= hoje ou indefinido?)
            # Assumindo contratos ativos se fim >= hoje.
            from datetime import date as dt_date
            hoje = dt_date.today()
            clientes_com_contrato = ContratosLocacao.objects.filter(
                fim__gte=hoje
            ).values_list('cliente_id', flat=True).distinct()
            
            q_origem = Q()
            if 'CONTRATO' in origem_receita:
                q_origem |= Q(cliente_id__in=clientes_com_contrato)
            if 'VENDA' in origem_receita:
                q_origem |= Q(~Q(cliente_id__in=clientes_com_contrato))
            
            # Se ambos selecionados, traz tudo (lógica OR acima já cobre).
            # Se só um, o filtro Q() aplica corretamente.
            
            # Precisamos aplicar esse Q ao QuerySet.
            # Como filters_cr é um dict de kwargs, não aceita Q diretamente.
            # Vamos aplicar filters_cr primeiro e depois o Q.
            
        qs_receber = ContasReceber.objects.filter(**filters_cr)
        
        if origem_receita:
             qs_receber = qs_receber.filter(q_origem)

        contas_receber = qs_receber.select_related('cliente').values(
            'id', 'vencimento', 'valor',
            'cliente__nome', 'historico', 'cliente__especificacao'
        )

        movimentacoes = []
        hoje = date.today()

        for conta in contas_pagar:
            venc = conta['vencimento'].date() if conta['vencimento'] else None
            dias = (venc - hoje).days if venc else 0
            movimentacoes.append({
                'id': f"cp_{conta['id']}",
                'tipo': 'saida_prevista',
                'categoria': conta.get('fornecedor__especificacao') or 'Outros',
                'data_vencimento': conta['vencimento'],
                'valor': float(conta['valor'] or 0),
                'contraparte': conta['fornecedor__nome'] or 'Fornecedor não informado',
                'historico': conta['historico'] or '',
                'dias_para_vencimento': dias,
                'status': 'vencido' if dias < 0 else ('urgente' if dias <= 3 else 'no_prazo')
            })

        for conta in contas_receber:
            venc = conta['vencimento'].date() if conta['vencimento'] else None
            dias = (venc - hoje).days if venc else 0
            movimentacoes.append({
                'id': f"cr_{conta['id']}",
                'tipo': 'entrada_prevista',
                'categoria': conta.get('cliente__especificacao') or 'Outros',
                'data_vencimento': conta['vencimento'],
                'valor': float(conta['valor'] or 0),
                'contraparte': conta['cliente__nome'] or 'Cliente não informado',
                'historico': conta['historico'] or '',
                'dias_para_vencimento': dias,
                'status': 'vencido' if dias < 0 else ('urgente' if dias <= 3 else 'no_prazo')
            })

        movimentacoes.sort(key=lambda x: x['data_vencimento'] if x['data_vencimento'] else date.min)

        total_entradas = sum(m['valor'] for m in movimentacoes if m['tipo'] == 'entrada_prevista')
        total_saidas = sum(m['valor'] for m in movimentacoes if m['tipo'] == 'saida_prevista')
        total_count = len(movimentacoes)

        # Paginação
        page = int(request.query_params.get('page', 1))
        page_size = int(request.query_params.get('page_size', 50))
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        paginated = movimentacoes[start_idx:end_idx]
        total_pages = (total_count + page_size - 1) // page_size if page_size > 0 else 1

        return Response({
            'periodo': {'data_inicio': str(data_inicio), 'data_fim': str(data_fim)},
            'resumo': {
                'total_entradas_previstas': total_entradas,
                'total_saidas_previstas': total_saidas,
                'saldo_previsto': total_entradas - total_saidas,
                'total_movimentacoes': total_count
            },
            'paginacao': {
                'page': page,
                'page_size': page_size,
                'total_pages': total_pages,
                'total_count': total_count
            },
            'movimentacoes': paginated
        })

    @action(detail=False, methods=['get'])
    def resumo_mensal(self, request):
        """
        Resumo mensal do fluxo de caixa realizado com classificações:
        - Entradas: Contrato vs Vendas
        - Saídas: Fixas vs Variáveis
        Otimizado com agregação no banco de dados.
        """
        data_inicio = self.parse_date(request.query_params.get('data_inicio'))
        data_fim = self.parse_date(request.query_params.get('data_fim'))
        
        if not data_inicio or not data_fim:
            return Response({'error': 'Parâmetros data inválidos'}, status=400)

        from django.db.models import Case, When, Value, DecimalField
        from django.db.models.functions import Coalesce
        from ..models.access import ContratosLocacao

        # Obter IDs de clientes com contratos (uma única query)
        clientes_com_contrato = list(
            ContratosLocacao.objects.filter(
                cliente__isnull=False
            ).values_list('cliente_id', flat=True).distinct()
        )

        # Agregação de Contas a Receber com classificação por contrato
        receber_mensal = ContasReceber.objects.filter(
            data_pagamento__isnull=False,
            data_pagamento__date__gte=data_inicio,
            data_pagamento__date__lte=data_fim,
            status='P'
        ).annotate(
            mes=TruncMonth('data_pagamento'),
            valor_contrato=Case(
                When(cliente_id__in=clientes_com_contrato, then='recebido'),
                default=Value(0),
                output_field=DecimalField()
            ),
            valor_vendas=Case(
                When(cliente_id__in=clientes_com_contrato, then=Value(0)),
                default='recebido',
                output_field=DecimalField()
            )
        ).values('mes').annotate(
            entradas_contrato=Coalesce(Sum('valor_contrato'), Value(0), output_field=DecimalField()),
            entradas_vendas=Coalesce(Sum('valor_vendas'), Value(0), output_field=DecimalField()),
            total_entradas=Coalesce(Sum('recebido'), Value(0), output_field=DecimalField())
        )

        # Para saídas, precisamos fazer a classificação em Python porque
        # a lógica de palavras-chave não pode ser feita eficientemente no ORM
        # Mas podemos otimizar buscando todos os fornecedores de uma vez
        
        # Agregação de Contas a Pagar por mês (sem classificação ainda)
        pagar_mensal = ContasPagar.objects.filter(
            data_pagamento__isnull=False,
            data_pagamento__date__gte=data_inicio,
            data_pagamento__date__lte=data_fim,
            status='P'
        ).annotate(
            mes=TruncMonth('data_pagamento')
        ).values('mes').annotate(
            total_saidas=Coalesce(Sum('valor_pago'), Value(0), output_field=DecimalField()),
            quantidade=Count('id')
        )

        # Para classificar saídas fixas/variáveis, precisamos de uma query separada
        # Primeiro, identificamos fornecedores e seus totais
        KEYWORDS_FIXOS = ['FOLHA', 'PROLABORE', 'PRO-LABORE', 'ALUGUEL', 'SALARIO', 'SALÁRIO', 
                         'INSS', 'FGTS', 'CONTADOR', 'CONTABILIDADE', 'LUZ', 'ENERGIA', 
                         'ÁGUA', 'AGUA', 'TELEFONE', 'INTERNET', 'SEGURO']

        # Buscar totais por fornecedor por mês
        saidas_por_fornecedor = ContasPagar.objects.filter(
            data_pagamento__isnull=False,
            data_pagamento__date__gte=data_inicio,
            data_pagamento__date__lte=data_fim,
            status='P'
        ).annotate(
            mes=TruncMonth('data_pagamento')
        ).values('mes', 'fornecedor__nome').annotate(
            total=Sum('valor_pago')
        )

        # Classificar saídas fixas/variáveis
        saidas_classificadas = {}
        for item in saidas_por_fornecedor:
            mes = item['mes']
            if mes not in saidas_classificadas:
                saidas_classificadas[mes] = {'saidas_fixas': 0, 'saidas_variaveis': 0}
            
            fornecedor_nome = (item['fornecedor__nome'] or '').upper()
            valor = float(item['total'] or 0)
            is_fixo = any(keyword in fornecedor_nome for keyword in KEYWORDS_FIXOS)
            
            if is_fixo:
                saidas_classificadas[mes]['saidas_fixas'] += valor
            else:
                saidas_classificadas[mes]['saidas_variaveis'] += valor

        # Combinar resultados
        meses_dict = {}
        
        for item in receber_mensal:
            mes = item['mes']
            meses_dict[mes] = {
                'mes': mes,
                'entradas_contrato': float(item['entradas_contrato'] or 0),
                'entradas_vendas': float(item['entradas_vendas'] or 0),
                'total_entradas': float(item['total_entradas'] or 0),
                'saidas_fixas': 0, 'saidas_variaveis': 0, 'total_saidas': 0, 'saldo': 0
            }

        for item in pagar_mensal:
            mes = item['mes']
            if mes not in meses_dict:
                meses_dict[mes] = {
                    'mes': mes,
                    'entradas_contrato': 0, 'entradas_vendas': 0, 'total_entradas': 0,
                    'saidas_fixas': 0, 'saidas_variaveis': 0, 'total_saidas': 0, 'saldo': 0
                }
            meses_dict[mes]['total_saidas'] = float(item['total_saidas'] or 0)
            
            # Adicionar classificação de saídas
            if mes in saidas_classificadas:
                meses_dict[mes]['saidas_fixas'] = saidas_classificadas[mes]['saidas_fixas']
                meses_dict[mes]['saidas_variaveis'] = saidas_classificadas[mes]['saidas_variaveis']

        # Calcular saldos e ordenar
        meses_list = []
        for mes, dados in sorted(meses_dict.items()):
            dados['saldo'] = dados['total_entradas'] - dados['total_saidas']
            meses_list.append(dados)

        totais = {
            'entradas_contrato': sum(m['entradas_contrato'] for m in meses_list),
            'entradas_vendas': sum(m['entradas_vendas'] for m in meses_list),
            'total_entradas': sum(m['total_entradas'] for m in meses_list),
            'saidas_fixas': sum(m['saidas_fixas'] for m in meses_list),
            'saidas_variaveis': sum(m['saidas_variaveis'] for m in meses_list),
            'total_saidas': sum(m['total_saidas'] for m in meses_list),
            'saldo_liquido': sum(m['saldo'] for m in meses_list)
        }

        return Response({
            'periodo': {'data_inicio': str(data_inicio), 'data_fim': str(data_fim)},
            'totais': totais,
            'meses': meses_list
        })

    @action(detail=False, methods=['get'])
    def resumo_diario(self, request):
        """
        Resumo diário do fluxo de caixa realizado.
        """
        data_inicio = self.parse_date(request.query_params.get('data_inicio'))
        data_fim = self.parse_date(request.query_params.get('data_fim'))
        
        if not data_inicio or not data_fim:
            return Response({'error': 'Parâmetros data inválidos'}, status=400)

        dias_dict = {}

        # Contas a Pagar (Saídas)
        pagar_diario = ContasPagar.objects.filter(
            data_pagamento__isnull=False,
            data_pagamento__date__gte=data_inicio,
            data_pagamento__date__lte=data_fim,
            status='P'
        ).annotate(
            dia=TruncDay('data_pagamento')
        ).values('dia').annotate(
            total=Sum('valor_pago'),
            quantidade=Count('id')
        )

        for item in pagar_diario:
            dia = item['dia']
            if dia not in dias_dict:
                dias_dict[dia] = {'data': dia, 'entradas': 0, 'saidas': 0, 'saldo': 0, 'qtd_entradas': 0, 'qtd_saidas': 0}
            dias_dict[dia]['saidas'] += float(item['total'] or 0)
            dias_dict[dia]['qtd_saidas'] += item['quantidade']

        # Contas a Receber (Entradas)
        receber_diario = ContasReceber.objects.filter(
            data_pagamento__isnull=False,
            data_pagamento__date__gte=data_inicio,
            data_pagamento__date__lte=data_fim,
            status='P'
        ).annotate(
            dia=TruncDay('data_pagamento')
        ).values('dia').annotate(
            total=Sum('recebido'),
            quantidade=Count('id')
        )

        for item in receber_diario:
            dia = item['dia']
            if dia not in dias_dict:
                dias_dict[dia] = {'data': dia, 'entradas': 0, 'saidas': 0, 'saldo': 0, 'qtd_entradas': 0, 'qtd_saidas': 0}
            dias_dict[dia]['entradas'] += float(item['total'] or 0)
            dias_dict[dia]['qtd_entradas'] += item['quantidade']

        # Calcular saldos
        dias_list = []
        for dia, dados in sorted(dias_dict.items()):
            dados['saldo'] = dados['entradas'] - dados['saidas']
            dias_list.append(dados)

        totais = {
            'total_entradas': sum(d['entradas'] for d in dias_list),
            'total_saidas': sum(d['saidas'] for d in dias_list),
            'saldo_liquido': sum(d['saldo'] for d in dias_list)
        }

        return Response({
            'periodo': {'data_inicio': str(data_inicio), 'data_fim': str(data_fim)},
            'totais': totais,
            'resumo_diario': dias_list
        })

    @action(detail=False, methods=['get'])
    def fluxo_completo(self, request):
        """
        Retorna fluxo de caixa combinado: realizado + previsto.
        - Passado: usa data_pagamento (status='P')
        - Futuro: usa vencimento (status='A')
        """
        data_inicio = self.parse_date(request.query_params.get('data_inicio'))
        data_fim = self.parse_date(request.query_params.get('data_fim'))
        
        if not data_inicio or not data_fim:
            return Response({'error': 'Parâmetros data inválidos'}, status=400)

        hoje = date.today()
        movimentacoes = []

        # --- PASSADO: Realizadas ---
        if data_inicio < hoje:
            data_fim_passado = min(data_fim, hoje)
            
            # CP Realizadas
            cp_realizadas = ContasPagar.objects.filter(
                data_pagamento__isnull=False,
                data_pagamento__date__gte=data_inicio,
                data_pagamento__date__lt=data_fim_passado,
                status='P'
            ).select_related('fornecedor').values(
                'id', 'data_pagamento', 'valor_pago', 'fornecedor__nome', 'historico'
            )
            for cp in cp_realizadas:
                movimentacoes.append({
                    'id': f"cp_{cp['id']}",
                    'tipo': 'saida',
                    'status_mov': 'realizado',
                    'data': cp['data_pagamento'],
                    'valor': float(cp['valor_pago'] or 0),
                    'contraparte': cp['fornecedor__nome'] or 'Fornecedor',
                    'historico': cp['historico'] or ''
                })

            # CR Realizadas
            cr_realizadas = ContasReceber.objects.filter(
                data_pagamento__isnull=False,
                data_pagamento__date__gte=data_inicio,
                data_pagamento__date__lt=data_fim_passado,
                status='P'
            ).select_related('cliente').values(
                'id', 'data_pagamento', 'recebido', 'cliente__nome', 'historico'
            )
            for cr in cr_realizadas:
                movimentacoes.append({
                    'id': f"cr_{cr['id']}",
                    'tipo': 'entrada',
                    'status_mov': 'realizado',
                    'data': cr['data_pagamento'],
                    'valor': float(cr['recebido'] or 0),
                    'contraparte': cr['cliente__nome'] or 'Cliente',
                    'historico': cr['historico'] or ''
                })

        # --- FUTURO: Previsões ---
        if data_fim >= hoje:
            data_inicio_futuro = max(data_inicio, hoje)
            
            # CP Previstas
            cp_previstas = ContasPagar.objects.filter(
                vencimento__date__gte=data_inicio_futuro,
                vencimento__date__lte=data_fim,
                status='A'
            ).select_related('fornecedor').values(
                'id', 'vencimento', 'valor', 'fornecedor__nome', 'historico'
            )
            for cp in cp_previstas:
                movimentacoes.append({
                    'id': f"cp_{cp['id']}",
                    'tipo': 'saida',
                    'status_mov': 'previsto',
                    'data': cp['vencimento'],
                    'valor': float(cp['valor'] or 0),
                    'contraparte': cp['fornecedor__nome'] or 'Fornecedor',
                    'historico': cp['historico'] or ''
                })

            # CR Previstas
            cr_previstas = ContasReceber.objects.filter(
                vencimento__date__gte=data_inicio_futuro,
                vencimento__date__lte=data_fim,
                status='A'
            ).select_related('cliente').values(
                'id', 'vencimento', 'valor', 'cliente__nome', 'historico'
            )
            for cr in cr_previstas:
                movimentacoes.append({
                    'id': f"cr_{cr['id']}",
                    'tipo': 'entrada',
                    'status_mov': 'previsto',
                    'data': cr['vencimento'],
                    'valor': float(cr['valor'] or 0),
                    'contraparte': cr['cliente__nome'] or 'Cliente',
                    'historico': cr['historico'] or ''
                })

        movimentacoes.sort(key=lambda x: x['data'] if x['data'] else datetime.min)

        # Totais
        realizado_entradas = sum(m['valor'] for m in movimentacoes if m['tipo'] == 'entrada' and m['status_mov'] == 'realizado')
        realizado_saidas = sum(m['valor'] for m in movimentacoes if m['tipo'] == 'saida' and m['status_mov'] == 'realizado')
        previsto_entradas = sum(m['valor'] for m in movimentacoes if m['tipo'] == 'entrada' and m['status_mov'] == 'previsto')
        previsto_saidas = sum(m['valor'] for m in movimentacoes if m['tipo'] == 'saida' and m['status_mov'] == 'previsto')

        return Response({
            'periodo': {'data_inicio': str(data_inicio), 'data_fim': str(data_fim)},
            'resumo': {
                'realizado': {
                    'entradas': realizado_entradas,
                    'saidas': realizado_saidas,
                    'saldo': realizado_entradas - realizado_saidas
                },
                'previsto': {
                    'entradas': previsto_entradas,
                    'saidas': previsto_saidas,
                    'saldo': previsto_entradas - previsto_saidas
                },
                'total': {
                    'entradas': realizado_entradas + previsto_entradas,
                    'saidas': realizado_saidas + previsto_saidas,
                    'saldo': (realizado_entradas + previsto_entradas) - (realizado_saidas + previsto_saidas)
                }
            },
            'movimentacoes': movimentacoes
        })
