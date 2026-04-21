from django.http import HttpResponse
from openpyxl import Workbook
from .models import Processo
from .utils import gerar_fatura_pdf


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