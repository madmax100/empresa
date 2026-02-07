from datetime import datetime, timedelta
from decimal import Decimal

from django.db import transaction
from django.db.models import Count, Sum
from django.utils import timezone
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from ..models.access import (
    ContasPagar,
    ItensNfEntrada,
    MovimentacoesEstoque,
    NotasFiscaisEntrada,
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


class ComprasResumoView(APIView):
    """Resumo de compras (NF de entrada, itens e contas a pagar)."""

    @staticmethod
    def _to_float(value):
        return float(value or Decimal('0.00'))

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
        fornecedor_id = request.query_params.get('fornecedor_id')

        if (data_inicio and not data_fim) or (data_fim and not data_inicio):
            return Response(
                {'error': 'Informe data_inicio e data_fim no formato YYYY-MM-DD.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if data_inicio and data_fim and data_inicio > data_fim:
            return Response(
                {'error': 'A data_inicio não pode ser maior que data_fim.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        notas = NotasFiscaisEntrada.objects.all().select_related('fornecedor')

        if fornecedor_id:
            notas = notas.filter(fornecedor_id=fornecedor_id)

        if data_inicio and data_fim:
            notas = notas.filter(
                data_emissao__date__gte=data_inicio,
                data_emissao__date__lte=data_fim
            )

        totais_notas = notas.aggregate(
            quantidade_notas=Count('id'),
            valor_total=Sum('valor_total'),
            valor_produtos=Sum('valor_produtos'),
            valor_frete=Sum('valor_frete'),
            valor_ipi=Sum('valor_ipi'),
            valor_icms=Sum('valor_icms'),
            valor_desconto=Sum('valor_desconto')
        )

        itens = ItensNfEntrada.objects.filter(nota_fiscal__in=notas).select_related('produto')
        totais_itens = itens.aggregate(
            quantidade_itens=Sum('quantidade'),
            valor_total_itens=Sum('valor_total')
        )

        top_fornecedores = list(
            notas.values('fornecedor__id', 'fornecedor__nome')
            .annotate(
                valor_total=Sum('valor_total'),
                quantidade_notas=Count('id')
            )
            .order_by('-valor_total')[:10]
        )

        for fornecedor in top_fornecedores:
            fornecedor['valor_total'] = self._to_float(fornecedor['valor_total'])

        top_produtos = list(
            itens.values('produto__id', 'produto__nome', 'produto__codigo')
            .annotate(
                quantidade=Sum('quantidade'),
                valor_total=Sum('valor_total')
            )
            .order_by('-valor_total')[:10]
        )

        for produto in top_produtos:
            produto['quantidade'] = self._to_float(produto['quantidade'])
            produto['valor_total'] = self._to_float(produto['valor_total'])

        contas_pagar = ContasPagar.objects.all()
        if fornecedor_id:
            contas_pagar = contas_pagar.filter(fornecedor_id=fornecedor_id)

        if data_inicio and data_fim:
            contas_pagar = contas_pagar.filter(
                data__date__gte=data_inicio,
                data__date__lte=data_fim
            )

        contas_resumo = contas_pagar.values('status').annotate(
            quantidade=Count('id'),
            valor_total=Sum('valor')
        )

        contas_status = {
            'A': {'status': 'Aberto', 'quantidade': 0, 'valor_total': 0.0},
            'P': {'status': 'Pago', 'quantidade': 0, 'valor_total': 0.0},
            'C': {'status': 'Cancelado', 'quantidade': 0, 'valor_total': 0.0}
        }

        for item in contas_resumo:
            status_key = item['status']
            if status_key in contas_status:
                contas_status[status_key]['quantidade'] = item['quantidade']
                contas_status[status_key]['valor_total'] = self._to_float(item['valor_total'])

        response = {
            'filtros': {
                'data_inicio': data_inicio.isoformat() if data_inicio else None,
                'data_fim': data_fim.isoformat() if data_fim else None,
                'fornecedor_id': fornecedor_id
            },
            'resumo_notas': {
                'quantidade_notas': totais_notas['quantidade_notas'] or 0,
                'valor_total': self._to_float(totais_notas['valor_total']),
                'valor_produtos': self._to_float(totais_notas['valor_produtos']),
                'valor_frete': self._to_float(totais_notas['valor_frete']),
                'valor_ipi': self._to_float(totais_notas['valor_ipi']),
                'valor_icms': self._to_float(totais_notas['valor_icms']),
                'valor_desconto': self._to_float(totais_notas['valor_desconto'])
            },
            'resumo_itens': {
                'quantidade_itens': self._to_float(totais_itens['quantidade_itens']),
                'valor_total_itens': self._to_float(totais_itens['valor_total_itens'])
            },
            'top_fornecedores': top_fornecedores,
            'top_produtos': top_produtos,
            'contas_pagar_status': list(contas_status.values())
        }

        return Response(response, status=status.HTTP_200_OK)


class ComprasCadastroView(APIView):
    """Cadastro de compras (NF de entrada + itens)."""

    @staticmethod
    def _decimal(value, default='0.00'):
        if value is None or value == '':
            return Decimal(default)
        return Decimal(str(value))

    def post(self, request, *args, **kwargs):
        payload = request.data or {}
        nota_data = payload.get('nota') or {}
        itens_data = payload.get('itens') or []

        if not nota_data:
            return Response(
                {'error': 'Informe os dados da nota em nota.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not itens_data:
            return Response(
                {'error': 'Informe ao menos um item em itens.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        numero_nota = nota_data.get('numero_nota')
        fornecedor_id = nota_data.get('fornecedor_id')
        data_emissao = nota_data.get('data_emissao')

        if not numero_nota or not fornecedor_id or not data_emissao:
            return Response(
                {'error': 'numero_nota, fornecedor_id e data_emissao são obrigatórios.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        for item in itens_data:
            if not item.get('produto_id'):
                return Response(
                    {'error': 'Cada item deve possuir produto_id.'},
                    status=status.HTTP_400_BAD_REQUEST
                )

        estoque_data = payload.get('estoque') or {}
        tipo_movimentacao_id = estoque_data.get('tipo_movimentacao_id')
        tipo_movimentacao = None

        if tipo_movimentacao_id:
            tipo_movimentacao = (
                TiposMovimentacaoEstoque.objects.filter(id=tipo_movimentacao_id, ativo=True)
                .first()
            )
        else:
            tipo_movimentacao = (
                TiposMovimentacaoEstoque.objects.filter(tipo='E', ativo=True).first()
            )

        if not tipo_movimentacao:
            return Response(
                {'error': 'Tipo de movimentação de entrada não encontrado.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        with transaction.atomic():
            nota = NotasFiscaisEntrada.objects.create(
                numero_nota=numero_nota,
                serie_nota=nota_data.get('serie_nota'),
                fornecedor_id=fornecedor_id,
                Produto_id=nota_data.get('Produto_id'),
                frete_id=nota_data.get('frete_id'),
                tipo_frete=nota_data.get('tipo_frete'),
                data_emissao=nota_data.get('data_emissao'),
                data_entrada=nota_data.get('data_entrada'),
                valor_produtos=self._decimal(nota_data.get('valor_produtos')),
                base_calculo_icms=self._decimal(nota_data.get('base_calculo_icms')),
                valor_icms=self._decimal(nota_data.get('valor_icms')),
                valor_ipi=self._decimal(nota_data.get('valor_ipi')),
                valor_icms_st=self._decimal(nota_data.get('valor_icms_st')),
                base_calculo_st=self._decimal(nota_data.get('base_calculo_st')),
                valor_desconto=self._decimal(nota_data.get('valor_desconto')),
                valor_frete=self._decimal(nota_data.get('valor_frete')),
                outras_despesas=self._decimal(nota_data.get('outras_despesas')),
                outros_encargos=self._decimal(nota_data.get('outros_encargos')),
                valor_total=self._decimal(nota_data.get('valor_total')),
                chave_nfe=nota_data.get('chave_nfe'),
                protocolo=nota_data.get('protocolo'),
                natureza_operacao=nota_data.get('natureza_operacao'),
                cfop=nota_data.get('cfop'),
                forma_pagamento=nota_data.get('forma_pagamento'),
                condicoes_pagamento=nota_data.get('condicoes_pagamento'),
                parcelas=nota_data.get('parcelas'),
                operacao=nota_data.get('operacao'),
                comprador=nota_data.get('comprador'),
                operador=nota_data.get('operador'),
                observacao=nota_data.get('observacao')
            )

            total_produtos = Decimal('0.00')
            total_itens = Decimal('0.00')

            for item in itens_data:
                produto_id = item.get('produto_id')
                quantidade = self._decimal(item.get('quantidade'), default='0.0000')
                valor_unitario = self._decimal(item.get('valor_unitario'))
                valor_total = self._decimal(item.get('valor_total'))

                if valor_total == Decimal('0.00'):
                    valor_total = quantidade * valor_unitario

                ItensNfEntrada.objects.create(
                    nota_fiscal=nota,
                    data=item.get('data'),
                    produto_id=produto_id,
                    quantidade=quantidade,
                    valor_unitario=valor_unitario,
                    valor_total=valor_total,
                    percentual_ipi=self._decimal(item.get('percentual_ipi')),
                    status=item.get('status'),
                    aliquota=self._decimal(item.get('aliquota')),
                    desconto=self._decimal(item.get('desconto')),
                    cfop=item.get('cfop'),
                    base_substituicao=self._decimal(item.get('base_substituicao')),
                    icms_substituicao=self._decimal(item.get('icms_substituicao')),
                    outras_despesas=self._decimal(item.get('outras_despesas')),
                    frete=self._decimal(item.get('frete')),
                    aliquota_substituicao=self._decimal(item.get('aliquota_substituicao')),
                    ncm=item.get('ncm'),
                    controle=item.get('controle')
                )

                total_produtos += valor_total
                total_itens += quantidade

            if nota.valor_produtos == Decimal('0.00'):
                nota.valor_produtos = total_produtos
            if nota.valor_total == Decimal('0.00'):
                nota.valor_total = total_produtos + nota.valor_frete + nota.valor_ipi + nota.valor_icms_st + nota.outras_despesas + nota.outros_encargos - nota.valor_desconto

            nota.save()

            data_movimentacao = nota.data_entrada or nota.data_emissao or timezone.now()
            local_destino_id = estoque_data.get('local_destino_id')

            for item in nota.itens.all():
                quantidade_item = item.quantidade or Decimal('0.0000')
                MovimentacoesEstoque.objects.create(
                    data_movimentacao=data_movimentacao,
                    tipo_movimentacao=tipo_movimentacao,
                    produto=item.produto,
                    lote_id=None,
                    local_origem_id=None,
                    local_destino_id=local_destino_id,
                    quantidade=quantidade_item,
                    custo_unitario=item.valor_unitario,
                    valor_total=item.valor_total,
                    nota_fiscal_entrada=nota,
                    observacoes='Entrada automática via compras',
                    documento_referencia=str(nota.numero_nota)
                )

                _atualizar_saldo_estoque(
                    produto_id=item.produto_id,
                    local_id=local_destino_id,
                    delta_quantidade=quantidade_item,
                    custo_unitario=item.valor_unitario,
                    data_movimentacao=data_movimentacao
                )

        return Response(
            {
                'id': nota.id,
                'numero_nota': nota.numero_nota,
                'fornecedor_id': nota.fornecedor_id,
                'valor_total': float(nota.valor_total or 0),
                'quantidade_itens': float(total_itens)
            },
            status=status.HTTP_201_CREATED
        )


class ComprasAtualizarView(APIView):
    """Atualiza uma compra (NF de entrada + itens)."""

    @staticmethod
    def _decimal(value, default='0.00'):
        if value is None or value == '':
            return Decimal(default)
        return Decimal(str(value))

    def put(self, request, nota_id, *args, **kwargs):
        payload = request.data or {}
        nota_data = payload.get('nota') or {}
        itens_data = payload.get('itens') or []

        if not nota_data:
            return Response(
                {'error': 'Informe os dados da nota em nota.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not itens_data:
            return Response(
                {'error': 'Informe ao menos um item em itens.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            nota = NotasFiscaisEntrada.objects.get(id=nota_id)
        except NotasFiscaisEntrada.DoesNotExist:
            return Response(
                {'error': 'Nota fiscal de entrada não encontrada.'},
                status=status.HTTP_404_NOT_FOUND
            )

        numero_nota = nota_data.get('numero_nota')
        fornecedor_id = nota_data.get('fornecedor_id')
        data_emissao = nota_data.get('data_emissao')

        if not numero_nota or not fornecedor_id or not data_emissao:
            return Response(
                {'error': 'numero_nota, fornecedor_id e data_emissao são obrigatórios.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        for item in itens_data:
            if not item.get('produto_id'):
                return Response(
                    {'error': 'Cada item deve possuir produto_id.'},
                    status=status.HTTP_400_BAD_REQUEST
                )

        estoque_data = payload.get('estoque') or {}
        tipo_movimentacao_id = estoque_data.get('tipo_movimentacao_id')
        tipo_movimentacao = None

        if tipo_movimentacao_id:
            tipo_movimentacao = (
                TiposMovimentacaoEstoque.objects.filter(id=tipo_movimentacao_id, ativo=True)
                .first()
            )
        else:
            tipo_movimentacao = (
                TiposMovimentacaoEstoque.objects.filter(tipo='E', ativo=True).first()
            )

        if not tipo_movimentacao:
            return Response(
                {'error': 'Tipo de movimentação de entrada não encontrado.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        with transaction.atomic():
            nota.numero_nota = numero_nota
            nota.serie_nota = nota_data.get('serie_nota')
            nota.fornecedor_id = fornecedor_id
            nota.Produto_id = nota_data.get('Produto_id')
            nota.frete_id = nota_data.get('frete_id')
            nota.tipo_frete = nota_data.get('tipo_frete')
            nota.data_emissao = nota_data.get('data_emissao')
            nota.data_entrada = nota_data.get('data_entrada')
            nota.valor_produtos = self._decimal(nota_data.get('valor_produtos'))
            nota.base_calculo_icms = self._decimal(nota_data.get('base_calculo_icms'))
            nota.valor_icms = self._decimal(nota_data.get('valor_icms'))
            nota.valor_ipi = self._decimal(nota_data.get('valor_ipi'))
            nota.valor_icms_st = self._decimal(nota_data.get('valor_icms_st'))
            nota.base_calculo_st = self._decimal(nota_data.get('base_calculo_st'))
            nota.valor_desconto = self._decimal(nota_data.get('valor_desconto'))
            nota.valor_frete = self._decimal(nota_data.get('valor_frete'))
            nota.outras_despesas = self._decimal(nota_data.get('outras_despesas'))
            nota.outros_encargos = self._decimal(nota_data.get('outros_encargos'))
            nota.valor_total = self._decimal(nota_data.get('valor_total'))
            nota.chave_nfe = nota_data.get('chave_nfe')
            nota.protocolo = nota_data.get('protocolo')
            nota.natureza_operacao = nota_data.get('natureza_operacao')
            nota.cfop = nota_data.get('cfop')
            nota.forma_pagamento = nota_data.get('forma_pagamento')
            nota.condicoes_pagamento = nota_data.get('condicoes_pagamento')
            nota.parcelas = nota_data.get('parcelas')
            nota.operacao = nota_data.get('operacao')
            nota.comprador = nota_data.get('comprador')
            nota.operador = nota_data.get('operador')
            nota.observacao = nota_data.get('observacao')

            nota.itens.all().delete()

            total_produtos = Decimal('0.00')
            total_itens = Decimal('0.00')

            for item in itens_data:
                produto_id = item.get('produto_id')
                quantidade = self._decimal(item.get('quantidade'), default='0.0000')
                valor_unitario = self._decimal(item.get('valor_unitario'))
                valor_total = self._decimal(item.get('valor_total'))

                if valor_total == Decimal('0.00'):
                    valor_total = quantidade * valor_unitario

                ItensNfEntrada.objects.create(
                    nota_fiscal=nota,
                    data=item.get('data'),
                    produto_id=produto_id,
                    quantidade=quantidade,
                    valor_unitario=valor_unitario,
                    valor_total=valor_total,
                    percentual_ipi=self._decimal(item.get('percentual_ipi')),
                    status=item.get('status'),
                    aliquota=self._decimal(item.get('aliquota')),
                    desconto=self._decimal(item.get('desconto')),
                    cfop=item.get('cfop'),
                    base_substituicao=self._decimal(item.get('base_substituicao')),
                    icms_substituicao=self._decimal(item.get('icms_substituicao')),
                    outras_despesas=self._decimal(item.get('outras_despesas')),
                    frete=self._decimal(item.get('frete')),
                    aliquota_substituicao=self._decimal(item.get('aliquota_substituicao')),
                    ncm=item.get('ncm'),
                    controle=item.get('controle')
                )

                total_produtos += valor_total
                total_itens += quantidade

            if nota.valor_produtos == Decimal('0.00'):
                nota.valor_produtos = total_produtos
            if nota.valor_total == Decimal('0.00'):
                nota.valor_total = (
                    total_produtos
                    + nota.valor_frete
                    + nota.valor_ipi
                    + nota.valor_icms_st
                    + nota.outras_despesas
                    + nota.outros_encargos
                    - nota.valor_desconto
                )

            nota.save()

            movimentos_anteriores = list(
                MovimentacoesEstoque.objects.filter(nota_fiscal_entrada=nota)
            )

            for movimento in movimentos_anteriores:
                _atualizar_saldo_estoque(
                    produto_id=movimento.produto_id,
                    local_id=movimento.local_destino_id,
                    delta_quantidade=-(movimento.quantidade or Decimal('0.0000')),
                    custo_unitario=movimento.custo_unitario,
                    data_movimentacao=movimento.data_movimentacao
                )

            MovimentacoesEstoque.objects.filter(nota_fiscal_entrada=nota).delete()

            data_movimentacao = nota.data_entrada or nota.data_emissao or timezone.now()
            local_destino_id = estoque_data.get('local_destino_id')

            for item in nota.itens.all():
                quantidade_item = item.quantidade or Decimal('0.0000')
                MovimentacoesEstoque.objects.create(
                    data_movimentacao=data_movimentacao,
                    tipo_movimentacao=tipo_movimentacao,
                    produto=item.produto,
                    lote_id=None,
                    local_origem_id=None,
                    local_destino_id=local_destino_id,
                    quantidade=quantidade_item,
                    custo_unitario=item.valor_unitario,
                    valor_total=item.valor_total,
                    nota_fiscal_entrada=nota,
                    observacoes='Atualização automática via compras',
                    documento_referencia=str(nota.numero_nota)
                )

                _atualizar_saldo_estoque(
                    produto_id=item.produto_id,
                    local_id=local_destino_id,
                    delta_quantidade=quantidade_item,
                    custo_unitario=item.valor_unitario,
                    data_movimentacao=data_movimentacao
                )

        return Response(
            {
                'id': nota.id,
                'numero_nota': nota.numero_nota,
                'fornecedor_id': nota.fornecedor_id,
                'valor_total': float(nota.valor_total or 0),
                'quantidade_itens': float(total_itens)
            },
            status=status.HTTP_200_OK
        )


class ComprasContaPagarView(APIView):
    """Gera uma conta a pagar vinculada à nota fiscal de entrada."""

    @staticmethod
    def _decimal(value, default='0.00'):
        if value is None or value == '':
            return Decimal(default)
        return Decimal(str(value))

    @staticmethod
    def _to_float(value):
        return float(value or Decimal('0.00'))

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
        fornecedor_id = request.query_params.get('fornecedor_id')
        status_param = request.query_params.get('status')

        if (data_inicio and not data_fim) or (data_fim and not data_inicio):
            return Response(
                {'error': 'Informe data_inicio e data_fim no formato YYYY-MM-DD.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if data_inicio and data_fim and data_inicio > data_fim:
            return Response(
                {'error': 'A data_inicio não pode ser maior que data_fim.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        contas = ContasPagar.objects.select_related('fornecedor', 'conta')

        if fornecedor_id:
            contas = contas.filter(fornecedor_id=fornecedor_id)

        if status_param:
            contas = contas.filter(status=status_param)

        if data_inicio and data_fim:
            contas = contas.filter(
                vencimento__date__gte=data_inicio,
                vencimento__date__lte=data_fim
            )

        contas = contas.order_by('-vencimento')[:200]

        response = [
            {
                'id': conta.id,
                'fornecedor_id': conta.fornecedor_id,
                'fornecedor_nome': conta.fornecedor.nome if conta.fornecedor else None,
                'data_emissao': conta.data,
                'vencimento': conta.vencimento,
                'valor': self._to_float(conta.valor),
                'valor_pago': self._to_float(conta.valor_pago),
                'valor_total_pago': self._to_float(conta.valor_total_pago),
                'forma_pagamento': conta.forma_pagamento,
                'numero_duplicata': conta.numero_duplicata,
                'status': conta.status
            }
            for conta in contas
        ]

        return Response(response, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        payload = request.data or {}
        nota_id = payload.get('nota_id')
        vencimento = payload.get('vencimento')

        if not nota_id or not vencimento:
            return Response(
                {'error': 'nota_id e vencimento são obrigatórios.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            nota = NotasFiscaisEntrada.objects.select_related('fornecedor').get(id=nota_id)
        except NotasFiscaisEntrada.DoesNotExist:
            return Response(
                {'error': 'Nota fiscal de entrada não encontrada.'},
                status=status.HTTP_404_NOT_FOUND
            )

        valor = self._decimal(payload.get('valor'), default=str(nota.valor_total or Decimal('0.00')))
        data_emissao = payload.get('data_emissao') or nota.data_emissao
        historico = payload.get('historico') or f'NF Entrada {nota.numero_nota}'

        with transaction.atomic():
            conta = ContasPagar.objects.create(
                data=data_emissao,
                vencimento=vencimento,
                valor=valor,
                fornecedor=nota.fornecedor,
                historico=historico,
                forma_pagamento=payload.get('forma_pagamento'),
                condicoes=payload.get('condicoes'),
                numero_duplicata=payload.get('numero_duplicata'),
                status=payload.get('status') or 'A',
                conta_id=payload.get('conta_id')
            )

        return Response(
            {
                'id': conta.id,
                'nota_id': nota.id,
                'fornecedor_id': conta.fornecedor_id,
                'valor': float(conta.valor or 0),
                'vencimento': conta.vencimento,
                'status': conta.status
            },
            status=status.HTTP_201_CREATED
        )


class ComprasDevolucaoView(APIView):
    """Registra devolução de itens de uma compra."""

    @staticmethod
    def _decimal(value, default='0.000'):
        if value is None or value == '':
            return Decimal(default)
        return Decimal(str(value))

    def post(self, request, *args, **kwargs):
        payload = request.data or {}
        nota_id = payload.get('nota_id')
        itens_data = payload.get('itens') or []
        estoque_data = payload.get('estoque') or {}

        if not nota_id:
            return Response(
                {'error': 'Informe o nota_id da compra.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not itens_data:
            return Response(
                {'error': 'Informe ao menos um item em itens.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            nota = NotasFiscaisEntrada.objects.get(id=nota_id)
        except NotasFiscaisEntrada.DoesNotExist:
            return Response(
                {'error': 'Nota fiscal de entrada não encontrada.'},
                status=status.HTTP_404_NOT_FOUND
            )

        local_origem_id = estoque_data.get('local_origem_id')
        if not local_origem_id:
            return Response(
                {'error': 'Informe local_origem_id em estoque.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        tipo_movimentacao_id = estoque_data.get('tipo_movimentacao_id')
        if tipo_movimentacao_id:
            tipo_movimentacao = (
                TiposMovimentacaoEstoque.objects.filter(id=tipo_movimentacao_id, ativo=True)
                .first()
            )
        else:
            tipo_movimentacao = (
                TiposMovimentacaoEstoque.objects.filter(tipo='S', ativo=True).first()
            )

        if not tipo_movimentacao:
            return Response(
                {'error': 'Tipo de movimentação de saída não encontrado.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        itens_nota = list(nota.itens.all())
        if not itens_nota:
            return Response(
                {'error': 'Nota fiscal sem itens cadastrados.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        resumo_itens = {}
        for item in itens_nota:
            resumo = resumo_itens.setdefault(
                item.produto_id,
                {'quantidade': Decimal('0.000'), 'valor': Decimal('0.00')}
            )
            resumo['quantidade'] += item.quantidade or Decimal('0.000')
            resumo['valor'] += item.valor_total or Decimal('0.00')

        devolucoes = MovimentacoesEstoque.objects.filter(
            nota_fiscal_entrada=nota,
            tipo_movimentacao__tipo='S'
        ).values('produto_id').annotate(quantidade=Sum('quantidade'))

        devolvido_por_produto = {item['produto_id']: item['quantidade'] for item in devolucoes}

        data_movimentacao = estoque_data.get('data_movimentacao') or timezone.now()

        movimentos_criados = []
        with transaction.atomic():
            for item in itens_data:
                produto_id = item.get('produto_id')
                quantidade = self._decimal(item.get('quantidade'), default='0.000')

                if not produto_id:
                    return Response(
                        {'error': 'Cada item deve possuir produto_id.'},
                        status=status.HTTP_400_BAD_REQUEST
                    )

                if quantidade <= 0:
                    return Response(
                        {'error': 'A quantidade devolvida deve ser maior que zero.'},
                        status=status.HTTP_400_BAD_REQUEST
                    )

                if produto_id not in resumo_itens:
                    return Response(
                        {'error': f'Produto {produto_id} não pertence à nota informada.'},
                        status=status.HTTP_400_BAD_REQUEST
                    )

                quantidade_comprada = resumo_itens[produto_id]['quantidade']
                quantidade_devolvida = devolvido_por_produto.get(produto_id, Decimal('0.000'))
                quantidade_disponivel = quantidade_comprada - quantidade_devolvida

                if quantidade > quantidade_disponivel:
                    return Response(
                        {'error': f'Quantidade devolvida maior que o disponível para o produto {produto_id}.'},
                        status=status.HTTP_400_BAD_REQUEST
                    )

                valor_total = resumo_itens[produto_id]['valor']
                custo_unitario = (
                    (valor_total / quantidade_comprada)
                    if quantidade_comprada > 0 else None
                )

                movimento = MovimentacoesEstoque.objects.create(
                    data_movimentacao=data_movimentacao,
                    tipo_movimentacao=tipo_movimentacao,
                    produto_id=produto_id,
                    lote_id=None,
                    local_origem_id=local_origem_id,
                    local_destino_id=None,
                    quantidade=quantidade,
                    custo_unitario=custo_unitario,
                    valor_total=(quantidade * custo_unitario) if custo_unitario is not None else None,
                    nota_fiscal_entrada=nota,
                    observacoes='Devolução de compra',
                    documento_referencia=str(nota.numero_nota)
                )

                _atualizar_saldo_estoque(
                    produto_id=produto_id,
                    local_id=local_origem_id,
                    delta_quantidade=-quantidade,
                    custo_unitario=custo_unitario,
                    data_movimentacao=data_movimentacao
                )

                movimentos_criados.append(movimento.id)

        return Response(
            {
                'nota_id': nota.id,
                'movimentos_criados': movimentos_criados,
                'total_itens': len(movimentos_criados)
            },
            status=status.HTTP_201_CREATED
        )


class ComprasDevolucaoListaView(APIView):
    """Lista devoluções de compra registradas no estoque."""

    @staticmethod
    def _to_float(value):
        return float(value or Decimal('0.00'))

    def get(self, request, *args, **kwargs):
        nota_id = request.query_params.get('nota_id')
        produto_id = request.query_params.get('produto_id')
        data_inicio = request.query_params.get('data_inicio')
        data_fim = request.query_params.get('data_fim')

        movimentos = MovimentacoesEstoque.objects.filter(
            nota_fiscal_entrada__isnull=False,
            tipo_movimentacao__tipo='S'
        ).select_related('produto', 'nota_fiscal_entrada', 'tipo_movimentacao')

        if nota_id:
            movimentos = movimentos.filter(nota_fiscal_entrada_id=nota_id)

        if produto_id:
            movimentos = movimentos.filter(produto_id=produto_id)

        if data_inicio and data_fim:
            try:
                data_inicio = datetime.strptime(data_inicio, '%Y-%m-%d').date()
                data_fim = datetime.strptime(data_fim, '%Y-%m-%d').date()
            except ValueError:
                return Response(
                    {'error': 'Informe data_inicio e data_fim no formato YYYY-MM-DD.'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            if data_inicio > data_fim:
                return Response(
                    {'error': 'A data_inicio não pode ser maior que data_fim.'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            movimentos = movimentos.filter(
                data_movimentacao__date__gte=data_inicio,
                data_movimentacao__date__lte=data_fim
            )
        elif data_inicio or data_fim:
            return Response(
                {'error': 'Informe data_inicio e data_fim no formato YYYY-MM-DD.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        movimentos = movimentos.order_by('-data_movimentacao')[:200]

        response = [
            {
                'movimento_id': movimento.id,
                'nota_id': movimento.nota_fiscal_entrada_id,
                'numero_nota': (
                    movimento.nota_fiscal_entrada.numero_nota
                    if movimento.nota_fiscal_entrada else None
                ),
                'produto_id': movimento.produto_id,
                'produto_nome': movimento.produto.nome if movimento.produto else None,
                'data_movimentacao': movimento.data_movimentacao,
                'quantidade': self._to_float(movimento.quantidade),
                'custo_unitario': self._to_float(movimento.custo_unitario),
                'valor_total': self._to_float(movimento.valor_total),
                'tipo_movimentacao': movimento.tipo_movimentacao.descricao if movimento.tipo_movimentacao else None,
                'observacoes': movimento.observacoes
            }
            for movimento in movimentos
        ]

        return Response(response, status=status.HTTP_200_OK)


class ComprasCancelarDevolucaoView(APIView):
    """Cancela uma devolução de compra e estorna o saldo de estoque."""

    def post(self, request, *args, **kwargs):
        payload = request.data or {}
        movimento_id = payload.get('movimento_id')

        if not movimento_id:
            return Response(
                {'error': 'Informe o movimento_id da devolução.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            movimento = MovimentacoesEstoque.objects.select_related(
                'tipo_movimentacao', 'nota_fiscal_entrada'
            ).get(id=movimento_id, tipo_movimentacao__tipo='S')
        except MovimentacoesEstoque.DoesNotExist:
            return Response(
                {'error': 'Movimento de devolução não encontrado.'},
                status=status.HTTP_404_NOT_FOUND
            )

        if not movimento.nota_fiscal_entrada_id:
            return Response(
                {'error': 'Movimento informado não pertence a uma devolução de compra.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not movimento.local_origem_id:
            return Response(
                {'error': 'Movimento sem local de origem configurado.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        with transaction.atomic():
            _atualizar_saldo_estoque(
                produto_id=movimento.produto_id,
                local_id=movimento.local_origem_id,
                delta_quantidade=(movimento.quantidade or Decimal('0.000')),
                custo_unitario=movimento.custo_unitario,
                data_movimentacao=movimento.data_movimentacao
            )

            movimento.delete()

        return Response(
            {'status': 'cancelado', 'movimento_id': movimento_id},
            status=status.HTTP_200_OK
        )


class ComprasDevolucaoSaldoView(APIView):
    """Consulta o saldo disponível para devolução por produto em uma nota."""

    @staticmethod
    def _to_float(value):
        return float(value or Decimal('0.00'))

    def get(self, request, nota_id, *args, **kwargs):
        try:
            nota = NotasFiscaisEntrada.objects.get(id=nota_id)
        except NotasFiscaisEntrada.DoesNotExist:
            return Response(
                {'error': 'Nota fiscal de entrada não encontrada.'},
                status=status.HTTP_404_NOT_FOUND
            )

        itens_nota = list(nota.itens.select_related('produto'))
        if not itens_nota:
            return Response(
                {'error': 'Nota fiscal sem itens cadastrados.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        resumo_itens = {}
        for item in itens_nota:
            resumo = resumo_itens.setdefault(
                item.produto_id,
                {
                    'produto_nome': item.produto.nome if item.produto else None,
                    'quantidade': Decimal('0.000'),
                    'valor': Decimal('0.00')
                }
            )
            resumo['quantidade'] += item.quantidade or Decimal('0.000')
            resumo['valor'] += item.valor_total or Decimal('0.00')

        devolucoes = MovimentacoesEstoque.objects.filter(
            nota_fiscal_entrada=nota,
            tipo_movimentacao__tipo='S'
        ).values('produto_id').annotate(quantidade=Sum('quantidade'))

        devolvido_por_produto = {item['produto_id']: item['quantidade'] for item in devolucoes}

        response = []
        for produto_id, dados in resumo_itens.items():
            quantidade_comprada = dados['quantidade']
            quantidade_devolvida = devolvido_por_produto.get(produto_id, Decimal('0.000'))
            quantidade_disponivel = quantidade_comprada - quantidade_devolvida
            response.append(
                {
                    'produto_id': produto_id,
                    'produto_nome': dados['produto_nome'],
                    'quantidade_comprada': self._to_float(quantidade_comprada),
                    'quantidade_devolvida': self._to_float(quantidade_devolvida),
                    'quantidade_disponivel': self._to_float(quantidade_disponivel)
                }
            )

        return Response(
            {
                'nota_id': nota.id,
                'numero_nota': nota.numero_nota,
                'itens': response
            },
            status=status.HTTP_200_OK
        )


class ComprasDevolucaoResumoView(APIView):
    """Resumo de devoluções de compras."""

    @staticmethod
    def _to_float(value):
        return float(value or Decimal('0.00'))

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
        fornecedor_id = request.query_params.get('fornecedor_id')

        if (data_inicio and not data_fim) or (data_fim and not data_inicio):
            return Response(
                {'error': 'Informe data_inicio e data_fim no formato YYYY-MM-DD.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if data_inicio and data_fim and data_inicio > data_fim:
            return Response(
                {'error': 'A data_inicio não pode ser maior que data_fim.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        movimentos = MovimentacoesEstoque.objects.filter(
            nota_fiscal_entrada__isnull=False,
            tipo_movimentacao__tipo='S'
        ).select_related('produto', 'nota_fiscal_entrada', 'nota_fiscal_entrada__fornecedor')

        if fornecedor_id:
            movimentos = movimentos.filter(nota_fiscal_entrada__fornecedor_id=fornecedor_id)

        if data_inicio and data_fim:
            movimentos = movimentos.filter(
                data_movimentacao__date__gte=data_inicio,
                data_movimentacao__date__lte=data_fim
            )

        totais = movimentos.aggregate(
            quantidade_total=Sum('quantidade'),
            valor_total=Sum('valor_total'),
        )

        top_fornecedores = list(
            movimentos.values(
                'nota_fiscal_entrada__fornecedor__id',
                'nota_fiscal_entrada__fornecedor__nome'
            )
            .annotate(
                quantidade=Sum('quantidade'),
                valor_total=Sum('valor_total')
            )
            .order_by('-valor_total')[:10]
        )

        for fornecedor in top_fornecedores:
            fornecedor['quantidade'] = self._to_float(fornecedor['quantidade'])
            fornecedor['valor_total'] = self._to_float(fornecedor['valor_total'])

        top_produtos = list(
            movimentos.values('produto__id', 'produto__nome', 'produto__codigo')
            .annotate(
                quantidade=Sum('quantidade'),
                valor_total=Sum('valor_total')
            )
            .order_by('-valor_total')[:10]
        )

        for produto in top_produtos:
            produto['quantidade'] = self._to_float(produto['quantidade'])
            produto['valor_total'] = self._to_float(produto['valor_total'])

        response = {
            'filtros': {
                'data_inicio': data_inicio.isoformat() if data_inicio else None,
                'data_fim': data_fim.isoformat() if data_fim else None,
                'fornecedor_id': fornecedor_id
            },
            'totais': {
                'quantidade_total': self._to_float(totais['quantidade_total']),
                'valor_total': self._to_float(totais['valor_total'])
            },
            'top_fornecedores': top_fornecedores,
            'top_produtos': top_produtos
        }

        return Response(response, status=status.HTTP_200_OK)


class ComprasDevolucaoPorNotaView(APIView):
    """Resumo de devoluções agrupado por nota fiscal de entrada."""

    @staticmethod
    def _to_float(value):
        return float(value or Decimal('0.00'))

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
        fornecedor_id = request.query_params.get('fornecedor_id')

        if (data_inicio and not data_fim) or (data_fim and not data_inicio):
            return Response(
                {'error': 'Informe data_inicio e data_fim no formato YYYY-MM-DD.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if data_inicio and data_fim and data_inicio > data_fim:
            return Response(
                {'error': 'A data_inicio não pode ser maior que data_fim.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        movimentos = MovimentacoesEstoque.objects.filter(
            nota_fiscal_entrada__isnull=False,
            tipo_movimentacao__tipo='S'
        ).select_related('nota_fiscal_entrada', 'nota_fiscal_entrada__fornecedor')

        if fornecedor_id:
            movimentos = movimentos.filter(nota_fiscal_entrada__fornecedor_id=fornecedor_id)

        if data_inicio and data_fim:
            movimentos = movimentos.filter(
                data_movimentacao__date__gte=data_inicio,
                data_movimentacao__date__lte=data_fim
            )

        resumo = list(
            movimentos.values(
                'nota_fiscal_entrada_id',
                'nota_fiscal_entrada__numero_nota',
                'nota_fiscal_entrada__fornecedor__id',
                'nota_fiscal_entrada__fornecedor__nome',
            )
            .annotate(
                quantidade_total=Sum('quantidade'),
                valor_total=Sum('valor_total')
            )
            .order_by('-valor_total')[:200]
        )

        for item in resumo:
            item['quantidade_total'] = self._to_float(item['quantidade_total'])
            item['valor_total'] = self._to_float(item['valor_total'])

        return Response(
            {
                'filtros': {
                    'data_inicio': data_inicio.isoformat() if data_inicio else None,
                    'data_fim': data_fim.isoformat() if data_fim else None,
                    'fornecedor_id': fornecedor_id
                },
                'notas': resumo
            },
            status=status.HTTP_200_OK
        )


class ComprasParcelasContaPagarView(APIView):
    """Gera parcelas de contas a pagar vinculadas à nota fiscal de entrada."""

    @staticmethod
    def _decimal(value, default='0.00'):
        if value is None or value == '':
            return Decimal(default)
        return Decimal(str(value))

    @staticmethod
    def _parse_date(value):
        if not value:
            return None
        try:
            return datetime.strptime(value, '%Y-%m-%d').date()
        except ValueError:
            return None

    def post(self, request, *args, **kwargs):
        payload = request.data or {}
        nota_id = payload.get('nota_id')
        numero_parcelas = payload.get('numero_parcelas')
        primeiro_vencimento = self._parse_date(payload.get('primeiro_vencimento'))
        intervalo_dias = int(payload.get('intervalo_dias') or 30)

        if not nota_id or not numero_parcelas or not primeiro_vencimento:
            return Response(
                {'error': 'nota_id, numero_parcelas e primeiro_vencimento são obrigatórios.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            numero_parcelas = int(numero_parcelas)
        except (TypeError, ValueError):
            return Response(
                {'error': 'numero_parcelas deve ser um número inteiro.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if numero_parcelas <= 0:
            return Response(
                {'error': 'numero_parcelas deve ser maior que zero.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if intervalo_dias <= 0:
            return Response(
                {'error': 'intervalo_dias deve ser maior que zero.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            nota = NotasFiscaisEntrada.objects.select_related('fornecedor').get(id=nota_id)
        except NotasFiscaisEntrada.DoesNotExist:
            return Response(
                {'error': 'Nota fiscal de entrada não encontrada.'},
                status=status.HTTP_404_NOT_FOUND
            )

        valor_total = self._decimal(payload.get('valor_total'), default=str(nota.valor_total or Decimal('0.00')))
        valor_parcela = (valor_total / Decimal(str(numero_parcelas))).quantize(Decimal('0.01'))
        historico_base = payload.get('historico') or f'NF Entrada {nota.numero_nota}'

        parcelas = []
        valor_acumulado = Decimal('0.00')

        with transaction.atomic():
            for parcela_num in range(1, numero_parcelas + 1):
                vencimento = primeiro_vencimento + timedelta(days=intervalo_dias * (parcela_num - 1))
                valor = valor_parcela

                if parcela_num == numero_parcelas:
                    valor = valor_total - valor_acumulado

                conta = ContasPagar.objects.create(
                    data=payload.get('data_emissao') or nota.data_emissao,
                    vencimento=vencimento,
                    valor=valor,
                    fornecedor=nota.fornecedor,
                    historico=f'{historico_base} - Parcela {parcela_num}/{numero_parcelas}',
                    forma_pagamento=payload.get('forma_pagamento'),
                    condicoes=payload.get('condicoes'),
                    numero_duplicata=payload.get('numero_duplicata'),
                    status=payload.get('status') or 'A',
                    conta_id=payload.get('conta_id')
                )

                parcelas.append(
                    {
                        'id': conta.id,
                        'parcela': parcela_num,
                        'vencimento': conta.vencimento,
                        'valor': float(conta.valor or 0),
                        'status': conta.status
                    }
                )

                valor_acumulado += valor

        return Response(
            {
                'nota_id': nota.id,
                'fornecedor_id': nota.fornecedor_id,
                'valor_total': float(valor_total),
                'parcelas': parcelas
            },
            status=status.HTTP_201_CREATED
        )


class ComprasBaixaContaPagarView(APIView):
    """Registra a baixa/pagamento de uma conta a pagar."""

    @staticmethod
    def _decimal(value, default='0.00'):
        if value is None or value == '':
            return Decimal(default)
        return Decimal(str(value))

    def post(self, request, *args, **kwargs):
        payload = request.data or {}
        conta_id = payload.get('conta_id')
        data_pagamento = payload.get('data_pagamento')

        if not conta_id or not data_pagamento:
            return Response(
                {'error': 'conta_id e data_pagamento são obrigatórios.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            conta = ContasPagar.objects.select_related('fornecedor').get(id=conta_id)
        except ContasPagar.DoesNotExist:
            return Response(
                {'error': 'Conta a pagar não encontrada.'},
                status=status.HTTP_404_NOT_FOUND
            )

        if conta.status == 'C':
            return Response(
                {'error': 'Conta a pagar cancelada não pode ser paga.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if conta.status == 'P':
            return Response(
                {'error': 'Conta a pagar já está paga.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        valor_pago = self._decimal(payload.get('valor_pago'), default=str(conta.valor or Decimal('0.00')))
        juros = self._decimal(payload.get('juros'))
        tarifas = self._decimal(payload.get('tarifas'))

        with transaction.atomic():
            conta.data_pagamento = data_pagamento
            conta.valor_pago = valor_pago
            conta.valor_total_pago = valor_pago + juros + tarifas
            conta.juros = juros
            conta.tarifas = tarifas
            conta.status = 'P'
            conta.save()

        return Response(
            {
                'id': conta.id,
                'fornecedor_id': conta.fornecedor_id,
                'valor_pago': float(conta.valor_pago or 0),
                'valor_total_pago': float(conta.valor_total_pago or 0),
                'data_pagamento': conta.data_pagamento,
                'status': conta.status
            },
            status=status.HTTP_200_OK
        )


class ComprasDetalheView(APIView):
    """Retorna detalhes de uma nota fiscal de entrada com seus itens."""

    @staticmethod
    def _to_float(value):
        return float(value or Decimal('0.00'))

    def get(self, request, nota_id, *args, **kwargs):
        try:
            nota = (
                NotasFiscaisEntrada.objects.select_related('fornecedor')
                .get(id=nota_id)
            )
        except NotasFiscaisEntrada.DoesNotExist:
            return Response(
                {'error': 'Nota fiscal de entrada não encontrada.'},
                status=status.HTTP_404_NOT_FOUND
            )

        itens = (
            ItensNfEntrada.objects.filter(nota_fiscal=nota)
            .select_related('produto')
            .order_by('id')
        )

        itens_response = [
            {
                'id': item.id,
                'produto_id': item.produto_id,
                'produto_nome': item.produto.nome if item.produto else None,
                'produto_codigo': item.produto.codigo if item.produto else None,
                'quantidade': self._to_float(item.quantidade),
                'valor_unitario': self._to_float(item.valor_unitario),
                'valor_total': self._to_float(item.valor_total),
                'cfop': item.cfop,
                'ncm': item.ncm,
                'status': item.status
            }
            for item in itens
        ]

        response = {
            'nota': {
                'id': nota.id,
                'numero_nota': nota.numero_nota,
                'serie_nota': nota.serie_nota,
                'fornecedor_id': nota.fornecedor_id,
                'fornecedor_nome': nota.fornecedor.nome if nota.fornecedor else None,
                'data_emissao': nota.data_emissao,
                'data_entrada': nota.data_entrada,
                'valor_produtos': self._to_float(nota.valor_produtos),
                'valor_total': self._to_float(nota.valor_total),
                'valor_frete': self._to_float(nota.valor_frete),
                'valor_ipi': self._to_float(nota.valor_ipi),
                'valor_icms': self._to_float(nota.valor_icms),
                'valor_desconto': self._to_float(nota.valor_desconto),
                'forma_pagamento': nota.forma_pagamento,
                'condicoes_pagamento': nota.condicoes_pagamento,
                'operacao': nota.operacao,
                'observacao': nota.observacao
            },
            'itens': itens_response
        }

        return Response(response, status=status.HTTP_200_OK)


class ComprasCancelarNotaView(APIView):
    """Cancela/exclui uma nota fiscal de entrada e seus itens."""

    def delete(self, request, nota_id, *args, **kwargs):
        try:
            nota = NotasFiscaisEntrada.objects.get(id=nota_id)
        except NotasFiscaisEntrada.DoesNotExist:
            return Response(
                {'error': 'Nota fiscal de entrada não encontrada.'},
                status=status.HTTP_404_NOT_FOUND
            )

        with transaction.atomic():
            movimentos = list(MovimentacoesEstoque.objects.filter(nota_fiscal_entrada=nota))

            for movimento in movimentos:
                _atualizar_saldo_estoque(
                    produto_id=movimento.produto_id,
                    local_id=movimento.local_destino_id,
                    delta_quantidade=-(movimento.quantidade or Decimal('0.0000')),
                    custo_unitario=movimento.custo_unitario,
                    data_movimentacao=movimento.data_movimentacao
                )

            MovimentacoesEstoque.objects.filter(nota_fiscal_entrada=nota).delete()
            nota.itens.all().delete()
            nota.delete()

        return Response(
            {'id': nota_id, 'status': 'cancelada'},
            status=status.HTTP_200_OK
        )


class ComprasListaView(APIView):
    """Lista notas fiscais de entrada com filtros básicos."""

    @staticmethod
    def _to_float(value):
        return float(value or Decimal('0.00'))

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
        fornecedor_id = request.query_params.get('fornecedor_id')
        numero_nota = request.query_params.get('numero_nota')

        if (data_inicio and not data_fim) or (data_fim and not data_inicio):
            return Response(
                {'error': 'Informe data_inicio e data_fim no formato YYYY-MM-DD.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if data_inicio and data_fim and data_inicio > data_fim:
            return Response(
                {'error': 'A data_inicio não pode ser maior que data_fim.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        notas = NotasFiscaisEntrada.objects.select_related('fornecedor')

        if fornecedor_id:
            notas = notas.filter(fornecedor_id=fornecedor_id)

        if numero_nota:
            notas = notas.filter(numero_nota__icontains=numero_nota)

        if data_inicio and data_fim:
            notas = notas.filter(
                data_emissao__date__gte=data_inicio,
                data_emissao__date__lte=data_fim
            )

        notas = notas.order_by('-data_emissao')[:200]

        response = [
            {
                'id': nota.id,
                'numero_nota': nota.numero_nota,
                'serie_nota': nota.serie_nota,
                'fornecedor_id': nota.fornecedor_id,
                'fornecedor_nome': nota.fornecedor.nome if nota.fornecedor else None,
                'data_emissao': nota.data_emissao,
                'data_entrada': nota.data_entrada,
                'valor_produtos': self._to_float(nota.valor_produtos),
                'valor_total': self._to_float(nota.valor_total),
                'operacao': nota.operacao
            }
            for nota in notas
        ]

        return Response(response, status=status.HTTP_200_OK)


class ComprasCancelarContaPagarView(APIView):
    """Cancela uma conta a pagar."""

    def post(self, request, *args, **kwargs):
        payload = request.data or {}
        conta_id = payload.get('conta_id')

        if not conta_id:
            return Response(
                {'error': 'conta_id é obrigatório.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            conta = ContasPagar.objects.get(id=conta_id)
        except ContasPagar.DoesNotExist:
            return Response(
                {'error': 'Conta a pagar não encontrada.'},
                status=status.HTTP_404_NOT_FOUND
            )

        if conta.status == 'P':
            return Response(
                {'error': 'Conta a pagar já foi paga e não pode ser cancelada.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if conta.status == 'C':
            return Response(
                {'error': 'Conta a pagar já está cancelada.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        with transaction.atomic():
            conta.status = 'C'
            conta.save()

        return Response(
            {
                'id': conta.id,
                'status': conta.status
            },
            status=status.HTTP_200_OK
        )
