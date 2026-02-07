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
from django.db.models import Sum, Count, Q, Value, DecimalField, F, DateTimeField, Case, When
from django.db.models.functions import TruncMonth, TruncDay, Coalesce
from datetime import datetime, date
import time

from ..models.access import ContasPagar, ContasReceber, ContratosLocacao
from .dre_views import DREView
from datetime import timedelta
from decimal import Decimal


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

        # Filtro de Especificação (Pagar)
        queries_pagar = Q()
        if specs_pagar:
            if '(Sem Categoria)' in specs_pagar:
                queries_pagar |= Q(fornecedor__especificacao__isnull=True) | Q(fornecedor__especificacao='')
                specs_pagar = [s for s in specs_pagar if s != '(Sem Categoria)']
            
            if specs_pagar:
                queries_pagar |= Q(fornecedor__especificacao__in=specs_pagar)

        contas_pagar = ContasPagar.objects.annotate(
            data_efetiva=Coalesce('data_pagamento', 'vencimento')
        ).filter(
            queries_pagar,
            data_efetiva__date__range=[data_inicio, data_fim],
            status='P'
        ).select_related('fornecedor').values(
            'id', 'data_efetiva', 'valor_total_pago', 'valor',
            'fornecedor__nome', 'historico', 'forma_pagamento', 'fornecedor__especificacao'
        )

        # Filtro de Especificação (Receber)
        queries_receber = Q()
        if specs_receber:
            if '(Sem Categoria)' in specs_receber:
                queries_receber |= Q(cliente__especificacao__isnull=True) | Q(cliente__especificacao='')
                specs_receber = [s for s in specs_receber if s != '(Sem Categoria)']
            
            if specs_receber:
                queries_receber |= Q(cliente__especificacao__in=specs_receber)

        # Filtro de Origem (Contrato vs Venda)
        filters_cr = {} 
        qs_receber = ContasReceber.objects.filter(queries_receber, **filters_cr)

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
            
            qs_receber = qs_receber.filter(q_origem)

        contas_receber = qs_receber.annotate(
            data_efetiva=Coalesce('data_pagamento', 'vencimento')
        ).filter(
            data_efetiva__date__range=[data_inicio, data_fim],
            status='P'
        ).select_related('cliente').values(
            'id', 'data_efetiva', 'valor_total_pago', 'valor',
            'cliente__nome', 'historico', 'forma_pagamento', 'cliente__especificacao'
        )

        movimentacoes = []

        for conta in contas_pagar:
            movimentacoes.append({
                'id': f"cp_{conta['id']}",
                'tipo': 'saida',
                'data': conta['data_efetiva'],
                'valor': float(conta['valor_total_pago'] or conta['valor'] or 0),
                'contraparte': conta['fornecedor__nome'] or 'Fornecedor não informado',
                'historico': conta['historico'] or '',
                'forma_pagamento': conta['forma_pagamento'] or '',
                'origem': 'contas_pagar'
            })

        for conta in contas_receber:
            movimentacoes.append({
                'id': f"cr_{conta['id']}",
                'tipo': 'entrada',
                'data': conta['data_efetiva'],
                'valor': float(conta['valor_total_pago'] or conta['valor'] or 0),
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
        Inclui opção "(Sem Categoria)" se houver itens sem especificação.
        """
        from ..models.access import Fornecedores, Clientes
        
        # Pagar
        especificacoes_pagar = list(Fornecedores.objects.exclude(
            especificacao__isnull=True
        ).exclude(
            especificacao=''
        ).values_list('especificacao', flat=True).distinct().order_by('especificacao'))
        
        has_empty_pagar = Fornecedores.objects.filter(Q(especificacao__isnull=True) | Q(especificacao='')).exists()
        if has_empty_pagar:
            especificacoes_pagar.insert(0, '(Sem Categoria)')

        # Receber
        especificacoes_receber = list(Clientes.objects.exclude(
            especificacao__isnull=True
        ).exclude(
            especificacao=''
        ).values_list('especificacao', flat=True).distinct().order_by('especificacao'))
        
        has_empty_receber = Clientes.objects.filter(Q(especificacao__isnull=True) | Q(especificacao='')).exists()
        if has_empty_receber:
            especificacoes_receber.insert(0, '(Sem Categoria)')
        
        return Response({
            'especificacoes_pagar': especificacoes_pagar,
            'especificacoes_receber': especificacoes_receber
        })

    @action(detail=False, methods=['get'])
    def movimentacoes_previstas(self, request):
        """
        Movimentações previstas (pendentes) com vencimento no período.
        """
        data_inicio = self.parse_date(request.query_params.get('data_inicio'))
        data_fim = self.parse_date(request.query_params.get('data_fim'))
        
        spec_pagar_raw = request.query_params.get('especificacao_pagar')
        spec_receber_raw = request.query_params.get('especificacao_receber')
        origem_receita_raw = request.query_params.get('origem_receita')
        
        specs_pagar = spec_pagar_raw.split(',') if spec_pagar_raw else []
        specs_receber = spec_receber_raw.split(',') if spec_receber_raw else []
        origem_receita = origem_receita_raw.split(',') if origem_receita_raw else []
        
        # Helper para lógica de filtro de categoria
        def get_category_query_pagar(specs):
            q = Q()
            if not specs: return q
            
            local_specs = list(specs)
            if '(Sem Categoria)' in local_specs:
                q |= Q(fornecedor__especificacao__isnull=True) | Q(fornecedor__especificacao='')
                local_specs = [s for s in local_specs if s != '(Sem Categoria)']
            
            if local_specs:
                q |= Q(fornecedor__especificacao__in=local_specs)
            return q

        def get_category_query_receber(specs):
            q = Q()
            if not specs: return q
            
            local_specs = list(specs)
            if '(Sem Categoria)' in local_specs:
                q |= Q(cliente__especificacao__isnull=True) | Q(cliente__especificacao='')
                local_specs = [s for s in local_specs if s != '(Sem Categoria)']
            
            if local_specs:
                q |= Q(cliente__especificacao__in=local_specs)
            return q
            
        q_cat_pagar = get_category_query_pagar(specs_pagar)
        q_cat_receber = get_category_query_receber(specs_receber)

        # Filtro de Origem (Contrato vs Venda)
        q_origem = Q()
        if origem_receita:
            from ..models.access import ContratosLocacao
            from datetime import date as dt_date
            hoje = dt_date.today()
            
            clientes_com_contrato = ContratosLocacao.objects.filter(
                fim__gte=hoje
            ).values_list('cliente_id', flat=True).distinct()
            
            if 'CONTRATO' in origem_receita:
                q_origem |= Q(cliente_id__in=clientes_com_contrato)
            if 'VENDA' in origem_receita:
                q_origem |= Q(~Q(cliente_id__in=clientes_com_contrato))
        
        if not data_inicio or not data_fim:
            return Response({'error': 'Parâmetros data inválidos'}, status=400)

        # Determina o escopo da listagem (antes, periodo, depois)
        # Default: 'periodo'
        scope = request.query_params.get('scope', 'periodo')

        # --- CÁLCULO DOS TOTAIS E CONTAGENS PARA TODOS OS ESCOPOS ---
        
        # 1. ANTES DO PERÍODO (< data_inicio)
        filters_cp_antes = {'vencimento__date__lt': data_inicio, 'status': 'A'}
        agg_cp_antes = ContasPagar.objects.filter(q_cat_pagar, **filters_cp_antes).aggregate(
            total=Coalesce(Sum('valor'), Value(0, output_field=DecimalField())),
            count=Count('id')
        )
        total_saidas_antes = agg_cp_antes['total']
        count_antes_cp = agg_cp_antes['count']

        filters_cr_antes = {'vencimento__date__lt': data_inicio, 'status': 'A'}
        qs_receber_antes = ContasReceber.objects.filter(q_cat_receber, **filters_cr_antes)
        if origem_receita: qs_receber_antes = qs_receber_antes.filter(q_origem)
        agg_cr_antes = qs_receber_antes.aggregate(
            total=Coalesce(Sum('valor'), Value(0, output_field=DecimalField())),
            count=Count('id')
        )
        total_entradas_antes = agg_cr_antes['total']
        count_antes_cr = agg_cr_antes['count']
        count_antes = count_antes_cp + count_antes_cr

        # 2. NO PERÍODO (>= data_inicio e <= data_fim)
        filters_cp_periodo = {'vencimento__date__gte': data_inicio, 'vencimento__date__lte': data_fim, 'status': 'A'}
        agg_cp_periodo = ContasPagar.objects.filter(q_cat_pagar, **filters_cp_periodo).aggregate(
            total=Coalesce(Sum('valor'), Value(0, output_field=DecimalField())),
            count=Count('id')
        )
        total_saidas_periodo = agg_cp_periodo['total']
        count_periodo_cp = agg_cp_periodo['count']

        filters_cr_periodo = {'vencimento__date__gte': data_inicio, 'vencimento__date__lte': data_fim, 'status': 'A'}
        qs_receber_periodo = ContasReceber.objects.filter(q_cat_receber, **filters_cr_periodo)
        if origem_receita: qs_receber_periodo = qs_receber_periodo.filter(q_origem)
        agg_cr_periodo = qs_receber_periodo.aggregate(
            total=Coalesce(Sum('valor'), Value(0, output_field=DecimalField())),
            count=Count('id')
        )
        total_entradas_periodo = agg_cr_periodo['total']
        count_periodo_cr = agg_cr_periodo['count']
        count_periodo = count_periodo_cp + count_periodo_cr

        # 3. DEPOIS DO PERÍODO (> data_fim)
        filters_cp_depois = {'vencimento__date__gt': data_fim, 'status': 'A'}
        agg_cp_depois = ContasPagar.objects.filter(q_cat_pagar, **filters_cp_depois).aggregate(
            total=Coalesce(Sum('valor'), Value(0, output_field=DecimalField())),
            count=Count('id')
        )
        total_saidas_depois = agg_cp_depois['total']
        count_depois_cp = agg_cp_depois['count']

        filters_cr_depois = {'vencimento__date__gt': data_fim, 'status': 'A'}
        qs_receber_depois = ContasReceber.objects.filter(q_cat_receber, **filters_cr_depois)
        if origem_receita: qs_receber_depois = qs_receber_depois.filter(q_origem)
        agg_cr_depois = qs_receber_depois.aggregate(
            total=Coalesce(Sum('valor'), Value(0, output_field=DecimalField())),
            count=Count('id')
        )
        total_entradas_depois = agg_cr_depois['total']
        count_depois_cr = agg_cr_depois['count']
        count_depois = count_depois_cp + count_depois_cr

        # --- SELEÇÃO DE MOVIMENTAÇÕES PARA EXIBIÇÃO ---
        # Baseado no 'scope', definimos quais QuerySets buscar para listar na tabela
        
        # Filtros de Listagem (Pagar)
        filters_cp_list = {'status': 'A'}
        
        # Filtros de Listagem (Receber)
        filters_cr_list = {'status': 'A'}

        if scope == 'antes':
            filters_cp_list['vencimento__date__lt'] = data_inicio
            filters_cr_list['vencimento__date__lt'] = data_inicio
        elif scope == 'depois':
            filters_cp_list['vencimento__date__gt'] = data_fim
            filters_cr_list['vencimento__date__gt'] = data_fim
        else: # periodo (default)
            filters_cp_list['vencimento__date__gte'] = data_inicio
            filters_cp_list['vencimento__date__lte'] = data_fim
            filters_cr_list['vencimento__date__gte'] = data_inicio
            filters_cr_list['vencimento__date__lte'] = data_fim

        # Buscando listas efetivas para paginação
        contas_pagar = ContasPagar.objects.filter(q_cat_pagar, **filters_cp_list).select_related('fornecedor').values(
            'id', 'vencimento', 'valor',
            'fornecedor__nome', 'historico', 'fornecedor__especificacao'
        )

        qs_receber_list = ContasReceber.objects.filter(q_cat_receber, **filters_cr_list)
        if origem_receita: qs_receber_list = qs_receber_list.filter(q_origem)
        
        contas_receber = qs_receber_list.select_related('cliente').values(
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

        # Totais finais da lista visualizada (pode ser redundante com totais acima, mas ok)
        total_list_count = len(movimentacoes)

        # Paginação
        page = int(request.query_params.get('page', 1))
        page_size = int(request.query_params.get('page_size', 50))
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        paginated = movimentacoes[start_idx:end_idx]
        total_pages = (total_list_count + page_size - 1) // page_size if page_size > 0 else 1

        return Response({
            'periodo': {'data_inicio': str(data_inicio), 'data_fim': str(data_fim)},
            'resumo': {
                # Totais do Período (Selecionado)
                'total_entradas_previstas': total_entradas_periodo,
                'total_saidas_previstas': total_saidas_periodo,
                'saldo_previsto': total_entradas_periodo - total_saidas_periodo,
                'count_periodo': count_periodo,
                
                # Totais Antes
                'total_entradas_antes': total_entradas_antes,
                'total_saidas_antes': total_saidas_antes,
                'count_antes': count_antes,
                
                # Totais Depois
                'total_entradas_depois': total_entradas_depois,
                'total_saidas_depois': total_saidas_depois,
                'count_depois': count_depois,
                
                # contagem total da lista retornada
                'total_movimentacoes': total_list_count 
            },
            'paginacao': {
                'page': page,
                'page_size': page_size,
                'total_pages': total_pages,
                'total_count': total_list_count
            },
            'movimentacoes': paginated
        })

    @action(detail=False, methods=['get'])
    def resumo_mensal(self, request):
        """
        Retorna resumo mensal baseado na metodologia do DRE (Competência para Receitas, Caixa para Despesas + CMV).
        Reutiliza a lógica do DREView para garantir consistência.
        """
        data_inicio = self.parse_date(request.query_params.get('data_inicio'))
        data_fim = self.parse_date(request.query_params.get('data_fim'))
        
        if not data_inicio or not data_fim:
            return Response({'error': 'Parâmetros data inválidos'}, status=400)

        # Ajustar para o primeiro dia do mês inicial
        current_date = data_inicio.replace(day=1)
        
        meses_list = []

        while current_date <= data_fim:
            # Definir intervalo do mês corrente
            # Próximo mês
            next_month = (current_date.replace(day=28) + timedelta(days=4)).replace(day=1)
            month_end = next_month - timedelta(days=1)
            
            # Instanciar DREView e configurar para sem impostos (comparação direta)
            dre_view = DREView()
            dre_view.PERCENTUAL_IMPOSTOS = Decimal(0)
            
            # Calcular DRE para este mês
            dre_data = dre_view._calcular_dre(current_date, month_end)
            
            # Mapear dados para o formato ResumoMensal
            # Receitas (Competência)
            entradas_contrato = Decimal(str(dre_data.get('faturamento_servicos_contratos', 0)))
            # Vendas = Vendas Mercadorias + Serviços Avulsos
            entradas_vendas = Decimal(str(dre_data.get('faturamento_vendas', 0))) + Decimal(str(dre_data.get('faturamento_servicos_avulsos', 0)))
            total_entradas = Decimal(str(dre_data.get('faturamento_bruto', 0)))
            
            # Despesas (Caixa + CMV)
            # DREView já calcula custos fixos e variáveis baseados em ContasPagar (Caixa)
            # --- Filtragem de Categorias (Backend-side) ---
            # Obter listas de exclusão da query string
            exclude_fixed = request.query_params.get('exclude_fixed', '').split(',')
            exclude_variable = request.query_params.get('exclude_variable', '').split(',')
            exclude_fixed = [c.strip() for c in exclude_fixed if c.strip()]
            exclude_variable = [c.strip() for c in exclude_variable if c.strip()]
            
            # Recalcular Custos Fixos
            base_fixos = Decimal(str(dre_data.get('custos_fixos', 0)))
            detalhe_fixos = dre_data.get('detalhe_custos_fixos', [])
            
            valor_excluido_fixo = Decimal(0)
            for item in detalhe_fixos:
                if item['categoria'] in exclude_fixed:
                    valor_excluido_fixo += Decimal(str(item.get('valor', 0)))
            
            saidas_fixas = base_fixos - valor_excluido_fixo
            if saidas_fixas < 0: saidas_fixas = Decimal(0)

            # Recalcular Custos Variáveis (Operacionais)
            base_variaveis = Decimal(str(dre_data.get('custos_variaveis', 0)))
            detalhe_variaveis = dre_data.get('detalhe_custos_variaveis', [])
            
            valor_excluido_variavel = Decimal(0)
            for item in detalhe_variaveis:
                if item['categoria'] in exclude_variable:
                    valor_excluido_variavel += Decimal(str(item.get('valor', 0)))
            
            custos_variaveis_operacionais = base_variaveis - valor_excluido_variavel
            if custos_variaveis_operacionais < 0: custos_variaveis_operacionais = Decimal(0)
            
            # CMV e Totais
            cmv = Decimal(str(dre_data.get('cmv', 0)))
            saidas_variaveis = custos_variaveis_operacionais + cmv
            total_saidas = saidas_fixas + saidas_variaveis
            
            # Resultado (Recalculado após filtros)
            saldo = Decimal(str(total_entradas)) - cmv - saidas_fixas - custos_variaveis_operacionais

            # Detalhamento de categorias para o frontend
            detalhe_fixos_v3 = {item['categoria']: float(item.get('valor', 0)) for item in detalhe_fixos if item['categoria'] not in exclude_fixed}
            detalhe_variaveis_v3 = {item['categoria']: float(item.get('valor', 0)) for item in detalhe_variaveis if item['categoria'] not in exclude_variable}

            meses_list.append({
                'mes': current_date.isoformat(), 
                'entradas_contrato': float(entradas_contrato),
                'entradas_vendas': float(entradas_vendas),
                'total_entradas': float(total_entradas),
                'saidas_fixas': float(saidas_fixas),
                'saidas_variaveis': float(saidas_variaveis),
                'cmv': float(cmv),
                'custos_variaveis': float(custos_variaveis_operacionais),
                'total_saidas': float(total_saidas),
                'saldo': float(saldo),
                'detalhe_fixos': detalhe_fixos_v3,
                'detalhe_variaveis': detalhe_variaveis_v3
            })

            
            current_date = next_month

        # Calcular totais
        totais = {
            'entradas_contrato': sum(m['entradas_contrato'] for m in meses_list),
            'entradas_vendas': sum(m['entradas_vendas'] for m in meses_list),
            'total_entradas': sum(m['total_entradas'] for m in meses_list),
            'saidas_fixas': sum(m['saidas_fixas'] for m in meses_list),
            'saidas_variaveis': sum(m['saidas_variaveis'] for m in meses_list),
            'cmv': sum(m['cmv'] for m in meses_list),
            'custos_variaveis': sum(m['custos_variaveis'] for m in meses_list),
            'total_saidas': sum(m['total_saidas'] for m in meses_list),
            'saldo_liquido': sum(m['saldo'] for m in meses_list)
        }

        # Coletar todas as categorias únicas que apareceram no período
        all_fixed_cats = sorted(list(set(cat for m in meses_list for cat in m['detalhe_fixos'].keys())))
        all_variable_cats = sorted(list(set(cat for m in meses_list for cat in m['detalhe_variaveis'].keys())))

        return Response({
            'totais': totais,
            'meses': meses_list,
            'categorias_fixas': all_fixed_cats,
            'categorias_variaveis': all_variable_cats
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
        pagar_diario = ContasPagar.objects.annotate(
            data_efetiva=Coalesce('data_pagamento', 'vencimento', output_field=DateTimeField())
        ).filter(
            data_efetiva__date__gte=data_inicio,
            data_efetiva__date__lte=data_fim,
            status='P'
        ).annotate(
            dia=TruncDay('data_efetiva'),
            valor_final=Case(
                When(valor_total_pago__gt=0, then=F('valor_total_pago')),
                default=F('valor'),
                output_field=DecimalField()
            )
        ).values('dia').annotate(
            total=Sum('valor_final'),
            quantidade=Count('id')
        )

        for item in pagar_diario:
            dia = item['dia']
            if dia not in dias_dict:
                dias_dict[dia] = {'data': dia, 'entradas': 0, 'saidas': 0, 'saldo': 0, 'qtd_entradas': 0, 'qtd_saidas': 0}
            dias_dict[dia]['saidas'] += float(item['total'] or 0)
            dias_dict[dia]['qtd_saidas'] += item['quantidade']

        # Contas a Receber (Entradas)
        receber_diario = ContasReceber.objects.annotate(
            data_efetiva=Coalesce('data_pagamento', 'vencimento', output_field=DateTimeField())
        ).filter(
            data_efetiva__date__gte=data_inicio,
            data_efetiva__date__lte=data_fim,
            status='P'
        ).annotate(
            dia=TruncDay('data_efetiva'),
            valor_final=Case(
                When(valor_total_pago__gt=0, then=F('valor_total_pago')),
                default=F('valor'),
                output_field=DecimalField()
            )
        ).values('dia').annotate(
            total=Sum('valor_final'),
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
