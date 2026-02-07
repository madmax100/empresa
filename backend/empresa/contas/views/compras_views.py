from datetime import datetime
from decimal import Decimal

from django.db import transaction
from django.db.models import Count, Sum
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from ..models.access import ContasPagar, ItensNfEntrada, NotasFiscaisEntrada


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
