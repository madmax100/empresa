# contas/views/relatorios_views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Sum, Count, Q
from datetime import datetime

from ..models.access import Fornecedores, ContasPagar, NotasFiscaisEntrada, NotasFiscaisSaida, NotasFiscaisServico, ItensNfSaida, MovimentacoesEstoque, SaldosEstoque

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


class RelatorioCustosVariaveisView(APIView):
    """
    Endpoint para relatórios de contas pagas de fornecedores 
    com tipos relacionados a DESPESAS VARIÁVEIS ou CUSTOS VARIÁVEIS em um período.
    
    Agrupa os valores pelo campo 'especificacao' da tabela de fornecedores.
    
    Utiliza a tabela ContasPagar filtrada por:
    - Status: 'P' (Pago)
    - Fornecedores com tipo contendo 'VARIAVEL', 'DESPESA VARIAVEL' ou 'CUSTO VARIAVEL'
    - Período de pagamento especificado
    """
    
    def safe_aggregate_value(self, value):
        """Helper para tratar valores None em agregações"""
        if value is None:
            return 0.0
        return float(value)
    
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
            
        # 2. Identificar fornecedores com tipos relacionados a custos variáveis
        fornecedores_variaveis = Fornecedores.objects.filter(
            Q(tipo__icontains='VARIAVEL') |
            Q(tipo__icontains='DESPESA VARIAVEL') |
            Q(tipo__icontains='CUSTO VARIAVEL')
        ).values_list('id', flat=True)
        
        if not fornecedores_variaveis.exists():
            return Response({
                'parametros': {
                    'data_inicio': data_inicio,
                    'data_fim': data_fim,
                    'filtro_aplicado': 'Fornecedores com tipo relacionado a CUSTOS VARIÁVEIS',
                    'fonte_dados': 'Contas a Pagar (status: Pago)',
                },
                'message': 'Nenhum fornecedor encontrado com tipo relacionado a custos variáveis.',
                'totais_gerais': {
                    'total_valor_original': 0.0,
                    'total_valor_pago': 0.0,
                    'total_juros': 0.0,
                    'total_tarifas': 0.0,
                },
                'resumo_por_especificacao': [],
                'total_contas_pagas': 0,
                'contas_pagas': []
            })
        
        # 3. Consultar contas pagas no período para fornecedores variáveis
        queryset = ContasPagar.objects.filter(
            status='P',  # Apenas contas pagas
            fornecedor_id__in=fornecedores_variaveis,
            data_pagamento__date__gte=data_inicio,
            data_pagamento__date__lte=data_fim
        ).select_related('fornecedor')
        
        # 4. Calcular totais gerais
        totais_gerais = queryset.aggregate(
            soma_valor_original=Sum('valor'),
            soma_total_pago=Sum('valor_total_pago'),
            soma_juros=Sum('juros'),
            soma_tarifas=Sum('tarifas')
        )
        
        # 5. Agrupar por especificação do fornecedor
        resumo_por_especificacao = {}
        for conta in queryset:
            especificacao = conta.fornecedor.especificacao if conta.fornecedor and conta.fornecedor.especificacao else 'Sem Especificação'
            
            if especificacao not in resumo_por_especificacao:
                resumo_por_especificacao[especificacao] = {
                    'especificacao': especificacao,
                    'valor_original_total': 0.0,
                    'valor_pago_total': 0.0,
                    'juros_total': 0.0,
                    'tarifas_total': 0.0,
                    'quantidade_contas': 0,
                    'fornecedores': set()
                }
            
            # Somar valores
            resumo_por_especificacao[especificacao]['valor_original_total'] += float(conta.valor or 0)
            resumo_por_especificacao[especificacao]['valor_pago_total'] += float(conta.valor_total_pago or 0)
            resumo_por_especificacao[especificacao]['juros_total'] += float(conta.juros or 0)
            resumo_por_especificacao[especificacao]['tarifas_total'] += float(conta.tarifas or 0)
            resumo_por_especificacao[especificacao]['quantidade_contas'] += 1
            
            if conta.fornecedor:
                resumo_por_especificacao[especificacao]['fornecedores'].add(conta.fornecedor.nome)
        
        # Converter sets para listas no resumo
        resumo_por_especificacao_limpo = []
        for especificacao_data in resumo_por_especificacao.values():
            especificacao_data['fornecedores'] = list(especificacao_data['fornecedores'])
            especificacao_data['quantidade_fornecedores'] = len(especificacao_data['fornecedores'])
            resumo_por_especificacao_limpo.append(especificacao_data)
        
        # Ordenar por valor pago (maior para menor)
        resumo_por_especificacao_limpo.sort(key=lambda x: x['valor_pago_total'], reverse=True)
        
        # 6. Detalhes das contas pagas
        pagamentos_detalhados = []
        for conta in queryset.order_by('-data_pagamento'):
            pagamentos_detalhados.append({
                'id': conta.id,
                'data_pagamento': conta.data_pagamento,
                'fornecedor_nome': conta.fornecedor.nome if conta.fornecedor else 'N/A',
                'fornecedor_tipo': conta.fornecedor.tipo if conta.fornecedor else 'N/A',
                'fornecedor_especificacao': conta.fornecedor.especificacao if conta.fornecedor and conta.fornecedor.especificacao else 'Sem Especificação',
                'valor_original': float(conta.valor or 0),
                'valor_pago': float(conta.valor_total_pago or 0),
                'juros': float(conta.juros or 0),
                'tarifas': float(conta.tarifas or 0),
                'historico': conta.historico,
                'forma_pagamento': conta.forma_pagamento,
            })
        
        # Estatísticas dos fornecedores
        total_fornecedores_variaveis = fornecedores_variaveis.count()
        fornecedores_com_pagamentos = queryset.values('fornecedor_id').distinct().count()
        
        return Response({
            'parametros': {
                'data_inicio': data_inicio,
                'data_fim': data_fim,
                'filtro_aplicado': 'Fornecedores com tipo relacionado a CUSTOS VARIÁVEIS',
                'fonte_dados': 'Contas a Pagar (status: Pago)',
            },
            'estatisticas_fornecedores': {
                'total_fornecedores_variaveis_cadastrados': total_fornecedores_variaveis,
                'fornecedores_com_pagamentos_no_periodo': fornecedores_com_pagamentos,
            },
            'totais_gerais': {
                'total_valor_original': self.safe_aggregate_value(totais_gerais['soma_valor_original']),
                'total_valor_pago': self.safe_aggregate_value(totais_gerais['soma_total_pago']),
                'total_juros': self.safe_aggregate_value(totais_gerais['soma_juros']),
                'total_tarifas': self.safe_aggregate_value(totais_gerais['soma_tarifas']),
            },
            'resumo_por_especificacao': resumo_por_especificacao_limpo,
            'total_contas_pagas': queryset.count(),
            'contas_pagas': pagamentos_detalhados
        })


class RelatorioFaturamentoView(APIView):
    """
    Endpoint para relatórios de faturamento baseado em notas fiscais em um período.
    
    Inclui:
    - Notas Fiscais de Entrada com operação relacionada a COMPRA
    - Notas Fiscais de Saída com operação relacionada a VENDA
    - Notas Fiscais de Serviço (todas, pois são prestação de serviços)
    
    Filtros aplicados:
    - NF Entrada: operação contendo 'COMPRA'
    - NF Saída: operação contendo 'VENDA'
    - NF Serviço: todas as notas de serviço
    - Período: data de emissão/data entre data_inicio e data_fim
    """
    
    def safe_aggregate_value(self, value):
        """Helper para tratar valores None em agregações"""
        if value is None:
            return 0.0
        return float(value)
    
    def _obter_ultimo_preco_entrada(self, produto_id, data_limite):
        """
        Busca o último preço de entrada do produto, mesmo anterior ao período
        """
        tipos_entrada = [1, 3]  # Entrada e Estoque Inicial
        
        # Busca última entrada com valor > 0 até a data limite
        ultima_entrada = MovimentacoesEstoque.objects.filter(
            produto_id=produto_id,
            tipo_movimentacao__id__in=tipos_entrada,
            quantidade__gt=0,
            custo_unitario__gt=0,
            data_movimentacao__date__lte=data_limite
        ).order_by('-data_movimentacao', '-id').first()
        
        if ultima_entrada:
            return {
                'preco': float(ultima_entrada.custo_unitario),
                'data': ultima_entrada.data_movimentacao.strftime('%Y-%m-%d %H:%M:%S'),
                'documento': ultima_entrada.documento_referencia or '',
                'encontrado': True
            }
        
        # Se não encontrou, tenta buscar no SaldosEstoque
        saldo = SaldosEstoque.objects.filter(produto_id=produto_id, custo_medio__gt=0).first()
        if saldo and saldo.custo_medio:
            return {
                'preco': float(saldo.custo_medio),
                'data': None,
                'documento': 'Custo médio atual',
                'encontrado': True
            }
        
        return {
            'preco': 0.0,
            'data': None,
            'documento': '',
            'encontrado': False
        }
    
    def _calcular_valores_preco_entrada(self, nf_saida_queryset, data_fim):
        """
        Calcula valores das vendas usando preços de entrada dos produtos
        """
        valor_total_preco_entrada = 0.0
        quantidade_itens_calculados = 0
        produtos_sem_preco_entrada = 0
        
        # Busca todos os itens das notas fiscais de saída no período
        itens_vendas = ItensNfSaida.objects.filter(
            nota_fiscal__in=nf_saida_queryset
        ).select_related('produto')
        
        for item in itens_vendas:
            if item.produto and item.quantidade:
                # Busca último preço de entrada do produto
                preco_info = self._obter_ultimo_preco_entrada(item.produto.id, data_fim)
                
                if preco_info['encontrado']:
                    valor_item_preco_entrada = float(item.quantidade) * preco_info['preco']
                    valor_total_preco_entrada += valor_item_preco_entrada
                    quantidade_itens_calculados += 1
                else:
                    produtos_sem_preco_entrada += 1
        
        return {
            'valor_total_preco_entrada': valor_total_preco_entrada,
            'quantidade_itens_calculados': quantidade_itens_calculados,
            'produtos_sem_preco_entrada': produtos_sem_preco_entrada
        }
    
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
        
        # 2. Consultar Notas Fiscais de Entrada (Compras)
        nf_entrada = NotasFiscaisEntrada.objects.filter(
            Q(operacao__icontains='COMPRA'),
            data_emissao__date__gte=data_inicio,
            data_emissao__date__lte=data_fim
        ).select_related('fornecedor')
        
        # 3. Consultar Notas Fiscais de Saída (Vendas)
        nf_saida = NotasFiscaisSaida.objects.filter(
            Q(operacao__icontains='VENDA'),
            data__date__gte=data_inicio,
            data__date__lte=data_fim
        ).select_related('cliente')
        
        # 4. Consultar Notas Fiscais de Serviço
        nf_servico = NotasFiscaisServico.objects.filter(
            data__date__gte=data_inicio,
            data__date__lte=data_fim
        ).select_related('cliente')
        
        # 5. Calcular totais por tipo de nota
        totais_entrada = nf_entrada.aggregate(
            soma_valor_produtos=Sum('valor_produtos'),
            soma_valor_total=Sum('valor_total'),
            soma_valor_icms=Sum('valor_icms'),
            soma_valor_ipi=Sum('valor_ipi'),
            quantidade_notas=Count('id')
        )
        
        totais_saida = nf_saida.aggregate(
            soma_valor_produtos=Sum('valor_produtos'),
            soma_valor_total=Sum('valor_total_nota'),
            soma_valor_icms=Sum('valor_icms'),
            soma_desconto=Sum('desconto'),
            quantidade_notas=Count('id')
        )
        
        totais_servico = nf_servico.aggregate(
            soma_valor_produtos=Sum('valor_produtos'),
            soma_valor_total=Sum('valor_total'),
            soma_valor_iss=Sum('iss'),
            quantidade_notas=Count('id')
        )
        
        # 5.1. Calcular valores das vendas usando preços de entrada
        calculos_preco_entrada = self._calcular_valores_preco_entrada(nf_saida, data_fim)
        
        # 6. Resumo por tipo de operação
        resumo_por_tipo = [
            {
                'tipo': 'Compras (NF Entrada)',
                'quantidade_notas': totais_entrada['quantidade_notas'] or 0,
                'valor_produtos': self.safe_aggregate_value(totais_entrada['soma_valor_produtos']),
                'valor_total': self.safe_aggregate_value(totais_entrada['soma_valor_total']),
                'impostos': self.safe_aggregate_value(totais_entrada['soma_valor_icms']) + self.safe_aggregate_value(totais_entrada['soma_valor_ipi']),
                'detalhes': {
                    'valor_icms': self.safe_aggregate_value(totais_entrada['soma_valor_icms']),
                    'valor_ipi': self.safe_aggregate_value(totais_entrada['soma_valor_ipi'])
                }
            },
            {
                'tipo': 'Vendas (NF Saída)',
                'quantidade_notas': totais_saida['quantidade_notas'] or 0,
                'valor_produtos': self.safe_aggregate_value(totais_saida['soma_valor_produtos']),
                'valor_total': self.safe_aggregate_value(totais_saida['soma_valor_total']),
                'impostos': self.safe_aggregate_value(totais_saida['soma_valor_icms']),
                'valor_preco_entrada': calculos_preco_entrada['valor_total_preco_entrada'],
                'margem_bruta': self.safe_aggregate_value(totais_saida['soma_valor_total']) - calculos_preco_entrada['valor_total_preco_entrada'],
                'detalhes': {
                    'valor_icms': self.safe_aggregate_value(totais_saida['soma_valor_icms']),
                    'valor_desconto': self.safe_aggregate_value(totais_saida['soma_desconto']),
                    'itens_calculados': calculos_preco_entrada['quantidade_itens_calculados'],
                    'produtos_sem_preco_entrada': calculos_preco_entrada['produtos_sem_preco_entrada']
                }
            },
            {
                'tipo': 'Serviços (NF Serviço)',
                'quantidade_notas': totais_servico['quantidade_notas'] or 0,
                'valor_produtos': self.safe_aggregate_value(totais_servico['soma_valor_produtos']),
                'valor_total': self.safe_aggregate_value(totais_servico['soma_valor_total']),
                'impostos': self.safe_aggregate_value(totais_servico['soma_valor_iss']),
                'detalhes': {
                    'valor_iss': self.safe_aggregate_value(totais_servico['soma_valor_iss'])
                }
            }
        ]
        
        # 7. Totais gerais do faturamento
        total_quantidade_notas = (
            (totais_entrada['quantidade_notas'] or 0) +
            (totais_saida['quantidade_notas'] or 0) +
            (totais_servico['quantidade_notas'] or 0)
        )
        
        total_valor_produtos = (
            self.safe_aggregate_value(totais_entrada['soma_valor_produtos']) +
            self.safe_aggregate_value(totais_saida['soma_valor_produtos']) +
            self.safe_aggregate_value(totais_servico['soma_valor_produtos'])
        )
        
        total_valor_geral = (
            self.safe_aggregate_value(totais_entrada['soma_valor_total']) +
            self.safe_aggregate_value(totais_saida['soma_valor_total']) +
            self.safe_aggregate_value(totais_servico['soma_valor_total'])
        )
        
        total_impostos = (
            self.safe_aggregate_value(totais_entrada['soma_valor_icms']) +
            self.safe_aggregate_value(totais_entrada['soma_valor_ipi']) +
            self.safe_aggregate_value(totais_saida['soma_valor_icms']) +
            self.safe_aggregate_value(totais_servico['soma_valor_iss'])
        )
        
        # 8. Top fornecedores (compras)
        top_fornecedores = []
        if nf_entrada.exists():
            fornecedores_resumo = nf_entrada.values('fornecedor__nome').annotate(
                valor_total=Sum('valor_total'),
                quantidade_notas=Count('id')
            ).order_by('-valor_total')[:10]
            
            for fornecedor in fornecedores_resumo:
                top_fornecedores.append({
                    'fornecedor': fornecedor['fornecedor__nome'] or 'Sem Fornecedor',
                    'valor_total': float(fornecedor['valor_total'] or 0),
                    'quantidade_notas': fornecedor['quantidade_notas']
                })
        
        # 9. Top clientes (vendas + serviços)
        top_clientes = []
        
        # Vendas
        if nf_saida.exists():
            clientes_vendas = nf_saida.values('cliente__nome').annotate(
                valor_total=Sum('valor_total_nota'),
                quantidade_notas=Count('id')
            )
        else:
            clientes_vendas = []
        
        # Serviços
        if nf_servico.exists():
            clientes_servicos = nf_servico.values('cliente__nome').annotate(
                valor_total=Sum('valor_total'),
                quantidade_notas=Count('id')
            )
        else:
            clientes_servicos = []
        
        # Combinar vendas e serviços por cliente
        clientes_combinados = {}
        
        for venda in clientes_vendas:
            nome = venda['cliente__nome'] or 'Sem Cliente'
            clientes_combinados[nome] = {
                'cliente': nome,
                'valor_total': float(venda['valor_total'] or 0),
                'quantidade_notas': venda['quantidade_notas'],
                'tipo': 'vendas'
            }
        
        for servico in clientes_servicos:
            nome = servico['cliente__nome'] or 'Sem Cliente'
            if nome in clientes_combinados:
                clientes_combinados[nome]['valor_total'] += float(servico['valor_total'] or 0)
                clientes_combinados[nome]['quantidade_notas'] += servico['quantidade_notas']
                clientes_combinados[nome]['tipo'] = 'vendas+serviços'
            else:
                clientes_combinados[nome] = {
                    'cliente': nome,
                    'valor_total': float(servico['valor_total'] or 0),
                    'quantidade_notas': servico['quantidade_notas'],
                    'tipo': 'serviços'
                }
        
        # Ordenar clientes por valor total
        top_clientes = sorted(clientes_combinados.values(), key=lambda x: x['valor_total'], reverse=True)[:10]
        
        # 10. Detalhes das notas (primeiras 50 de cada tipo)
        notas_detalhadas = {
            'compras': [],
            'vendas': [],
            'servicos': []
        }
        
        # Compras
        for nf in nf_entrada.order_by('-data_emissao')[:50]:
            notas_detalhadas['compras'].append({
                'id': nf.id,
                'numero_nota': nf.numero_nota,
                'data_emissao': nf.data_emissao,
                'fornecedor': nf.fornecedor.nome if nf.fornecedor else 'N/A',
                'operacao': nf.operacao,
                'valor_produtos': float(nf.valor_produtos or 0),
                'valor_total': float(nf.valor_total or 0),
                'valor_icms': float(nf.valor_icms or 0),
                'valor_ipi': float(nf.valor_ipi or 0)
            })
        
        # Vendas
        for nf in nf_saida.order_by('-data')[:50]:
            notas_detalhadas['vendas'].append({
                'id': nf.id,
                'numero_nota': nf.numero_nota,
                'data': nf.data,
                'cliente': nf.cliente.nome if nf.cliente else 'N/A',
                'operacao': nf.operacao,
                'valor_produtos': float(nf.valor_produtos or 0),
                'valor_total': float(nf.valor_total_nota or 0),
                'valor_icms': float(nf.valor_icms or 0),
                'desconto': float(nf.desconto or 0)
            })
        
        # Serviços
        for nf in nf_servico.order_by('-data')[:50]:
            notas_detalhadas['servicos'].append({
                'id': nf.id,
                'numero_nota': nf.numero_nota,
                'data': nf.data,
                'cliente': nf.cliente.nome if nf.cliente else 'N/A',
                'operacao': nf.operacao,
                'valor_produtos': float(nf.valor_produtos or 0),
                'valor_total': float(nf.valor_produtos or 0),  # NotasFiscaisServico usa valor_produtos como total
                'valor_iss': float(nf.iss or 0)
            })
        
        return Response({
            'parametros': {
                'data_inicio': data_inicio,
                'data_fim': data_fim,
                'filtros_aplicados': {
                    'nf_entrada': 'Operação contendo COMPRA',
                    'nf_saida': 'Operação contendo VENDA',
                    'nf_servico': 'Todas as notas de serviço'
                },
                'fonte_dados': 'Notas Fiscais (Entrada, Saída e Serviço)'
            },
            'totais_gerais': {
                'total_quantidade_notas': total_quantidade_notas,
                'total_valor_produtos': total_valor_produtos,
                'total_valor_geral': total_valor_geral,
                'total_impostos': total_impostos,
                'analise_vendas': {
                    'valor_vendas': self.safe_aggregate_value(totais_saida['soma_valor_total']),
                    'valor_preco_entrada': calculos_preco_entrada['valor_total_preco_entrada'],
                    'margem_bruta': self.safe_aggregate_value(totais_saida['soma_valor_total']) - calculos_preco_entrada['valor_total_preco_entrada'],
                    'percentual_margem': round(
                        ((self.safe_aggregate_value(totais_saida['soma_valor_total']) - calculos_preco_entrada['valor_total_preco_entrada']) / 
                         self.safe_aggregate_value(totais_saida['soma_valor_total']) * 100) if self.safe_aggregate_value(totais_saida['soma_valor_total']) > 0 else 0, 2
                    ),
                    'itens_analisados': calculos_preco_entrada['quantidade_itens_calculados'],
                    'produtos_sem_preco_entrada': calculos_preco_entrada['produtos_sem_preco_entrada']
                }
            },
            'resumo_por_tipo': resumo_por_tipo,
            'top_fornecedores': top_fornecedores,
            'top_clientes': top_clientes,
            'notas_detalhadas': notas_detalhadas
        })
