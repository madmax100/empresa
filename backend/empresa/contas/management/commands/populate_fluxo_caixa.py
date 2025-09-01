from django.core.management.base import BaseCommand
from contas.models.fluxo_caixa import FluxoCaixaLancamento, ConfiguracaoFluxoCaixa
from contas.models.access import ContasReceber, ContasPagar, ContratosLocacao
from decimal import Decimal
from datetime import date, timedelta

class Command(BaseCommand):
    def validate_decimal(self, value):
        if value is None:
            return Decimal('0.00')
        try:
            return Decimal(str(value))
        except:
            return Decimal('0.00')

    def exists_lancamento(self, fonte_tipo, fonte_id, data=None):
        query = FluxoCaixaLancamento.objects.filter(
            fonte_tipo=fonte_tipo,
            fonte_id=fonte_id
        )
        if data:
            query = query.filter(data=data)
        return query.exists()

    def handle(self, *args, **kwargs):
        try:
            contador = {
                'receber': 0,
                'pagar': 0,
                'contratos': 0,
                'skipped': 0
            }

            self.stdout.write('Iniciando migração do fluxo de caixa...')

            # Create initial configuration
            config, created = ConfiguracaoFluxoCaixa.objects.get_or_create(
                defaults={
                    'saldo_inicial': Decimal('10000.00'),
                    'data_inicial_controle': date(2024, 1, 1),
                    'dias_previsao': 90,
                    'categorias': ['aluguel', 'vendas', 'contratos', 'despesas'],
                    'saldo_minimo_alerta': Decimal('5000.00')
                }
            )

            # Get existing financial data
            contas_receber = ContasReceber.objects.filter(status='A')
            contas_pagar = ContasPagar.objects.filter(status='A')
            contratos = ContratosLocacao.objects.all()

            # Create entries from accounts receivable
            self.stdout.write('Processando contas a receber...')
            for conta in contas_receber:
                if conta.vencimento:
                    if not self.exists_lancamento('conta_receber', conta.id):
                        FluxoCaixaLancamento.objects.create(
                            data=conta.vencimento,
                            tipo='entrada',
                            valor=self.validate_decimal(conta.valor),
                            realizado=conta.status == 'P',
                            data_realizacao=conta.data_pagamento if conta.status == 'P' else None,
                            descricao=conta.historico or f'Recebimento - {conta.cliente.nome if conta.cliente else "Cliente"}',
                            categoria='vendas',
                            fonte_tipo='conta_receber',
                            fonte_id=conta.id,
                            cliente=conta.cliente
                        )
                        contador['receber'] += 1
                else:
                    contador['skipped'] += 1
                    self.stdout.write(self.style.WARNING(
                        f'Ignorando conta a receber {conta.id} - data de vencimento ausente'
                    ))

            # Create entries from accounts payable
            self.stdout.write('Processando contas a pagar...')
            for conta in contas_pagar:
                if conta.vencimento:
                    if not self.exists_lancamento('conta_pagar', conta.id):
                        FluxoCaixaLancamento.objects.create(
                            data=conta.vencimento,
                            tipo='saida',
                            valor=self.validate_decimal(conta.valor),
                            realizado=conta.status == 'P',
                            data_realizacao=conta.data_pagamento if conta.status == 'P' else None,
                            descricao=conta.historico or f'Pagamento - {conta.fornecedor.nome if conta.fornecedor else "Fornecedor"}',
                            categoria='despesas',
                            fonte_tipo='conta_pagar',
                            fonte_id=conta.id
                        )
                        contador['pagar'] += 1
                else:
                    contador['skipped'] += 1
                    self.stdout.write(self.style.WARNING(
                        f'Ignorando conta a pagar {conta.id} - data de vencimento ausente'
                    ))

            # Create entries from contracts
            self.stdout.write('Processando contratos...')
            for contrato in contratos:
                valor_parcela = self.validate_decimal(contrato.valorpacela)
                if all([valor_parcela > 0, contrato.inicio, contrato.fim]):
                    data_atual = contrato.inicio
                    while data_atual <= contrato.fim:
                        if not self.exists_lancamento('contrato', contrato.id, data_atual):
                            FluxoCaixaLancamento.objects.create(
                                data=data_atual,
                                tipo='entrada',
                                valor=valor_parcela,
                                realizado=data_atual < date.today(),
                                descricao=f'Contrato {contrato.contrato} - {contrato.cliente.nome if contrato.cliente else "Cliente"}',
                                categoria='contratos',
                                fonte_tipo='contrato',
                                fonte_id=contrato.id,
                                cliente=contrato.cliente
                            )
                            contador['contratos'] += 1
                        data_atual += timedelta(days=30)
                else:
                    contador['skipped'] += 1
                    self.stdout.write(self.style.WARNING(
                        f'Ignorando contrato {contrato.id} - dados incompletos ou valor inválido'
                    ))

            # Relatório final
            self.stdout.write('\nMigração concluída com sucesso!')
            self.stdout.write('Resumo dos lançamentos criados:')
            self.stdout.write(f'- Contas a receber: {contador["receber"]}')
            self.stdout.write(f'- Contas a pagar: {contador["pagar"]}')
            self.stdout.write(f'- Parcelas de contratos: {contador["contratos"]}')
            self.stdout.write(f'- Registros ignorados: {contador["skipped"]}')

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Erro durante a migração: {str(e)}')
            )
            raise

        self.stdout.write(self.style.SUCCESS('Migração do fluxo de caixa finalizada!'))