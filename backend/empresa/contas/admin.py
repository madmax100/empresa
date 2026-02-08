from django.contrib import admin

from .models import (
    CentroCusto,
    ItemLancamentoContabil,
    LancamentoContabil,
    PeriodoContabil,
    PlanoContas,
)


@admin.register(PlanoContas)
class PlanoContasAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'nome', 'tipo', 'natureza', 'nivel', 'ativa')
    search_fields = ('codigo', 'nome')
    list_filter = ('tipo', 'natureza', 'ativa')


@admin.register(CentroCusto)
class CentroCustoAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'nome', 'ativo')
    search_fields = ('codigo', 'nome')
    list_filter = ('ativo',)


@admin.register(PeriodoContabil)
class PeriodoContabilAdmin(admin.ModelAdmin):
    list_display = ('mes', 'ano', 'status', 'fechado_em')
    list_filter = ('status', 'ano')
    ordering = ('-ano', '-mes')


class ItemLancamentoContabilInline(admin.TabularInline):
    model = ItemLancamentoContabil
    extra = 0


@admin.register(LancamentoContabil)
class LancamentoContabilAdmin(admin.ModelAdmin):
    list_display = ('data', 'descricao', 'origem', 'documento_ref')
    search_fields = ('descricao', 'documento_ref')
    list_filter = ('origem',)
    date_hierarchy = 'data'
    inlines = (ItemLancamentoContabilInline,)


@admin.register(ItemLancamentoContabil)
class ItemLancamentoContabilAdmin(admin.ModelAdmin):
    list_display = ('lancamento', 'conta', 'tipo', 'valor', 'centro_custo')
    list_filter = ('tipo', 'centro_custo')
