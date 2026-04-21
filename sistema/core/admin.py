from django.contrib import admin, messages
from django.db import transaction
from .models import (
    Cliente,
    Processo,
    ItemFatura,
    CotacaoMoeda,
    DadosBancarios,
    ContaPagar,
    Cotacao,
    ItemCotacao,
    CustoCotacao,
    CotacaoCambio,
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


def gerar_processo_da_cotacao(cotacao):
    if cotacao.processo_gerado:
        return cotacao.processo_gerado

    with transaction.atomic():
        processo = Processo.objects.create(
            cliente=cotacao.cliente,
            referencia_cliente=cotacao.referencia_cliente,
            tipo=cotacao.tipo,
            moeda_principal=cotacao.moeda_principal,
            tarifa_cotacao=cotacao.tarifa_cotacao,
            data_cotacao=cotacao.data_cotacao,
            iof_percentual=cotacao.iof_percentual,
            pol=cotacao.pol,
            destino=cotacao.destino,
            transbordo=cotacao.transbordo,
            booking=cotacao.booking,
            transit_time=cotacao.transit_time,
            armador=cotacao.armador,
            saida=cotacao.saida,
            previsao_chegada=cotacao.previsao_chegada,
            container_type=cotacao.container_type,
            navio=cotacao.navio,
            place_of_delivery=cotacao.place_of_delivery,
            pickup_container=cotacao.pickup_container,
            status='ABERTO',
        )

        for item in cotacao.itens_cotacao.all():
            ItemFatura.objects.create(
                processo=processo,
                descricao=item.descricao,
                moeda=item.moeda,
                valor=item.valor,
            )

        for custo in cotacao.custos_cotacao.all():
            ContaPagar.objects.create(
                processo=processo,
                descricao=custo.descricao,
                fornecedor=custo.fornecedor,
                moeda=custo.moeda,
                valor=custo.valor,
            )

        if cotacao.cotacoes_moeda.exists():
            for cambio in cotacao.cotacoes_moeda.all():
                CotacaoMoeda.objects.create(
                    processo=processo,
                    moeda=cambio.moeda,
                    valor=cambio.valor,
                )
        elif cotacao.tarifa_cotacao:
            CotacaoMoeda.objects.create(
                processo=processo,
                moeda=cotacao.moeda_principal,
                valor=cotacao.tarifa_cotacao,
            )

        cotacao.processo_gerado = processo
        cotacao.status = 'APROVADA'
        cotacao.save()

        return processo


@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ('nome', 'empresa', 'cnpj', 'email', 'telefone', 'criado_em')
    search_fields = ('nome', 'empresa', 'cnpj')


@admin.register(Processo)
class ProcessoAdmin(admin.ModelAdmin):
    list_display = (
        'numero_processo',
        'numero_fatura',
        'cliente',
        'referencia_cliente',
        'data_emissao',
        'tipo',
        'moeda_principal',
        'status',
        'mostrar_total_faturado',
        'mostrar_total_custo',
        'mostrar_lucro',
    )

    search_fields = (
        'numero_processo',
        'numero_fatura',
        'referencia_cliente',
        'cliente__nome',
        'cliente__empresa',
        'booking',
    )

    list_filter = (
        'tipo',
        'status',
        'moeda_principal',
    )

    inlines = [ItemFaturaInline, CotacaoMoedaInline, ContaPagarInline]

    def mostrar_total_faturado(self, obj):
        return f"R$ {obj.total_faturado_com_iof_brl():.2f}"
    mostrar_total_faturado.short_description = "Total faturado"

    def mostrar_total_custo(self, obj):
        return f"R$ {obj.total_custo_brl():.2f}"
    mostrar_total_custo.short_description = "Total custo"

    def mostrar_lucro(self, obj):
        return f"R$ {obj.lucro_brl():.2f}"
    mostrar_lucro.short_description = "Lucro"


@admin.register(DadosBancarios)
class DadosBancariosAdmin(admin.ModelAdmin):
    list_display = (
        'banco',
        'agencia',
        'conta_corrente',
        'favorecido',
        'cnpj',
    )
    search_fields = ('banco', 'favorecido', 'cnpj')


@admin.register(ContaPagar)
class ContaPagarAdmin(admin.ModelAdmin):
    list_display = (
        'processo',
        'descricao',
        'fornecedor',
        'moeda',
        'valor',
        'vencimento',
        'pago',
        'data_pagamento',
    )
    search_fields = ('processo__numero_processo', 'descricao', 'fornecedor')
    list_filter = ('moeda', 'pago', 'vencimento')


@admin.register(Cotacao)
class CotacaoAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'cliente',
        'referencia_cliente',
        'tipo',
        'moeda_principal',
        'status',
        'processo_gerado',
        'criado_em',
    )

    search_fields = (
        'cliente__nome',
        'cliente__empresa',
        'referencia_cliente',
        'booking',
    )

    list_filter = (
        'tipo',
        'status',
        'moeda_principal',
        'criado_em',
    )

    inlines = [ItemCotacaoInline, CustoCotacaoInline, CotacaoCambioInline]
    actions = ['aprovar_cotacoes']

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)

        if obj.status == 'APROVADA' and not obj.processo_gerado:
            processo = gerar_processo_da_cotacao(obj)
            self.message_user(
                request,
                f'Cotação aprovada e processo {processo.numero_processo} criado com sucesso.',
                level=messages.SUCCESS
            )

    def aprovar_cotacoes(self, request, queryset):
        total = 0

        for cotacao in queryset:
            if not cotacao.processo_gerado:
                gerar_processo_da_cotacao(cotacao)
                total += 1

        self.message_user(
            request,
            f'{total} cotação(ões) aprovada(s) e transformada(s) em processo.',
            level=messages.SUCCESS
        )

    aprovar_cotacoes.short_description = "Aprovar cotações selecionadas e gerar processos"