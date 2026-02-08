from datetime import datetime
from decimal import Decimal

from django.db.models import Count, Sum
from django.utils import timezone
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from ..models.access import AtividadesCRM, Oportunidades


def _parse_date(value):
    if not value:
        return None
    try:
        return datetime.strptime(value, '%Y-%m-%d').date()
    except ValueError:
        return None


class CrmFunilResumoView(APIView):
    """Resumo do funil por etapa e status."""

    def get(self, request, *args, **kwargs):
        data_inicio = _parse_date(request.query_params.get('data_inicio'))
        data_fim = _parse_date(request.query_params.get('data_fim'))

        oportunidades = Oportunidades.objects.select_related('etapa')

        if data_inicio and data_fim:
            oportunidades = oportunidades.filter(
                data_criacao__date__gte=data_inicio,
                data_criacao__date__lte=data_fim
            )
        elif data_inicio or data_fim:
            return Response(
                {'error': 'Informe data_inicio e data_fim no formato YYYY-MM-DD.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        resumo = list(
            oportunidades.values('etapa__id', 'etapa__nome', 'status')
            .annotate(
                quantidade=Count('id'),
                valor_total=Sum('valor_estimado')
            )
            .order_by('etapa__nome', 'status')
        )

        for item in resumo:
            item['valor_total'] = float(item['valor_total'] or Decimal('0.00'))

        return Response(
            {
                'filtros': {
                    'data_inicio': data_inicio.isoformat() if data_inicio else None,
                    'data_fim': data_fim.isoformat() if data_fim else None
                },
                'resumo': resumo
            },
            status=status.HTTP_200_OK
        )


class CrmAtividadesPendentesView(APIView):
    """Lista atividades pendentes do CRM."""

    def get(self, request, *args, **kwargs):
        usuario_id = request.query_params.get('usuario_id')
        data_inicio = _parse_date(request.query_params.get('data_inicio'))
        data_fim = _parse_date(request.query_params.get('data_fim'))

        atividades = AtividadesCRM.objects.select_related('oportunidade')
        atividades = atividades.filter(concluida=False)

        if usuario_id:
            atividades = atividades.filter(usuario_id=usuario_id)

        if data_inicio and data_fim:
            atividades = atividades.filter(
                data_agendada__date__gte=data_inicio,
                data_agendada__date__lte=data_fim
            )
        elif data_inicio or data_fim:
            return Response(
                {'error': 'Informe data_inicio e data_fim no formato YYYY-MM-DD.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        response = [
            {
                'id': atividade.id,
                'oportunidade_id': atividade.oportunidade_id,
                'oportunidade_titulo': atividade.oportunidade.titulo if atividade.oportunidade else None,
                'tipo': atividade.tipo,
                'data_agendada': atividade.data_agendada,
                'usuario_id': atividade.usuario_id,
                'descricao': atividade.descricao,
            }
            for atividade in atividades.order_by('data_agendada')[:200]
        ]

        return Response(
            {'quantidade': len(response), 'resultados': response},
            status=status.HTTP_200_OK
        )


class CrmOportunidadesResumoView(APIView):
    """Resumo geral de oportunidades."""

    def get(self, request, *args, **kwargs):
        responsavel_id = request.query_params.get('responsavel_id')
        status_filtro = request.query_params.get('status')

        oportunidades = Oportunidades.objects.all()
        if responsavel_id:
            oportunidades = oportunidades.filter(responsavel_id=responsavel_id)
        if status_filtro:
            oportunidades = oportunidades.filter(status=status_filtro)

        totais = oportunidades.aggregate(
            quantidade=Count('id'),
            valor_total=Sum('valor_estimado')
        )

        return Response(
            {
                'quantidade': totais['quantidade'] or 0,
                'valor_total': float(totais['valor_total'] or Decimal('0.00')),
                'data_referencia': timezone.now()
            },
            status=status.HTTP_200_OK
        )
