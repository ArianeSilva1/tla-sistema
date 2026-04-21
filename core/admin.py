from django.contrib import admin
from .models import (
    Cliente,
    Processo,
    ItemFatura,
    CotacaoMoeda,
    ContaPagar,
    DadosBancarios,
    Cotacao,
    ItemCotacao,
    CustoCotacao,
    CotacaoCambio,
    FollowUp,
)


class ItemFaturaInline(admin.TabularInline):
    model = ItemFatura
    extra = 1


class CotacaoMoedaInline(admin.TabularInline):
    model = CotacaoMoeda
    extra = 1


class ContaPagarInline(admin.TabularInline):
    model = ContaPagar
    extra = 1


class ItemCotacaoInline(admin.TabularInline):
    model = ItemCotacao
    extra = 1


class CustoCotacaoInline(admin.TabularInline):
    model = CustoCotacao
    extra = 1


class CotacaoCambioInline(admin.TabularInline):
    model = CotacaoCambio
    extra = 1


@admin.register(Processo)
class ProcessoAdmin(admin.ModelAdmin):
    list_display = (
        'numero_processo',
        'cliente',
        'referencia_cliente',
        'tipo',
        'status',
        'moeda_principal',
        'data_emissao',
        'previsao_chegada',
    )
    search_fields = (
        'numero_processo',
        'numero_fatura',
        'referencia_cliente',
        'cliente__nome',
        'cliente__empresa',
        'booking',
        'navio',
    )
    list_filter = ('tipo', 'status', 'moeda_principal', 'data_emissao')
    inlines = [ItemFaturaInline, CotacaoMoedaInline, ContaPagarInline]


@admin.register(Cotacao)
class CotacaoAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'cliente',
        'referencia_cliente',
        'tipo',
        'status',
        'moeda_principal',
        'data_cotacao',
        'processo_gerado',
    )
    search_fields = (
        'cliente__nome',
        'cliente__empresa',
        'referencia_cliente',
        'booking',
        'navio',
    )
    list_filter = ('tipo', 'status', 'moeda_principal', 'data_cotacao')
    inlines = [ItemCotacaoInline, CustoCotacaoInline, CotacaoCambioInline]


@admin.register(FollowUp)
class FollowUpAdmin(admin.ModelAdmin):
    list_display = ('processo', 'descricao', 'data', 'concluido')
    list_filter = ('concluido', 'data')
    search_fields = (
        'descricao',
        'processo__numero_processo',
        'processo__referencia_cliente',
        'processo__cliente__nome',
        'processo__cliente__empresa',
    )
    ordering = ('data',)


admin.site.register(Cliente)
admin.site.register(DadosBancarios)