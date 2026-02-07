from decimal import Decimal

from django.db import models, transaction
from django.utils import timezone
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from ..models.access import (
    AtividadesCRM,
    EtapasFunil,
    ItensPropostaCRM,
    OportunidadesCRM,
    PropostasCRM,
)


def _recalcular_total_proposta(proposta):
    total = ItensPropostaCRM.objects.filter(proposta=proposta).aggregate(
        total=models.Sum('valor_total')
    )['total'] or Decimal('0.00')
    proposta.valor_total = total
    proposta.save(update_fields=['valor_total'])
    proposta.clean()
    proposta.save(update_fields=['valor_total'])


class CRMOportunidadeMoverEtapaView(APIView):
    """Move oportunidade para outra etapa do funil."""

    def post(self, request, *args, **kwargs):
        oportunidade_id = request.data.get('oportunidade_id')
        etapa_id = request.data.get('etapa_id')

        if not oportunidade_id or not etapa_id:
            return Response({'error': 'Informe oportunidade_id e etapa_id.'}, status=status.HTTP_400_BAD_REQUEST)

        oportunidade = OportunidadesCRM.objects.filter(id=oportunidade_id).first()
        if not oportunidade:
            return Response({'error': 'Oportunidade não encontrada.'}, status=status.HTTP_404_NOT_FOUND)

        etapa = EtapasFunil.objects.filter(id=etapa_id).first()
        if not etapa:
            return Response({'error': 'Etapa não encontrada.'}, status=status.HTTP_404_NOT_FOUND)

        oportunidade.etapa = etapa
        oportunidade.funil = etapa.funil
        oportunidade.probabilidade = etapa.probabilidade
        oportunidade.save(update_fields=['etapa', 'funil', 'probabilidade'])

        return Response(
            {'oportunidade_id': oportunidade.id, 'etapa_id': etapa.id},
            status=status.HTTP_200_OK
        )


class CRMOportunidadeFecharView(APIView):
    """Fecha oportunidade como ganha ou perdida."""

    def post(self, request, *args, **kwargs):
        oportunidade_id = request.data.get('oportunidade_id')
        status_novo = request.data.get('status')
        motivo_perda = request.data.get('motivo_perda')

        if not oportunidade_id or status_novo not in ['GANHA', 'PERDIDA', 'CANCELADA']:
            return Response(
                {'error': 'Informe oportunidade_id e status (GANHA, PERDIDA, CANCELADA).'},
                status=status.HTTP_400_BAD_REQUEST
            )

        oportunidade = OportunidadesCRM.objects.filter(id=oportunidade_id).first()
        if not oportunidade:
            return Response({'error': 'Oportunidade não encontrada.'}, status=status.HTTP_404_NOT_FOUND)

        oportunidade.status = status_novo
        oportunidade.motivo_perda = motivo_perda
        oportunidade.save(update_fields=['status', 'motivo_perda'])

        return Response({'oportunidade_id': oportunidade.id, 'status': oportunidade.status}, status=status.HTTP_200_OK)


class CRMAtividadeConcluirView(APIView):
    """Conclui atividade de CRM."""

    def post(self, request, *args, **kwargs):
        atividade_id = request.data.get('atividade_id')
        if not atividade_id:
            return Response({'error': 'Informe atividade_id.'}, status=status.HTTP_400_BAD_REQUEST)

        atividade = AtividadesCRM.objects.filter(id=atividade_id).first()
        if not atividade:
            return Response({'error': 'Atividade não encontrada.'}, status=status.HTTP_404_NOT_FOUND)

        atividade.concluida = True
        atividade.data_conclusao = timezone.now()
        atividade.save(update_fields=['concluida', 'data_conclusao'])

        return Response({'atividade_id': atividade.id, 'concluida': True}, status=status.HTTP_200_OK)


class CRMPropostaRegistrarView(APIView):
    """Registra proposta com itens vinculados a uma oportunidade."""

    def post(self, request, *args, **kwargs):
        data = request.data
        itens = data.get('itens', [])
        if not itens:
            return Response({'error': 'Informe itens da proposta.'}, status=status.HTTP_400_BAD_REQUEST)

        with transaction.atomic():
            proposta = PropostasCRM.objects.create(
                oportunidade_id=data.get('oportunidade_id'),
                numero_proposta=data.get('numero_proposta'),
                data_emissao=data.get('data_emissao') or timezone.now(),
                validade=data.get('validade'),
                desconto=Decimal(str(data.get('desconto') or '0')),
                observacoes=data.get('observacoes'),
                status='RASCUNHO'
            )

            total = Decimal('0.00')
            for item in itens:
                quantidade = Decimal(str(item.get('quantidade') or '0'))
                valor_unitario = Decimal(str(item.get('valor_unitario') or '0'))
                desconto_item = Decimal(str(item.get('desconto') or '0'))
                valor_total = (quantidade * valor_unitario) - desconto_item
                ItensPropostaCRM.objects.create(
                    proposta=proposta,
                    produto_id=item.get('produto_id'),
                    quantidade=quantidade,
                    valor_unitario=valor_unitario,
                    desconto=desconto_item,
                    valor_total=valor_total
                )
                total += valor_total

            proposta.valor_total = total
            proposta.save(update_fields=['valor_total'])

        return Response(
            {'proposta_id': proposta.id, 'valor_total': float(proposta.valor_total)},
            status=status.HTTP_201_CREATED
        )
