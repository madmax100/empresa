# contas/views/estoque_views.py
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q, Sum, F
from datetime import datetime, date
from decimal import Decimal
from collections import defaultdict

from ..models.access import MovimentacoesEstoque, Produtos, EstoqueInicial, Grupos


class EstoqueViewSet(viewsets.ViewSet):
    """ViewSet para controle de estoque com base no estoque inicial de 2025"""
    
    def _carregar_estoque_inicial(self):
        """Carrega o estoque inicial de 01/01/2025 da tabela EstoqueInicial"""
        estoque_inicial = {}
        
        # Usar tabela específica de estoque inicial
        estoques_iniciais = EstoqueInicial.objects.filter(
            data_inicial=date(2025, 1, 1)
        ).select_related('produto')
        
        for est in estoques_iniciais:
            produto_id = est.produto.id
            
            estoque_inicial[produto_id] = {
                'produto_id': produto_id,
                'quantidade_inicial': est.quantidade_inicial,
                'custo_unitario': est.valor_unitario_inicial,
                'valor_total_inicial': est.valor_total_inicial,
                'data_inicial': est.data_inicial,
                'documento': 'EST_INICIAL_2025'
            }
            
        return estoque_inicial
    
    def _carregar_movimentacoes(self, data_final):
        """Carrega todas as movimentações até a data especificada"""
        movimentacoes = defaultdict(list)
        
        movs = MovimentacoesEstoque.objects.filter(
            data_movimentacao__date__gt='2025-01-01',
            data_movimentacao__date__lte=data_final
        ).exclude(
            documento_referencia='EST_INICIAL_2025'
        ).select_related('produto').order_by('data_movimentacao')
        
        for mov in movs:
            produto_id = mov.produto if isinstance(mov.produto, int) else mov.produto.id
            
            movimentacoes[produto_id].append({
                'id': mov.id,
                'data': mov.data_movimentacao.date(),
                'quantidade': mov.quantidade,
                'tipo_movimentacao': mov.tipo_movimentacao,
                'custo_unitario': mov.custo_unitario,
                'valor_total': mov.valor_total,
                'documento': mov.documento_referencia,
                'observacoes': mov.observacoes
            })
            
        return movimentacoes
    
    def _calcular_estoque_produto(self, produto_id, dados_iniciais, movimentacoes_produto, data_final):
        """Calcula o estoque atual de um produto específico"""
        quantidade_atual = dados_iniciais['quantidade_inicial']
        valor_total_atual = dados_iniciais['valor_total_inicial']
        
        # Aplica as movimentações
        for mov in movimentacoes_produto:
            if mov['data'] <= data_final:
                # Obtém o ID do tipo de movimentação
                tipo_id = mov['tipo_movimentacao'].id if mov['tipo_movimentacao'] else 0
                
                # Tipo 1 = Entrada, Tipo 2 = Saída, Tipo 3 = Estoque Inicial
                if tipo_id in [1, 3]:  # Entrada ou Estoque Inicial
                    quantidade_atual += mov['quantidade']
                    valor_total_atual += mov['valor_total']
                elif tipo_id == 2:  # Saída
                    quantidade_atual -= mov['quantidade']
                    valor_total_atual -= mov['valor_total']
        
        return quantidade_atual, valor_total_atual
    
    @action(detail=False, methods=['get'])
    def estoque_atual(self, request):
        """Retorna o estoque atual até uma data específica"""
        try:
            # Parâmetros
            data_str = request.query_params.get('data', date.today().strftime('%Y-%m-%d'))
            produto_id = request.query_params.get('produto_id')
            limite = int(request.query_params.get('limite', '0'))  # Limite de registros (0 = todos)
            
            # Converte data
            try:
                data_final = datetime.strptime(data_str, '%Y-%m-%d').date()
            except ValueError:
                return Response(
                    {'error': 'Formato de data inválido. Use YYYY-MM-DD'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Carrega dados
            estoque_inicial = self._carregar_estoque_inicial()
            movimentacoes = self._carregar_movimentacoes(data_final)
            
            resultado = []
            
            # Se produto específico foi solicitado
            if produto_id:
                try:
                    produto_id = int(produto_id)
                    if produto_id not in estoque_inicial:
                        return Response(
                            {'error': f'Produto {produto_id} não encontrado no estoque inicial'},
                            status=status.HTTP_404_NOT_FOUND
                        )
                    
                    produtos_calcular = {produto_id: estoque_inicial[produto_id]}
                except ValueError:
                    return Response(
                        {'error': 'ID do produto deve ser um número'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            else:
                produtos_calcular = estoque_inicial
                # Limita resultados se não for produto específico
                if limite > 0:
                    produtos_ids = list(produtos_calcular.keys())[:limite]
                    produtos_calcular = {pid: produtos_calcular[pid] for pid in produtos_ids}
            
            # Calcula estoque para produtos selecionados
            for pid, dados_iniciais in produtos_calcular.items():
                try:
                    movs_produto = movimentacoes.get(pid, [])
                    quantidade_atual, valor_atual = self._calcular_estoque_produto(
                        pid, dados_iniciais, movs_produto, data_final
                    )
                    
                    # Busca informações do produto com grupo
                    try:
                        produto = Produtos.objects.select_related().get(id=pid)
                        nome_produto = produto.nome or f"Produto ID {pid}"
                        referencia = produto.referencia or "N/A"
                        
                        # Buscar informações do grupo
                        if produto.grupo_id:
                            try:
                                grupo = Grupos.objects.get(id=produto.grupo_id)
                                nome_grupo = grupo.nome
                                grupo_id = grupo.id
                            except Grupos.DoesNotExist:
                                nome_grupo = "Sem Grupo"
                                grupo_id = None
                        else:
                            nome_grupo = "Sem Grupo"
                            grupo_id = None
                            
                    except Produtos.DoesNotExist:
                        nome_produto = f"Produto ID {pid}"
                        referencia = "N/A"
                        nome_grupo = "Sem Grupo"
                        grupo_id = None
                    
                    # Serializa movimentações recentes para JSON
                    movimentacoes_serializadas = []
                    if movs_produto:
                        for mov in movs_produto[-3:]:  # Últimas 3
                            try:
                                mov_serializada = {
                                    'data': mov.data.strftime('%Y-%m-%d') if hasattr(mov, 'data') and mov.data else 'N/A',
                                    'tipo': mov.tipo.nome if hasattr(mov, 'tipo') and mov.tipo else 'N/A',
                                    'quantidade': float(mov.quantidade) if hasattr(mov, 'quantidade') else 0.0,
                                    'valor_unitario': float(mov.valor_unitario) if hasattr(mov, 'valor_unitario') else 0.0,
                                    'valor_total': float(mov.valor_total) if hasattr(mov, 'valor_total') else 0.0,
                                    'observacoes': str(mov.observacoes) if hasattr(mov, 'observacoes') and mov.observacoes else 'N/A'
                                }
                                movimentacoes_serializadas.append(mov_serializada)
                            except Exception as e:
                                # Se erro ao serializar movimentação, adiciona erro
                                movimentacoes_serializadas.append({
                                    'erro': f'Erro ao serializar movimentação: {str(e)}'
                                })
                    
                    resultado.append({
                        'produto_id': pid,
                        'nome': nome_produto,
                        'referencia': referencia,
                        'grupo_id': grupo_id,
                        'grupo_nome': nome_grupo,
                        'quantidade_inicial': float(dados_iniciais['quantidade_inicial']),
                        'quantidade_atual': float(quantidade_atual),
                        'variacao_quantidade': float(quantidade_atual - dados_iniciais['quantidade_inicial']),
                        'custo_unitario_inicial': float(dados_iniciais['custo_unitario']),
                        'valor_inicial': float(dados_iniciais['valor_total_inicial']),
                        'valor_atual': float(valor_atual),
                        'variacao_valor': float(valor_atual - dados_iniciais['valor_total_inicial']),
                        'total_movimentacoes': len(movs_produto),
                        'data_calculo': data_final.strftime('%Y-%m-%d'),
                        'movimentacoes_recentes': movimentacoes_serializadas
                    })
                except Exception as e:
                    # Se erro em produto específico, continua com próximo
                    print(f"Erro ao processar produto {pid}: {str(e)}")
                    continue
            
            # Ordenar resultado apenas se não for muitos produtos
            if not produto_id and len(resultado) <= 1000:
                ordem = request.query_params.get('ordem', 'nome')
                reverso = request.query_params.get('reverso', 'false').lower() == 'true'
                
                if ordem in ['nome', 'quantidade_atual', 'valor_atual', 'total_movimentacoes']:
                    try:
                        resultado.sort(key=lambda x: x[ordem], reverse=reverso)
                    except (KeyError, TypeError):
                        # Se houver erro na ordenação, usar ordenação padrão por nome
                        resultado.sort(key=lambda x: str(x['nome']), reverse=False)
            
            # Estatísticas gerais (se não for produto específico)
            estatisticas = None
            if not produto_id:
                try:
                    total_produtos = len(resultado)
                    produtos_com_estoque = len([p for p in resultado if p['quantidade_atual'] > 0])
                    valor_total_inicial = sum(p['valor_inicial'] for p in resultado)
                    valor_total_atual = sum(p['valor_atual'] for p in resultado)
                    
                    estatisticas = {
                        'total_produtos': total_produtos,
                        'produtos_com_estoque': produtos_com_estoque,
                        'produtos_zerados': total_produtos - produtos_com_estoque,
                        'valor_total_inicial': round(valor_total_inicial, 2),
                        'valor_total_atual': round(valor_total_atual, 2),
                        'variacao_total': round(valor_total_atual - valor_total_inicial, 2),
                        'data_calculo': data_final.strftime('%Y-%m-%d')
                    }
                except Exception as e:
                    print(f"Erro ao calcular estatísticas: {str(e)}")
                    estatisticas = {'erro': 'Erro ao calcular estatísticas'}
            
            return Response({
                'estoque': resultado,
                'estatisticas': estatisticas,
                'parametros': {
                    'data_consulta': data_final.strftime('%Y-%m-%d'),
                    'produto_id': produto_id,
                    'total_registros': len(resultado),
                    'limite_aplicado': limite if limite > 0 else None
                }
            })
            
        except Exception as e:
            return Response(
                {'error': f'Erro interno: {str(e)}'},
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
        """Retorna produtos com estoque crítico (baixo)"""
        try:
            data_str = request.query_params.get('data', date.today().strftime('%Y-%m-%d'))
            limite = float(request.query_params.get('limite', '5'))  # Limite padrão: 5 unidades
            
            # Converte data
            try:
                data_final = datetime.strptime(data_str, '%Y-%m-%d').date()
            except ValueError:
                return Response(
                    {'error': 'Formato de data inválido. Use YYYY-MM-DD'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Carrega dados diretamente
            estoque_inicial = self._carregar_estoque_inicial()
            movimentacoes = self._carregar_movimentacoes(data_final)
            
            estoque_critico = []
            
            # Calcula para todos os produtos
            for produto_id, dados_iniciais in estoque_inicial.items():
                movs_produto = movimentacoes.get(produto_id, [])
                quantidade_atual, valor_atual = self._calcular_estoque_produto(
                    produto_id, dados_iniciais, movs_produto, data_final
                )
                
                # Verifica se está no critério de estoque crítico
                if 0 < quantidade_atual <= limite:
                    # Busca informações do produto
                    try:
                        produto = Produtos.objects.get(id=produto_id)
                        nome_produto = produto.nome
                        referencia = produto.referencia
                    except:
                        nome_produto = f"Produto ID {produto_id}"
                        referencia = "N/A"
                    
                    estoque_critico.append({
                        'produto_id': produto_id,
                        'nome': nome_produto,
                        'referencia': referencia,
                        'quantidade_inicial': float(dados_iniciais['quantidade_inicial']),
                        'quantidade_atual': float(quantidade_atual),
                        'valor_atual': float(valor_atual),
                        'total_movimentacoes': len(movs_produto)
                    })
            
            # Ordena por quantidade (menor primeiro)
            estoque_critico.sort(key=lambda x: x['quantidade_atual'])
            
            return Response({
                'estoque_critico': estoque_critico,
                'parametros': {
                    'data_consulta': data_final.strftime('%Y-%m-%d'),
                    'limite_critico': limite,
                    'total_produtos_criticos': len(estoque_critico)
                }
            })
            
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'])
    def produtos_mais_movimentados(self, request):
        """Retorna produtos com mais movimentações"""
        try:
            data_str = request.query_params.get('data', date.today().strftime('%Y-%m-%d'))
            limite = int(request.query_params.get('limite', '10'))  # Top 10 por padrão
            
            # Converte data
            try:
                data_final = datetime.strptime(data_str, '%Y-%m-%d').date()
            except ValueError:
                return Response(
                    {'error': 'Formato de data inválido. Use YYYY-MM-DD'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Carrega dados
            estoque_inicial = self._carregar_estoque_inicial()
            movimentacoes = self._carregar_movimentacoes(data_final)
            
            # Lista produtos por número de movimentações
            produtos_movimentados = []
            
            for produto_id, dados_iniciais in estoque_inicial.items():
                movs_produto = movimentacoes.get(produto_id, [])
                
                # Busca informações do produto
                try:
                    produto = Produtos.objects.get(id=produto_id)
                    nome_produto = produto.nome
                    referencia = produto.referencia
                except:
                    nome_produto = f"Produto ID {produto_id}"
                    referencia = "N/A"
                
                produtos_movimentados.append({
                    'produto_id': produto_id,
                    'nome': nome_produto,
                    'referencia': referencia,
                    'total_movimentacoes': len(movs_produto),
                    'ultima_movimentacao': movs_produto[-1]['data'].strftime('%Y-%m-%d') if movs_produto else None,
                    'tipos_movimentacao': list(set([str(m['tipo_movimentacao']) for m in movs_produto])) if movs_produto else []
                })
            
            # Ordena por número de movimentações (maior primeiro)
            produtos_movimentados.sort(key=lambda x: x['total_movimentacoes'], reverse=True)
            
            return Response({
                'produtos_mais_movimentados': produtos_movimentados[:limite],
                'parametros': {
                    'data_consulta': data_final.strftime('%Y-%m-%d'),
                    'limite': limite,
                    'total_produtos_analisados': len(produtos_movimentados)
                }
            })
            
        except Exception as e:
            return Response(
                {'error': str(e)},
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
