from datetime import date

from django.db.models import F, Sum
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.estoque.models import (
    LocalEstoque,
    MovimentacaoEstoque,
    PosicaoEstoque,
    Produto,
    SaldoEstoque,
    TipoMovimentacaoEstoque,
)
from apps.estoque.serializers import (
    LocalEstoqueSerializer,
    MovimentacaoEstoqueSerializer,
    PosicaoEstoqueSerializer,
    ProdutoSerializer,
    SaldoEstoqueSerializer,
    TipoMovimentacaoEstoqueSerializer,
)


class ResumoEstoqueView(APIView):
    def get(self, request):
        total_itens = Produto.objects.count()
        total_valor = (
            SaldoEstoque.objects.aggregate(
                total=Sum(F("quantidade") * F("custo_medio"))
            )["total"]
            or 0
        )
        ultimo_inventario = (
            MovimentacaoEstoque.objects.order_by("-data_movimentacao")
            .values_list("data_movimentacao", flat=True)
            .first()
        )

        return Response(
            {
                "itens": total_itens,
                "valor_total": float(total_valor),
                "ultimo_inventario": ultimo_inventario,
                "pendencias": [
                    "importar_saldo_inicial",
                    "validar_movimentacoes",
                ],
            }
        )


class RelatorioValorEstoqueView(APIView):
    def get(self, request):
        data_param = request.query_params.get("data")
        data_posicao = date.fromisoformat(data_param) if data_param else date.today()
        saldos = SaldoEstoque.objects.select_related("produto").all()
        total_valor = sum(
            float(saldo.quantidade) * float(saldo.custo_medio) for saldo in saldos
        )

        detalhes = [
            {
                "produto_id": saldo.produto_id,
                "produto_descricao": saldo.produto.nome,
                "categoria": saldo.produto.categoria,
                "quantidade_em_estoque": float(saldo.quantidade),
                "custo_unitario": float(saldo.custo_medio),
                "valor_total_produto": float(saldo.quantidade) * float(saldo.custo_medio),
            }
            for saldo in saldos
        ]

        return Response(
            {
                "data_posicao": data_posicao,
                "valor_total_estoque": float(total_valor),
                "total_produtos_em_estoque": saldos.count(),
                "detalhes_por_produto": detalhes,
            }
        )


class MovimentacoesPeriodoView(APIView):
    def get(self, request):
        data_inicio = request.query_params.get("data_inicio")
        data_fim = request.query_params.get("data_fim")
        if not data_inicio or not data_fim:
            return Response(
                {"erro": "data_inicio e data_fim são obrigatórios."}, status=400
            )

        movimentacoes = MovimentacaoEstoque.objects.filter(
            data_movimentacao__range=(data_inicio, data_fim),
            tipo=MovimentacaoEstoque.TIPO_SAIDA,
        ).select_related("produto")

        produtos = {}
        for mov in movimentacoes:
            produto_id = mov.produto_id
            if produto_id not in produtos:
                produtos[produto_id] = {
                    "produto_id": produto_id,
                    "nome": mov.produto.nome,
                    "quantidade_saida": 0,
                    "valor_saida": 0,
                    "ultimo_preco_entrada": float(mov.produto.preco_entrada),
                }
            produtos[produto_id]["quantidade_saida"] += float(mov.quantidade)
            produtos[produto_id]["valor_saida"] += float(mov.valor_unitario) * float(
                mov.quantidade
            )

        produtos_movimentados = []
        valor_total_saidas = 0
        valor_total_saidas_preco_entrada = 0
        for item in produtos.values():
            valor_saida_preco_entrada = item["quantidade_saida"] * item[
                "ultimo_preco_entrada"
            ]
            diferenca_preco = item["valor_saida"] - valor_saida_preco_entrada
            margem_percentual = (
                (diferenca_preco / item["valor_saida"]) * 100
                if item["valor_saida"]
                else 0
            )
            produtos_movimentados.append(
                {
                    **item,
                    "valor_saida_preco_entrada": valor_saida_preco_entrada,
                    "diferenca_preco": diferenca_preco,
                    "margem_percentual": margem_percentual,
                }
            )
            valor_total_saidas += item["valor_saida"]
            valor_total_saidas_preco_entrada += valor_saida_preco_entrada

        lucro_bruto = valor_total_saidas - valor_total_saidas_preco_entrada
        margem_total = (
            (lucro_bruto / valor_total_saidas) * 100 if valor_total_saidas else 0
        )

        return Response(
            {
                "produtos_movimentados": produtos_movimentados,
                "resumo": {
                    "total_produtos": len(produtos_movimentados),
                    "valor_total_saidas": valor_total_saidas,
                    "valor_total_saidas_preco_entrada": valor_total_saidas_preco_entrada,
                    "margem_total": margem_total,
                    "lucro_bruto": lucro_bruto,
                },
            }
        )


class ProdutoViewSet(viewsets.ModelViewSet):
    queryset = Produto.objects.all().order_by("nome")
    serializer_class = ProdutoSerializer


class MovimentacaoEstoqueViewSet(viewsets.ModelViewSet):
    queryset = MovimentacaoEstoque.objects.select_related("produto").all()
    serializer_class = MovimentacaoEstoqueSerializer


class TipoMovimentacaoEstoqueViewSet(viewsets.ModelViewSet):
    queryset = TipoMovimentacaoEstoque.objects.all()
    serializer_class = TipoMovimentacaoEstoqueSerializer


class LocalEstoqueViewSet(viewsets.ModelViewSet):
    queryset = LocalEstoque.objects.all()
    serializer_class = LocalEstoqueSerializer


class SaldoEstoqueViewSet(viewsets.ModelViewSet):
    queryset = SaldoEstoque.objects.select_related("produto", "local").all()
    serializer_class = SaldoEstoqueSerializer


class PosicaoEstoqueViewSet(viewsets.ModelViewSet):
    queryset = PosicaoEstoque.objects.select_related("local").all()
    serializer_class = PosicaoEstoqueSerializer
