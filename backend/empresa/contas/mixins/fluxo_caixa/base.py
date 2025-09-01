from decimal import Decimal
from datetime import date, datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
from django.db.models import Q, Sum, F, Case, When, Value, DecimalField
from django.core.exceptions import ValidationError
from django.db import transaction
from rest_framework.decorators import action
from rest_framework.response import Response

from contas.models import ContasPagar, ContasReceber, ContratosLocacao

class FluxoCaixaBaseMixin:
    """
    Mixin base com funcionalidades essenciais e avançadas para o fluxo de caixa
    """

    def get_queryset(self):
        """Retorna queryset com filtros aplicados"""
        queryset = super().get_queryset()
        
        # Filtros básicos
        filtros = self._build_base_filters()
        
        # Filtros avançados
        filtros.extend(self._build_advanced_filters())
        
        # Aplica todos os filtros
        for filtro in filtros:
            queryset = queryset.filter(filtro)

        # Otimiza queries com select_related
        queryset = self._optimize_queryset(queryset)
            
        return queryset

    def _optimize_queryset(self, queryset):
        """Otimiza queryset com joins necessários"""
        return queryset.select_related(
            'cliente',
            'fornecedor',
            'conta_bancaria'
        ).prefetch_related(
            'lancamento_estornado',
            'estornos'
        )

    def _build_base_filters(self) -> List[Q]:
        """Constrói filtros básicos baseados nos parâmetros da request"""
        filtros = []
        params = self.request.query_params

        # Filtros de data
        if data_inicial := params.get('data_inicial'):
            filtros.append(Q(data__gte=data_inicial))
        if data_final := params.get('data_final'):
            filtros.append(Q(data__lte=data_final))

        # Filtros simples
        campos_simples = ['tipo', 'categoria', 'fonte_tipo', 'cliente', 'fornecedor']
        for campo in campos_simples:
            if valor := params.get(campo):
                filtros.append(Q(**{campo: valor}))

        return filtros

    def _build_advanced_filters(self) -> List[Q]:
        """Constrói filtros avançados baseados nos parâmetros da request"""
        filtros = []
        params = self.request.query_params

        # Status de realização
        if status := params.get('realizado'):
            filtros.append(Q(realizado=status.lower() == 'true'))

        # Filtros de valor
        if valor_min := params.get('valor_min'):
            filtros.append(Q(valor__gte=Decimal(valor_min)))
        if valor_max := params.get('valor_max'):
            filtros.append(Q(valor__lte=Decimal(valor_max)))

        # Filtros de data de realização
        if data_realizacao_inicial := params.get('data_realizacao_inicial'):
            filtros.append(Q(data_realizacao__date__gte=data_realizacao_inicial))
        if data_realizacao_final := params.get('data_realizacao_final'):
            filtros.append(Q(data_realizacao__date__lte=data_realizacao_final))

        # Filtros de estorno
        if params.get('estornado') == 'true':
            filtros.append(Q(data_estorno__isnull=False))
        elif params.get('estornado') == 'false':
            filtros.append(Q(data_estorno__isnull=True))

        # Busca por descrição
        if busca := params.get('busca'):
            filtros.append(
                Q(descricao__icontains=busca) | 
                Q(observacoes__icontains=busca)
            )

        return filtros

    @action(detail=True, methods=['POST'])
    def realizar(self, request, pk=None):
        """Realiza um lançamento"""
        lancamento = self.get_object()
        
        try:
            with transaction.atomic():
                self._validar_realizacao(lancamento)
                self._processar_realizacao(lancamento)
                self._atualizar_saldos(lancamento.data)
                
                return Response(self.get_serializer(lancamento).data)
        except ValidationError as e:
            return Response({'error': str(e)}, status=400)

    def _validar_realizacao(self, lancamento):
        """Valida se um lançamento pode ser realizado"""
        if lancamento.realizado:
            raise ValidationError('Lançamento já realizado')
            
        if lancamento.data_estorno:
            raise ValidationError('Lançamento estornado não pode ser realizado')
            
        if lancamento.data > date.today():
            raise ValidationError('Não é possível realizar lançamentos futuros')

    def _processar_realizacao(self, lancamento):
        """Processa a realização de um lançamento"""
        lancamento.realizado = True
        lancamento.data_realizacao = datetime.now()
        lancamento.save()
        
        # Atualiza documento de origem
        if fonte := self._get_documento_fonte(lancamento):
            fonte.processar_realizacao()

    @action(detail=True, methods=['POST'])
    def estornar(self, request, pk=None):
        """Estorna um lançamento"""
        lancamento = self.get_object()
        
        try:
            with transaction.atomic():
                self._validar_estorno(lancamento)
                estorno = self._processar_estorno(lancamento, request.data.get('motivo'))
                self._atualizar_saldos(lancamento.data)
                
                return Response(self.get_serializer(estorno).data)
        except ValidationError as e:
            return Response({'error': str(e)}, status=400)

    def _validar_estorno(self, lancamento):
        """Valida se um lançamento pode ser estornado"""
        if not lancamento.realizado:
            raise ValidationError('Apenas lançamentos realizados podem ser estornados')
            
        if lancamento.data_estorno:
            raise ValidationError('Lançamento já estornado')

    def _processar_estorno(self, lancamento, motivo=None):
        """Processa o estorno de um lançamento"""
        # Registra estorno no lançamento original
        lancamento.data_estorno = datetime.now()
        lancamento.save()
        
        # Cria lançamento de estorno
        estorno = self.get_queryset().model.objects.create(
            data=date.today(),
            tipo='entrada' if lancamento.tipo == 'saida' else 'saida',
            valor=lancamento.valor,
            descricao=f'Estorno: {lancamento.descricao}',
            categoria=lancamento.categoria,
            realizado=True,
            data_realizacao=datetime.now(),
            lancamento_estornado=lancamento,
            observacoes=f'Motivo do estorno: {motivo}' if motivo else None
        )
        
        # Atualiza documento de origem
        if fonte := self._get_documento_fonte(lancamento):
            fonte.processar_estorno()
            
        return estorno

    def _get_documento_fonte(self, lancamento):
        """Retorna o documento de origem do lançamento"""
        if not lancamento.fonte_tipo or not lancamento.fonte_id:
            return None
            
        try:
            if lancamento.fonte_tipo == 'conta_receber':
                return ContasReceber.objects.get(id=lancamento.fonte_id)
            elif lancamento.fonte_tipo == 'conta_pagar':
                return ContasPagar.objects.get(id=lancamento.fonte_id)
            elif lancamento.fonte_tipo == 'contrato':
                return ContratosLocacao.objects.get(id=lancamento.fonte_id)
        except:
            return None

    def _atualizar_saldos(self, data_inicial: date):
        """Atualiza saldos diários a partir de uma data"""
        from contas.models import SaldoDiario
        
        # Busca último saldo antes da data
        saldo_anterior = SaldoDiario.objects.filter(
            data__lt=data_inicial
        ).order_by('-data').first()
        
        saldo_atual = saldo_anterior.saldo_final if saldo_anterior else Decimal('0')
        
        # Atualiza saldos dia a dia
        data_atual = data_inicial
        while data_atual <= date.today():
            lancamentos_dia = self.get_queryset().filter(
                data=data_atual,
                realizado=True,
                data_estorno__isnull=True
            )
            
            entradas = lancamentos_dia.filter(tipo='entrada').aggregate(
                total=Sum('valor'))['total'] or Decimal('0')
            saidas = lancamentos_dia.filter(tipo='saida').aggregate(
                total=Sum('valor'))['total'] or Decimal('0')
            
            saldo_atual += entradas - saidas
            
            SaldoDiario.objects.update_or_create(
                data=data_atual,
                defaults={
                    'saldo_inicial': saldo_atual - (entradas - saidas),
                    'total_entradas': entradas,
                    'total_saidas': saidas,
                    'saldo_final': saldo_atual
                }
            )
            
            data_atual += timedelta(days=1)

    @action(detail=False, methods=['GET'])
    def saldos(self, request):
        """Retorna saldos do período"""
        try:
            data_inicial = datetime.strptime(
                request.query_params.get('data_inicial', date.today().strftime('%Y-%m-%d')),
                '%Y-%m-%d'
            ).date()
            data_final = datetime.strptime(
                request.query_params.get('data_final', date.today().strftime('%Y-%m-%d')),
                '%Y-%m-%d'
            ).date()
            
            # Valida período
            self._validar_periodo(data_inicial, data_final)
            
            # Calcula saldos
            saldos = self._calcular_saldos_periodo(data_inicial, data_final)
            projecao = self._calcular_projecao_saldo(data_final)
            
            return Response({
                'periodo': {
                    'inicio': data_inicial,
                    'fim': data_final
                },
                'saldos': saldos,
                'projecao': projecao
            })
            
        except ValidationError as e:
            return Response({'error': str(e)}, status=400)

    def _validar_periodo(self, data_inicial: date, data_final: date):
        """Valida um período de datas"""
        if data_inicial > data_final:
            raise ValidationError("Data inicial não pode ser maior que data final")
            
        if (data_final - data_inicial).days > 366:
            raise ValidationError("Período máximo de consulta é de 1 ano")

    def _calcular_saldos_periodo(self, data_inicial: date, data_final: date) -> List[Dict]:
        """Calcula saldos diários para um período"""
        from contas.models import SaldoDiario
        
        return SaldoDiario.objects.filter(
            data__range=[data_inicial, data_final]
        ).values(
            'data',
            'saldo_inicial',
            'total_entradas',
            'total_saidas',
            'saldo_final'
        ).order_by('data')

    def _calcular_projecao_saldo(self, data_base: date) -> Dict[str, Any]:
        """Calcula projeção de saldo"""
        # Saldo atual
        saldo_atual = self._obter_saldo_inicial(date.today())
        
        # Projeção próximos 30 dias
        lancamentos_futuros = self.get_queryset().filter(
            data__gt=data_base,
            data__lte=data_base + timedelta(days=30)
        )
        
        entradas_previstas = lancamentos_futuros.filter(
            tipo='entrada'
        ).aggregate(total=Sum('valor'))['total'] or Decimal('0')
        
        saidas_previstas = lancamentos_futuros.filter(
            tipo='saida'
        ).aggregate(total=Sum('valor'))['total'] or Decimal('0')
        
        return {
            'saldo_atual': float(saldo_atual),
            'entradas_previstas': float(entradas_previstas),
            'saidas_previstas': float(saidas_previstas),
            'saldo_projetado': float(saldo_atual + entradas_previstas - saidas_previstas)
        }