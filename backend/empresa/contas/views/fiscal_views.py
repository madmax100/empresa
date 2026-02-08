from datetime import datetime
from decimal import Decimal

from django.db import transaction
from django.db.models import Sum
from django.utils import timezone
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from ..models.access import (
    ApuracoesFiscais,
    ImpostosFiscais,
    ItensApuracaoFiscal,
    NotasFiscaisEntrada,
    NotasFiscaisSaida,
)


def _parse_date(value):
    if not value:
        return None
    try:
        return datetime.strptime(value, '%Y-%m-%d').date()
    except ValueError:
        return None


class FiscalApuracaoGerarView(APIView):
    """Gera apuração fiscal simples (ICMS/IPI) com base nas notas fiscais."""

    def post(self, request, *args, **kwargs):
        payload = request.data or {}
        data_inicio = _parse_date(payload.get('data_inicio'))
        data_fim = _parse_date(payload.get('data_fim'))

        if not data_inicio or not data_fim:
            return Response(
                {'error': 'Informe data_inicio e data_fim no formato YYYY-MM-DD.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if data_inicio > data_fim:
            return Response(
                {'error': 'data_inicio não pode ser maior que data_fim.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        notas_saida = NotasFiscaisSaida.objects.filter(
            data__date__gte=data_inicio,
            data__date__lte=data_fim
        )
        notas_entrada = NotasFiscaisEntrada.objects.filter(
            data_emissao__date__gte=data_inicio,
            data_emissao__date__lte=data_fim
        )

        saida_icms = notas_saida.aggregate(total=Sum('valor_icms'))['total'] or Decimal('0.00')
        entrada_icms = notas_entrada.aggregate(total=Sum('valor_icms'))['total'] or Decimal('0.00')
        saida_ipi = notas_saida.aggregate(total=Sum('valor_ipi'))['total'] or Decimal('0.00')
        entrada_ipi = notas_entrada.aggregate(total=Sum('valor_ipi'))['total'] or Decimal('0.00')

        with transaction.atomic():
            apuracao = ApuracoesFiscais.objects.create(
                data_inicio=data_inicio,
                data_fim=data_fim,
                data_apuracao=timezone.now(),
                total_debitos=saida_icms + saida_ipi,
                total_creditos=entrada_icms + entrada_ipi,
                saldo=(saida_icms + saida_ipi) - (entrada_icms + entrada_ipi),
            )

            imposto_icms, _ = ImpostosFiscais.objects.get_or_create(
                codigo='ICMS',
                defaults={'nome': 'ICMS', 'tipo': 'ICMS'}
            )
            imposto_ipi, _ = ImpostosFiscais.objects.get_or_create(
                codigo='IPI',
                defaults={'nome': 'IPI', 'tipo': 'IPI'}
            )

            ItensApuracaoFiscal.objects.create(
                apuracao=apuracao,
                imposto=imposto_icms,
                valor_debito=saida_icms,
                valor_credito=entrada_icms,
                saldo=saida_icms - entrada_icms
            )
            ItensApuracaoFiscal.objects.create(
                apuracao=apuracao,
                imposto=imposto_ipi,
                valor_debito=saida_ipi,
                valor_credito=entrada_ipi,
                saldo=saida_ipi - entrada_ipi
            )

        return Response(
            {
                'apuracao_id': apuracao.id,
                'periodo': {
                    'data_inicio': data_inicio.isoformat(),
                    'data_fim': data_fim.isoformat(),
                },
                'total_debitos': float(apuracao.total_debitos),
                'total_creditos': float(apuracao.total_creditos),
                'saldo': float(apuracao.saldo),
            },
            status=status.HTTP_201_CREATED
        )


class FiscalApuracaoResumoView(APIView):
    """Resumo de apurações fiscais."""

    def get(self, request, *args, **kwargs):
        data_inicio = _parse_date(request.query_params.get('data_inicio'))
        data_fim = _parse_date(request.query_params.get('data_fim'))

        apuracoes = ApuracoesFiscais.objects.all()
        if data_inicio and data_fim:
            apuracoes = apuracoes.filter(
                data_inicio__gte=data_inicio,
                data_fim__lte=data_fim
            )
        elif data_inicio or data_fim:
            return Response(
                {'error': 'Informe data_inicio e data_fim no formato YYYY-MM-DD.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        resumo = [
            {
                'id': apuracao.id,
                'data_inicio': apuracao.data_inicio,
                'data_fim': apuracao.data_fim,
                'status': apuracao.status,
                'total_debitos': float(apuracao.total_debitos or Decimal('0.00')),
                'total_creditos': float(apuracao.total_creditos or Decimal('0.00')),
                'saldo': float(apuracao.saldo or Decimal('0.00')),
            }
            for apuracao in apuracoes.order_by('-data_apuracao')[:200]
        ]

        return Response(
            {'quantidade': len(resumo), 'resultados': resumo},
            status=status.HTTP_200_OK
        )
