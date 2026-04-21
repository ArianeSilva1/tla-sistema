from django.shortcuts import render
from django.http import HttpResponse
from django.utils import timezone
from openpyxl import Workbook

from .models import Processo
from .utils import gerar_fatura_pdf


def home(request):
    return render(request, 'core/home.html')


def fatura_pdf(request, processo_id):
    return gerar_fatura_pdf(processo_id)


def relatorio_excel(request):
    wb = Workbook()
    ws = wb.active
    ws.title = "Relatório Financeiro"

    ws.append([
        "Processo",
        "Fatura",
        "Cliente",
        "Referência Cliente",
        "Tipo",
        "Moeda Principal",
        "Total Faturado (R$)",
        "Total Custo (R$)",
        "Lucro (R$)",
    ])

    for processo in Processo.objects.all():
        ws.append([
            processo.numero_processo,
            processo.numero_fatura,
            processo.cliente.empresa or processo.cliente.nome,
            processo.referencia_cliente,
            processo.get_tipo_display(),
            processo.moeda_principal,
            float(processo.total_faturado_com_iof_brl()),
            float(processo.total_custo_brl()),
            float(processo.lucro_brl()),
        ])

    response = HttpResponse(
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    response["Content-Disposition"] = 'attachment; filename="relatorio_financeiro.xlsx"'

    wb.save(response)
    return response


def dashboard(request):
    processos = Processo.objects.select_related('cliente').all().order_by('-id')
    hoje = timezone.now().date()

    total_processos = processos.count()

    atrasados = processos.filter(
        etd__lt=hoje,
        status_operacional__in=[
            'AGUARDANDO_BOOKING',
            'SI_PENDENTE',
            'PRE_ALERTA_PENDENTE',
            'ATRASADO',
        ]
    ).count()

    aguardando_booking = processos.filter(
        status_operacional='AGUARDANDO_BOOKING'
    ).count()

    embarcados = processos.filter(
        status_operacional='EMBARCADO'
    ).count()

    context = {
        'processos': processos,
        'total_processos': total_processos,
        'atrasados': atrasados,
        'aguardando_booking': aguardando_booking,
        'embarcados': embarcados,
        'hoje': hoje,
    }

    return render(request, 'core/dashboard.html', context)