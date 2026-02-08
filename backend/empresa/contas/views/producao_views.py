from datetime import datetime
from decimal import Decimal

from django.db import transaction
from django.db.models import Sum
from django.utils import timezone
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from ..models.access import (
    ApontamentosProducao,
    ConsumosProducao,
    ItensOrdemProducao,
    MovimentacoesEstoque,
    OrdensProducao,
    SaldosEstoque,
    TiposMovimentacaoEstoque,
)


def _decimal(value, default='0.0000'):
    if value is None or value == '':
        return Decimal(default)
    return Decimal(str(value))


def _parse_date(value):
    if not value:
        return None
    try:
        return datetime.strptime(value, '%Y-%m-%d').date()
    except ValueError:
        return None


def _atualizar_saldo_estoque(produto_id, local_id, delta_quantidade, custo_unitario, data_movimentacao):
    if not produto_id or not local_id:
        return

    saldo, _ = SaldosEstoque.objects.get_or_create(
        produto_id=produto_id,
        local_id=local_id,
        lote_id=None,
        defaults={
            'quantidade': Decimal('0.000'),
            'custo_medio': Decimal('0.0000')
        }
    )

    quantidade_atual = saldo.quantidade or Decimal('0.000')
    nova_quantidade = quantidade_atual + delta_quantidade

    if delta_quantidade > 0 and custo_unitario is not None:
        custo_atual = saldo.custo_medio or Decimal('0.0000')
        valor_atual = quantidade_atual * custo_atual
        valor_entrada = delta_quantidade * custo_unitario
        if nova_quantidade > 0:
            saldo.custo_medio = (valor_atual + valor_entrada) / nova_quantidade

    saldo.quantidade = nova_quantidade
    saldo.ultima_movimentacao = data_movimentacao
    saldo.save()


def _tipo_movimentacao(tipo):
    return TiposMovimentacaoEstoque.objects.filter(tipo=tipo, ativo=True).first()


class ProducaoOrdemGerarView(APIView):
    """Gera ordem de produção com itens (insumos)."""

    def post(self, request, *args, **kwargs):
        payload = request.data or {}
        ordem_data = payload.get('ordem') or {}
        itens_data = payload.get('itens') or []

        if not ordem_data.get('numero_ordem') or not ordem_data.get('produto_final_id'):
            return Response(
                {'error': 'numero_ordem e produto_final_id são obrigatórios.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not itens_data:
            return Response(
                {'error': 'Informe ao menos um insumo em itens.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        with transaction.atomic():
            ordem = OrdensProducao.objects.create(
                numero_ordem=ordem_data.get('numero_ordem'),
                produto_final_id=ordem_data.get('produto_final_id'),
                local_id_id=ordem_data.get('local_id'),
                quantidade_planejada=_decimal(ordem_data.get('quantidade_planejada')),
                data_inicio=ordem_data.get('data_inicio'),
                observacoes=ordem_data.get('observacoes'),
            )

            for item in itens_data:
                ItensOrdemProducao.objects.create(
                    ordem=ordem,
                    produto_insumo_id=item.get('produto_insumo_id'),
                    quantidade=_decimal(item.get('quantidade')),
                )

        return Response(
            {'id': ordem.id, 'numero_ordem': ordem.numero_ordem, 'status': ordem.status},
            status=status.HTTP_201_CREATED
        )


class ProducaoOrdemAprovarView(APIView):
    """Aprova a ordem de produção."""

    def post(self, request, *args, **kwargs):
        ordem_id = (request.data or {}).get('ordem_id')
        if not ordem_id:
            return Response({'error': 'ordem_id é obrigatório.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            ordem = OrdensProducao.objects.get(id=ordem_id)
        except OrdensProducao.DoesNotExist:
            return Response({'error': 'Ordem não encontrada.'}, status=status.HTTP_404_NOT_FOUND)

        ordem.status = 'A'
        ordem.save(update_fields=['status'])
        return Response({'id': ordem.id, 'status': ordem.status}, status=status.HTTP_200_OK)


class ProducaoOrdemIniciarView(APIView):
    """Marca a ordem como em produção."""

    def post(self, request, *args, **kwargs):
        ordem_id = (request.data or {}).get('ordem_id')
        if not ordem_id:
            return Response({'error': 'ordem_id é obrigatório.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            ordem = OrdensProducao.objects.get(id=ordem_id)
        except OrdensProducao.DoesNotExist:
            return Response({'error': 'Ordem não encontrada.'}, status=status.HTTP_404_NOT_FOUND)

        ordem.status = 'E'
        if not ordem.data_inicio:
            ordem.data_inicio = timezone.now()
        ordem.save(update_fields=['status', 'data_inicio'])
        return Response({'id': ordem.id, 'status': ordem.status}, status=status.HTTP_200_OK)


class ProducaoConsumoApontarView(APIView):
    """Aponta consumo de insumos e baixa estoque."""

    def post(self, request, *args, **kwargs):
        payload = request.data or {}
        ordem_id = payload.get('ordem_id')
        local_id = payload.get('local_id')
        itens = payload.get('itens') or []

        if not ordem_id or not local_id:
            return Response({'error': 'ordem_id e local_id são obrigatórios.'}, status=status.HTTP_400_BAD_REQUEST)

        if not itens:
            return Response({'error': 'Informe itens de consumo.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            ordem = OrdensProducao.objects.get(id=ordem_id)
        except OrdensProducao.DoesNotExist:
            return Response({'error': 'Ordem não encontrada.'}, status=status.HTTP_404_NOT_FOUND)

        tipo_saida = _tipo_movimentacao('S')
        data_movimentacao = timezone.now()

        with transaction.atomic():
            for item in itens:
                produto_id = item.get('produto_id')
                quantidade = _decimal(item.get('quantidade'))
                if quantidade <= 0:
                    continue

                ConsumosProducao.objects.create(
                    ordem=ordem,
                    produto_id=produto_id,
                    local_id_id=local_id,
                    quantidade=quantidade,
                    data_consumo=data_movimentacao,
                )

                MovimentacoesEstoque.objects.create(
                    data_movimentacao=data_movimentacao,
                    tipo_movimentacao=tipo_saida,
                    produto_id=produto_id,
                    local_origem_id=local_id,
                    quantidade=quantidade,
                    observacoes='Consumo produção',
                    documento_referencia=ordem.numero_ordem,
                )

                _atualizar_saldo_estoque(
                    produto_id=produto_id,
                    local_id=local_id,
                    delta_quantidade=-quantidade,
                    custo_unitario=None,
                    data_movimentacao=data_movimentacao,
                )

        return Response({'status': 'consumo_registrado'}, status=status.HTTP_201_CREATED)


class ProducaoApontarView(APIView):
    """Aponta produção e adiciona saldo de estoque do produto final."""

    def post(self, request, *args, **kwargs):
        payload = request.data or {}
        ordem_id = payload.get('ordem_id')
        local_id = payload.get('local_id')
        quantidade = _decimal(payload.get('quantidade'))

        if not ordem_id or not local_id:
            return Response({'error': 'ordem_id e local_id são obrigatórios.'}, status=status.HTTP_400_BAD_REQUEST)

        if quantidade <= 0:
            return Response({'error': 'quantidade deve ser maior que zero.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            ordem = OrdensProducao.objects.get(id=ordem_id)
        except OrdensProducao.DoesNotExist:
            return Response({'error': 'Ordem não encontrada.'}, status=status.HTTP_404_NOT_FOUND)

        data_movimentacao = timezone.now()
        tipo_entrada = _tipo_movimentacao('E')

        with transaction.atomic():
            ApontamentosProducao.objects.create(
                ordem=ordem,
                local_id_id=local_id,
                quantidade=quantidade,
                data_apontamento=data_movimentacao,
            )

            ordem.quantidade_produzida = (ordem.quantidade_produzida or Decimal('0.0000')) + quantidade
            ordem.save(update_fields=['quantidade_produzida'])

            MovimentacoesEstoque.objects.create(
                data_movimentacao=data_movimentacao,
                tipo_movimentacao=tipo_entrada,
                produto_id=ordem.produto_final_id,
                local_destino_id=local_id,
                quantidade=quantidade,
                observacoes='Produção finalizada',
                documento_referencia=ordem.numero_ordem,
            )

            _atualizar_saldo_estoque(
                produto_id=ordem.produto_final_id,
                local_id=local_id,
                delta_quantidade=quantidade,
                custo_unitario=None,
                data_movimentacao=data_movimentacao,
            )

        return Response(
            {'status': 'apontado', 'quantidade_produzida': float(ordem.quantidade_produzida)},
            status=status.HTTP_201_CREATED
        )


class ProducaoOrdemFinalizarView(APIView):
    """Finaliza a ordem de produção."""

    def post(self, request, *args, **kwargs):
        ordem_id = (request.data or {}).get('ordem_id')
        if not ordem_id:
            return Response({'error': 'ordem_id é obrigatório.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            ordem = OrdensProducao.objects.get(id=ordem_id)
        except OrdensProducao.DoesNotExist:
            return Response({'error': 'Ordem não encontrada.'}, status=status.HTTP_404_NOT_FOUND)

        ordem.status = 'F'
        ordem.data_fim = timezone.now()
        ordem.save(update_fields=['status', 'data_fim'])
        return Response({'id': ordem.id, 'status': ordem.status}, status=status.HTTP_200_OK)


class ProducaoOrdemCancelarView(APIView):
    """Cancela a ordem de produção."""

    def post(self, request, *args, **kwargs):
        ordem_id = (request.data or {}).get('ordem_id')
        if not ordem_id:
            return Response({'error': 'ordem_id é obrigatório.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            ordem = OrdensProducao.objects.get(id=ordem_id)
        except OrdensProducao.DoesNotExist:
            return Response({'error': 'Ordem não encontrada.'}, status=status.HTTP_404_NOT_FOUND)

        ordem.status = 'X'
        ordem.save(update_fields=['status'])
        return Response({'id': ordem.id, 'status': ordem.status}, status=status.HTTP_200_OK)


class ProducaoOrdensListaView(APIView):
    """Lista ordens de produção com filtros."""

    def get(self, request, *args, **kwargs):
        status_filtro = request.query_params.get('status')
        data_inicio = _parse_date(request.query_params.get('data_inicio'))
        data_fim = _parse_date(request.query_params.get('data_fim'))

        ordens = OrdensProducao.objects.select_related('produto_final')

        if status_filtro:
            ordens = ordens.filter(status=status_filtro)
        if data_inicio and data_fim:
            ordens = ordens.filter(
                data_inicio__date__gte=data_inicio,
                data_inicio__date__lte=data_fim
            )
        elif data_inicio or data_fim:
            return Response(
                {'error': 'Informe data_inicio e data_fim no formato YYYY-MM-DD.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        response = [
            {
                'id': ordem.id,
                'numero_ordem': ordem.numero_ordem,
                'produto_final_id': ordem.produto_final_id,
                'produto_final_nome': ordem.produto_final.nome if ordem.produto_final else None,
                'quantidade_planejada': float(ordem.quantidade_planejada or 0),
                'quantidade_produzida': float(ordem.quantidade_produzida or 0),
                'status': ordem.status,
                'data_inicio': ordem.data_inicio,
            }
            for ordem in ordens.order_by('-data_inicio')[:200]
        ]

        return Response({'quantidade': len(response), 'resultados': response}, status=status.HTTP_200_OK)


class ProducaoResumoView(APIView):
    """Resumo de produção por período."""

    def get(self, request, *args, **kwargs):
        data_inicio = _parse_date(request.query_params.get('data_inicio'))
        data_fim = _parse_date(request.query_params.get('data_fim'))

        ordens = OrdensProducao.objects.all()
        if data_inicio and data_fim:
            ordens = ordens.filter(
                data_inicio__date__gte=data_inicio,
                data_inicio__date__lte=data_fim
            )
        elif data_inicio or data_fim:
            return Response(
                {'error': 'Informe data_inicio e data_fim no formato YYYY-MM-DD.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        totais = ordens.aggregate(
            quantidade_planejada=Sum('quantidade_planejada'),
            quantidade_produzida=Sum('quantidade_produzida'),
        )

        return Response(
            {
                'quantidade_planejada': float(totais['quantidade_planejada'] or Decimal('0.00')),
                'quantidade_produzida': float(totais['quantidade_produzida'] or Decimal('0.00')),
            },
            status=status.HTTP_200_OK
        )
