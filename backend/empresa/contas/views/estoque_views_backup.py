# contas/views/estoque_views.py
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q, Sum, F, Count, Max
from datetime import datetime, date, timedelta
from decimal import Decimal
from collections import defaultdict
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.utils import timezone

from ..models.access import MovimentacoesEstoque, Produtos, EstoqueInicial, Grupos
from ..services.stock_calculation_service import StockCalculationService


class EstoqueViewSet(viewsets.ViewSet):
    """ViewSet para controle de estoque com a nova metodologia de cálculo."""

    @action(detail=False, methods=['get'])
    def estoque_atual(self, request):
        """
        Retorna o estoque em uma data específica usando a nova metodologia de cálculo.
        O cálculo pode ser progressivo (a partir de um 'reset') ou
        retroativo (a partir do estoque atual do produto).
        """
        try:
            # Parâmetros da requisição
            data_str = request.query_params.get('data', date.today().strftime('%Y-%m-%d'))
            produto_id = request.query_params.get('produto_id')
            grupo_id = request.query_params.get('grupo_id')
            limite = int(request.query_params.get('limite', '50'))
            offset = int(request.query_params.get('offset', '0'))
            ordem = request.query_params.get('ordem', 'nome')
            reverso = request.query_params.get('reverso', 'false').lower() == 'true'

            # Converte a string de data para um objeto date
            try:
                data_final = datetime.strptime(data_str, '%Y-%m-%d').date()
            except ValueError:
                return Response(
                    {'error': 'Formato de data inválido. Use YYYY-MM-DD'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Define a query base de produtos
            produtos_query = Produtos.objects.filter(ativo=True)

            # Filtra por grupo, se solicitado
            if grupo_id:
                try:
                    produtos_query = produtos_query.filter(grupo_id=int(grupo_id))
                except (ValueError, TypeError):
                    return Response(
                        {'error': 'ID do grupo deve ser um número inteiro válido.'},
                        status=status.HTTP_400_BAD_REQUEST
                    )

            # Filtra por um produto específico, se solicitado
            if produto_id:
                try:
                    produtos_query = produtos_query.filter(id=int(produto_id))
                except (ValueError, TypeError):
                    return Response(
                        {'error': 'ID do produto deve ser um número inteiro válido.'},
                        status=status.HTTP_400_BAD_REQUEST
                    )

            ordem = request.query_params.get('ordem', 'nome')
            reverso = request.query_params.get('reverso', 'false').lower() == 'true'

            # Mapeia 'valor_atual' (campo calculado) para 'preco_custo' (campo do DB)
            order_param = ordem
            if order_param == 'valor_atual':
                order_param = 'preco_custo'

            # Valida o campo de ordenação para segurança
            order_field = order_param if order_param in ['nome', 'preco_custo'] else 'nome'
            if reverso:
                order_field = f'-{order_field}'
            
            produtos_query = produtos_query.order_by(order_field)

            # Paginação aplicada no banco de dados
            total_registros = produtos_query.count()
            produtos_paginados_query = produtos_query[offset : offset + limite]
            
            # Coleta os produtos da página
            produtos_da_pagina = list(produtos_paginados_query)

            # Calcula o estoque e o valor apenas para os produtos da página
            dados_completos = []
            for produto in produtos_da_pagina:
                quantidade_na_data = StockCalculationService.calculate_stock_at_date(
                    produto.id, data_final
                )
                custo_unitario = produto.preco_custo or Decimal('0')
                valor_na_data = quantidade_na_data * custo_unitario
                dados_completos.append({
                    'produto_id': produto.id,
                    'nome': produto.nome or f"Produto ID {produto.id}",
                    'referencia': produto.referencia or "N/A",
                    'grupo_id': produto.grupo_id,
                    'quantidade_atual': float(quantidade_na_data),
                    'custo_unitario_atual': float(custo_unitario),
                    'valor_atual': float(valor_na_data),
                })

            # Ordenação em memória (agora sobre um conjunto de dados muito menor)
            if ordem in ['nome', 'valor_atual']:
                sort_key = lambda x: x[ordem]
                dados_completos.sort(key=sort_key, reverse=reverso)
            
            # A paginação já foi aplicada, então usamos 'dados_completos' diretamente
            produtos_paginados = dados_completos

            # Otimização: Buscar todos os grupos necessários de uma vez para a página atual
            grupo_ids = [p['grupo_id'] for p in produtos_paginados if p['grupo_id'] is not None]
            grupos = Grupos.objects.filter(id__in=grupo_ids)
            grupo_map = {grupo.id: grupo.nome for grupo in grupos}

            resultado = []
            valor_total_geral = Decimal('0')
            produtos_com_estoque = 0
            produtos_zerados = 0

            # Adiciona nomes de grupo e formata a saída final
            for produto_data in produtos_paginados:
                grupo_id = produto_data['grupo_id']
                grupo_nome = grupo_map.get(grupo_id, "Sem Grupo")
                
                produto_data['grupo_nome'] = grupo_nome
                produto_data['data_calculo'] = data_final.strftime('%Y-%m-%d')
                produto_data['quantidade_inicial'] = 0
                produto_data['variacao_quantidade'] = 0
                produto_data['custo_unitario_inicial'] = 0
                produto_data['valor_inicial'] = 0
                produto_data['variacao_valor'] = 0
                produto_data['total_movimentacoes'] = 0
                produto_data['movimentacoes_recentes'] = []
                resultado.append(produto_data)

            # Calcula estatísticas totais (considerando todos os produtos, não apenas a página)
            # Nota: Fazer isso para todos os produtos pode ser lento.
            # Uma abordagem otimizada seria fazer isso em uma task separada ou simplificar.
            # Por enquanto, calculamos com base na página para manter a performance.
            
            for res in resultado:
                valor_total_geral += Decimal(res['valor_atual'])
                if res['quantidade_atual'] > 0:
                    produtos_com_estoque += 1
                else:
                    produtos_zerados += 1

            estatisticas = {
                'total_produtos': total_registros, # Total real de produtos
                'produtos_com_estoque': produtos_com_estoque, # Apenas da página
                'produtos_zerados': produtos_zerados, # Apenas da página
                'valor_total_atual': round(float(valor_total_geral), 2), # Apenas da página
                'data_calculo': data_final.strftime('%Y-%m-%d'),
                # Campos legados
                'valor_total_inicial': 0,
                'variacao_total': 0,
            }

            return Response({
                'results': resultado,
                'estatisticas': estatisticas,
                'parametros': {
                    'data_consulta': data_final.strftime('%Y-%m-%d'),
                    'produto_id': produto_id,
                    'grupo_id': grupo_id,
                    'total_registros': total_registros,
                    'limite_aplicado': limite,
                    'offset': offset,
                }
            })

        except Exception as e:
            import traceback
            traceback.print_exc()
            return Response(
                {'error': f'Erro interno no servidor: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'])
    def movimentacoes_periodo(self, request):
        """
        Retorna produtos movimentados em um período específico com análise completa
        incluindo último preço de entrada e cálculos de margem
        """
        try:
            # Parâmetros da requisição
            data_inicio_str = request.query_params.get('data_inicio')
            data_fim_str = request.query_params.get('data_fim')
            incluir_detalhes = request.query_params.get('incluir_detalhes', 'false').lower() == 'true'
            produto_id = request.query_params.get('produto_id')
            limite = request.query_params.get('limite')
            ordenar_por = request.query_params.get('ordenar_por', 'valor_saida')
            ordem = request.query_params.get('ordem', 'DESC').upper()
            
            # Validação de parâmetros obrigatórios
            if not data_inicio_str or not data_fim_str:
                return Response(
                    {'error': 'Parâmetros data_inicio e data_fim são obrigatórios. Formato: YYYY-MM-DD'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Converte e valida datas
            try:
                data_inicio = datetime.strptime(data_inicio_str, '%Y-%m-%d').date()
                data_fim = datetime.strptime(data_fim_str, '%Y-%m-%d').date()
            except ValueError:
                return Response(
                    {'error': 'Formato de data inválido. Use YYYY-MM-DD'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            if data_inicio > data_fim:
                return Response(
                    {'error': 'data_inicio deve ser menor ou igual a data_fim'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Tipos de movimentação
            tipos_entrada = [1, 3]  # Entrada e Estoque Inicial
            tipos_saida = [2]       # Saída
            
            # Query principal: movimentações no período
            query = MovimentacoesEstoque.objects.filter(
                data_movimentacao__date__gte=data_inicio,
                data_movimentacao__date__lte=data_fim
            ).exclude(
                documento_referencia='EST_INICIAL_2025'
            ).select_related('produto', 'tipo_movimentacao')
            
            # Filtro por produto específico se solicitado
            if produto_id:
                try:
                    produto_id = int(produto_id)
                    query = query.filter(produto_id=produto_id)
                except ValueError:
                    return Response(
                        {'error': 'produto_id deve ser um número inteiro'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            
            movimentacoes = query.order_by('data_movimentacao')
            
            if not movimentacoes.exists():
                return Response(self._resumo_vazio(data_inicio, data_fim, incluir_detalhes, limite))
            
            # Agrupa movimentações por produto
            produtos_movimentados = {}
            produtos_ids = set()
            
            for mov in movimentacoes:
                pid = mov.produto.id if mov.produto else mov.produto_id
                produtos_ids.add(pid)
                tipo_id = mov.tipo_movimentacao.id if mov.tipo_movimentacao else 0
                
                if pid not in produtos_movimentados:
                    # Busca informações do produto
                    try:
                        produto_obj = Produtos.objects.get(id=pid)
                        nome_produto = produto_obj.nome or f"Produto ID {pid}"
                        referencia = produto_obj.referencia or "N/A"
                    except Produtos.DoesNotExist:
                        nome_produto = f"Produto ID {pid}"
                        referencia = "N/A"
                    
                    produtos_movimentados[pid] = {
                        'produto_id': pid,
                        'nome': nome_produto,
                        'referencia': referencia,
                        'quantidade_entrada': 0.0,
                        'quantidade_saida': 0.0,
                        'valor_entrada': 0.0,
                        'valor_saida': 0.0,
                        'saldo_quantidade': 0.0,
                        'saldo_valor': 0.0,
                        'total_movimentacoes': 0,
                        'primeira_movimentacao': None,
                        'ultima_movimentacao': None,
                        'movimentacoes_detalhadas': []
                    }
                
                produto_data = produtos_movimentados[pid]
                
                # Contabiliza movimentação
                quantidade = float(mov.quantidade or 0)
                valor_total = float(mov.valor_total or 0)
                valor_unitario = float(mov.custo_unitario or 0)
                
                if tipo_id in tipos_entrada:
                    produto_data['quantidade_entrada'] += quantidade
                    produto_data['valor_entrada'] += valor_total
                elif tipo_id in tipos_saida:
                    produto_data['quantidade_saida'] += quantidade
                    produto_data['valor_saida'] += valor_total
                
                # Atualiza contadores e datas
                produto_data['total_movimentacoes'] += 1
                data_mov_str = mov.data_movimentacao.strftime('%Y-%m-%d %H:%M:%S')
                
                if not produto_data['primeira_movimentacao']:
                    produto_data['primeira_movimentacao'] = data_mov_str
                produto_data['ultima_movimentacao'] = data_mov_str
                
                # Adiciona aos detalhes (sempre coletamos para análise)
                is_entrada = tipo_id in tipos_entrada
                mov_detalhada = {
                    'id': mov.id,
                    'data': data_mov_str,
                    'tipo': str(mov.tipo_movimentacao) if mov.tipo_movimentacao else 'N/A',
                    'tipo_codigo': self._get_tipo_codigo(tipo_id),
                    'quantidade': quantidade,
                    'valor_unitario': valor_unitario,
                    'valor_total': valor_total,
                    'documento': mov.documento_referencia or '',
                    'operador': mov.observacoes or '',  # Adaptar conforme estrutura
                    'observacoes': mov.observacoes or '',
                    'is_entrada': is_entrada,
                    'is_saida': not is_entrada
                }
                
                produto_data['movimentacoes_detalhadas'].append(mov_detalhada)
            
            # Busca último preço de entrada para cada produto
            for pid in produtos_ids:
                ultimo_preco_info = self._obter_ultimo_preco_entrada(pid, data_fim)
                produto_data = produtos_movimentados[pid]
                
                # Calcula campos derivados
                quantidade_saida = produto_data['quantidade_saida']
                valor_saida = produto_data['valor_saida']
                ultimo_preco = ultimo_preco_info['preco']
                
                # Valor de saída baseado no preço de entrada
                valor_saida_preco_entrada = quantidade_saida * ultimo_preco
                diferenca_preco = valor_saida - valor_saida_preco_entrada
                
                # Adiciona novos campos obrigatórios
                produto_data.update({
                    'ultimo_preco_entrada': ultimo_preco,
                    'data_ultimo_preco_entrada': ultimo_preco_info['data'],
                    'valor_saida_preco_entrada': round(valor_saida_preco_entrada, 2),
                    'diferenca_preco': round(diferenca_preco, 2),
                    'tem_entrada_anterior': ultimo_preco_info['encontrado'],
                    'saldo_quantidade': produto_data['quantidade_entrada'] - produto_data['quantidade_saida'],
                    'saldo_valor': produto_data['valor_entrada'] - produto_data['valor_saida']
                })
                
                # Adiciona informações de diferença nas saídas detalhadas
                if incluir_detalhes:
                    for mov_det in produto_data['movimentacoes_detalhadas']:
                        if mov_det['is_saida'] and ultimo_preco > 0:
                            mov_det['valor_saida_preco_entrada'] = mov_det['quantidade'] * ultimo_preco
                            mov_det['diferenca_unitaria'] = mov_det['valor_unitario'] - ultimo_preco
            
            # Converte para lista
            resultado = list(produtos_movimentados.values())
            
            # Ordenação
            campo_ordenacao = {
                'valor_saida': lambda x: x['valor_saida'],
                'diferenca_preco': lambda x: x['diferenca_preco'],
                'quantidade_saida': lambda x: x['quantidade_saida'],
                'total_movimentacoes': lambda x: x['total_movimentacoes'],
                'nome': lambda x: x['nome']
            }.get(ordenar_por, lambda x: x['valor_saida'])
            
            resultado.sort(key=campo_ordenacao, reverse=(ordem == 'DESC'))
            
            # Aplica limite se especificado
            if limite:
                try:
                    limite_int = int(limite)
                    resultado = resultado[:limite_int]
                except ValueError:
                    pass
            
            # Remove detalhes se não solicitado
            if not incluir_detalhes:
                for produto in resultado:
                    del produto['movimentacoes_detalhadas']
            
            # Calcula resumo expandido
            resumo = self._calcular_resumo_expandido(resultado, data_inicio, data_fim)
            
            return Response({
                'produtos_movimentados': resultado,
                'resumo': resumo,
                'parametros': {
                    'data_inicio': data_inicio.strftime('%Y-%m-%d'),
                    'data_fim': data_fim.strftime('%Y-%m-%d'),
                    'incluir_detalhes': incluir_detalhes,
                    'limite_aplicado': limite,
                    'produto_id': produto_id,
                    'ordenar_por': ordenar_por,
                    'ordem': ordem
                }
            })
            
        except Exception as e:
            return Response(
                {'error': f'Erro interno: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'])
    def estoque_critico(self, request):
        """Retorna produtos com estoque crítico (baixo) usando a nova metodologia."""
        try:
            data_str = request.query_params.get('data', date.today().strftime('%Y-%m-%d'))
            limite_critico = float(request.query_params.get('limite', '5'))

            try:
                data_final = datetime.strptime(data_str, '%Y-%m-%d').date()
            except ValueError:
                return Response(
                    {'error': 'Formato de data inválido. Use YYYY-MM-DD'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            produtos_ativos = Produtos.objects.filter(ativo=True)
            estoque_critico_list = []

            for produto in produtos_ativos:
                quantidade_na_data = StockCalculationService.calculate_stock_at_date(
                    produto.id, data_final
                )

                if 0 < quantidade_na_data <= Decimal(limite_critico):
                    custo_unitario = produto.preco_custo or Decimal('0')
                    valor_na_data = quantidade_na_data * custo_unitario
                    
                    estoque_critico_list.append({
                        'produto_id': produto.id,
                        'nome': produto.nome,
                        'referencia': produto.referencia,
                        'quantidade_atual': float(quantidade_na_data),
                        'valor_atual': float(valor_na_data),
                        'total_movimentacoes': 0, # Campo legado, precisa de query extra
                    })

            # Ordena por quantidade (menor primeiro)
            estoque_critico_list.sort(key=lambda x: x['quantidade_atual'])

            return Response({
                'produtos': estoque_critico_list,
                'parametros': {
                    'data_consulta': data_final.strftime('%Y-%m-%d'),
                    'limite_critico': limite_critico,
                    'total_produtos_criticos': len(estoque_critico_list)
                }
            })

        except Exception as e:
            return Response(
                {'error': f'Erro interno no servidor: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['get'])
    def produtos_mais_movimentados(self, request):
        """Retorna produtos com mais movimentações em um período."""
        try:
            # Por padrão, analisamos os últimos 30 dias
            data_fim_str = request.query_params.get('data', timezone.now().strftime('%Y-%m-%d'))
            dias = int(request.query_params.get('dias', '30'))
            limite = int(request.query_params.get('limite', '10'))

            try:
                data_fim_naive = datetime.strptime(data_fim_str, '%Y-%m-%d')
                # Torna a data 'aware' usando o fuso horário atual
                data_fim = timezone.make_aware(data_fim_naive, timezone.get_current_timezone())
                # Define o fim do dia para a consulta
                data_fim = data_fim.replace(hour=23, minute=59, second=59, microsecond=999999)
                data_inicio = data_fim - timedelta(days=dias)
            except ValueError:
                return Response(
                    {'error': 'Formato de data inválido. Use YYYY-MM-DD'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Agrega movimentações por produto
            movimentacoes = MovimentacoesEstoque.objects.filter(
                data_movimentacao__gte=data_inicio,
                data_movimentacao__lte=data_fim
            ).values('produto_id').annotate(
                total_movimentacoes=Count('id'),
                ultima_movimentacao=Max('data_movimentacao')
            ).order_by('-total_movimentacoes')[:limite]

            produtos_movimentados = []
            produto_ids = [m['produto_id'] for m in movimentacoes]
            produtos = Produtos.objects.in_bulk(produto_ids)

            for mov in movimentacoes:
                produto = produtos.get(mov['produto_id'])
                if produto:
                    produtos_movimentados.append({
                        'produto_id': produto.id,
                        'nome': produto.nome,
                        'referencia': produto.referencia,
                        'total_movimentacoes': mov['total_movimentacoes'],
                        'ultima_movimentacao': mov['ultima_movimentacao'].strftime('%Y-%m-%d') if mov['ultima_movimentacao'] else None,
                        'tipos_movimentacao': [] # Campo legado, precisa de query extra
                    })

            return Response({
                'produtos_mais_movimentados': produtos_movimentados,
                'parametros': {
                    'data_consulta': data_fim.strftime('%Y-%m-%d'),
                    'periodo_dias': dias,
                    'limite': limite,
                }
            })

        except Exception as e:
            return Response(
                {'error': f'Erro interno no servidor: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'])
    def valor_total_estoque(self, request):
        """
        Calcula e retorna o valor total do estoque para todos os produtos ativos.
        Este endpoint pode ser lento e deve ser usado com moderação.
        """
        try:
            data_str = request.query_params.get('data', date.today().strftime('%Y-%m-%d'))
            
            try:
                data_final = datetime.strptime(data_str, '%Y-%m-%d').date()
            except ValueError:
                return Response(
                    {'error': 'Formato de data inválido. Use YYYY-MM-DD'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            todos_produtos = Produtos.objects.filter(ativo=True)
            valor_total_estoque = Decimal('0')
            produtos_processados = 0
            produtos_com_erro = 0

            for produto in todos_produtos:
                try:
                    quantidade_na_data = StockCalculationService.calculate_stock_at_date(
                        produto.id, data_final
                    )
                    custo_unitario = produto.preco_custo or Decimal('0')
                    valor_produto = quantidade_na_data * custo_unitario
                    valor_total_estoque += valor_produto
                    produtos_processados += 1
                except Exception:
                    produtos_com_erro += 1
            
            return Response({
                'valor_total_estoque': round(float(valor_total_estoque), 2),
                'data_calculo': data_final.strftime('%Y-%m-%d'),
                'total_produtos_processados': produtos_processados,
                'total_produtos_ativos': todos_produtos.count(),
                'produtos_com_erro_calculo': produtos_com_erro,
            })

        except Exception as e:
            return Response(
                {'error': f'Erro interno no servidor: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['get'])
    def valor_estoque_por_grupo(self, request):
        """
        Calcula e retorna o valor total do estoque agrupado por grupo de produto.
        """
        try:
            data_str = request.query_params.get('data', date.today().strftime('%Y-%m-%d'))
            
            try:
                data_final = datetime.strptime(data_str, '%Y-%m-%d').date()
            except ValueError:
                return Response(
                    {'error': 'Formato de data inválido. Use YYYY-MM-DD'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            todos_produtos = Produtos.objects.filter(ativo=True)
            estoque_por_grupo = defaultdict(Decimal)

            for produto in todos_produtos:
                try:
                    quantidade_na_data = StockCalculationService.calculate_stock_at_date(
                        produto.id, data_final
                    )
                    custo_unitario = produto.preco_custo or Decimal('0')
                    valor_produto = quantidade_na_data * custo_unitario
                    
                    grupo_id = produto.grupo_id if produto.grupo_id is not None else 0
                    estoque_por_grupo[grupo_id] += valor_produto
                except Exception:
                    # Ignora produtos com erro no cálculo
                    continue
            
            # Busca os nomes dos grupos
            grupo_ids = list(estoque_por_grupo.keys())
            if 0 in grupo_ids:
                grupo_ids.remove(0) # Não busca o grupo com ID 0

            grupos = Grupos.objects.filter(id__in=grupo_ids)
            grupo_map = {grupo.id: grupo.nome for grupo in grupos}
            grupo_map[0] = "Sem Grupo" # Adiciona o nome para o grupo padrão

            # Formata o resultado final
            resultado = []
            for grupo_id, valor_total in estoque_por_grupo.items():
                resultado.append({
                    'grupo_id': grupo_id,
                    'grupo_nome': grupo_map.get(grupo_id, f"Grupo Desconhecido ({grupo_id})"),
                    'valor_total_estoque': round(float(valor_total), 2)
                })

            # Ordena o resultado pelo valor (maior primeiro)
            resultado.sort(key=lambda x: x['valor_total_estoque'], reverse=True)

            return Response({
                'estoque_por_grupo': resultado,
                'data_calculo': data_final.strftime('%Y-%m-%d'),
            })

        except Exception as e:
            return Response(
                {'error': f'Erro interno no servidor: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def _obter_ultimo_preco_entrada(self, produto_id, data_limite):
        """
        Busca o último preço de entrada do produto, mesmo anterior ao período
        """
        tipos_entrada = [1, 3]  # Entrada e Estoque Inicial
        
        # Busca última entrada com valor > 0 até a data limite
        ultima_entrada = MovimentacoesEstoque.objects.filter(
            produto_id=produto_id,
            tipo_movimentacao__id__in=tipos_entrada,
            quantidade__gt=0,
            custo_unitario__gt=0,
            data_movimentacao__date__lte=data_limite
        ).order_by('-data_movimentacao', '-id').first()
        
        if ultima_entrada:
            return {
                'preco': float(ultima_entrada.custo_unitario),
                'data': ultima_entrada.data_movimentacao.strftime('%Y-%m-%d %H:%M:%S'),
                'documento': ultima_entrada.documento_referencia or '',
                'encontrado': True
            }
        
        return {
            'preco': 0.0,
            'data': None,
            'documento': '',
            'encontrado': False
        }
    
    def _get_tipo_codigo(self, tipo_id):
        """Converte ID do tipo para código legível"""
        tipos = {
            1: 'ENT',
            2: 'SAI', 
            3: 'EST_INICIAL'
        }
        return tipos.get(tipo_id, 'DESCONHECIDO')
    
    def _calcular_resumo_expandido(self, produtos, data_inicio, data_fim):
        """Calcula resumo expandido com todos os campos obrigatórios"""
        if not produtos:
            return self._resumo_vazio(data_inicio, data_fim, False, None)['resumo']
        
        total_produtos = len(produtos)
        total_movimentacoes = sum(p['total_movimentacoes'] for p in produtos)
        valor_total_entradas = sum(p['valor_entrada'] for p in produtos)
        valor_total_saidas = sum(p['valor_saida'] for p in produtos)
        valor_total_saidas_preco_entrada = sum(p['valor_saida_preco_entrada'] for p in produtos)
        quantidade_total_entradas = sum(p['quantidade_entrada'] for p in produtos)
        quantidade_total_saidas = sum(p['quantidade_saida'] for p in produtos)
        produtos_com_entrada = sum(1 for p in produtos if p['tem_entrada_anterior'])
        
        diferenca_total_precos = valor_total_saidas - valor_total_saidas_preco_entrada
        margem_total = 0
        if valor_total_saidas_preco_entrada > 0:
            margem_total = (diferenca_total_precos / valor_total_saidas_preco_entrada) * 100
        
        return {
            'periodo': f"{data_inicio.strftime('%Y-%m-%d')} a {data_fim.strftime('%Y-%m-%d')}",
            'total_produtos': total_produtos,
            'total_movimentacoes': total_movimentacoes,
            'valor_total_entradas': round(valor_total_entradas, 2),
            'valor_total_saidas': round(valor_total_saidas, 2),
            'valor_total_saidas_preco_entrada': round(valor_total_saidas_preco_entrada, 2),
            'diferenca_total_precos': round(diferenca_total_precos, 2),
            'margem_total': round(margem_total, 2),
            'saldo_periodo': round(valor_total_entradas - valor_total_saidas, 2),
            'quantidade_total_entradas': round(quantidade_total_entradas, 2),
            'quantidade_total_saidas': round(quantidade_total_saidas, 2),
            'produtos_com_entrada_anterior': produtos_com_entrada,
            'produtos_sem_entrada_anterior': total_produtos - produtos_com_entrada
        }
    
    def _resumo_vazio(self, data_inicio, data_fim, incluir_detalhes, limite):
        """Retorna estrutura vazia quando não há movimentações"""
        return {
            'produtos_movimentados': [],
            'resumo': {
                'periodo': f"{data_inicio.strftime('%Y-%m-%d')} a {data_fim.strftime('%Y-%m-%d')}",
                'total_produtos': 0,
                'total_movimentacoes': 0,
                'valor_total_entradas': 0.0,
                'valor_total_saidas': 0.0,
                'valor_total_saidas_preco_entrada': 0.0,
                'diferenca_total_precos': 0.0,
                'margem_total': 0.0,
                'saldo_periodo': 0.0,
                'quantidade_total_entradas': 0.0,
                'quantidade_total_saidas': 0.0,
                'produtos_com_entrada_anterior': 0,
                'produtos_sem_entrada_anterior': 0
            },
            'parametros': {
                'data_inicio': data_inicio.strftime('%Y-%m-%d'),
                'data_fim': data_fim.strftime('%Y-%m-%d'),
                'incluir_detalhes': incluir_detalhes,
                'limite_aplicado': limite
            }
        }
    
    # ========================================
    # HISTORICAL STOCK CALCULATION ENDPOINTS
    # ========================================
    
    @action(detail=False, methods=['get'])
    def calculate_historical_stock(self, request):
        """
        Calculate historical stock for a product at a specific date.
        
        Purpose: Calculate what the stock level was at any historical date
        using movement history and stock resets ("000000" movements).
        
        Parameters:
        - produto_id (required): ID of the product
        - data (required): Date in YYYY-MM-DD format
        
        Returns historical stock calculation based on movements and resets.
        """
        try:
            # Get parameters
            produto_id = request.query_params.get('produto_id')
            data_str = request.query_params.get('data')
            
            # Validate required parameters
            if not produto_id:
                return Response(
                    {'error': 'Parameter produto_id is required'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            if not data_str:
                return Response(
                    {'error': 'Parameter data is required (format: YYYY-MM-DD)'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Validate produto_id
            try:
                produto_id = int(produto_id)
            except ValueError:
                return Response(
                    {'error': 'produto_id must be a valid integer'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Validate and parse date
            try:
                target_date = datetime.strptime(data_str, '%Y-%m-%d').date()
            except ValueError:
                return Response(
                    {'error': 'Invalid date format. Use YYYY-MM-DD'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Ensure target date is not in the future
            if target_date > date.today():
                return Response(
                    {'error': 'Cannot calculate stock for future dates'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Calculate historical stock
            try:
                historical_stock = StockCalculationService.calculate_stock_at_date(
                    produto_id, target_date
                )
                
                # Get product information
                try:
                    produto = Produtos.objects.get(id=produto_id)
                    produto_info = {
                        'id': produto.id,
                        'codigo': produto.codigo,
                        'nome': produto.nome,
                        'ativo': produto.ativo,
                        'current_stock': float(produto.estoque_atual or 0)
                    }
                except Produtos.DoesNotExist:
                    return Response(
                        {'error': f'Product with ID {produto_id} not found'},
                        status=status.HTTP_404_NOT_FOUND
                    )
                
                # Get stock reset information for context
                base_stock, reset_date = StockCalculationService.get_base_stock_reset(
                    produto_id, datetime.combine(target_date, datetime.max.time())
                )
                
                return Response({
                    'produto': produto_info,
                    'historical_calculation': {
                        'target_date': target_date.strftime('%Y-%m-%d'),
                        'historical_stock': float(historical_stock),
                        'calculation_method': 'movements_and_resets'
                    },
                    'calculation_basis': {
                        'has_stock_reset': reset_date is not None,
                        'reset_date': reset_date.isoformat() if reset_date else None,
                        'reset_quantity': float(base_stock) if reset_date else None,
                        'base_calculation': 'reset_quantity' if reset_date else 'zero_start'
                    }
                })
                
            except ValueError as e:
                return Response(
                    {'error': str(e)},
                    status=status.HTTP_400_BAD_REQUEST
                )
            except Exception as e:
                return Response(
                    {'error': f'Error calculating historical stock: {str(e)}'},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
                
        except Exception as e:
            return Response(
                {'error': f'Internal server error: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'])
    def stock_movements_analysis(self, request):
        """
        Analyze stock movements for products over a specified period.
        
        Purpose: Provide detailed analysis of stock movements, including
        entries, exits, and stock resets for reporting and audit purposes.
        
        Parameters:
        - produto_ids (optional): Comma-separated list of product IDs
        - start_date (required): Start date in YYYY-MM-DD format
        - end_date (required): End date in YYYY-MM-DD format
        - limit (optional): Maximum number of products to analyze (default: 50)
        
        Returns movement analysis for the specified period.
        """
        try:
            # Get parameters
            produto_ids_str = request.query_params.get('produto_ids')
            start_date_str = request.query_params.get('start_date')
            end_date_str = request.query_params.get('end_date')
            limit_str = request.query_params.get('limit', '50')
            
            # Validate required parameters
            if not start_date_str or not end_date_str:
                return Response(
                    {'error': 'Parameters start_date and end_date are required (format: YYYY-MM-DD)'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Parse and validate dates
            try:
                start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
                end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
            except ValueError:
                return Response(
                    {'error': 'Invalid date format. Use YYYY-MM-DD'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            if start_date > end_date:
                return Response(
                    {'error': 'start_date must be before or equal to end_date'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Parse produto_ids if provided
            produto_ids = None
            if produto_ids_str:
                try:
                    produto_ids = [int(pid.strip()) for pid in produto_ids_str.split(',')]
                except ValueError:
                    return Response(
                        {'error': 'produto_ids must be comma-separated integers'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            
            # Parse limit
            try:
                limit = int(limit_str)
                if limit <= 0 or limit > 500:
                    limit = 50
            except ValueError:
                limit = 50
            
            # Get products to analyze
            if produto_ids:
                produtos = Produtos.objects.filter(id__in=produto_ids, ativo=True)
            else:
                produtos = Produtos.objects.filter(ativo=True)[:limit]
            
            # Analyze movements for each product
            analysis_results = []
            for produto in produtos:
                try:
                    movement_summary = StockCalculationService.get_stock_movements_summary(
                        produto.id, start_date, end_date
                    )
                    
                    # Calculate stock at start and end of period
                    stock_at_start = StockCalculationService.calculate_stock_at_date(produto.id, start_date)
                    stock_at_end = StockCalculationService.calculate_stock_at_date(produto.id, end_date)
                    
                    analysis_results.append({
                        'produto': {
                            'id': produto.id,
                            'codigo': produto.codigo,
                            'nome': produto.nome,
                            'current_stock': float(produto.estoque_atual or 0)
                        },
                        'period_analysis': {
                            'start_date': start_date.strftime('%Y-%m-%d'),
                            'end_date': end_date.strftime('%Y-%m-%d'),
                            'stock_at_start': float(stock_at_start),
                            'stock_at_end': float(stock_at_end),
                            'net_change': float(stock_at_end - stock_at_start)
                        },
                        'movements': {
                            'total_movements': len(movement_summary['stock_resets']) + len(movement_summary['regular_movements']),
                            'regular_movements': len(movement_summary['regular_movements']),
                            'stock_resets': len(movement_summary['stock_resets']),
                            'totals': {
                                'entrada': float(movement_summary['totals']['entrada']),
                                'saida': float(movement_summary['totals']['saida']),
                                'net_movement': float(movement_summary['totals']['net_movement'])
                            }
                        }
                    })
                    
                except Exception as e:
                    # Skip products with errors but log them
                    analysis_results.append({
                        'produto': {
                            'id': produto.id,
                            'codigo': produto.codigo,
                            'nome': produto.nome
                        },
                        'error': str(e)
                    })
            
            return Response({
                'analysis_results': analysis_results,
                'summary': {
                    'period': {
                        'start_date': start_date.strftime('%Y-%m-%d'),
                        'end_date': end_date.strftime('%Y-%m-%d'),
                        'days_analyzed': (end_date - start_date).days + 1
                    },
                    'products_analyzed': len(analysis_results),
                    'products_with_movements': len([r for r in analysis_results if 'movements' in r and r['movements']['total_movements'] > 0])
                },
                'parameters': {
                    'produto_ids_requested': len(produto_ids) if produto_ids else None,
                    'limit_applied': limit,
                    'analysis_timestamp': datetime.now().isoformat()
                }
            })
            
        except Exception as e:
            return Response(
                {'error': f'Internal server error: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'])
    def stock_timeline(self, request):
        """
        Generate a timeline of stock levels for a product over a date range.
        
        Purpose: Show how stock levels changed over time for analysis,
        reporting, and audit purposes.
        
        Parameters:
        - produto_id (required): ID of the product
        - start_date (required): Start date in YYYY-MM-DD format
        - end_date (required): End date in YYYY-MM-DD format
        - interval (optional): 'daily', 'weekly', 'monthly' (default: 'daily')
        
        Returns timeline of stock levels at specified intervals.
        """
        try:
            # Get parameters
            produto_id = request.query_params.get('produto_id')
            start_date_str = request.query_params.get('start_date')
            end_date_str = request.query_params.get('end_date')
            interval = request.query_params.get('interval', 'daily')
            
            # Validate required parameters
            if not produto_id:
                return Response(
                    {'error': 'Parameter produto_id is required'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            if not start_date_str or not end_date_str:
                return Response(
                    {'error': 'Parameters start_date and end_date are required (format: YYYY-MM-DD)'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Validate produto_id
            try:
                produto_id = int(produto_id)
            except ValueError:
                return Response(
                    {'error': 'produto_id must be a valid integer'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Parse and validate dates
            try:
                start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
                end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
            except ValueError:
                return Response(
                    {'error': 'Invalid date format. Use YYYY-MM-DD'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            if start_date > end_date:
                return Response(
                    {'error': 'start_date must be before or equal to end_date'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Validate interval
            if interval not in ['daily', 'weekly', 'monthly']:
                return Response(
                    {'error': 'interval must be daily, weekly, or monthly'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Get product information
            try:
                produto = Produtos.objects.get(id=produto_id)
            except Produtos.DoesNotExist:
                return Response(
                    {'error': f'Product with ID {produto_id} not found'},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Generate timeline points
            timeline_points = []
            current_date = start_date
            
            # Determine date increment based on interval
            if interval == 'daily':
                delta = timedelta(days=1)
                max_points = 365  # Limit to prevent excessive data
            elif interval == 'weekly':
                delta = timedelta(weeks=1)
                max_points = 104  # ~2 years
            else:  # monthly
                delta = timedelta(days=30)  # Approximate month
                max_points = 60   # ~5 years
            
            point_count = 0
            while current_date <= end_date and point_count < max_points:
                try:
                    stock_level = StockCalculationService.calculate_stock_at_date(produto_id, current_date)
                    timeline_points.append({
                        'date': current_date.strftime('%Y-%m-%d'),
                        'stock_level': float(stock_level)
                    })
                except Exception as e:
                    # Skip dates with calculation errors
                    timeline_points.append({
                        'date': current_date.strftime('%Y-%m-%d'),
                        'stock_level': None,
                        'error': str(e)
                    })
                
                current_date += delta
                point_count += 1
            
            # Calculate summary statistics
            valid_points = [p for p in timeline_points if p.get('stock_level') is not None]
            if valid_points:
                stock_levels = [p['stock_level'] for p in valid_points]
                min_stock = min(stock_levels)
                max_stock = max(stock_levels)
                avg_stock = sum(stock_levels) / len(stock_levels)
            else:
                min_stock = max_stock = avg_stock = 0
            
            return Response({
                'produto': {
                    'id': produto.id,
                    'codigo': produto.codigo,
                    'nome': produto.nome,
                    'current_stock': float(produto.estoque_atual or 0)
                },
                'timeline': {
                    'period': {
                        'start_date': start_date.strftime('%Y-%m-%d'),
                        'end_date': end_date.strftime('%Y-%m-%d'),
                        'interval': interval
                    },
                    'points': timeline_points,
                    'statistics': {
                        'total_points': len(timeline_points),
                        'valid_points': len(valid_points),
                        'min_stock': min_stock,
                        'max_stock': max_stock,
                        'avg_stock': round(avg_stock, 2)
                    }
                }
            })
            
        except Exception as e:
            return Response(
                {'error': f'Internal server error: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'])
    def stock_resets_report(self, request):
        """
        Generate report of stock resets for analysis and audit purposes.
        
        Purpose: Analyze stock reset patterns and provide insights into
        when and how stock levels were reset using "000000" movements.
        
        Parameters:
        - produto_ids (optional): Comma-separated list of product IDs
        - start_date (optional): Start date for reset analysis (YYYY-MM-DD)
        - end_date (optional): End date for reset analysis (YYYY-MM-DD)
        - limit (optional): Maximum number of products to analyze (default: 100)
        
        Returns analysis of stock resets and their impact.
        """
        try:
            # Get parameters
            produto_ids_str = request.query_params.get('produto_ids')
            start_date_str = request.query_params.get('start_date')
            end_date_str = request.query_params.get('end_date')
            limit_str = request.query_params.get('limit', '100')
            
            # Parse dates if provided
            start_date = None
            end_date = None
            if start_date_str:
                try:
                    start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
                except ValueError:
                    return Response(
                        {'error': 'Invalid start_date format. Use YYYY-MM-DD'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            
            if end_date_str:
                try:
                    end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
                except ValueError:
                    return Response(
                        {'error': 'Invalid end_date format. Use YYYY-MM-DD'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            
            if start_date and end_date and start_date > end_date:
                return Response(
                    {'error': 'start_date must be before or equal to end_date'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Parse produto_ids if provided
            produto_ids = None
            if produto_ids_str:
                try:
                    produto_ids = [int(pid.strip()) for pid in produto_ids_str.split(',')]
                except ValueError:
                    return Response(
                        {'error': 'produto_ids must be comma-separated integers'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            
            # Parse limit
            try:
                limit = int(limit_str)
                if limit <= 0 or limit > 500:
                    limit = 100
            except ValueError:
                limit = 100
            
            # Build query for stock resets
            reset_query = MovimentacoesEstoque.objects.filter(
                documento_referencia='000000'
            ).select_related('produto', 'tipo_movimentacao')
            
            # Apply filters
            if produto_ids:
                reset_query = reset_query.filter(produto_id__in=produto_ids)
            
            if start_date:
                reset_query = reset_query.filter(data_movimentacao__date__gte=start_date)
            
            if end_date:
                reset_query = reset_query.filter(data_movimentacao__date__lte=end_date)
            
            # Get resets ordered by date
            resets = reset_query.order_by('-data_movimentacao')
            
            # Group by product
            products_with_resets = {}
            for reset in resets:
                produto_id = reset.produto.id
                if produto_id not in products_with_resets:
                    products_with_resets[produto_id] = {
                        'produto': {
                            'id': reset.produto.id,
                            'codigo': reset.produto.codigo,
                            'nome': reset.produto.nome,
                            'current_stock': float(reset.produto.estoque_atual or 0)
                        },
                        'resets': []
                    }
                
                products_with_resets[produto_id]['resets'].append({
                    'date': reset.data_movimentacao.date().strftime('%Y-%m-%d'),
                    'quantity': float(reset.quantidade),
                    'movement_type': reset.tipo_movimentacao.descricao if reset.tipo_movimentacao else 'N/A'
                })
            
            # Convert to list and apply limit
            reset_analysis = list(products_with_resets.values())[:limit]
            
            # Calculate summary statistics
            total_resets = resets.count()
            products_with_resets_count = len(products_with_resets)
            
            # Date range of resets
            if resets.exists():
                first_reset = resets.order_by('data_movimentacao').first()
                last_reset = resets.order_by('-data_movimentacao').first()
                reset_date_range = {
                    'earliest': first_reset.data_movimentacao.date().strftime('%Y-%m-%d'),
                    'latest': last_reset.data_movimentacao.date().strftime('%Y-%m-%d')
                }
            else:
                reset_date_range = None
            
            return Response({
                'reset_analysis': reset_analysis,
                'summary': {
                    'total_resets': total_resets,
                    'products_with_resets': products_with_resets_count,
                    'products_returned': len(reset_analysis),
                    'reset_date_range': reset_date_range,
                    'analysis_period': {
                        'start_date': start_date.strftime('%Y-%m-%d') if start_date else None,
                        'end_date': end_date.strftime('%Y-%m-%d') if end_date else None
                    }
                },
                'parameters': {
                    'produto_ids_requested': len(produto_ids) if produto_ids else None,
                    'limit_aplicado': limit,
                    'report_timestamp': datetime.now().isoformat()
                }
            })
            
        except Exception as e:
            return Response(
                {'error': f'Internal server error: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'])
    def product_stock_history(self, request):
        """
        Get comprehensive stock history for a single product.
        
        Purpose: Provide detailed historical analysis of a product's stock
        movements, resets, and calculated levels over time for reporting
        and audit purposes.
        
        Parameters:
        - produto_id (required): ID of the product
        - days_history (optional): Number of days of history to include (default: 90)
        - include_movements (optional): Include detailed movement list (default: true)
        
        Returns comprehensive stock history for the product.
        """
        try:
            # Get parameters
            produto_id = request.query_params.get('produto_id')
            days_history_str = request.query_params.get('days_history', '90')
            include_movements_str = request.query_params.get('include_movements', 'true')
            
            # Validate required parameters
            if not produto_id:
                return Response(
                    {'error': 'Parameter produto_id is required'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Validate produto_id
            try:
                produto_id = int(produto_id)
            except ValueError:
                return Response(
                    {'error': 'produto_id must be a valid integer'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Parse days_history
            try:
                days_history = int(days_history_str)
                if days_history <= 0 or days_history > 1095:  # Max 3 years
                    days_history = 90
            except ValueError:
                days_history = 90
            
            # Parse include_movements
            include_movements = include_movements_str.lower() in ['true', '1', 'yes']
            
            # Get product information
            try:
                produto = Produtos.objects.get(id=produto_id)
            except Produtos.DoesNotExist:
                return Response(
                    {'error': f'Product with ID {produto_id} not found'},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Calculate date range
            end_date = date.today()
            start_date = end_date - timedelta(days=days_history)
            
            # Get movement summary
            movement_summary = StockCalculationService.get_stock_movements_summary(
                produto_id, start_date, end_date
            )
            
            # Calculate stock at key points
            stock_at_start = StockCalculationService.calculate_stock_at_date(produto_id, start_date)
            stock_at_end = StockCalculationService.calculate_stock_at_date(produto_id, end_date)
            
            # Get stock reset information
            base_stock, most_recent_reset = StockCalculationService.get_base_stock_reset(
                produto_id, datetime.combine(end_date, datetime.max.time())
            )
            
            # Build response
            response_data = {
                'produto': {
                    'id': produto.id,
                    'codigo': produto.codigo,
                    'nome': produto.nome,
                    'current_stock': float(produto.estoque_atual or 0),
                    'ativo': produto.ativo
                },
                'analysis_period': {
                    'start_date': start_date.strftime('%Y-%m-%d'),
                    'end_date': end_date.strftime('%Y-%m-%d'),
                    'days_analyzed': days_history
                },
                'stock_levels': {
                    'stock_at_period_start': float(stock_at_start),
                    'stock_at_period_end': float(stock_at_end),
                    'current_stock_from_table': float(produto.estoque_atual or 0),
                    'net_change_in_period': float(stock_at_end - stock_at_start)
                },
                'stock_reset_info': {
                    'has_recent_reset': most_recent_reset is not None,
                    'most_recent_reset_date': most_recent_reset.isoformat() if most_recent_reset else None,
                    'reset_quantity': float(base_stock) if most_recent_reset else None,
                    'total_resets_in_period': len(movement_summary['stock_resets'])
                },
                'movement_summary': {
                    'total_movements': len(movement_summary['stock_resets']) + len(movement_summary['regular_movimentos']),
                    'regular_movements': len(movement_summary['regular_movimentos']),
                    'stock_resets': len(movement_summary['stock_resets']),
                    'totals': {
                        'entrada': float(movement_summary['totals']['entrada']),
                        'saida': float(movement_summary['totals']['saida']),
                        'net_movement': float(movement_summary['totals']['net_movement'])
                    }
                }
            }
            
            # Include detailed movements if requested
            if include_movements:
                response_data['detailed_movements'] = {
                    'stock_resets': movement_summary['stock_resets'],
                    'regular_movements': movement_summary['regular_movimentos']
                }
            
            response_data['metadata'] = {
                'analysis_timestamp': datetime.now().isoformat(),
                'include_movements': include_movements
            }
            
            return Response(response_data)
            
        except Exception as e:
            return Response(
                {'error': f'Internal server error: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'])
    def produtos_criticos(self, request):
        """Retorna produtos com estoque crítico (baixo) usando a nova metodologia."""
        try:
            data_str = request.query_params.get('data', date.today().strftime('%Y-%m-%d'))
            limite_critico = float(request.query_params.get('limite', '5'))

            try:
                data_final = datetime.strptime(data_str, '%Y-%m-%d').date()
            except ValueError:
                return Response(
                    {'error': 'Formato de data inválido. Use YYYY-MM-DD'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            produtos_ativos = Produtos.objects.filter(ativo=True)
            estoque_critico_list = []

            for produto in produtos_ativos:
                quantidade_na_data = StockCalculationService.calculate_stock_at_date(
                    produto.id, data_final
                )

                if 0 < quantidade_na_data <= Decimal(limite_critico):
                    custo_unitario = produto.preco_custo or Decimal('0')
                    valor_na_data = quantidade_na_data * custo_unitario

                    estoque_critico_list.append({
                        'produto_id': produto.id,
                        'nome': produto.nome,
                        'referencia': produto.referencia,
                        'quantidade_atual': float(quantidade_na_data),
                        'valor_atual': float(valor_na_data),
                        'total_movimentacoes': 0, # Campo legado, precisa de query extra
                    })

            # Ordena por quantidade (menor primeiro)
            estoque_critico_list.sort(key=lambda x: x['quantidade_atual'])

            return Response({
                'produtos': estoque_critico_list,
                'parametros': {
                    'data_consulta': data_final.strftime('%Y-%m-%d'),
                    'limite_critico': limite_critico,
                    'total_produtos_criticos': len(estoque_critico_list)
                }
            })

        except Exception as e:
            return Response(
                {'error': f'Erro interno no servidor: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            ) 
 