from django.contrib import admin
from .models import (
    Cliente,
    Processo,
    ItemFatura,
    CotacaoMoeda,
    ContaPagar,
    ContaReceber,
    DadosBancarios,
    Cotacao,
    ItemCotacao,
    CustoCotacao,
    CotacaoCambio,
    FollowUp,
    TarefaOperacional,
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
 
 
class ContaReceberInline(admin.TabularInline):
    model = ContaReceber
    extra = 1
 
 
class FollowUpInline(admin.TabularInline):
    model = FollowUp
    extra = 1
 
 
class TarefaOperacionalInline(admin.TabularInline):
    model = TarefaOperacional
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
 
 
@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ('nome', 'empresa', 'cnpj', 'email', 'telefone', 'criado_em')
    search_fields = ('nome', 'empresa', 'cnpj', 'email', 'telefone')
    list_filter = ('criado_em',)
    ordering = ('nome',)
 
 
@admin.register(Processo)
class ProcessoAdmin(admin.ModelAdmin):
    list_display = (
        'numero_processo',
        'cliente',
        'tipo',
        'status',
        'status_operacional',
        'responsavel',
        'prioridade',
        'booking',
        'armador',
        'saida',
        'previsao_chegada',
        'valor_recebido',
        'ultima_atualizacao',
    )
    search_fields = (
        'numero_processo',
        'numero_fatura',
        'referencia_cliente',
        'cliente__nome',
        'cliente__empresa',
        'booking',
        'armador',
        'navio',
        'destino',
        'pol',
    )
    list_filter = (
        'tipo',
        'status',
        'status_operacional',
        'prioridade',
        'moeda_principal',
        'armador',
        'saida',
        'previsao_chegada',
        'data_emissao',
        'draft_ok',
        'si_enviado',
        'pre_alerta_enviado',
    )
    readonly_fields = (
        'numero_processo',
        'numero_fatura',
        'data_emissao',
        'ultima_atualizacao',
        'mostrar_total_faturado_brl',
        'mostrar_total_custo_brl',
        'mostrar_total_iof_brl',
        'mostrar_total_faturado_com_iof_brl',
        'mostrar_total_recebido_brl',
        'mostrar_lucro_brl',
    )
    autocomplete_fields = ('cliente',)
    inlines = [
        ItemFaturaInline,
        CotacaoMoedaInline,
        ContaPagarInline,
        ContaReceberInline,
        FollowUpInline,
        TarefaOperacionalInline,
    ]
 
    fieldsets = (
        ('Identificação', {
            'fields': (
                'cliente',
                'numero_processo',
                'numero_fatura',
                'referencia_cliente',
                'tipo',
                'status',
                'status_operacional',
                'prioridade',
                'responsavel',
            )
        }),
        ('Financeiro', {
            'fields': (
                'moeda_principal',
                'tarifa_cotacao',
                'data_cotacao',
                'iof_percentual',
                'valor_recebido',
            )
        }),
        ('Operacional / Logística', {
            'fields': (
                'origem',
                'pol',
                'destino',
                'transbordo',
                'modal',
                'booking',
                'armador',
                'cia_aerea',
                'navio',
                'transit_time',
                'container_type',
                'place_of_delivery',
                'pickup_container',
            )
        }),
        ('Datas', {
            'fields': (
                'data_emissao',
                'saida',
                'previsao_chegada',
                'etd',
                'eta',
            )
        }),
        ('Controle operacional', {
            'fields': (
                'draft_ok',
                'si_enviado',
                'pre_alerta_enviado',
                'pendencias',
                'observacoes',
                'ultima_atualizacao',
            )
        }),
        ('Resumo financeiro em BRL', {
            'fields': (
                'mostrar_total_faturado_brl',
                'mostrar_total_custo_brl',
                'mostrar_total_iof_brl',
                'mostrar_total_faturado_com_iof_brl',
                'mostrar_total_recebido_brl',
                'mostrar_lucro_brl',
            )
        }),
    )
 
    def mostrar_total_faturado_brl(self, obj):
        return obj.total_faturado_brl()
    mostrar_total_faturado_brl.short_description = 'Total faturado (BRL)'
 
    def mostrar_total_custo_brl(self, obj):
        return obj.total_custo_brl()
    mostrar_total_custo_brl.short_description = 'Total custo (BRL)'
 
    def mostrar_total_iof_brl(self, obj):
        return obj.total_iof_brl()
    mostrar_total_iof_brl.short_description = 'Total IOF (BRL)'
 
    def mostrar_total_faturado_com_iof_brl(self, obj):
        return obj.total_faturado_com_iof_brl()
    mostrar_total_faturado_com_iof_brl.short_description = 'Faturado com IOF (BRL)'
 
    def mostrar_total_recebido_brl(self, obj):
        return obj.total_recebido_brl()
    mostrar_total_recebido_brl.short_description = 'Total recebido (BRL)'
 
    def mostrar_lucro_brl(self, obj):
        return obj.lucro_brl()
    mostrar_lucro_brl.short_description = 'Lucro (BRL)'
 
 
@admin.register(Cotacao)
class CotacaoAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'cliente',
        'tipo',
        'status',
        'moeda_principal',
        'tarifa_cotacao',
        'data_cotacao',
        'booking',
        'armador',
        'criado_em',
        'processo_gerado',
    )
    search_fields = (
        'cliente__nome',
        'cliente__empresa',
        'referencia_cliente',
        'booking',
        'armador',
        'navio',
        'destino',
        'pol',
    )
    list_filter = (
        'tipo',
        'status',
        'moeda_principal',
        'armador',
        'data_cotacao',
        'criado_em',
    )
    readonly_fields = ('criado_em',)
    autocomplete_fields = ('cliente', 'processo_gerado')
    inlines = [
        ItemCotacaoInline,
        CustoCotacaoInline,
        CotacaoCambioInline,
    ]
 
    fieldsets = (
        ('Identificação', {
            'fields': (
                'cliente',
                'processo_gerado',
                'referencia_cliente',
                'tipo',
                'status',
                'criado_em',
            )
        }),
        ('Financeiro', {
            'fields': (
                'moeda_principal',
                'tarifa_cotacao',
                'data_cotacao',
                'iof_percentual',
            )
        }),
        ('Operacional / Logística', {
            'fields': (
                'pol',
                'destino',
                'transbordo',
                'booking',
                'armador',
                'navio',
                'transit_time',
                'container_type',
                'place_of_delivery',
                'pickup_container',
                'saida',
                'previsao_chegada',
                'observacoes',
            )
        }),
    )
 
 
@admin.register(ContaPagar)
class ContaPagarAdmin(admin.ModelAdmin):
    list_display = (
        'descricao',
        'processo',
        'fornecedor',
        'moeda',
        'valor',
        'vencimento',
        'pago',
        'data_pagamento',
    )
    search_fields = (
        'descricao',
        'fornecedor',
        'processo__numero_processo',
        'processo__cliente__nome',
        'processo__cliente__empresa',
    )
    list_filter = ('moeda', 'pago', 'vencimento', 'data_pagamento')
    autocomplete_fields = ('processo',)
 
 
@admin.register(ContaReceber)
class ContaReceberAdmin(admin.ModelAdmin):
    list_display = (
        'descricao',
        'processo',
        'cliente',
        'moeda',
        'valor',
        'vencimento',
        'recebido',
        'data_recebimento',
    )
    search_fields = (
        'descricao',
        'cliente',
        'processo__numero_processo',
        'processo__cliente__nome',
        'processo__cliente__empresa',
    )
    list_filter = ('moeda', 'recebido', 'vencimento', 'data_recebimento')
    autocomplete_fields = ('processo',)
 
 
@admin.register(ItemFatura)
class ItemFaturaAdmin(admin.ModelAdmin):
    list_display = ('descricao', 'processo', 'moeda', 'valor')
    search_fields = (
        'descricao',
        'processo__numero_processo',
        'processo__cliente__nome',
        'processo__cliente__empresa',
    )
    list_filter = ('moeda',)
    autocomplete_fields = ('processo',)
 
 
@admin.register(CotacaoMoeda)
class CotacaoMoedaAdmin(admin.ModelAdmin):
    list_display = ('processo', 'moeda', 'valor')
    search_fields = (
        'processo__numero_processo',
        'processo__cliente__nome',
        'processo__cliente__empresa',
    )
    list_filter = ('moeda',)
    autocomplete_fields = ('processo',)
 
 
@admin.register(DadosBancarios)
class DadosBancariosAdmin(admin.ModelAdmin):
    list_display = ('banco', 'agencia', 'conta_corrente', 'favorecido', 'cnpj')
    search_fields = ('banco', 'agencia', 'conta_corrente', 'favorecido', 'cnpj')
 
 
@admin.register(ItemCotacao)
class ItemCotacaoAdmin(admin.ModelAdmin):
    list_display = ('descricao', 'cotacao', 'moeda', 'valor')
    search_fields = (
        'descricao',
        'cotacao__cliente__nome',
        'cotacao__cliente__empresa',
        'cotacao__referencia_cliente',
    )
    list_filter = ('moeda',)
    autocomplete_fields = ('cotacao',)
 
 
@admin.register(CustoCotacao)
class CustoCotacaoAdmin(admin.ModelAdmin):
    list_display = ('descricao', 'cotacao', 'fornecedor', 'moeda', 'valor')
    search_fields = (
        'descricao',
        'fornecedor',
        'cotacao__cliente__nome',
        'cotacao__cliente__empresa',
        'cotacao__referencia_cliente',
    )
    list_filter = ('moeda',)
    autocomplete_fields = ('cotacao',)
 
 
@admin.register(CotacaoCambio)
class CotacaoCambioAdmin(admin.ModelAdmin):
    list_display = ('cotacao', 'moeda', 'valor')
    search_fields = (
        'cotacao__cliente__nome',
        'cotacao__cliente__empresa',
        'cotacao__referencia_cliente',
    )
    list_filter = ('moeda',)
    autocomplete_fields = ('cotacao',)
 
 
@admin.register(FollowUp)
class FollowUpAdmin(admin.ModelAdmin):
    list_display = ('processo', 'data', 'concluido', 'criado_em')
    search_fields = (
        'descricao',
        'processo__numero_processo',
        'processo__cliente__nome',
        'processo__cliente__empresa',
    )
    list_filter = ('concluido', 'data', 'criado_em')
    autocomplete_fields = ('processo',)
 
 
@admin.register(TarefaOperacional)
class TarefaOperacionalAdmin(admin.ModelAdmin):
    list_display = (
        'descricao',
        'processo',
        'prazo',
        'responsavel',
        'status',
        'criado_em',
        'atualizado_em',
    )
    search_fields = (
        'descricao',
        'responsavel',
        'processo__numero_processo',
        'processo__cliente__nome',
        'processo__cliente__empresa',
    )
    list_filter = ('status', 'prazo', 'criado_em', 'atualizado_em')
    autocomplete_fields = ('processo',)
