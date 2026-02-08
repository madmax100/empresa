from datetime import datetime
from decimal import Decimal

from django.db import transaction
from django.db.models import Sum
from django.utils import timezone
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from ..models.access import (
    AtivosPatrimonio,
    DepreciacoesAtivos,
    ManutencoesAtivos,
)


def _parse_date(value):
    if not value:
        return None
    try:
        return datetime.strptime(value, '%Y-%m-%d').date()
    except ValueError:
        return None


def _decimal(value, default='0.00'):
    if value is None or value == '':
        return Decimal(default)
    return Decimal(str(value))


class AtivosDepreciacaoGerarView(APIView):
    """Gera depreciação mensal para ativos."""

    def post(self, request, *args, **kwargs):
        competencia = _parse_date((request.data or {}).get('competencia'))
        if not competencia:
            return Response(
                {'error': 'competencia é obrigatória (YYYY-MM-DD).'},
                status=status.HTTP_400_BAD_REQUEST
            )

        ativos = AtivosPatrimonio.objects.filter(status='A', vida_util_meses__gt=0)
        geradas = []

        with transaction.atomic():
            for ativo in ativos:
                valor_base = (ativo.valor_aquisicao or Decimal('0.00')) - (ativo.valor_residual or Decimal('0.00'))
                if valor_base <= 0:
                    continue
                valor_mensal = valor_base / Decimal(ativo.vida_util_meses)

                acumulado = DepreciacoesAtivos.objects.filter(ativo=ativo).aggregate(
                    total=Sum('valor_depreciado')
                )['total'] or Decimal('0.00')

                DepreciacoesAtivos.objects.create(
                    ativo=ativo,
                    competencia=competencia,
                    valor_depreciado=valor_mensal,
                    valor_acumulado=acumulado + valor_mensal,
                )
                geradas.append(ativo.id)

        return Response(
            {'competencia': competencia.isoformat(), 'ativos_processados': geradas},
            status=status.HTTP_201_CREATED
        )


class ManutencaoAbrirView(APIView):
    """Abre manutenção para um ativo."""

    def post(self, request, *args, **kwargs):
        payload = request.data or {}
        ativo_id = payload.get('ativo_id')
        if not ativo_id:
            return Response({'error': 'ativo_id é obrigatório.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            ativo = AtivosPatrimonio.objects.get(id=ativo_id)
        except AtivosPatrimonio.DoesNotExist:
            return Response({'error': 'Ativo não encontrado.'}, status=status.HTTP_404_NOT_FOUND)

        manutencao = ManutencoesAtivos.objects.create(
            ativo=ativo,
            tipo=payload.get('tipo') or 'Preventiva',
            data_abertura=payload.get('data_abertura') or timezone.now(),
            responsavel_id=payload.get('responsavel_id'),
            custo_previsto=_decimal(payload.get('custo_previsto')),
            observacoes=payload.get('observacoes'),
        )

        return Response({'id': manutencao.id, 'status': manutencao.status}, status=status.HTTP_201_CREATED)


class ManutencaoFinalizarView(APIView):
    """Finaliza manutenção."""

    def post(self, request, *args, **kwargs):
        payload = request.data or {}
        manutencao_id = payload.get('manutencao_id')
        if not manutencao_id:
            return Response({'error': 'manutencao_id é obrigatório.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            manutencao = ManutencoesAtivos.objects.get(id=manutencao_id)
        except ManutencoesAtivos.DoesNotExist:
            return Response({'error': 'Manutenção não encontrada.'}, status=status.HTTP_404_NOT_FOUND)

        manutencao.status = 'F'
        manutencao.data_fechamento = payload.get('data_fechamento') or timezone.now()
        manutencao.custo_real = _decimal(payload.get('custo_real'))
        manutencao.save(update_fields=['status', 'data_fechamento', 'custo_real'])

        return Response({'id': manutencao.id, 'status': manutencao.status}, status=status.HTTP_200_OK)


class ManutencaoCancelarView(APIView):
    """Cancela manutenção."""

    def post(self, request, *args, **kwargs):
        manutencao_id = (request.data or {}).get('manutencao_id')
        if not manutencao_id:
            return Response({'error': 'manutencao_id é obrigatório.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            manutencao = ManutencoesAtivos.objects.get(id=manutencao_id)
        except ManutencoesAtivos.DoesNotExist:
            return Response({'error': 'Manutenção não encontrada.'}, status=status.HTTP_404_NOT_FOUND)

        manutencao.status = 'C'
        manutencao.save(update_fields=['status'])
        return Response({'id': manutencao.id, 'status': manutencao.status}, status=status.HTTP_200_OK)


class AtivosResumoView(APIView):
    """Resumo de ativos e custos de manutenção."""

    def get(self, request, *args, **kwargs):
        status_filtro = request.query_params.get('status')
        ativos = AtivosPatrimonio.objects.all()
        if status_filtro:
            ativos = ativos.filter(status=status_filtro)

        manutencoes = ManutencoesAtivos.objects.all()

        resumo = {
            'ativos_total': ativos.count(),
            'valor_aquisicao_total': float(
                ativos.aggregate(total=Sum('valor_aquisicao'))['total'] or Decimal('0.00')
            ),
            'custo_manutencao_total': float(
                manutencoes.aggregate(total=Sum('custo_real'))['total'] or Decimal('0.00')
            ),
        }

        return Response(resumo, status=status.HTTP_200_OK)
