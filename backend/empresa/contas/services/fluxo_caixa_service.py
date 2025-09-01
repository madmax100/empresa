import logging
from decimal import Decimal
from collections import defaultdict
from datetime import datetime, date, timedelta
from django.db import transaction
import traceback
from django.db.models import Sum, Q, Prefetch
from django.core.exceptions import ValidationError
from rest_framework.decorators import action
from rest_framework.response import Response

from contas.services.config import LOGGING

from ..models.fluxo_caixa import (
    FluxoCaixaLancamento, 
    SaldoDiario, 
    ConfiguracaoFluxoCaixa
)
from ..models.access import (
    ContasPagar,
    ContasReceber,
    ContratosLocacao,
    Grupos,
    ItensNfSaida,
    ItensNfServico,
    NotasFiscaisEntrada,
    NotasFiscaisSaida,
    NotasFiscaisServico
)
# Configurar logging
logging.config.dictConfig(LOGGING)
logger = logging.getLogger('fluxo_caixa')

class FluxoCaixaService:
    BATCH_SIZE = 1000  # Tamanho do lote para operações em massa

    @staticmethod
    def get_configuracao():
        """Retorna a configuração atual do fluxo de caixa"""
        return ConfiguracaoFluxoCaixa.get_instance()

    @staticmethod
    def criar_lancamento(
        data,
        tipo,
        valor,
        descricao,
        categoria,
        fonte_tipo=None,
        fonte_id=None,
        cliente=None,
        fornecedor=None,
        conta_bancaria=None,
        realizado=False,
        data_realizacao=None,
        observacoes=None
    ):
        """Cria um novo lançamento no fluxo de caixa"""
        try:
            # Determinar categoria baseado na fonte
            if fonte_tipo in ['nfs', 'conta_receber'] and tipo == 'entrada':
                if fonte_tipo == 'nfserv':
                    categoria = 'servicos'
                elif fonte_tipo == 'nfs':
                    # Verificar tipo de operação da NF
                    nota = NotasFiscaisSaida.objects.get(id=fonte_id)
                    if nota.operacao and 'LOCACAO' in nota.operacao.upper():
                        categoria = 'locacao_maquinas'
                    else:
                        categoria = 'vendas'
                    
            logger.info(f"Criando lançamento: fonte_tipo={fonte_tipo}, categoria={categoria}")
                    
            lancamento = FluxoCaixaLancamento(
                data=data,
                tipo=tipo,
                valor=valor,
                descricao=descricao,
                categoria=categoria,
                fonte_tipo=fonte_tipo,
                fonte_id=fonte_id,
                cliente=cliente,
                fornecedor=fornecedor,
                conta_bancaria=conta_bancaria,
                realizado=realizado,
                data_realizacao=data_realizacao,
                observacoes=observacoes
            )
            lancamento.full_clean()
            lancamento.save()
            
            # Atualiza saldo diário
            FluxoCaixaService.atualizar_saldo_diario(data)
            
            return lancamento
        except ValidationError as e:
            raise Exception(f"Erro ao criar lançamento: {str(e)}")
        
    def _determinar_categoria_por_operacao(nota, tipo_documento='nfs'):
        """
        Determina a categoria do lançamento baseado na operação da nota fiscal

        Args:
            nota: NotaFiscalSaida ou NotaFiscalEntrada
            tipo_documento: 'nfs' para nota fiscal de saída ou 'nfe' para nota fiscal de entrada

        Returns:
            str: categoria do lançamento
        """
        try:
            if not nota.operacao:
                logger.warning(f"Nota {nota.numero_nota} sem operação definida")
                return 'vendas' if tipo_documento == 'nfs' else 'compra'

            operacao = nota.operacao.upper()

            # Log para debug
            logger.debug(f"Determinando categoria para nota {nota.numero_nota} - Operação: {operacao}")

            # Mapeamento de termos nas operações para categorias
            if tipo_documento == 'nfs':
                # Notas fiscais de saída
                if any(termo in operacao for termo in ['VENDA', 'REVENDA']):
                    return 'vendas'
                elif any(termo in operacao for termo in ['ALUGUEL', 'LOCACAO', 'LOCAÇÃO']):
                    return 'aluguel'
                elif any(termo in operacao for termo in ['SERVICO', 'SERVIÇO', 'MANUTENCAO', 'MANUTENÇÃO']):
                    return 'servicos'
                elif 'DEVOLUCAO' in operacao or 'DEVOLUÇÃO' in operacao:
                    return 'devolucao'
                elif 'COMODATO' in operacao:
                    return 'comodato'
                elif 'SIMPLES REMESSA' in operacao:
                    return 'simplesRemessa'
                elif 'ADIANTAMENTO' in operacao:
                    return 'adiantamento'
                else:
                    logger.warning(f"Operação não mapeada para NFS {nota.numero_nota}: {operacao}")
                    return 'vendas'  # default para notas de saída
            else:
                # Notas fiscais de entrada
                if any(termo in operacao for termo in ['COMPRA', 'AQUISICAO']):
                    return 'compra'
                elif any(termo in operacao for termo in ['SERVICO', 'SERVIÇO', 'MANUTENCAO', 'MANUTENÇÃO']):
                    return 'servicos'
                elif 'DEVOLUCAO' in operacao or 'DEVOLUÇÃO' in operacao:
                    return 'devolucao'
                elif 'COMODATO' in operacao:
                    return 'comodato'
                elif 'SIMPLES REMESSA' in operacao:
                    return 'simplesRemessa'
                elif 'ADIANTAMENTO' in operacao:
                    return 'adiantamento'
                else:
                    logger.warning(f"Operação não mapeada para NFE {nota.numero_nota}: {operacao}")
                    return 'compra'  # default para notas de entrada

        except Exception as e:
            logger.error(f"Erro ao determinar categoria da nota {nota.numero_nota}: {str(e)}")
            return 'vendas' if tipo_documento == 'nfs' else 'compra'
        

    @staticmethod
    def _determinar_subcategoria_saida(nota, grupos_cache=None):
        """Determina a subcategoria da nota fiscal baseada nos grupos dos produtos"""
        try:
            # Mapeamento de grupos para subcategorias
            GRUPOS_SUPRIMENTOS = {'SUPRIMENTOS', 'MATERIAL DE EXPEDIENTE'}
            GRUPOS_LOCACAO = {'LOCACAO', 'SEDUC', 'ALAOR TJ', 'DEMONSTRACAO'}
            GRUPOS_MAQUINAS = {
                'DUPLICADORES', 'COPIADORAS', 'IMPRESSORAS', 
                'MAQUINAS USADAS', 'CONSOLE', 'ESTABILIZADORES'
            }
            GRUPOS_PECAS = {'PEÇAS', 'BACKUP'}
            
            # Verificar subcategoria predominante nos itens
            subcategorias = defaultdict(Decimal)
            itens_processados = 0
            
            # Log inicial
            logger.info(f"Determinando subcategoria para nota {nota.numero_nota}")
            logger.info(f"Total de itens: {nota.itens.count()}")
            
            for item in nota.itens.all():
                itens_processados += 1
                valor = item.valor_total or 0
                if item.produto and item.produto.grupo_id:
                    grupo_nome = (grupos_cache.get(item.produto.grupo_id, 'OUTROS') if grupos_cache else 'OUTROS').upper()
                    
                    # Log detalhado do item
                    logger.info(
                        f"Nota {nota.numero_nota} - Item {itens_processados}: "
                        f"Produto={item.produto.id}, "
                        f"Grupo={grupo_nome}, "
                        f"Valor={valor}")

                    # Classificar baseado no grupo exato
                    if grupo_nome in GRUPOS_SUPRIMENTOS:
                        subcategorias['suprimentos'] += valor
                        logger.info(f"Item {itens_processados} classificado como suprimentos")
                    elif grupo_nome in GRUPOS_LOCACAO:
                        subcategorias['locacao_maquinas'] += valor
                        logger.info(f"Item {itens_processados} classificado como locacao_maquinas")
                    elif grupo_nome in GRUPOS_MAQUINAS:
                        subcategorias['maquinas'] += valor
                        logger.info(f"Item {itens_processados} classificado como maquinas")
                    elif grupo_nome in GRUPOS_PECAS:
                        subcategorias['manutencao'] += valor
                        logger.info(f"Item {itens_processados} classificado como manutencao")
                    else:
                        subcategorias['vendas'] += valor
                        logger.info(f"Item {itens_processados} classificado como vendas (grupo não mapeado)")
                else:
                    subcategorias['vendas'] += valor
                    logger.info(
                        f"Item {itens_processados} classificado como vendas "
                        f"({'sem produto' if not item.produto else 'sem grupo'}) - "
                        f"Valor: {valor}"
                    )

            # Log dos totais por subcategoria
            logger.info(f"Nota {nota.numero_nota} - Totais por subcategoria: {dict(subcategorias)}")

            # Determinar subcategoria pelo maior valor
            if subcategorias:
                subcategoria = max(subcategorias.items(), key=lambda x: x[1])[0]
                logger.info(
                    f"Nota {nota.numero_nota} - "
                    f"Subcategoria predominante: {subcategoria} "
                    f"(Valor: {subcategorias[subcategoria]})"
                )
                return subcategoria
            
            logger.warning(f"Nota {nota.numero_nota} - Nenhuma subcategoria encontrada, usando 'vendas'")
            return 'vendas'  # Subcategoria default

        except Exception as e:
            logger.error(f"Erro ao determinar subcategoria da nota {nota.numero_nota}: {str(e)}")
            logger.error(traceback.format_exc())  # Log do stacktrace completo
            return 'vendas'  # Subcategoria default em caso de erro
        
    def _determinar_categoria_servico(nota_servico):
        """
        Determina a categoria correta para uma nota fiscal de serviço
        baseado principalmente nos itens
        """
        try:
            # Buscar itens da nota
            itens = ItensNfServico.objects.filter(nota_fiscal=nota_servico)
            
            # Verificar valores
            total_itens = sum(item.valor_total or 0 for item in itens)
            if abs(total_itens - nota_servico.valor_produtos) > 0.01:  # tolerância de 0.01
                logger.warning(
                    f"NFSe {nota_servico.numero_nota}: Divergência de valores - "
                    f"Nota: {nota_servico.valor_produtos}, Itens: {total_itens}"
                )

            # Se tiver apenas um item, usa a categoria dele
            if itens.count() == 1:
                servico_desc = (itens.first().servico or '').upper()
                print(servico_desc)
                if servico_desc:
                    if 'CONTRATO' in servico_desc or 'LOCACAO' in servico_desc or 'LOCAÇÃO' in servico_desc:
                        return 'locacao_maquinas'
                    elif 'MANUTENCAO' in servico_desc or 'MANUTENÇÃO' in servico_desc or 'ASSISTÊNCIA' in servico_desc or 'ASSISTENCIA' in servico_desc:
                        return 'manutencao'
                    else:
                        return 'servicos'

            # Se tiver múltiplos itens
            categorias = set()
            for item in itens:
                servico_desc = (item.servico or '').upper()
                if 'CONTRATO' in servico_desc or 'LOCACAO' in servico_desc or 'LOCAÇÃO' in servico_desc:
                    categorias.add('locacao_maquinas')
                elif 'MANUTENCAO' in servico_desc or 'MANUTENÇÃO' in servico_desc or 'ASSISTÊNCIA' in servico_desc or 'ASSISTENCIA' in servico_desc:
                    categorias.add('manutencao')
                else:
                    categorias.add('servicos')

            # Log dos itens encontrados
            logger.debug(f"NFSe {nota_servico.numero_nota} - Categorias encontradas: {categorias}")

            # Se houver apenas uma categoria, usa ela
            if len(categorias) == 1:
                return categorias.pop()

            # Se houver múltiplas categorias, decide pela predominante em valor
            valores_por_categoria = {
                'locacao_maquinas': 0,
                'manutencao': 0,
                'servicos': 0
            }

            for item in itens:
                servico_desc = (item.servico or '').upper()
                if 'CONTRATO' in servico_desc or 'LOCACAO' in servico_desc or 'LOCAÇÃO' in servico_desc:
                    valores_por_categoria['locacao_maquinas'] += item.valor_total or 0
                elif 'MANUTENCAO' in servico_desc or 'MANUTENÇÃO' in servico_desc or 'ASSISTÊNCIA' in servico_desc or 'ASSISTENCIA' in servico_desc:
                    valores_por_categoria['manutencao'] += item.valor_total or 0
                else:
                    valores_por_categoria['servicos'] += item.valor_total or 0

            # Retorna a categoria com maior valor
            categoria_predominante = max(valores_por_categoria.items(), key=lambda x: x[1])[0]
            logger.info(
                f"NFSe {nota_servico.numero_nota} - Múltiplas categorias, usando predominante: {categoria_predominante}"
            )
            return categoria_predominante

        except Exception as e:
            logger.error(f"Erro ao determinar categoria da NFSe {nota_servico.numero_nota}: {str(e)}")
            return 'servicos'  # default em caso de erro
        
    @staticmethod
    def sincronizar_notas_saida():
        """Sincroniza lançamentos com notas fiscais de saída"""
        try:
            with transaction.atomic():
                # Buscar IDs já sincronizados
                saidas_sincronizadas = set(FluxoCaixaLancamento.objects.filter(
                    fonte_tipo='nfs'
                ).values_list('fonte_id', flat=True))

                # Carregar grupos em memória
                grupos_cache = {g.id: g.nome for g in Grupos.objects.all()}

                # Query principal
                lancamentos = []
                notas_saida = NotasFiscaisSaida.objects.exclude(
                    id__in=saidas_sincronizadas
                ).filter(
                    data__isnull=False
                ).select_related(
                    'cliente'
                ).prefetch_related(
                    'itens',
                    'itens__produto',
                    'itens__produto__grupo'
                ).iterator(chunk_size=100)

                # Debug para verificar quantas notas serão processadas
                total_notas = NotasFiscaisSaida.objects.exclude(
                    id__in=saidas_sincronizadas
                ).filter(
                    data__isnull=False
                ).count()
                logger.info(f"Total de notas para processar: {total_notas}")

                # Verificar dados dos grupos
                grupos_ids = {g.id: g.nome for g in Grupos.objects.all()}
                logger.info(f"Total de grupos carregados: {len(grupos_ids)}")
                logger.info("Grupos disponíveis:")
                for gid, gnome in grupos_ids.items():
                    logger.info(f"ID: {gid} - Nome: {gnome}")

                for nota in notas_saida:
                    # Determinar categoria pela operação
                    categoria = FluxoCaixaService._determinar_categoria_por_operacao(nota, 'nfs')
                    
                    # Determinar subcategoria pelos itens/grupos
                    subcategoria = FluxoCaixaService._determinar_subcategoria_saida(nota, grupos_cache)
                    
                    logger.info(
                        f"NFS {nota.numero_nota} classificada como categoria={categoria}, "
                        f"subcategoria={subcategoria} (Operação: {nota.operacao})"
                    )

                    lancamentos.append(FluxoCaixaLancamento(
                        data=nota.data,
                        tipo='entrada',
                        valor=nota.valor_total_nota,
                        descricao=f"NF {nota.numero_nota} - {nota.cliente}",
                        categoria=categoria,
                        subcategoria=subcategoria,
                        fonte_tipo='nfs',
                        fonte_id=nota.id,
                        cliente=nota.cliente,
                        realizado=bool(nota.data),
                        data_realizacao=nota.data,
                        observacoes=f"Operação: {nota.operacao}"
                    ))

                    if len(lancamentos) >= 1000:  # BATCH_SIZE
                        FluxoCaixaLancamento.objects.bulk_create(lancamentos)
                        lancamentos = []

                # Criar lote final
                if lancamentos:
                    FluxoCaixaLancamento.objects.bulk_create(lancamentos)

                total_sincronizado = FluxoCaixaLancamento.objects.filter(
                    fonte_tipo='nfs'
                ).count()
                logger.info(f"Sincronização de notas de saída concluída. Total: {total_sincronizado}")
                return "Sincronização de notas de saída concluída com sucesso"

        except Exception as e:
            logger.error(f"Erro na sincronização de notas de saída: {str(e)}")
            raise

    @staticmethod
    def sincronizar_notas_entrada():
        """Sincroniza lançamentos com notas fiscais de entrada"""
        try:
            with transaction.atomic():
                # Buscar IDs já sincronizados
                nfe_sincronizadas = set(FluxoCaixaLancamento.objects.filter(
                    fonte_tipo='nfe'
                ).values_list('fonte_id', flat=True))

                # Carregar grupos em memória
                grupos_cache = {g.id: g.nome for g in Grupos.objects.all()}

                # Query principal
                lancamentos = []
                notas_entrada = NotasFiscaisEntrada.objects.exclude(
                    id__in=nfe_sincronizadas
                ).filter(
                    data_emissao__isnull=False
                ).select_related(
                    'fornecedor'
                ).prefetch_related(
                    'itens',
                    'itens__produto'
                ).iterator(chunk_size=100)

                for nota in notas_entrada:
                    # Determinar categoria pela operação
                    categoria = FluxoCaixaService._determinar_categoria_por_operacao(nota, 'nfe')
                    
                    # Determinar subcategoria pelos itens/grupos
                    subcategoria = FluxoCaixaService._determinar_subcategoria_saida(nota, grupos_cache)
                    
                    logger.info(
                        f"NFE {nota.numero_nota} classificada como categoria={categoria}, "
                        f"subcategoria={subcategoria} (Operação: {nota.operacao})"
                    )

                    lancamentos.append(FluxoCaixaLancamento(
                        data=nota.data_emissao,
                        tipo='saida',
                        valor=nota.valor_total,
                        descricao=f"NF {nota.numero_nota} - {nota.fornecedor}",
                        categoria=categoria,
                        subcategoria=subcategoria,
                        fonte_tipo='nfe',
                        fonte_id=nota.id,
                        fornecedor=nota.fornecedor,
                        realizado=bool(nota.data_entrada),
                        data_realizacao=nota.data_entrada,
                        observacoes=f"Operação: {nota.operacao}"
                    ))

                    if len(lancamentos) >= 1000:  # BATCH_SIZE
                        FluxoCaixaLancamento.objects.bulk_create(lancamentos)
                        lancamentos = []

                # Criar lote final
                if lancamentos:
                    FluxoCaixaLancamento.objects.bulk_create(lancamentos)

                total_sincronizado = FluxoCaixaLancamento.objects.filter(
                    fonte_tipo='nfe'
                ).count()
                logger.info(f"Sincronização de notas de entrada concluída. Total: {total_sincronizado}")
                return "Sincronização de notas de entrada concluída com sucesso"

        except Exception as e:
            logger.error(f"Erro na sincronização de notas de entrada: {str(e)}")
            raise


    @staticmethod
    def sincronizar_notas_servico():
        """Sincroniza lançamentos com notas fiscais de serviço"""
        try:
            print("Sincronizando notas de serviço...")
            with transaction.atomic():
                # Buscar IDs já sincronizados
                servicos_sincronizados = set(FluxoCaixaLancamento.objects.filter(
                    fonte_tipo='nfserv'
                ).values_list('fonte_id', flat=True))

                # Buscar notas de serviço não sincronizadas
                lancamentos = []
                notas_servico = NotasFiscaisServico.objects.exclude(
                    id__in=servicos_sincronizados
                ).filter(
                    data__isnull=False
                ).select_related(
                    'cliente'
                ).prefetch_related(
                    'itens'
                ).iterator(chunk_size=100)

                for nota in notas_servico:
                    # Validar valores
                    total_itens = sum(
                        item.valor_total or 0 
                        for item in nota.itens.all()
                    )
                    if abs(total_itens - nota.valor_produtos) > 0.01:
                        logger.warning(
                            f"NFSe {nota.numero_nota}: Divergência de valores - "
                            f"Nota: {nota.valor_produtos}, Itens: {total_itens}. "
                            "Usando valor total dos itens."
                        )
                        valor_lancar = total_itens
                    else:
                        valor_lancar = nota.valor_produtos

                    # Determinar categoria usando função específica
                    categoria = FluxoCaixaService._determinar_categoria_servico(nota)
                    print(categoria)
                    
                    # Log detalhado
                    logger.info(
                        f"NFSe {nota.numero_nota} categorizada como {categoria} "
                        f"(Valor: {valor_lancar}, Itens: {nota.itens.count()})"
                    )

                    # Criar lançamento
                    lancamentos.append(FluxoCaixaLancamento(
                        data=nota.data,
                        tipo='entrada',
                        valor=valor_lancar,
                        descricao=f"NFS {nota.numero_nota} - {nota.cliente}",
                        categoria=categoria,
                        fonte_tipo='nfserv',
                        fonte_id=nota.id,
                        cliente=nota.cliente,
                        realizado=bool(nota.data),
                        data_realizacao=nota.data,
                        observacoes=f"Total Itens: {total_itens}"
                    ))

                    if len(lancamentos) >= 1000:  # BATCH_SIZE
                        FluxoCaixaLancamento.objects.bulk_create(lancamentos)
                        lancamentos = []

                # Criar lote final
                if lancamentos:
                    FluxoCaixaLancamento.objects.bulk_create(lancamentos)

                total_sincronizado = FluxoCaixaLancamento.objects.filter(
                    fonte_tipo='nfserv'
                ).count()
                logger.info(f"Sincronização de notas de serviço concluída. Total: {total_sincronizado}")
                return "Sincronização de notas de serviço concluída com sucesso"

        except Exception as e:
            logger.error(f"Erro na sincronização de notas de serviço: {str(e)}")
            raise

    
    @staticmethod
    def sincronizar_contas():
        """Sincroniza lançamentos com contas a pagar/receber de forma otimizada"""
        try:
            with transaction.atomic():
                # Buscar IDs já sincronizados
                cp_sincronizadas = set(FluxoCaixaLancamento.objects.filter(
                    fonte_tipo='conta_pagar'
                ).values_list('fonte_id', flat=True))

                cr_sincronizadas = set(FluxoCaixaLancamento.objects.filter(
                    fonte_tipo='conta_receber'
                ).values_list('fonte_id', flat=True))

                # Contas a Pagar - em lote
                lancamentos = []
                contas_pagar = ContasPagar.objects.exclude(
                    id__in=cp_sincronizadas
                ).filter(
                    status='A',
                    vencimento__isnull=False
                ).select_related('fornecedor', 'conta').iterator()

                for conta in contas_pagar:
                    lancamentos.append(FluxoCaixaLancamento(
                        data=conta.vencimento,
                        tipo='saida',
                        valor=conta.valor,
                        descricao=f"Pagamento: {conta.historico or conta.fornecedor}",
                        categoria='despesas_operacionais',
                        fonte_tipo='conta_pagar',
                        fonte_id=conta.id,
                        fornecedor=conta.fornecedor,
                        conta_bancaria=conta.conta,
                        realizado=conta.status == 'P',
                        data_realizacao=conta.data_pagamento
                    ))

                    if len(lancamentos) >= FluxoCaixaService.BATCH_SIZE:
                        FluxoCaixaLancamento.objects.bulk_create(lancamentos)
                        lancamentos = []

                # Criar lote final de contas a pagar
                if lancamentos:
                    FluxoCaixaLancamento.objects.bulk_create(lancamentos)

                # Contas a Receber - em lote
                lancamentos = []
                contas_receber = ContasReceber.objects.exclude(
                    id__in=cr_sincronizadas
                ).filter(
                    status='A',
                    vencimento__isnull=False
                ).select_related('cliente', 'conta').iterator()

                for conta in contas_receber:
                    lancamentos.append(FluxoCaixaLancamento(
                        data=conta.vencimento,
                        tipo='entrada',
                        valor=conta.valor,
                        descricao=f"Recebimento: {conta.historico or conta.cliente}",
                        categoria='vendas',
                        fonte_tipo='conta_receber',
                        fonte_id=conta.id,
                        cliente=conta.cliente,
                        conta_bancaria=conta.conta,
                        realizado=conta.status == 'P',
                        data_realizacao=conta.data_pagamento
                    ))

                    if len(lancamentos) >= FluxoCaixaService.BATCH_SIZE:
                        FluxoCaixaLancamento.objects.bulk_create(lancamentos)
                        lancamentos = []

                # Criar lote final de contas a receber
                if lancamentos:
                    FluxoCaixaLancamento.objects.bulk_create(lancamentos)

                return "Sincronização concluída com sucesso"

        except Exception as e:
            logger.error(f"Erro na sincronização: {str(e)}")
            raise

    @staticmethod
    def sincronizar_tudo():
        """Sincroniza todos os lançamentos"""
        try:
            start_time = datetime.now()
            logger.info("Iniciando sincronização completa...")
            
            FluxoCaixaService.sincronizar_notas_servico()
            FluxoCaixaService.sincronizar_notas_saida()
            FluxoCaixaService.sincronizar_notas_entrada()
            FluxoCaixaService.sincronizar_contas()
            
            end_time = datetime.now()
            duration = end_time - start_time
            logger.info(f"Sincronização completa concluída em {duration}")
            
            return "Sincronização completa concluída com sucesso"
        except Exception as e:
            logger.error(f"Erro na sincronização completa: {str(e)}")
            raise

    @staticmethod
    def estornar_lancamento(lancamento_id, data_estorno=None, observacoes=None):
        """Estorna um lançamento existente"""
        try:
            with transaction.atomic():
                lancamento = FluxoCaixaLancamento.objects.get(id=lancamento_id)
                if lancamento.data_estorno:
                    raise ValidationError("Lançamento já estornado")

                data_estorno = data_estorno or datetime.now()
                lancamento.data_estorno = data_estorno
                if observacoes:
                    lancamento.observacoes = (lancamento.observacoes or '') + f"\nEstorno: {observacoes}"
                lancamento.save()

                # Cria lançamento de estorno
                FluxoCaixaService.criar_lancamento(
                    data=data_estorno.date(),
                    tipo='entrada' if lancamento.tipo == 'saida' else 'saida',
                    valor=lancamento.valor,
                    descricao=f"Estorno: {lancamento.descricao}",
                    categoria=lancamento.categoria,
                    fonte_tipo='estorno',
                    fonte_id=lancamento.id,
                    cliente=lancamento.cliente,
                    fornecedor=lancamento.fornecedor,
                    conta_bancaria=lancamento.conta_bancaria,
                    realizado=True,
                    data_realizacao=data_estorno,
                    observacoes=observacoes
                )

                # Atualiza saldos
                FluxoCaixaService.atualizar_saldo_diario(lancamento.data)
                FluxoCaixaService.atualizar_saldo_diario(data_estorno.date())

                return lancamento
        except FluxoCaixaLancamento.DoesNotExist:
            raise Exception("Lançamento não encontrado")
        except Exception as e:
            raise Exception(f"Erro ao estornar lançamento: {str(e)}")

    @staticmethod
    def atualizar_saldo_diario(data):
        """Atualiza ou cria o saldo diário para uma data específica"""
        try:
            # Busca saldo anterior
            saldo_anterior = SaldoDiario.objects.filter(
                data__lt=data
            ).order_by('-data').first()

            saldo_inicial = saldo_anterior.saldo_final if saldo_anterior else \
                          FluxoCaixaService.get_configuracao().saldo_inicial

            # Busca ou cria saldo do dia
            saldo_diario, created = SaldoDiario.objects.get_or_create(
                data=data,
                defaults={'saldo_inicial': saldo_inicial}
            )

            if not created:
                saldo_diario.saldo_inicial = saldo_inicial

            saldo_diario.processado = False
            saldo_diario.save()  # Isso vai disparar o cálculo dos totais

            # Atualiza saldos futuros
            saldos_futuros = SaldoDiario.objects.filter(data__gt=data)
            for saldo in saldos_futuros:
                saldo_anterior = SaldoDiario.objects.filter(
                    data__lt=saldo.data
                ).order_by('-data').first()
                
                saldo.saldo_inicial = saldo_anterior.saldo_final
                saldo.processado = False
                saldo.save()

        except Exception as e:
            raise Exception(f"Erro ao atualizar saldo diário: {str(e)}")

    @staticmethod
    def _converter_para_date(data_valor):
        """Converte um valor de data para date, seja ele date ou datetime"""
        if isinstance(data_valor, datetime):
            return data_valor.date()
        if isinstance(data_valor, date):
            return data_valor
        return None

    
    @action(detail=False, methods=['POST'])
    def limpar_lancamentos(self, request):
        """
        Endpoint para limpar todos os lançamentos do fluxo de caixa.
        Requer confirmação via parâmetro 'confirmar=true'
        """
        try:
            # Verifica se a confirmação foi enviada
            confirmar = request.data.get('confirmar', '').lower() == 'true'
            if not confirmar:
                return Response({
                    'status': 'erro',
                    'mensagem': 'É necessário confirmar a operação enviando confirmar=true'
                }, status=400)

            # Executa a limpeza
            with transaction.atomic():
                # Conta a quantidade de registros antes de deletar
                total_registros = FluxoCaixaLancamento.objects.count()
                
                # Deleta todos os registros
                FluxoCaixaLancamento.objects.all().delete()

            return Response({
                'status': 'sucesso',
                'mensagem': f'Todos os lançamentos foram removidos ({total_registros} registros)',
                'proximo_passo': 'Use o endpoint /sincronizar_contas/ para recriar os lançamentos'
            })

        except Exception as e:
            return Response({
                'status': 'erro',
                'mensagem': str(e)
            }, status=400)

    @action(detail=False, methods=['POST'])
    def limpar_e_sincronizar(self, request):
        """
        Endpoint que limpa todos os lançamentos e realiza nova sincronização.
        Requer confirmação via parâmetro 'confirmar=true'
        """
        try:
            # Verifica se a confirmação foi enviada
            confirmar = request.data.get('confirmar', '').lower() == 'true'
            if not confirmar:
                return Response({
                    'status': 'erro',
                    'mensagem': 'É necessário confirmar a operação enviando confirmar=true'
                }, status=400)

            # Executa a limpeza e sincronização
            with transaction.atomic():
                # Conta registros antes
                total_antes = FluxoCaixaLancamento.objects.count()
                
                # Limpa todos os registros
                FluxoCaixaLancamento.objects.all().delete()
                
                # Realiza nova sincronização
                FluxoCaixaService.sincronizar_contas()
                
                # Conta registros depois
                total_depois = FluxoCaixaLancamento.objects.count()

            return Response({
                'status': 'sucesso',
                'mensagem': 'Limpeza e sincronização concluídas com sucesso',
                'detalhes': {
                    'registros_removidos': total_antes,
                    'novos_registros': total_depois
                }
            })

        except Exception as e:
            return Response({
                'status': 'erro',
                'mensagem': str(e)
            }, status=400)
            

    @staticmethod
    def verificar_saldo_negativo():
        """Verifica se há previsão de saldo negativo"""
        config = FluxoCaixaService.get_configuracao()
        if not config.alerta_saldo_negativo:
            return []

        saldos = FluxoCaixaService.gerar_previsao_fluxo()
        alertas = []
        
        for saldo in saldos:
            if saldo.saldo_final < config.saldo_minimo_alerta:
                alertas.append({
                    'data': saldo.data,
                    'saldo_previsto': saldo.saldo_final,
                    'saldo_minimo': config.saldo_minimo_alerta
                })

        return alertas

    @staticmethod
    def get_relatorio_periodo(data_inicial, data_final):
        """Gera relatório de movimentações do período"""
        lancamentos = FluxoCaixaLancamento.objects.filter(
            data__gte=data_inicial,
            data__lte=data_final,
            data_estorno__isnull=True
        )

        totais = {
            'entradas': {
                'realizado': sum(l.valor for l in lancamentos if l.tipo == 'entrada' and l.realizado),
                'previsto': sum(l.valor for l in lancamentos if l.tipo == 'entrada' and not l.realizado),
            },
            'saidas': {
                'realizado': sum(l.valor for l in lancamentos if l.tipo == 'saida' and l.realizado),
                'previsto': sum(l.valor for l in lancamentos if l.tipo == 'saida' and not l.realizado),
            }
        }

        totais['saldo_realizado'] = totais['entradas']['realizado'] - totais['saidas']['realizado']
        totais['saldo_previsto'] = (totais['entradas']['realizado'] + totais['entradas']['previsto']) - \
                                  (totais['saidas']['realizado'] + totais['saidas']['previsto'])

        return {
            'lancamentos': lancamentos,
            'totais': totais,
            'periodo': {
                'inicio': data_inicial,
                'fim': data_final
            }
        }