from decimal import Decimal
from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta
from typing import Dict, Any, List, Optional
from django.db.models import (
    Sum, Avg, Count, F, Q, Case, When, DecimalField, FloatField,
    ExpressionWrapper
)
from django.db.models.functions import ExtractMonth, ExtractYear
from rest_framework.decorators import action
from rest_framework.response import Response

class ContratosAnalysisMixin:
    """
    Mixin para análise detalhada de contratos de locação
    """

    @action(detail=False, methods=['GET'])
    def indicadores_contratos(self, request):
        """
        Indicadores gerais dos contratos de locação
        """
        try:
            hoje = date.today()
            
            # Filtra contratos ativos
            contratos = self._get_contratos_ativos(hoje)

            # Análises
            indicadores = self._calcular_indicadores_base(contratos)
            analise_carteira = self._analisar_carteira_contratos(contratos)
            previsoes = self._gerar_previsoes_contratos(contratos)

            # Identifica contratos próximos ao vencimento
            vencimentos = self._analisar_vencimentos(contratos, hoje)

            return Response({
                'data_referencia': hoje,
                'indicadores_base': indicadores,
                'analise_carteira': analise_carteira,
                'previsoes': previsoes,
                'vencimentos': vencimentos,
                'alertas': self._gerar_alertas_contratos(
                    indicadores, analise_carteira, vencimentos
                )
            })

        except Exception as e:
            return Response({'error': str(e)}, status=400)

    def _get_contratos_ativos(self, data_referencia: date):
        """Retorna queryset de contratos ativos"""
        from contas.models import ContratosLocacao
        
        return (
            ContratosLocacao.objects.filter(
                fim__gte=data_referencia
            ).select_related(
                'cliente', 
                'vendedor'
            ).prefetch_related(
                'itens_contrato',
                'itens_contrato__produto'
            )
        )

    def _calcular_indicadores_base(self, contratos) -> Dict[str, Any]:
        """Calcula indicadores base dos contratos"""
        total_contratos = contratos.count()
        total_itens = sum(c.itens_contrato.count() for c in contratos)

        valor_total = contratos.aggregate(
            total=Sum('valorcontrato')
        )['total'] or Decimal('0')

        return {
            'total_contratos': total_contratos,
            'total_itens': total_itens,
            'valor_total_contratos': float(valor_total),
            'valor_medio_contrato': float(
                valor_total / total_contratos if total_contratos > 0 else 0
            ),
            'valor_medio_item': float(
                valor_total / total_itens if total_itens > 0 else 0
            ),
            'itens_por_contrato': float(
                total_itens / total_contratos if total_contratos > 0 else 0
            )
        }

    def _analisar_carteira_contratos(self, contratos) -> Dict[str, Any]:
        """Análise detalhada da carteira de contratos"""
        # Análise por tipo
        analise_tipo = contratos.values(
            'tipocontrato'
        ).annotate(
            quantidade=Count('id'),
            valor_total=Sum('valorcontrato'),
            valor_medio=Avg('valorcontrato'),
            quantidade_itens=Count('itens_contrato')
        ).order_by('tipocontrato')

        # Análise por cliente
        analise_cliente = contratos.values(
            'cliente__id',
            'cliente__nome'
        ).annotate(
            quantidade_contratos=Count('id'),
            valor_total=Sum('valorcontrato'),
            quantidade_itens=Count('itens_contrato')
        ).order_by('-valor_total')

        # Análise por produto
        analise_produtos = (
            contratos.values(
                'itens_contrato__produto__codigo',
                'itens_contrato__produto__nome'
            ).annotate(
                quantidade=Count('id'),
                valor_total=Sum('itens_contrato__valor_locacao')
            ).order_by('-quantidade')
        )

        return {
            'por_tipo': [{
                'tipo': t['tipocontrato'],
                'quantidade': t['quantidade'],
                'valor_total': float(t['valor_total']),
                'valor_medio': float(t['valor_medio']),
                'quantidade_itens': t['quantidade_itens']
            } for t in analise_tipo],
            'por_cliente': [{
                'cliente_id': c['cliente__id'],
                'cliente_nome': c['cliente__nome'],
                'quantidade_contratos': c['quantidade_contratos'],
                'valor_total': float(c['valor_total']),
                'quantidade_itens': c['quantidade_itens']
            } for c in analise_cliente],
            'por_produto': [{
                'codigo': p['itens_contrato__produto__codigo'],
                'nome': p['itens_contrato__produto__nome'],
                'quantidade': p['quantidade'],
                'valor_total': float(p['valor_total'])
            } for p in analise_produtos]
        }

    def _gerar_previsoes_contratos(self, contratos) -> Dict[str, Any]:
        """Gera previsões para os contratos"""
        hoje = date.today()
        
        # Análise de renovações históricas
        historico_renovacoes = (
            contratos.filter(
                fim__lt=hoje,
                renovado=True
            ).count()
        )
        
        total_encerrados = (
            contratos.filter(
                fim__lt=hoje
            ).count()
        )

        taxa_renovacao = (
            historico_renovacoes / total_encerrados * 100
            if total_encerrados > 0 else 0
        )

        # Projeção próximos meses
        projecoes = []
        for mes in range(1, 7):  # Próximos 6 meses
            data_final = hoje + relativedelta(months=mes)
            
            contratos_mes = contratos.filter(
                fim__range=[
                    data_final.replace(day=1),
                    data_final.replace(day=1) + relativedelta(months=1) - timedelta(days=1)
                ]
            )
            
            valor_mes = contratos_mes.aggregate(
                total=Sum('valorcontrato')
            )['total'] or Decimal('0')
            
            projecoes.append({
                'mes': data_final.strftime('%Y-%m'),
                'contratos': contratos_mes.count(),
                'valor_total': float(valor_mes),
                'probabilidade_renovacao': float(
                    self._calcular_probabilidade_renovacao(
                        contratos_mes, taxa_renovacao
                    )
                )
            })

        return {
            'historico': {
                'total_encerrados': total_encerrados,
                'renovados': historico_renovacoes,
                'taxa_renovacao': float(taxa_renovacao)
            },
            'projecoes': projecoes
        }

    def _calcular_probabilidade_renovacao(self, contratos, taxa_base: float) -> float:
        """Calcula probabilidade de renovação de contratos"""
        if not contratos.exists():
            return 0

        fatores = []
        for contrato in contratos:
            # Histórico do cliente
            historico_cliente = contrato.cliente.contratos.filter(
                fim__lt=date.today()
            )
            
            if historico_cliente.exists():
                renovacoes_cliente = historico_cliente.filter(
                    renovado=True
                ).count()
                taxa_cliente = (
                    renovacoes_cliente / historico_cliente.count() * 100
                )
                fatores.append(taxa_cliente)

            # Valor do contrato
            if contrato.valorcontrato > 10000:
                fatores.append(80)  # Contratos de alto valor tendem a renovar mais
            
            # Tempo de relacionamento
            anos_relacionamento = (
                date.today() - contrato.cliente.data_cadastro
            ).days / 365 if contrato.cliente.data_cadastro else 0
            
            if anos_relacionamento > 2:
                fatores.append(70)  # Clientes antigos tendem a renovar mais

        # Média ponderada dos fatores
        if fatores:
            return sum(fatores) / len(fatores)
        return taxa_base

    def _analisar_vencimentos(self, contratos, data_referencia: date) -> List[Dict[str, Any]]:
        """Analisa contratos próximos ao vencimento"""
        vencimentos = []
        
        # Próximos 90 dias
        for dias in [30, 60, 90]:
            data_limite = data_referencia + timedelta(days=dias)
            
            contratos_periodo = contratos.filter(
                fim__range=[data_referencia, data_limite]
            )
            
            if contratos_periodo.exists():
                vencimentos.append({
                    'periodo': f'proximos_{dias}_dias',
                    'quantidade': contratos_periodo.count(),
                    'valor_total': float(
                        contratos_periodo.aggregate(
                            total=Sum('valorcontrato')
                        )['total'] or 0
                    ),
                    'contratos': [{
                        'id': c.id,
                        'numero': c.contrato,
                        'cliente': c.cliente.nome,
                        'vencimento': c.fim,
                        'valor': float(c.valorcontrato)
                    } for c in contratos_periodo]
                })

        return vencimentos

    def _gerar_alertas_contratos(self, indicadores: Dict[str, Any],
                                carteira: Dict[str, Any],
                                vencimentos: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Gera alertas baseados nas análises de contratos"""
        alertas = []

        # Alerta de concentração por cliente
        for cliente in carteira['por_cliente']:
            participacao = (
                cliente['valor_total'] / indicadores['valor_total_contratos'] * 100
                if indicadores['valor_total_contratos'] > 0 else 0
            )
            
            if participacao > 30:
                alertas.append({
                    'tipo': 'concentracao_cliente',
                    'severidade': 'alta',
                    'mensagem': (
                        f"Alta concentração no cliente {cliente['cliente_nome']} "
                        f"({participacao:.1f}%)"
                    ),
                    'detalhes': {
                        'cliente_id': cliente['cliente_id'],
                        'participacao': participacao
                    }
                })

        # Alerta de vencimentos
        for periodo in vencimentos:
            if periodo['valor_total'] > 100000:  # Exemplo de threshold
                alertas.append({
                    'tipo': 'vencimentos',
                    'severidade': 'media',
                    'mensagem': (
                        f"Alto valor de contratos vencendo nos "
                        f"{periodo['periodo'].replace('proximos_', '').replace('_dias', '')} "
                        f"dias: R$ {periodo['valor_total']:,.2f}"
                    ),
                    'detalhes': {
                        'periodo': periodo['periodo'],
                        'quantidade': periodo['quantidade'],
                        'valor_total': periodo['valor_total']
                    }
                })

        return alertas

    @action(detail=False, methods=['GET'])
    def analise_performance(self, request):
        """
        Análise de performance dos contratos
        - Métricas operacionais
        - Análise financeira
        - Comparativos
        """
        try:
            hoje = date.today()
            periodo_meses = int(request.query_params.get('periodo', 12))
            
            contratos = self._get_contratos_periodo(hoje, periodo_meses)
            resultados = self._analisar_performance_contratos(contratos, periodo_meses)
            
            return Response({
                'periodo': {
                    'meses': periodo_meses,
                    'inicio': hoje - relativedelta(months=periodo_meses),
                    'fim': hoje
                },
                'resultados': resultados,
                'recomendacoes': self._gerar_recomendacoes_performance(resultados)
            })

        except Exception as e:
            return Response({'error': str(e)}, status=400)

    def _get_contratos_periodo(self, data_referencia: date, periodo_meses: int):
        """Retorna contratos do período"""
        from contas.models import ContratosLocacao
        
        data_inicial = data_referencia - relativedelta(months=periodo_meses)
        
        return ContratosLocacao.objects.filter(
            Q(inicio__range=[data_inicial, data_referencia]) |
            Q(fim__range=[data_inicial, data_referencia]) |
            Q(inicio__lte=data_inicial, fim__gte=data_referencia)
        ).select_related(
            'cliente'
        ).prefetch_related(
            'itens_contrato',
            'itens_contrato__produto'
        )

    def _analisar_performance_contratos(self, contratos, periodo_meses: int) -> List[Dict[str, Any]]:
        """Análise detalhada da performance dos contratos"""
        resultados = []
        
        for contrato in contratos:
            # Análise dos itens
            itens_analise = self._analisar_itens_contrato(contrato)
            
            # Métricas financeiras
            metricas_financeiras = self._calcular_metricas_financeiras(
                contrato, periodo_meses
            )
            
            # Indicadores operacionais
            indicadores = self._calcular_indicadores_contrato(
                contrato, itens_analise
            )
            
            resultados.append({
                'contrato': {
                    'id': contrato.id,
                    'numero': contrato.contrato,
                    'cliente': contrato.cliente.nome,
                    'inicio': contrato.inicio,
                    'fim': contrato.fim
                },
                'itens': itens_analise,
                'metricas_financeiras': metricas_financeiras,
                'indicadores': indicadores,
                'score': self._calcular_score_contrato(
                    itens_analise,
                    metricas_financeiras,
                    indicadores
                )
            })

        return sorted(resultados , key=lambda x: x['score'], reverse=True)

    def _analisar_itens_contrato(self, contrato) -> List[Dict[str, Any]]:
        """Análise detalhada dos itens do contrato"""
        itens = []
        
        for item in contrato.itens_contrato.all():
            # Calcula custos de manutenção
            custos_manutencao = self._calcular_custos_manutencao(item)
            
            # Calcula disponibilidade
            disponibilidade = self._calcular_disponibilidade_equipamento(item)
            
            itens.append({
                'item': {
                    'numero_serie': item.numeroserie,
                    'produto': item.produto.nome,
                    'categoria': item.categoria.nome if item.categoria else 'N/A'
                },
                'custos': custos_manutencao,
                'disponibilidade': disponibilidade,
                'valor_locacao': float(item.valor_locacao),
                'rentabilidade': self._calcular_rentabilidade_item(
                    item, custos_manutencao
                )
            })
        
        return itens

    def _calcular_custos_manutencao(self, item) -> Dict[str, Any]:
        """Calcula custos de manutenção do item"""
        from contas.models import MovimentacoesEstoque
        
        # Busca movimentações de manutenção
        manutencoes = MovimentacoesEstoque.objects.filter(
            tipo_movimentacao__tipo='S',  # Saída para manutenção
            documento_referencia=item.numeroserie
        )
        
        custo_total = manutencoes.aggregate(
            total=Sum(F('quantidade') * F('custo_unitario'))
        )['total'] or Decimal('0')
        
        return {
            'total': float(custo_total),
            'quantidade_manutencoes': manutencoes.count(),
            'custo_medio': float(
                custo_total / manutencoes.count()
                if manutencoes.exists() else 0
            ),
            'ultima_manutencao': manutencoes.order_by(
                '-data_movimentacao'
            ).first().data_movimentacao if manutencoes.exists() else None
        }

    def _calcular_disponibilidade_equipamento(self, item) -> Dict[str, Any]:
        """Calcula disponibilidade do equipamento"""
        from contas.models import MovimentacoesEstoque
        
        # Período total do contrato
        dias_contrato = (item.contrato.fim - item.contrato.inicio).days
        
        # Dias em manutenção
        manutencoes = MovimentacoesEstoque.objects.filter(
            tipo_movimentacao__tipo='S',
            documento_referencia=item.numeroserie,
            data_movimentacao__range=[
                item.contrato.inicio,
                item.contrato.fim
            ]
        )
        
        dias_manutencao = sum(
            (m.data_retorno - m.data_movimentacao).days
            for m in manutencoes
            if m.data_retorno
        )
        
        return {
            'dias_totais': dias_contrato,
            'dias_manutencao': dias_manutencao,
            'percentual': float(
                (dias_contrato - dias_manutencao) / dias_contrato * 100
                if dias_contrato > 0 else 0
            )
        }

    def _calcular_rentabilidade_item(self, item, custos: Dict[str, Any]) -> Dict[str, Any]:
        """Calcula rentabilidade do item"""
        # Receita total
        receita = item.valor_locacao * item.contrato.numeroparcelas
        
        # Custos totais (aquisição + manutenção)
        custo_total = item.produto.preco_custo + Decimal(str(custos['total']))
        
        # Margem
        margem = ((receita - custo_total) / receita * 100) if receita > 0 else 0
        
        return {
            'receita_total': float(receita),
            'custo_total': float(custo_total),
            'margem': float(margem),
            'roi': float(
                (receita - custo_total) / custo_total * 100
                if custo_total > 0 else 0
            )
        }

    def _calcular_metricas_financeiras(self, contrato, periodo_meses: int) -> Dict[str, Any]:
        """Calcula métricas financeiras do contrato"""
        # Faturamento realizado
        faturamento = self._calcular_faturamento_contrato(contrato, periodo_meses)
        
        # Custos totais
        custos = self._calcular_custos_contrato(contrato, periodo_meses)
        
        # Margens
        if faturamento['total'] > 0:
            margem_bruta = (
                (faturamento['total'] - custos['total']) / 
                faturamento['total'] * 100
            )
            margem_liquida = (
                (faturamento['total'] - custos['total'] - custos['impostos']) /
                faturamento['total'] * 100
            )
        else:
            margem_bruta = margem_liquida = 0

        return {
            'faturamento': faturamento,
            'custos': custos,
            'margens': {
                'bruta': float(margem_bruta),
                'liquida': float(margem_liquida)
            },
            'ticket_medio': float(
                faturamento['total'] / faturamento['quantidade']
                if faturamento['quantidade'] > 0 else 0
            )
        }

    def _calcular_faturamento_contrato(self, contrato, periodo_meses: int) -> Dict[str, Any]:
        """Calcula faturamento realizado do contrato"""
        from contas.models import NotasFiscaisSaida
        
        notas = NotasFiscaisSaida.objects.filter(
            cliente=contrato.cliente,
            data__range=[
                date.today() - relativedelta(months=periodo_meses),
                date.today()
            ]
        )
        
        return {
            'total': float(
                notas.aggregate(total=Sum('valor_total'))['total'] or 0
            ),
            'quantidade': notas.count(),
            'media_mensal': float(
                (notas.aggregate(total=Sum('valor_total'))['total'] or 0) /
                periodo_meses
            )
        }

    def _calcular_custos_contrato(self, contrato, periodo_meses: int) -> Dict[str, Any]:
        """Calcula custos totais do contrato"""
        # Custos de aquisição
        custo_aquisicao = sum(
            item.produto.preco_custo
            for item in contrato.itens_contrato.all()
        )
        
        # Custos de manutenção
        custos_manutencao = sum(
            self._calcular_custos_manutencao(item)['total']
            for item in contrato.itens_contrato.all()
        )
        
        # Custos operacionais (estimativa)
        custos_operacionais = custo_aquisicao * Decimal('0.1')  # 10% ao mês
        
        # Impostos (estimativa)
        impostos = (contrato.valorcontrato * Decimal('0.15'))  # 15% de impostos
        
        total = (
            custo_aquisicao +
            Decimal(str(custos_manutencao)) +
            custos_operacionais +
            impostos
        )

        return {
            'aquisicao': float(custo_aquisicao),
            'manutencao': float(custos_manutencao),
            'operacionais': float(custos_operacionais),
            'impostos': float(impostos),
            'total': float(total)
        }

    def _calcular_indicadores_contrato(self, contrato, 
                                     itens_analise: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calcula indicadores operacionais do contrato"""
        # Disponibilidade média
        disponibilidade = sum(
            item['disponibilidade']['percentual']
            for item in itens_analise
        ) / len(itens_analise) if itens_analise else 0
        
        # Tempo médio entre falhas (MTBF)
        total_manutencoes = sum(
            item['custos']['quantidade_manutencoes']
            for item in itens_analise
        )
        
        dias_totais = sum(
            item['disponibilidade']['dias_totais']
            for item in itens_analise
        )
        
        mtbf = (
            dias_totais / total_manutencoes
            if total_manutencoes > 0 else dias_totais
        )
        
        # Custos de manutenção por equipamento
        custo_medio_manutencao = sum(
            item['custos']['total']
            for item in itens_analise
        ) / len(itens_analise) if itens_analise else 0

        return {
            'disponibilidade': float(disponibilidade),
            'mtbf': float(mtbf),
            'custo_medio_manutencao': float(custo_medio_manutencao),
            'idade_media_equipamentos': self._calcular_idade_media_equipamentos(
                contrato
            )
        }

    def _calcular_idade_media_equipamentos(self, contrato) -> float:
        """Calcula idade média dos equipamentos do contrato"""
        idades = []
        
        for item in contrato.itens_contrato.all():
            if item.produto.data_fabricacao:
                idade = (date.today() - item.produto.data_fabricacao).days / 365
                idades.append(idade)
        
        return sum(idades) / len(idades) if idades else 0

    def _calcular_score_contrato(self, itens_analise: List[Dict[str, Any]],
                                metricas_financeiras: Dict[str, Any],
                                indicadores: Dict[str, Any]) -> float:
        """Calcula score geral do contrato (0-100)"""
        score = 0
        
        # Componente financeiro (40%)
        score += min(metricas_financeiras['margens']['liquida'], 40) * 0.4
        
        # Componente operacional (30%)
        score += min(indicadores['disponibilidade'], 100) * 0.3
        
        # Componente de rentabilidade (30%)
        rentabilidade_media = sum(
            item['rentabilidade']['margem']
            for item in itens_analise
        ) / len(itens_analise) if itens_analise else 0
        
        score += min(rentabilidade_media, 100) * 0.3
        
        return score

    def _gerar_recomendacoes_performance(self, resultados: List[Dict[str, Any]]) -> List[Dict[str, str]]:
        """Gera recomendações baseadas na análise de performance"""
        recomendacoes = []
        
        # Analisa scores baixos
        contratos_baixo_score = [
            r for r in resultados
            if r['score'] < 60
        ]
        
        if contratos_baixo_score:
            recomendacoes.append({
                'tipo': 'performance',
                'severidade': 'alta',
                'mensagem': f'{len(contratos_baixo_score)} contratos com baixa performance',
                'acoes': [
                    'Revisar condições contratuais',
                    'Avaliar substituição de equipamentos',
                    'Analisar custos operacionais'
                ]
            })

        # Analisa disponibilidade
        contratos_baixa_disponibilidade = [
            r for r in resultados
            if r['indicadores']['disponibilidade'] < 90
        ]
        
        if contratos_baixa_disponibilidade:
            recomendacoes.append({
                'tipo': 'disponibilidade',
                'severidade': 'alta',
                'mensagem': 'Baixa disponibilidade de equipamentos',
                'acoes': [
                    'Implementar manutenção preventiva',
                    'Revisar processo de atendimento',
                    'Avaliar qualidade dos equipamentos'
                ]
            })

        # Analisa rentabilidade
        contratos_baixa_rentabilidade = [
            r for r in resultados
            if r['metricas_financeiras']['margens']['liquida'] < 15
        ]
        
        if contratos_baixa_rentabilidade:
            recomendacoes.append({
                'tipo': 'rentabilidade',
                'severidade': 'alta',
                'mensagem': 'Contratos com baixa rentabilidade',
                'acoes': [
                    'Revisar política de preços',
                    'Otimizar custos de manutenção',
                    'Analisar estrutura operacional'
                ]
            })

        return recomendacoes