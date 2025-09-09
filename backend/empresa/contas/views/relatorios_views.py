# contas/views/relatorios_views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Sum, Count, Q
from datetime import datetime

from ..models.access import Fornecedores, ContasPagar

class RelatorioCustosFixosView(APIView):
    """
    Endpoint para relatórios de contas pagas de fornecedores 
    com tipos DESPESA FIXA ou CUSTO FIXO em um período.
    
    Utiliza a tabela ContasPagar filtrada por:
    - Status: 'P' (Pago)
    - Fornecedores com tipo 'DESPESA FIXA' ou 'CUSTO FIXO'
    - Período de pagamento especificado
    """
    
    def get(self, request, *args, **kwargs):
        # 1. Validação de Parâmetros
        data_inicio_str = request.query_params.get('data_inicio')
        data_fim_str = request.query_params.get('data_fim')
        
        if not data_inicio_str or not data_fim_str:
            return Response(
                {'error': 'Parâmetros data_inicio e data_fim são obrigatórios.'},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        try:
            data_inicio = datetime.strptime(data_inicio_str, '%Y-%m-%d').date()
            data_fim = datetime.strptime(data_fim_str, '%Y-%m-%d').date()
        except ValueError:
            return Response(
                {'error': 'Formato de data inválido. Use YYYY-MM-DD.'},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        if data_inicio > data_fim:
            return Response(
                {'error': 'A data de início não pode ser maior que a data de fim.'},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        # Parâmetro opcional para categorias
        categorias_param = request.query_params.get('categorias')
        if categorias_param:
            categorias_filtro = [cat.strip() for cat in categorias_param.split(',')]
        else:
            # Categorias padrão para custos e despesas fixas
            categorias_filtro = ['despesas_operacionais', 'despesas_administrativas', 'impostos', 'aluguel']

        # 2. Lógica de Negócio - Filtrar por fornecedores com tipos fixos
        
        # Primeiro, obter fornecedores com tipos "DESPESA FIXA" ou "CUSTO FIXO"
        fornecedores_fixos = Fornecedores.objects.filter(
            Q(tipo__icontains='DESPESA FIXA') | Q(tipo__icontains='CUSTO FIXO')
        ).values_list('id', flat=True)
        
        # Filtrar contas pagas por esses fornecedores no período
        queryset = ContasPagar.objects.filter(
            status='P',  # Apenas contas pagas
            data_pagamento__date__range=(data_inicio, data_fim),
            fornecedor_id__in=fornecedores_fixos
        ).select_related('fornecedor', 'conta').order_by('-data_pagamento')
        
        # 3. Estrutura da Resposta
        
        # Detalhes dos pagamentos
        pagamentos_detalhados = []
        for conta in queryset:
            # Função auxiliar para tratar valores numéricos None
            def safe_float(value):
                return float(value) if value is not None else 0.0
            
            pagamentos_detalhados.append({
                'id': conta.id,
                'data_pagamento': conta.data_pagamento.strftime('%Y-%m-%d') if conta.data_pagamento else 'N/A',
                'data_vencimento': conta.vencimento.strftime('%Y-%m-%d') if conta.vencimento else 'N/A',
                'valor_original': safe_float(conta.valor),
                'valor_pago': safe_float(conta.valor_pago),
                'juros': safe_float(conta.juros),
                'tarifas': safe_float(conta.tarifas),
                'valor_total_pago': safe_float(conta.valor_total_pago),
                'historico': conta.historico or 'N/A',
                'fornecedor': conta.fornecedor.nome if conta.fornecedor else 'N/A',
                'fornecedor_tipo': conta.fornecedor.tipo if conta.fornecedor and conta.fornecedor.tipo else 'N/A',
                'conta_bancaria': str(conta.conta) if conta.conta else 'N/A',
                'forma_pagamento': conta.forma_pagamento or 'N/A',
                'numero_duplicata': conta.numero_duplicata or 'N/A',
            })
            
        # Resumo agregado por tipo de fornecedor
        resumo_por_tipo = queryset.values('fornecedor__tipo').annotate(
            total_pago=Sum('valor_total_pago'),
            quantidade_contas=Count('id'),
            total_valor_original=Sum('valor'),
            total_juros=Sum('juros'),
            total_tarifas=Sum('tarifas')
        ).order_by('-total_pago')
        
        # Função auxiliar para tratar valores None em agregações
        def safe_aggregate_value(value):
            return float(value) if value is not None else 0.0
        
        # Tratar valores None nos resumos
        resumo_por_tipo_limpo = []
        for item in resumo_por_tipo:
            resumo_por_tipo_limpo.append({
                'fornecedor__tipo': item['fornecedor__tipo'] or 'N/A',
                'total_pago': safe_aggregate_value(item['total_pago']),
                'quantidade_contas': item['quantidade_contas'] or 0,
                'total_valor_original': safe_aggregate_value(item['total_valor_original']),
                'total_juros': safe_aggregate_value(item['total_juros']),
                'total_tarifas': safe_aggregate_value(item['total_tarifas'])
            })
        
        # Resumo agregado por fornecedor
        resumo_por_fornecedor = queryset.values('fornecedor__nome', 'fornecedor__tipo').annotate(
            total_pago=Sum('valor_total_pago'),
            quantidade_contas=Count('id'),
            total_valor_original=Sum('valor'),
            total_juros=Sum('juros'),
            total_tarifas=Sum('tarifas')
        ).order_by('-total_pago')
        
        # Tratar valores None no resumo por fornecedor
        resumo_por_fornecedor_limpo = []
        for item in resumo_por_fornecedor:
            resumo_por_fornecedor_limpo.append({
                'fornecedor__nome': item['fornecedor__nome'] or 'N/A',
                'fornecedor__tipo': item['fornecedor__tipo'] or 'N/A',
                'total_pago': safe_aggregate_value(item['total_pago']),
                'quantidade_contas': item['quantidade_contas'] or 0,
                'total_valor_original': safe_aggregate_value(item['total_valor_original']),
                'total_juros': safe_aggregate_value(item['total_juros']),
                'total_tarifas': safe_aggregate_value(item['total_tarifas'])
            })
        
        # Totais gerais
        totais_gerais = queryset.aggregate(
            soma_total_pago=Sum('valor_total_pago'),
            soma_valor_original=Sum('valor'),
            soma_juros=Sum('juros'),
            soma_tarifas=Sum('tarifas')
        )
        
        # Estatísticas dos fornecedores
        total_fornecedores_fixos = len(fornecedores_fixos)
        fornecedores_com_pagamentos = queryset.values('fornecedor_id').distinct().count()
        
        return Response({
            'parametros': {
                'data_inicio': data_inicio,
                'data_fim': data_fim,
                'filtro_aplicado': 'Fornecedores com tipo DESPESA FIXA ou CUSTO FIXO',
                'fonte_dados': 'Contas a Pagar (status: Pago)',
            },
            'estatisticas_fornecedores': {
                'total_fornecedores_fixos_cadastrados': total_fornecedores_fixos,
                'fornecedores_com_pagamentos_no_periodo': fornecedores_com_pagamentos,
            },
            'totais_gerais': {
                'total_valor_original': safe_aggregate_value(totais_gerais['soma_valor_original']),
                'total_valor_pago': safe_aggregate_value(totais_gerais['soma_total_pago']),
                'total_juros': safe_aggregate_value(totais_gerais['soma_juros']),
                'total_tarifas': safe_aggregate_value(totais_gerais['soma_tarifas']),
            },
            'resumo_por_tipo_fornecedor': resumo_por_tipo_limpo,
            'resumo_por_fornecedor': resumo_por_fornecedor_limpo,
            'total_contas_pagas': queryset.count(),
            'contas_pagas': pagamentos_detalhados
        })
