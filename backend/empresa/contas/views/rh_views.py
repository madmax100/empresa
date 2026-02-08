from datetime import datetime
from decimal import Decimal

from django.db import transaction
from django.db.models import Sum
from django.utils import timezone
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from ..models.access import (
    BeneficiosRH,
    FolhasPagamento,
    ItensFolhaPagamento,
    PagamentosFuncionarios,
    VinculosBeneficiosRH,
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


class RhFolhaGerarView(APIView):
    """Gera folha de pagamento a partir de pagamentos de funcionários."""

    def post(self, request, *args, **kwargs):
        competencia = _parse_date((request.data or {}).get('competencia'))
        if not competencia:
            return Response(
                {'error': 'competencia é obrigatória (YYYY-MM-DD).'},
                status=status.HTTP_400_BAD_REQUEST
            )

        pagamentos = PagamentosFuncionarios.objects.filter(competencia=competencia)
        if not pagamentos.exists():
            return Response(
                {'error': 'Nenhum pagamento encontrado para a competência.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        with transaction.atomic():
            folha = FolhasPagamento.objects.create(competencia=competencia)
            total_bruto = Decimal('0.00')
            total_descontos = Decimal('0.00')
            total_liquido = Decimal('0.00')

            for pagamento in pagamentos:
                beneficios_total = VinculosBeneficiosRH.objects.filter(
                    funcionario=pagamento.funcionario_id,
                    ativo=True
                ).aggregate(total=Sum('valor'))['total'] or Decimal('0.00')

                valor_liquido = pagamento.valor_liquido or Decimal('0.00')
                descontos = pagamento.descontos or Decimal('0.00')

                ItensFolhaPagamento.objects.create(
                    folha=folha,
                    funcionario_id=pagamento.funcionario_id_id,
                    salario_base=pagamento.salario_base,
                    horas_extras=pagamento.valor_horas_extras or Decimal('0.00'),
                    descontos=descontos,
                    beneficios=beneficios_total,
                    valor_liquido=valor_liquido,
                )

                total_bruto += pagamento.salario_base or Decimal('0.00')
                total_descontos += descontos
                total_liquido += valor_liquido

            folha.total_bruto = total_bruto
            folha.total_descontos = total_descontos
            folha.total_liquido = total_liquido
            folha.save(update_fields=['total_bruto', 'total_descontos', 'total_liquido'])

        return Response(
            {
                'folha_id': folha.id,
                'competencia': competencia.isoformat(),
                'total_bruto': float(total_bruto),
                'total_descontos': float(total_descontos),
                'total_liquido': float(total_liquido),
            },
            status=status.HTTP_201_CREATED
        )


class RhFolhaFecharView(APIView):
    """Fecha folha de pagamento."""

    def post(self, request, *args, **kwargs):
        folha_id = (request.data or {}).get('folha_id')
        if not folha_id:
            return Response({'error': 'folha_id é obrigatório.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            folha = FolhasPagamento.objects.get(id=folha_id)
        except FolhasPagamento.DoesNotExist:
            return Response({'error': 'Folha não encontrada.'}, status=status.HTTP_404_NOT_FOUND)

        folha.status = 'F'
        folha.data_fechamento = timezone.now()
        folha.save(update_fields=['status', 'data_fechamento'])

        return Response({'id': folha.id, 'status': folha.status}, status=status.HTTP_200_OK)


class RhResumoBeneficiosView(APIView):
    """Resumo de benefícios ativos."""

    def get(self, request, *args, **kwargs):
        beneficios = BeneficiosRH.objects.filter(ativo=True)
        total = VinculosBeneficiosRH.objects.filter(ativo=True).aggregate(
            total=Sum('valor')
        )['total'] or Decimal('0.00')

        return Response(
            {
                'beneficios_ativos': beneficios.count(),
                'valor_total_beneficios': float(total),
            },
            status=status.HTTP_200_OK
        )
