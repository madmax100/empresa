from datetime import datetime
from decimal import Decimal

from django.db import transaction
from django.utils import timezone
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from ..models.access import (
    ContasReceber,
    ItensNfSaida,
    ItensPedidoVenda,
    MovimentacoesEstoque,
    NotasFiscaisSaida,
    OrcamentosVenda,
    PedidosVenda,
    SaldosEstoque,
    TiposMovimentacaoEstoque,
)


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
    saldo.quantidade = quantidade_atual + delta_quantidade
    saldo.ultima_movimentacao = data_movimentacao
    if delta_quantidade > 0 and custo_unitario is not None:
        custo_atual = saldo.custo_medio or Decimal('0.0000')
        valor_atual = quantidade_atual * custo_atual
        valor_entrada = delta_quantidade * custo_unitario
        if saldo.quantidade > 0:
            saldo.custo_medio = (valor_atual + valor_entrada) / saldo.quantidade
    saldo.save()


class VendasCadastroView(APIView):
    @staticmethod
    def _parse_datetime(value):
        if not value:
            return None
        if isinstance(value, datetime):
            return value
        try:
            return datetime.fromisoformat(value)
        except (TypeError, ValueError):
            return None

    def post(self, request, *args, **kwargs):
        payload = request.data
        itens = payload.get('itens', [])

        if not itens:
            return Response(
                {'error': 'Informe ao menos um item para o pedido.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        with transaction.atomic():
            pedido = PedidosVenda.objects.create(
                numero_pedido=payload.get('numero_pedido'),
                cliente_id=payload.get('cliente_id'),
                vendedor_id=payload.get('vendedor_id'),
                orcamento_id=payload.get('orcamento_id'),
                data_emissao=self._parse_datetime(payload.get('data_emissao')) or timezone.now(),
                forma_pagamento=payload.get('forma_pagamento'),
                condicoes_pagamento=payload.get('condicoes_pagamento'),
                prazo_entrega=payload.get('prazo_entrega'),
                desconto=Decimal(str(payload.get('desconto', '0.00'))),
                frete=Decimal(str(payload.get('frete', '0.00'))),
                impostos=Decimal(str(payload.get('impostos', '0.00'))),
                observacoes=payload.get('observacoes'),
                status='RASCUNHO'
            )

            valor_produtos = Decimal('0.00')
            for item in itens:
                quantidade = Decimal(str(item.get('quantidade', '0.0000')))
                valor_unitario = Decimal(str(item.get('valor_unitario', '0.00')))
                desconto_item = Decimal(str(item.get('desconto', '0.00')))
                valor_total_item = (quantidade * valor_unitario) - desconto_item
                valor_produtos += valor_total_item

                ItensPedidoVenda.objects.create(
                    pedido=pedido,
                    produto_id=item.get('produto_id'),
                    quantidade=quantidade,
                    valor_unitario=valor_unitario,
                    desconto=desconto_item,
                    valor_total=valor_total_item
                )

            pedido.valor_produtos = valor_produtos
            pedido.save()

        return Response(
            {'message': 'Pedido criado com sucesso', 'pedido_id': pedido.id},
            status=status.HTTP_201_CREATED
        )


class VendasAprovarView(APIView):
    def post(self, request, *args, **kwargs):
        pedido_id = request.data.get('pedido_id')
        pedido = PedidosVenda.objects.filter(id=pedido_id).first()

        if not pedido:
            return Response({'error': 'Pedido não encontrado.'}, status=status.HTTP_404_NOT_FOUND)

        if pedido.status != 'RASCUNHO':
            return Response(
                {'error': 'Apenas pedidos em rascunho podem ser aprovados.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        pedido.status = 'APROVADO'
        pedido.data_aprovacao = timezone.now()
        pedido.save()

        return Response({'message': 'Pedido aprovado com sucesso.'})


class VendasCancelarView(APIView):
    def post(self, request, *args, **kwargs):
        pedido_id = request.data.get('pedido_id')
        pedido = PedidosVenda.objects.filter(id=pedido_id).first()

        if not pedido:
            return Response({'error': 'Pedido não encontrado.'}, status=status.HTTP_404_NOT_FOUND)

        if pedido.status == 'FATURADO':
            return Response(
                {'error': 'Pedidos faturados não podem ser cancelados por este endpoint.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        pedido.status = 'CANCELADO'
        pedido.save()
        return Response({'message': 'Pedido cancelado com sucesso.'})


class VendasFaturarView(APIView):
    @staticmethod
    def _parse_datetime(value):
        if not value:
            return None
        if isinstance(value, datetime):
            return value
        try:
            return datetime.fromisoformat(value)
        except (TypeError, ValueError):
            return None

    def post(self, request, *args, **kwargs):
        payload = request.data
        pedido_id = payload.get('pedido_id')
        numero_nota = payload.get('numero_nota')
        data_emissao = self._parse_datetime(payload.get('data_emissao')) or timezone.now()
        vencimento = self._parse_datetime(payload.get('vencimento'))
        tipo_movimentacao_id = payload.get('tipo_movimentacao_id')
        local_id = payload.get('local_id')

        pedido = PedidosVenda.objects.filter(id=pedido_id).prefetch_related('itens').first()

        if not pedido:
            return Response({'error': 'Pedido não encontrado.'}, status=status.HTTP_404_NOT_FOUND)

        if pedido.status != 'APROVADO':
            return Response(
                {'error': 'Somente pedidos aprovados podem ser faturados.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not numero_nota:
            return Response(
                {'error': 'Informe o numero_nota para faturar.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        tipo_movimentacao = None
        if tipo_movimentacao_id:
            tipo_movimentacao = TiposMovimentacaoEstoque.objects.filter(id=tipo_movimentacao_id).first()
        if not tipo_movimentacao:
            tipo_movimentacao = TiposMovimentacaoEstoque.objects.filter(tipo='S', ativo=True).first()

        with transaction.atomic():
            nota = NotasFiscaisSaida.objects.create(
                numero_nota=numero_nota,
                data=data_emissao,
                cliente=pedido.cliente,
                valor_produtos=pedido.valor_produtos,
                desconto=pedido.desconto,
                valor_frete=pedido.frete,
                valor_icms=pedido.impostos,
                valor_ipi=Decimal('0.00'),
                outras_despesas=Decimal('0.00'),
                seguro=Decimal('0.00'),
                vendedor=pedido.vendedor,
                forma_pagamento=pedido.forma_pagamento,
                condicoes=pedido.condicoes_pagamento,
            )

            for item in pedido.itens.all():
                ItensNfSaida.objects.create(
                    nota_fiscal=nota,
                    data=data_emissao,
                    produto=item.produto,
                    quantidade=item.quantidade,
                    valor_unitario=item.valor_unitario,
                    desconto=item.desconto,
                    valor_total=item.valor_total
                )

                saldo = None
                if local_id:
                    saldo = SaldosEstoque.objects.filter(produto=item.produto, local_id=local_id).first()
                custo_unitario = saldo.custo_medio if saldo else item.valor_unitario

                MovimentacoesEstoque.objects.create(
                    data_movimentacao=data_emissao,
                    tipo_movimentacao=tipo_movimentacao,
                    produto=item.produto,
                    local_origem_id=local_id,
                    quantidade=item.quantidade,
                    custo_unitario=custo_unitario,
                    valor_total=item.valor_total,
                    nota_fiscal_saida=nota,
                    documento_referencia=f"Pedido {pedido.numero_pedido or pedido.id}"
                )

                _atualizar_saldo_estoque(
                    produto_id=item.produto_id,
                    local_id=local_id,
                    delta_quantidade=-item.quantidade,
                    custo_unitario=custo_unitario,
                    data_movimentacao=data_emissao
                )

            ContasReceber.objects.create(
                documento=numero_nota,
                data=data_emissao,
                valor=pedido.valor_total,
                cliente=pedido.cliente,
                vencimento=vencimento or data_emissao,
                historico=f"Pedido de venda {pedido.numero_pedido or pedido.id}",
                forma_pagamento=pedido.forma_pagamento,
                condicoes=pedido.condicoes_pagamento,
                status='A'
            )

            pedido.status = 'FATURADO'
            pedido.data_faturamento = data_emissao
            pedido.save()

        return Response({'message': 'Pedido faturado com sucesso', 'nota_fiscal_id': nota.id})


class VendasConverterOrcamentoView(APIView):
    def post(self, request, *args, **kwargs):
        orcamento_id = request.data.get('orcamento_id')
        orcamento = OrcamentosVenda.objects.filter(id=orcamento_id).prefetch_related('itens').first()

        if not orcamento:
            return Response({'error': 'Orçamento não encontrado.'}, status=status.HTTP_404_NOT_FOUND)

        if orcamento.status not in ['ABERTO', 'APROVADO']:
            return Response(
                {'error': 'Somente orçamentos abertos/aprovados podem ser convertidos.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        with transaction.atomic():
            pedido = PedidosVenda.objects.create(
                cliente=orcamento.cliente,
                vendedor=orcamento.vendedor,
                orcamento=orcamento,
                data_emissao=timezone.now(),
                valor_produtos=orcamento.valor_produtos,
                desconto=orcamento.desconto,
                frete=orcamento.frete,
                impostos=orcamento.impostos,
                observacoes=orcamento.observacoes,
                status='RASCUNHO'
            )

            for item in orcamento.itens.all():
                ItensPedidoVenda.objects.create(
                    pedido=pedido,
                    produto=item.produto,
                    quantidade=item.quantidade,
                    valor_unitario=item.valor_unitario,
                    desconto=item.desconto,
                    valor_total=item.valor_total
                )

            orcamento.status = 'CONVERTIDO'
            orcamento.save()

        return Response(
            {'message': 'Orçamento convertido em pedido', 'pedido_id': pedido.id},
            status=status.HTTP_201_CREATED
        )
