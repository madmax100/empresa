from django.db.models.signals import post_save
from django.dispatch import receiver
from ..models import ContasPagar, ContasReceber, FluxoCaixaLancamento

@receiver(post_save, sender=ContasPagar)
def atualizar_fluxo_conta_pagar(sender, instance, created, **kwargs):
    if created:
        FluxoCaixaLancamento.objects.criar_lancamento_conta_pagar(instance)
    else:
        lancamento = FluxoCaixaLancamento.objects.filter(
            fonte_tipo='conta_pagar',
            fonte_id=instance.id
        ).first()
        
        if lancamento and instance.status == 'P':
            lancamento.realizado = True
            lancamento.data_realizacao = instance.data_pagamento
            lancamento.save()

@receiver(post_save, sender=ContasReceber)
def atualizar_fluxo_conta_receber(sender, instance, created, **kwargs):
    if created:
        FluxoCaixaLancamento.objects.criar_lancamento_conta_receber(instance)
    else:
        lancamento = FluxoCaixaLancamento.objects.filter(
            fonte_tipo='conta_receber',
            fonte_id=instance.id
        ).first()
        
        if lancamento and instance.status == 'P':
            lancamento.realizado = True
            lancamento.data_realizacao = instance.data_pagamento
            lancamento.save()