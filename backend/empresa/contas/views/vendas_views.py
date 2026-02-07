from datetime import datetime, timedelta
from decimal import Decimal

from django.db import transaction
from django.db.models import Count, Sum
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


class VendasListaView(APIView):
    @staticmethod
    def _parse_date(value):
        if not value:
            return None
        try:
            return datetime.strptime(value, '%Y-%m-%d').date()
        except ValueError:
            return None

    def get(self, request, *args, **kwargs):
        data_inicio = self._parse_date(request.query_params.get('data_inicio'))
        data_fim = self._parse_date(request.query_params.get('data_fim'))
        cliente_id = request.query_params.get('cliente_id')
        status_filtro = request.query_params.get('status')

        pedidos = PedidosVenda.objects.all().select_related('cliente', 'vendedor')
        if cliente_id:
            pedidos = pedidos.filter(cliente_id=cliente_id)
        if status_filtro:
            pedidos = pedidos.filter(status=status_filtro)
        if data_inicio and data_fim:
            pedidos = pedidos.filter(data_emissao__date__gte=data_inicio, data_emissao__date__lte=data_fim)

        resultados = []
        for pedido in pedidos.order_by('-data_emissao')[:200]:
            resultados.append({
                'id': pedido.id,
                'numero_pedido': pedido.numero_pedido,
                'data_emissao': pedido.data_emissao,
                'cliente_id': pedido.cliente_id,
                'cliente_nome': getattr(pedido.cliente, 'nome', None),
                'vendedor_id': pedido.vendedor_id,
                'status': pedido.status,
                'valor_produtos': float(pedido.valor_produtos or Decimal('0.00')),
                'valor_total': float(pedido.valor_total or Decimal('0.00'))
            })

        return Response({'resultados': resultados, 'total': pedidos.count()})


class VendasResumoView(APIView):
    @staticmethod
    def _parse_date(value):
        if not value:
            return None
        try:
            return datetime.strptime(value, '%Y-%m-%d').date()
        except ValueError:
            return None

    def get(self, request, *args, **kwargs):
        data_inicio = self._parse_date(request.query_params.get('data_inicio'))
        data_fim = self._parse_date(request.query_params.get('data_fim'))
        vendedor_id = request.query_params.get('vendedor_id')

        pedidos = PedidosVenda.objects.all()
        if vendedor_id:
            pedidos = pedidos.filter(vendedor_id=vendedor_id)
        if data_inicio and data_fim:
            pedidos = pedidos.filter(data_emissao__date__gte=data_inicio, data_emissao__date__lte=data_fim)

        resumo = pedidos.aggregate(
            total_pedidos=Count('id'),
            valor_total=Sum('valor_total'),
            valor_produtos=Sum('valor_produtos')
        )
        resumo['valor_total'] = float(resumo['valor_total'] or Decimal('0.00'))
        resumo['valor_produtos'] = float(resumo['valor_produtos'] or Decimal('0.00'))

        top_clientes = list(
            pedidos.values('cliente__id', 'cliente__nome')
            .annotate(valor_total=Sum('valor_total'), total=Count('id'))
            .order_by('-valor_total')[:10]
        )
        for cliente in top_clientes:
            cliente['valor_total'] = float(cliente['valor_total'] or Decimal('0.00'))

        return Response({'resumo': resumo, 'top_clientes': top_clientes})


class VendasContaReceberBaixaView(APIView):
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
        conta_id = request.data.get('conta_id')
        data_pagamento = request.data.get('data_pagamento')
        valor_recebido = request.data.get('valor_recebido')
        juros = request.data.get('juros', '0.00')
        tarifas = request.data.get('tarifas', '0.00')
        desconto = request.data.get('desconto', '0.00')

        conta = ContasReceber.objects.filter(id=conta_id).first()
        if not conta:
            return Response({'error': 'Conta a receber não encontrada.'}, status=status.HTTP_404_NOT_FOUND)
        if conta.status in ['P', 'C']:
            return Response({'error': 'Conta já paga ou cancelada.'}, status=status.HTTP_400_BAD_REQUEST)

        if not data_pagamento or valor_recebido is None:
            return Response({'error': 'Informe data_pagamento e valor_recebido.'}, status=status.HTTP_400_BAD_REQUEST)

        conta.data_pagamento = self._parse_datetime(data_pagamento)
        conta.recebido = Decimal(str(valor_recebido))
        conta.juros = Decimal(str(juros))
        conta.tarifas = Decimal(str(tarifas))
        conta.desconto = Decimal(str(desconto))
        conta.status = 'P'
        conta.save()

        return Response({'message': 'Conta recebida com sucesso.'})


class VendasContaReceberEstornoView(APIView):
    def post(self, request, *args, **kwargs):
        conta_id = request.data.get('conta_id')
        conta = ContasReceber.objects.filter(id=conta_id).first()
        if not conta:
            return Response({'error': 'Conta a receber não encontrada.'}, status=status.HTTP_404_NOT_FOUND)
        if conta.status != 'P':
            return Response({'error': 'Apenas contas pagas podem ser estornadas.'}, status=status.HTTP_400_BAD_REQUEST)

        conta.status = 'A'
        conta.data_pagamento = None
        conta.recebido = Decimal('0.00')
        conta.juros = Decimal('0.00')
        conta.tarifas = Decimal('0.00')
        conta.desconto = Decimal('0.00')
        conta.save()

        return Response({'message': 'Estorno realizado com sucesso.'})


class VendasContaReceberAgingView(APIView):
    def get(self, request, *args, **kwargs):
        data_referencia = request.query_params.get('data_referencia')
        cliente_id = request.query_params.get('cliente_id')

        if data_referencia:
            try:
                data_ref = datetime.strptime(data_referencia, '%Y-%m-%d').date()
            except ValueError:
                return Response({'error': 'data_referencia inválida.'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            data_ref = timezone.now().date()

        contas = ContasReceber.objects.filter(status='A')
        if cliente_id:
            contas = contas.filter(cliente_id=cliente_id)

        buckets = [
            {'label': '0-30', 'inicio': 0, 'fim': 30},
            {'label': '31-60', 'inicio': 31, 'fim': 60},
            {'label': '61-90', 'inicio': 61, 'fim': 90},
            {'label': '91+', 'inicio': 91, 'fim': None},
        ]

        resposta = []
        for bucket in buckets:
            limite_inferior = data_ref - timedelta(days=bucket['inicio'])
            if bucket['fim'] is None:
                filtro = contas.filter(vencimento__date__lte=limite_inferior)
            else:
                limite_superior = data_ref - timedelta(days=bucket['fim'])
                filtro = contas.filter(vencimento__date__lte=limite_inferior, vencimento__date__gte=limite_superior)
            total = filtro.aggregate(valor_total=Sum('valor'))['valor_total'] or Decimal('0.00')
            resposta.append({'faixa': bucket['label'], 'valor_total': float(total), 'quantidade': filtro.count()})

        return Response({'data_referencia': data_ref, 'aging': resposta})


class VendasContaReceberAtrasadasView(APIView):
    def get(self, request, *args, **kwargs):
        data_referencia = request.query_params.get('data_referencia')
        cliente_id = request.query_params.get('cliente_id')

        if data_referencia:
            try:
                data_ref = datetime.strptime(data_referencia, '%Y-%m-%d').date()
            except ValueError:
                return Response({'error': 'data_referencia inválida.'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            data_ref = timezone.now().date()

        contas = ContasReceber.objects.filter(status='A', vencimento__date__lt=data_ref)
        if cliente_id:
            contas = contas.filter(cliente_id=cliente_id)

        resultados = []
        for conta in contas.select_related('cliente').order_by('vencimento'):
            dias = (data_ref - conta.vencimento.date()).days if conta.vencimento else 0
            resultados.append({
                'id': conta.id,
                'cliente_id': conta.cliente_id,
                'cliente_nome': getattr(conta.cliente, 'nome', None),
                'vencimento': conta.vencimento,
                'dias_atraso': dias,
                'valor': float(conta.valor or Decimal('0.00'))
            })

        return Response({'resultados': resultados, 'total': contas.count()})


class VendasDetalheView(APIView):
    def get(self, request, pedido_id, *args, **kwargs):
        pedido = (
            PedidosVenda.objects
            .filter(id=pedido_id)
            .select_related('cliente', 'vendedor')
            .prefetch_related('itens__produto')
            .first()
        )
        if not pedido:
            return Response({'error': 'Pedido não encontrado.'}, status=status.HTTP_404_NOT_FOUND)

        itens = []
        for item in pedido.itens.all():
            itens.append({
                'id': item.id,
                'produto_id': item.produto_id,
                'produto_nome': getattr(item.produto, 'nome', None),
                'quantidade': float(item.quantidade or Decimal('0.0000')),
                'valor_unitario': float(item.valor_unitario or Decimal('0.00')),
                'desconto': float(item.desconto or Decimal('0.00')),
                'valor_total': float(item.valor_total or Decimal('0.00')),
            })

        return Response({
            'pedido': {
                'id': pedido.id,
                'numero_pedido': pedido.numero_pedido,
                'data_emissao': pedido.data_emissao,
                'cliente_id': pedido.cliente_id,
                'cliente_nome': getattr(pedido.cliente, 'nome', None),
                'vendedor_id': pedido.vendedor_id,
                'status': pedido.status,
                'valor_produtos': float(pedido.valor_produtos or Decimal('0.00')),
                'desconto': float(pedido.desconto or Decimal('0.00')),
                'frete': float(pedido.frete or Decimal('0.00')),
                'impostos': float(pedido.impostos or Decimal('0.00')),
                'valor_total': float(pedido.valor_total or Decimal('0.00')),
                'observacoes': pedido.observacoes,
            },
            'itens': itens
        })


class VendasAtualizarView(APIView):
    def post(self, request, pedido_id, *args, **kwargs):
        payload = request.data
        itens = payload.get('itens', [])

        pedido = PedidosVenda.objects.filter(id=pedido_id).prefetch_related('itens').first()
        if not pedido:
            return Response({'error': 'Pedido não encontrado.'}, status=status.HTTP_404_NOT_FOUND)
        if pedido.status != 'RASCUNHO':
            return Response(
                {'error': 'Apenas pedidos em rascunho podem ser atualizados.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not itens:
            return Response({'error': 'Informe ao menos um item.'}, status=status.HTTP_400_BAD_REQUEST)

        with transaction.atomic():
            pedido.forma_pagamento = payload.get('forma_pagamento', pedido.forma_pagamento)
            pedido.condicoes_pagamento = payload.get('condicoes_pagamento', pedido.condicoes_pagamento)
            pedido.prazo_entrega = payload.get('prazo_entrega', pedido.prazo_entrega)
            pedido.desconto = Decimal(str(payload.get('desconto', pedido.desconto or '0.00')))
            pedido.frete = Decimal(str(payload.get('frete', pedido.frete or '0.00')))
            pedido.impostos = Decimal(str(payload.get('impostos', pedido.impostos or '0.00')))
            pedido.observacoes = payload.get('observacoes', pedido.observacoes)
            pedido.itens.all().delete()

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

        return Response({'message': 'Pedido atualizado com sucesso.'})


class VendasEstornoFaturamentoView(APIView):
    def post(self, request, *args, **kwargs):
        pedido_id = request.data.get('pedido_id')
        local_id = request.data.get('local_id')
        pedido = PedidosVenda.objects.filter(id=pedido_id).first()
        if not pedido:
            return Response({'error': 'Pedido não encontrado.'}, status=status.HTTP_404_NOT_FOUND)
        if pedido.status != 'FATURADO':
            return Response({'error': 'Apenas pedidos faturados podem ser estornados.'}, status=status.HTTP_400_BAD_REQUEST)

        numero_nota = request.data.get('numero_nota')
        if numero_nota:
            nota = NotasFiscaisSaida.objects.filter(cliente=pedido.cliente, numero_nota=numero_nota).first()
        else:
            nota = NotasFiscaisSaida.objects.filter(cliente=pedido.cliente).order_by('-data').first()
        if not nota:
            return Response({'error': 'Nota fiscal de saída não encontrada.'}, status=status.HTTP_404_NOT_FOUND)

        with transaction.atomic():
            itens_nf = ItensNfSaida.objects.filter(nota_fiscal=nota)
            for item in itens_nf:
                saldo = None
                if local_id:
                    saldo = SaldosEstoque.objects.filter(produto=item.produto, local_id=local_id).first()
                custo_unitario = saldo.custo_medio if saldo else item.valor_unitario

                _atualizar_saldo_estoque(
                    produto_id=item.produto_id,
                    local_id=local_id,
                    delta_quantidade=item.quantidade,
                    custo_unitario=custo_unitario,
                    data_movimentacao=timezone.now()
                )

            MovimentacoesEstoque.objects.filter(nota_fiscal_saida=nota).delete()
            itens_nf.delete()
            ContasReceber.objects.filter(documento=nota.numero_nota).delete()
            nota.delete()

            pedido.status = 'APROVADO'
            pedido.data_faturamento = None
            pedido.save()

        return Response({'message': 'Faturamento estornado com sucesso.'})


class VendasDevolucaoView(APIView):
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
        nota_id = payload.get('nota_id')
        itens = payload.get('itens', [])
        local_id = payload.get('local_id')
        data_movimentacao = self._parse_datetime(payload.get('data_movimentacao')) or timezone.now()
        tipo_movimentacao_id = payload.get('tipo_movimentacao_id')

        if not nota_id or not itens:
            return Response(
                {'error': 'Informe nota_id e itens.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        nota = NotasFiscaisSaida.objects.filter(id=nota_id).first()
        if not nota:
            return Response({'error': 'Nota fiscal de saída não encontrada.'}, status=status.HTTP_404_NOT_FOUND)

        tipo_movimentacao = None
        if tipo_movimentacao_id:
            tipo_movimentacao = TiposMovimentacaoEstoque.objects.filter(id=tipo_movimentacao_id).first()
        if not tipo_movimentacao:
            tipo_movimentacao = TiposMovimentacaoEstoque.objects.filter(tipo='E', ativo=True).first()

        itens_nf = ItensNfSaida.objects.filter(nota_fiscal=nota)
        itens_por_produto = {item.produto_id: item for item in itens_nf}

        devolvidos = (
            MovimentacoesEstoque.objects
            .filter(nota_fiscal_saida=nota, documento_referencia__startswith='DEVOLUCAO')
            .values('produto_id')
            .annotate(quantidade_total=Sum('quantidade'))
        )
        devolvido_map = {row['produto_id']: row['quantidade_total'] or Decimal('0.0000') for row in devolvidos}

        movimentos_criados = []

        with transaction.atomic():
            for item in itens:
                produto_id = item.get('produto_id')
                quantidade = Decimal(str(item.get('quantidade', '0.0000')))
                if not produto_id or quantidade <= 0:
                    return Response({'error': 'Itens inválidos.'}, status=status.HTTP_400_BAD_REQUEST)
                if produto_id not in itens_por_produto:
                    return Response({'error': f'Produto {produto_id} não pertence à nota.'}, status=status.HTTP_400_BAD_REQUEST)

                quantidade_vendida = itens_por_produto[produto_id].quantidade or Decimal('0.0000')
                quantidade_devolvida = devolvido_map.get(produto_id, Decimal('0.0000'))
                disponivel = quantidade_vendida - quantidade_devolvida
                if quantidade > disponivel:
                    return Response(
                        {'error': f'Quantidade acima do disponível para devolução do produto {produto_id}.'},
                        status=status.HTTP_400_BAD_REQUEST
                    )

                saldo = None
                if local_id:
                    saldo = SaldosEstoque.objects.filter(produto_id=produto_id, local_id=local_id).first()
                custo_unitario = saldo.custo_medio if saldo else itens_por_produto[produto_id].valor_unitario

                movimento = MovimentacoesEstoque.objects.create(
                    data_movimentacao=data_movimentacao,
                    tipo_movimentacao=tipo_movimentacao,
                    produto_id=produto_id,
                    local_destino_id=local_id,
                    quantidade=quantidade,
                    custo_unitario=custo_unitario,
                    valor_total=quantidade * (custo_unitario or Decimal('0.00')),
                    nota_fiscal_saida=nota,
                    documento_referencia=f'DEVOLUCAO {nota.numero_nota}'
                )
                movimentos_criados.append(movimento.id)

                _atualizar_saldo_estoque(
                    produto_id=produto_id,
                    local_id=local_id,
                    delta_quantidade=quantidade,
                    custo_unitario=custo_unitario,
                    data_movimentacao=data_movimentacao
                )

        return Response({'message': 'Devolução registrada com sucesso.', 'movimentos': movimentos_criados})


class VendasDevolucaoListaView(APIView):
    @staticmethod
    def _parse_date(value):
        if not value:
            return None
        try:
            return datetime.strptime(value, '%Y-%m-%d').date()
        except ValueError:
            return None

    def get(self, request, *args, **kwargs):
        nota_id = request.query_params.get('nota_id')
        produto_id = request.query_params.get('produto_id')
        data_inicio = self._parse_date(request.query_params.get('data_inicio'))
        data_fim = self._parse_date(request.query_params.get('data_fim'))

        movimentos = MovimentacoesEstoque.objects.filter(documento_referencia__startswith='DEVOLUCAO')
        if nota_id:
            movimentos = movimentos.filter(nota_fiscal_saida_id=nota_id)
        if produto_id:
            movimentos = movimentos.filter(produto_id=produto_id)
        if data_inicio and data_fim:
            movimentos = movimentos.filter(
                data_movimentacao__date__gte=data_inicio,
                data_movimentacao__date__lte=data_fim
            )

        resultados = []
        for mov in movimentos.select_related('produto', 'nota_fiscal_saida').order_by('-data_movimentacao')[:200]:
            resultados.append({
                'id': mov.id,
                'nota_id': mov.nota_fiscal_saida_id,
                'numero_nota': mov.nota_fiscal_saida.numero_nota if mov.nota_fiscal_saida else None,
                'produto_id': mov.produto_id,
                'produto_nome': getattr(mov.produto, 'nome', None),
                'data_movimentacao': mov.data_movimentacao,
                'quantidade': float(mov.quantidade or Decimal('0.0000')),
                'custo_unitario': float(mov.custo_unitario or Decimal('0.0000')),
            })

        return Response({'resultados': resultados, 'total': movimentos.count()})


class VendasDevolucaoCancelarView(APIView):
    def post(self, request, *args, **kwargs):
        movimento_id = request.data.get('movimento_id')
        local_id = request.data.get('local_id')

        movimento = MovimentacoesEstoque.objects.filter(id=movimento_id, documento_referencia__startswith='DEVOLUCAO').first()
        if not movimento:
            return Response({'error': 'Movimento de devolução não encontrado.'}, status=status.HTTP_404_NOT_FOUND)

        with transaction.atomic():
            _atualizar_saldo_estoque(
                produto_id=movimento.produto_id,
                local_id=local_id,
                delta_quantidade=-movimento.quantidade,
                custo_unitario=movimento.custo_unitario,
                data_movimentacao=timezone.now()
            )
            movimento.delete()

        return Response({'message': 'Devolução cancelada com sucesso.'})


class VendasDevolucaoSaldoView(APIView):
    def get(self, request, nota_id, *args, **kwargs):
        nota = NotasFiscaisSaida.objects.filter(id=nota_id).first()
        if not nota:
            return Response({'error': 'Nota fiscal de saída não encontrada.'}, status=status.HTTP_404_NOT_FOUND)

        itens_nf = ItensNfSaida.objects.filter(nota_fiscal=nota)
        devolvidos = (
            MovimentacoesEstoque.objects
            .filter(nota_fiscal_saida=nota, documento_referencia__startswith='DEVOLUCAO')
            .values('produto_id')
            .annotate(quantidade_total=Sum('quantidade'))
        )
        devolvido_map = {row['produto_id']: row['quantidade_total'] or Decimal('0.0000') for row in devolvidos}

        saldo_itens = []
        for item in itens_nf:
            devolvido = devolvido_map.get(item.produto_id, Decimal('0.0000'))
            saldo_itens.append({
                'produto_id': item.produto_id,
                'produto_nome': getattr(item.produto, 'nome', None),
                'quantidade_vendida': float(item.quantidade or Decimal('0.0000')),
                'quantidade_devolvida': float(devolvido),
                'quantidade_disponivel': float((item.quantidade or Decimal('0.0000')) - devolvido)
            })

        return Response({'nota_id': nota_id, 'saldos': saldo_itens})
