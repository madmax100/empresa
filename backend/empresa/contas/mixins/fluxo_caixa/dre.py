from decimal import Decimal
from datetime import date, datetime
from typing import Dict, Any, List
from django.db.models import Sum, F, Q
from rest_framework.decorators import action
from rest_framework.response import Response

class DREMixin:
    """
    Mixin para cálculos e análises de DRE (Demonstrativo de Resultados)
    """
    
    @action(detail=False, methods=['GET'])
    def dre(self, request):
        """Gera DRE para o período especificado"""
        try:
            data_inicial = datetime.strptime(
                request.query_params.get('data_inicial'), 
                '%Y-%m-%d'
            ).date()
            data_final = datetime.strptime(
                request.query_params.get('data_final'),
                '%Y-%m-%d'
            ).date()

            # Calcula resultados do DRE
            resultados = self._calcular_resultados_dre(data_inicial, data_final)
            
            # Calcula análises complementares
            analises = self._analisar_resultados_dre(resultados)
            
            return Response({
                'periodo': {
                    'inicio': data_inicial,
                    'fim': data_final
                },
                'resultados': resultados,
                'analises': analises,
                'indicadores': self._calcular_indicadores_dre(resultados)
            })
            
        except Exception as e:
            return Response({'error': str(e)}, status=400)

    def _calcular_resultados_dre(self, data_inicial: date, data_final: date) -> Dict[str, Any]:
        """Calcula os resultados do DRE para o período"""
        lancamentos = self.get_queryset().filter(
            data__range=[data_inicial, data_final],
            realizado=True
        )

        # Receita Bruta
        receita_bruta = lancamentos.filter(
            tipo='entrada'
        ).aggregate(
            total=Sum('valor')
        )['total'] or Decimal('0')

        # Deduções
        deducoes = receita_bruta * Decimal('0.15')  # 15% de impostos e deduções
        
        # Receita Líquida
        receita_liquida = receita_bruta - deducoes

        # Custos Operacionais
        custos_operacionais = lancamentos.filter(
            tipo='saida',
            categoria__in=['suprimentos', 'servicos', 'locacao_maquinas']
        ).aggregate(
            total=Sum('valor')
        )['total'] or Decimal('0')

        # Despesas Operacionais
        despesas_operacionais = lancamentos.filter(
            tipo='saida',
            categoria__in=['despesas_operacionais', 'despesas_administrativas']
        ).aggregate(
            total=Sum('valor')
        )['total'] or Decimal('0')

        # Resultado Operacional
        resultado_operacional = receita_liquida - custos_operacionais - despesas_operacionais

        # Resultado por Categoria
        resultado_categorias = self._calcular_resultado_categorias(lancamentos)

        return {
            'receita_bruta': float(receita_bruta),
            'deducoes': float(deducoes),
            'receita_liquida': float(receita_liquida),
            'custos_operacionais': float(custos_operacionais),
            'despesas_operacionais': float(despesas_operacionais),
            'resultado_operacional': float(resultado_operacional),
            'resultado_categorias': resultado_categorias
        }

    def _analisar_resultados_dre(self, resultados: Dict[str, Any]) -> Dict[str, Any]:
        """Análise detalhada dos resultados do DRE"""
        receita_liquida = Decimal(str(resultados['receita_liquida']))
        
        if receita_liquida == 0:
            return {
                'margem_liquida': 0,
                'margem_operacional': 0,
                'participacao_custos': 0,
                'participacao_despesas': 0
            }

        return {
            'margem_liquida': float(
                (Decimal(str(resultados['resultado_operacional'])) / receita_liquida) * 100
            ),
            'margem_operacional': float(
                (Decimal(str(resultados['resultado_operacional'])) / receita_liquida) * 100
            ),
            'participacao_custos': float(
                (Decimal(str(resultados['custos_operacionais'])) / receita_liquida) * 100
            ),
            'participacao_despesas': float(
                (Decimal(str(resultados['despesas_operacionais'])) / receita_liquida) * 100
            )
        }

    def _calcular_indicadores_dre(self, resultados: Dict[str, Any]) -> Dict[str, Any]:
        """Calcula indicadores financeiros baseados no DRE"""
        receita_liquida = Decimal(str(resultados['receita_liquida']))
        
        if receita_liquida == 0:
            return {
                'rentabilidade': 0,
                'eficiencia_operacional': 0,
                'indice_despesas': 0
            }

        return {
            'rentabilidade': float(
                (Decimal(str(resultados['resultado_operacional'])) / receita_liquida) * 100
            ),
            'eficiencia_operacional': float(
                (Decimal(str(resultados['custos_operacionais'])) / receita_liquida) * 100
            ),
            'indice_despesas': float(
                (Decimal(str(resultados['despesas_operacionais'])) / receita_liquida) * 100
            )
        }

    def _calcular_resultado_categorias(self, lancamentos) -> Dict[str, Dict[str, float]]:
        """Calcula resultados detalhados por categoria"""
        categorias = {}
        
        for categoria in dict(self.get_queryset().model.CATEGORIA_CHOICES):
            lanc_categoria = lancamentos.filter(categoria=categoria)
            
            receitas = lanc_categoria.filter(
                tipo='entrada'
            ).aggregate(
                total=Sum('valor')
            )['total'] or Decimal('0')
            
            despesas = lanc_categoria.filter(
                tipo='saida'
            ).aggregate(
                total=Sum('valor')
            )['total'] or Decimal('0')

            if receitas > 0 or despesas > 0:
                categorias[categoria] = {
                    'receitas': float(receitas),
                    'despesas': float(despesas),
                    'resultado': float(receitas - despesas)
                }

        return categorias