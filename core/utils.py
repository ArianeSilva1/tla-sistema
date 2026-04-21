from decimal import Decimal
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from django.http import HttpResponse
from django.conf import settings
from .models import Processo, DadosBancarios
import os


def gerar_fatura_pdf(processo_id):
    processo = Processo.objects.get(id=processo_id)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="fatura_{processo.numero_processo}.pdf"'

    c = canvas.Canvas(response, pagesize=A4)
    largura, altura = A4

    margem_esq = 40
    margem_dir = largura - 40
    y = altura - 42

    azul = colors.HexColor("#1F3A5F")
    cinza = colors.HexColor("#666666")
    cinza_claro = colors.HexColor("#D9D9D9")
    preto = colors.black

    # =========================
    # LOGO
    # =========================
    logo_path = os.path.join(settings.BASE_DIR, 'core', 'static', 'logo.png')

    if os.path.exists(logo_path):
        c.drawImage(
            logo_path,
            margem_esq,
            y - 62,
            width=155,
            height=82,
            preserveAspectRatio=True,
            mask='auto'
        )

    # =========================
    # CABEÇALHO DIREITO
    # =========================
    c.setFillColor(azul)
    c.setFont("Helvetica-Bold", 20)
    c.drawRightString(margem_dir, y, "TLA MULTIMODAL")

    y -= 22
    c.setFillColor(preto)
    c.setFont("Helvetica-Bold", 11)
    c.drawRightString(margem_dir, y, "INVOICE / FATURA DE SERVIÇOS")

    y -= 15
    c.setFillColor(cinza)
    c.setFont("Helvetica", 9)
    c.drawRightString(margem_dir, y, "TLA MULTIMODAL LOGÍSTICA LTDA")
    y -= 12
    c.drawRightString(margem_dir, y, "São Paulo - SP")
    y -= 12
    c.drawRightString(margem_dir, y, "financeiro@tlamultimodal.com")

    y -= 16
    c.setStrokeColor(azul)
    c.setLineWidth(1)
    c.line(margem_esq, y, margem_dir, y)

    # =========================
    # BLOCO SUPERIOR
    # =========================
    y -= 24

    c.setFillColor(azul)
    c.setFont("Helvetica-Bold", 10)
    c.drawString(margem_esq, y, "SHIPMENT / FATURA DETAILS")

    y -= 18
    c.setFillColor(preto)
    c.setFont("Helvetica", 9.5)

    c.drawString(margem_esq, y, f"Para: {processo.cliente.empresa or processo.cliente.nome}")
    c.drawRightString(margem_dir, y, f"Data: {processo.data_emissao.strftime('%d/%m/%Y') if processo.data_emissao else ''}")

    y -= 16
    c.drawString(margem_esq, y, f"Processo: {processo.numero_processo}")
    c.drawString(220, y, f"Referência: {processo.referencia_cliente or ''}")
    c.drawRightString(margem_dir, y, f"Embarque: {processo.get_tipo_display()}")

    y -= 16
    c.drawString(margem_esq, y, f"CNPJ do cliente: {processo.cliente.cnpj or ''}")
    c.drawString(220, y, f"Fatura: {processo.numero_fatura or ''}")

    y -= 16
    c.drawString(margem_esq, y, f"POL: {processo.pol or ''}")
    c.drawString(220, y, f"Destino: {processo.destino or ''}")
    c.drawRightString(margem_dir, y, f"Transbordo: {processo.transbordo or ''}")

    y -= 16
    c.drawString(margem_esq, y, f"No Booking: {processo.booking or ''}")
    c.drawString(220, y, f"Transit Time: {processo.transit_time or ''}")
    c.drawRightString(margem_dir, y, f"Armador: {processo.armador or ''}")

    y -= 16
    c.drawString(
        margem_esq,
        y,
        f"Saída: {processo.saida.strftime('%d/%m/%Y') if processo.saida else ''}"
    )
    c.drawString(
        220,
        y,
        f"Previsão chegada: {processo.previsao_chegada.strftime('%d/%m/%Y') if processo.previsao_chegada else ''}"
    )

    y -= 16
    c.drawString(margem_esq, y, f"Container Type: {processo.container_type or ''}")
    c.drawString(220, y, f"Navio: {processo.navio or ''}")

    y -= 16
    c.drawString(margem_esq, y, f"Place of delivery: {processo.place_of_delivery or ''}")
    c.drawString(320, y, f"Pick up Container: {processo.pickup_container or ''}")

    y -= 18
    c.setStrokeColor(cinza_claro)
    c.setLineWidth(0.8)
    c.line(margem_esq, y, margem_dir, y)

    # =========================
    # TABELA - CABEÇALHO
    # =========================
    y -= 22

    c.setFillColor(azul)
    c.setFont("Helvetica-Bold", 10)
    c.drawString(margem_esq, y, "NEGOCIAÇÃO")
    c.drawString(300, y, "MOEDA")
    c.drawRightString(margem_dir, y, "VALORES")

    y -= 10
    c.setStrokeColor(cinza_claro)
    c.setLineWidth(0.8)
    c.line(margem_esq, y, margem_dir, y)

    # =========================
    # COTAÇÕES
    # =========================
    cotacoes = {}
    lista_cotacoes = list(processo.cotacoes.all())

    for cotacao in lista_cotacoes:
        cotacoes[cotacao.moeda] = cotacao.valor

    total_brl_direto = Decimal("0.00")
    total_estrangeiro_convertido = Decimal("0.00")
    total_geral_sem_iof = Decimal("0.00")

    # =========================
    # ITENS
    # =========================
    y -= 18
    c.setFillColor(preto)
    c.setFont("Helvetica", 10)

    for item in processo.itens.all():
        moeda = item.moeda
        valor = item.valor

        if moeda == "BRL":
            valor_convertido = valor
            total_brl_direto += valor
        else:
            cotacao = cotacoes.get(moeda)
            if cotacao:
                valor_convertido = valor * cotacao
                total_estrangeiro_convertido += valor_convertido
            else:
                valor_convertido = Decimal("0.00")

        total_geral_sem_iof += valor_convertido

        c.drawString(margem_esq, y, item.descricao[:32])
        c.drawString(300, y, moeda)
        c.drawRightString(margem_dir, y, f"{valor:.2f}")

        y -= 16

    y -= 2
    c.setStrokeColor(cinza_claro)
    c.line(margem_esq, y, margem_dir, y)

    # =========================
    # COTAÇÕES DE MOEDA
    # =========================
    y -= 22
    c.setFillColor(azul)
    c.setFont("Helvetica-Bold", 10)
    c.drawString(margem_esq, y, "COTAÇÕES DE MOEDA")

    y -= 18
    c.setFillColor(preto)
    c.setFont("Helvetica", 10)

    if lista_cotacoes:
        for cotacao in lista_cotacoes:
            c.drawString(margem_esq, y, f"{cotacao.moeda}")
            c.drawRightString(220, y, f"{cotacao.valor:.4f}")
            y -= 15
    else:
        c.drawString(margem_esq, y, "Nenhuma cotação cadastrada")
        y -= 15

    # =========================
    # RESUMO FINANCEIRO
    # =========================
    iof_percentual = processo.iof_percentual or Decimal("0.00")
    valor_iof = total_estrangeiro_convertido * (iof_percentual / Decimal("100.00"))
    total_final = total_geral_sem_iof + valor_iof

    y -= 8
    c.setStrokeColor(cinza_claro)
    c.line(margem_esq, y, margem_dir, y)

    y -= 22
    c.setFillColor(azul)
    c.setFont("Helvetica-Bold", 10)
    c.drawString(margem_esq, y, "RESUMO FINANCEIRO")

    y -= 18
    c.setFillColor(preto)
    c.setFont("Helvetica", 10)
    c.drawString(margem_esq, y, "Moeda principal:")
    c.drawRightString(280, y, f"{processo.moeda_principal or ''}")

    c.drawString(330, y, "Tarifa cotação:")
    c.drawRightString(margem_dir, y, f"{processo.tarifa_cotacao or ''}")

    y -= 16
    c.drawString(margem_esq, y, "Total em reais sem IOF:")
    c.drawRightString(margem_dir, y, f"R$ {total_geral_sem_iof:.2f}")

    y -= 16
    c.drawString(margem_esq, y, "Total BRL direto:")
    c.drawRightString(margem_dir, y, f"R$ {total_brl_direto:.2f}")

    y -= 16
    c.drawString(margem_esq, y, "Total estrangeiro convertido:")
    c.drawRightString(margem_dir, y, f"R$ {total_estrangeiro_convertido:.2f}")

    y -= 16
    c.drawString(margem_esq, y, f"IOF ({iof_percentual}%):")
    c.drawRightString(margem_dir, y, f"R$ {valor_iof:.2f}")

    if processo.valor_recebido:
        y -= 16
        c.drawString(margem_esq, y, "Valor recebido:")
        c.drawRightString(margem_dir, y, f"R$ {processo.valor_recebido:.2f}")

    # =========================
    # TOTAL FINAL DESTACADO
    # =========================
    y -= 24

    c.setFillColor(colors.HexColor("#F2F5F9"))
    c.rect(margem_esq, y - 12, largura - 80, 28, stroke=0, fill=1)

    c.setFillColor(azul)
    c.setFont("Helvetica-Bold", 13)
    c.drawString(margem_esq + 10, y, "VALOR TOTAL EM REAIS")
    c.drawRightString(margem_dir - 10, y, f"R$ {total_final:.2f}")

    # =========================
    # DADOS PARA PAGAMENTO
    # =========================
    dados = DadosBancarios.objects.first()

    if dados:
        y -= 34
        c.setStrokeColor(cinza_claro)
        c.setLineWidth(0.8)
        c.line(margem_esq, y, margem_dir, y)

        y -= 20
        c.setFillColor(azul)
        c.setFont("Helvetica-Bold", 10)
        c.drawString(margem_esq, y, "DADOS PARA PAGAMENTO")

        y -= 18
        c.setFillColor(preto)
        c.setFont("Helvetica", 10)
        c.drawString(margem_esq, y, f"Banco: {dados.banco}")
        y -= 15
        c.drawString(margem_esq, y, f"Agencia: {dados.agencia}")
        y -= 15
        c.drawString(margem_esq, y, f"Conta Corrente: {dados.conta_corrente}")
        y -= 15
        c.drawString(margem_esq, y, f"Favorecido: {dados.favorecido}")
        y -= 15
        c.drawString(margem_esq, y, f"CNPJ: {dados.cnpj}")

    # =========================
    # RODAPÉ
    # =========================
    c.setFillColor(cinza)
    c.setFont("Helvetica", 8)
    c.drawString(margem_esq, 22, "Documento gerado automaticamente pelo sistema TLA Multimodal.")

    c.save()
    return response