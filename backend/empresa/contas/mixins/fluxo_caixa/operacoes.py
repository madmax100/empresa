from django.db import transaction
from django.core.exceptions import ValidationError
from rest_framework.decorators import action
from rest_framework.response import Response
from decimal import Decimal
from typing import List, Dict, Any
import pandas as pd
from datetime import datetime

class FluxoCaixaOperacoesMixin:
    """Mixin para operações do fluxo de caixa"""

    @action(detail=False, methods=['POST'])
    @transaction.atomic
    def importar_planilha(self, request):
        """Importa lançamentos de uma planilha Excel/CSV"""
        try:
            file = request.FILES.get('file')
            if not file:
                raise ValidationError("Arquivo não fornecido")

            # Lê o arquivo (Excel ou CSV)
            if file.name.endswith('.csv'):
                df = pd.read_csv(file)
            else:
                df = pd.read_excel(file)

            # Valida colunas obrigatórias
            required_columns = ['data', 'tipo', 'valor', 'descricao', 'categoria']
            missing_columns = [col for col in required_columns if col not in df.columns]
            if missing_columns:
                raise ValidationError(f"Colunas obrigatórias faltando: {missing_columns}")

            # Processa cada linha
            lancamentos = []
            erros = []
            
            for index, row in df.iterrows():
                try:
                    lancamento = self._validate_and_prepare_lancamento(row)
                    lancamentos.append(lancamento)
                except Exception as e:
                    erros.append({
                        'linha': index + 2,  # +2 para compensar cabeçalho e índice 0
                        'erro': str(e)
                    })

            # Se houver erros, não importa nada
            if erros:
                raise ValidationError({
                    'message': 'Erros encontrados na planilha',
                    'erros': erros
                })

            # Importa os lançamentos
            self.get_queryset().model.objects.bulk_create(lancamentos)

            return Response({
                'message': f'{len(lancamentos)} lançamentos importados com sucesso'
            })

        except Exception as e:
            return Response({
                'error': str(e)
            }, status=400)

    def _validate_and_prepare_lancamento(self, row: pd.Series) -> Any:
        """Valida e prepara um lançamento a partir de uma linha da planilha"""
        # Valida data
        try:
            data = pd.to_datetime(row['data']).date()
        except:
            raise ValidationError("Data inválida")

        # Valida tipo
        tipo = str(row['tipo']).lower()
        if tipo not in ['entrada', 'saida']:
            raise ValidationError("Tipo deve ser 'entrada' ou 'saida'")

        # Valida valor
        try:
            valor = Decimal(str(row['valor']))
            if valor <= 0:
                raise ValidationError("Valor deve ser maior que zero")
        except:
            raise ValidationError("Valor inválido")

        # Valida categoria
        categoria = str(row['categoria']).lower()
        if categoria not in [choice[0] for choice in self.get_queryset().model.CATEGORIA_CHOICES]:
            raise ValidationError(f"Categoria '{categoria}' inválida")

        # Cria o objeto (sem salvar)
        return self.get_queryset().model(
            data=data,
            tipo=tipo,
            valor=valor,
            descricao=row['descricao'],
            categoria=categoria,
            realizado=False
        )

    @action(detail=False, methods=['POST'])
    @transaction.atomic
    def processar_lote(self, request):
        """Processa operações em lote (realizar/estornar)"""
        operacao = request.data.get('operacao')
        ids = request.data.get('ids', [])

        if not ids:
            return Response({'error': 'Nenhum ID fornecido'}, status=400)

        if operacao not in ['realizar', 'estornar']:
            return Response({'error': 'Operação inválida'}, status=400)

        lancamentos = self.get_queryset().filter(id__in=ids)
        
        if operacao == 'realizar':
            for lancamento in lancamentos:
                if not lancamento.realizado:
                    lancamento.realizar()
        else:
            for lancamento in lancamentos:
                if lancamento.realizado and not lancamento.data_estorno:
                    lancamento.estornar()

        return Response({
            'message': f'{len(ids)} lançamentos processados com sucesso'
        })

    @action(detail=False, methods=['POST'])
    @transaction.atomic
    def atualizar_lote(self, request):
        """Atualiza múltiplos lançamentos em lote"""
        atualizacoes = request.data.get('atualizacoes', [])
        
        if not atualizacoes:
            return Response({'error': 'Nenhuma atualização fornecida'}, status=400)

        resultados = []
        for atualizacao in atualizacoes:
            try:
                lancamento = self.get_queryset().get(id=atualizacao['id'])
                
                # Atualiza apenas campos permitidos
                campos_permitidos = ['categoria', 'descricao', 'observacoes']
                for campo in campos_permitidos:
                    if campo in atualizacao:
                        setattr(lancamento, campo, atualizacao[campo])
                
                lancamento.save()
                resultados.append({
                    'id': lancamento.id,
                    'status': 'sucesso'
                })
            except Exception as e:
                resultados.append({
                    'id': atualizacao.get('id'),
                    'status': 'erro',
                    'erro': str(e)
                })

        return Response({
            'message': f'{len(resultados)} atualizações processadas',
            'resultados': resultados
        })