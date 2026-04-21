from django.db import models
from django.utils import timezone
from decimal import Decimal
 
 
MOEDA_CHOICES = [
    ('BRL', 'Real'),
    ('USD', 'Dólar'),
    ('EUR', 'Euro'),
    ('GBP', 'Libra'),
]
 
TIPO_PROCESSO_CHOICES = [
    ('IMPORTACAO', 'Importação'),
    ('EXPORTACAO', 'Exportação'),
]
 
STATUS_PROCESSO_CHOICES = [
    ('ABERTO', 'Aberto'),
    ('ANDAMENTO', 'Em andamento'),
    ('FINALIZADO', 'Finalizado'),
]
 
PRIORIDADE_CHOICES = [
    ('BAIXA', 'Baixa'),
    ('MEDIA', 'Média'),
    ('ALTA', 'Alta'),
]
 
MODAL_CHOICES = [
    ('MARITIMO', 'Marítimo'),
    ('AEREO', 'Aéreo'),
    ('RODOVIARIO', 'Rodoviário'),
]
 
STATUS_OPERACIONAL_CHOICES = [
    ('AGUARDANDO_BOOKING', 'Aguardando booking'),
    ('BOOKING_CONFIRMADO', 'Booking confirmado'),
    ('DRAFT_CONFERENCIA', 'Draft em conferência'),
    ('SI_PENDENTE', 'SI pendente'),
    ('PRE_ALERTA_PENDENTE', 'Pré-alerta pendente'),
    ('EMBARCADO', 'Embarcado'),
    ('CHEGADA_PENDENTE', 'Chegada pendente'),
    ('FATURAMENTO_PENDENTE', 'Faturamento pendente'),
    ('FINALIZADO', 'Finalizado'),
    ('ATRASADO', 'Atrasado'),
]
 
STATUS_TAREFA_CHOICES = [
    ('PENDENTE', 'Pendente'),
    ('EM_ANDAMENTO', 'Em andamento'),
    ('CONCLUIDO', 'Concluído'),
    ('CANCELADO', 'Cancelado'),
]
 
STATUS_COTACAO_CHOICES = [
    ('EM_ANALISE', 'Em análise'),
    ('ENVIADA', 'Enviada'),
    ('APROVADA', 'Aprovada'),
    ('RECUSADA', 'Recusada'),
]
 
 
class Cliente(models.Model):
    nome = models.CharField(max_length=100)
    empresa = models.CharField(max_length=150, blank=True, null=True)
    cnpj = models.CharField(max_length=18, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    telefone = models.CharField(max_length=20, blank=True, null=True)
    criado_em = models.DateTimeField(auto_now_add=True)
 
    class Meta:
        verbose_name = 'Cliente'
        verbose_name_plural = 'Clientes'
        ordering = ['nome']
 
    def __str__(self):
        if self.empresa:
            return f"{self.nome} - {self.empresa}"
        return self.nome
 
 
class Processo(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
 
    numero_processo = models.CharField(max_length=20, unique=True, blank=True)
    numero_fatura = models.CharField(max_length=20, unique=True, blank=True, null=True)
 
    referencia_cliente = models.CharField(max_length=100, blank=True, null=True)
    data_emissao = models.DateField(auto_now_add=True)
 
    tipo = models.CharField(max_length=20, choices=TIPO_PROCESSO_CHOICES)
 
    moeda_principal = models.CharField(max_length=10, choices=MOEDA_CHOICES, default='BRL')
    tarifa_cotacao = models.DecimalField(max_digits=14, decimal_places=4, blank=True, null=True)
    data_cotacao = models.DateField(blank=True, null=True)
    iof_percentual = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    valor_recebido = models.DecimalField(max_digits=14, decimal_places=2, blank=True, null=True)
 
    status = models.CharField(max_length=20, choices=STATUS_PROCESSO_CHOICES, default='ABERTO')
 
    # Campos logísticos
    origem = models.CharField(max_length=100, blank=True, null=True)
    pol = models.CharField(max_length=100, blank=True, null=True)
    destino = models.CharField(max_length=100, blank=True, null=True)
    transbordo = models.CharField(max_length=100, blank=True, null=True)
    modal = models.CharField(max_length=20, choices=MODAL_CHOICES, blank=True, null=True)
 
    booking = models.CharField(max_length=100, blank=True, null=True)
    transit_time = models.CharField(max_length=20, blank=True, null=True)
    armador = models.CharField(max_length=100, blank=True, null=True)
    cia_aerea = models.CharField(max_length=100, blank=True, null=True)
 
    saida = models.DateField(blank=True, null=True)
    previsao_chegada = models.DateField(blank=True, null=True)
    etd = models.DateField(blank=True, null=True)
    eta = models.DateField(blank=True, null=True)
 
    container_type = models.CharField(max_length=100, blank=True, null=True)
    navio = models.CharField(max_length=100, blank=True, null=True)
    place_of_delivery = models.CharField(max_length=100, blank=True, null=True)
    pickup_container = models.CharField(max_length=100, blank=True, null=True)
 
    # Dashboard operacional
    responsavel = models.CharField(max_length=100, blank=True, null=True)
    prioridade = models.CharField(max_length=10, choices=PRIORIDADE_CHOICES, default='MEDIA')
    status_operacional = models.CharField(
        max_length=30,
        choices=STATUS_OPERACIONAL_CHOICES,
        default='AGUARDANDO_BOOKING'
    )
    pendencias = models.TextField(blank=True, null=True)
    observacoes = models.TextField(blank=True, null=True)
 
    draft_ok = models.BooleanField(default=False)
    si_enviado = models.BooleanField(default=False)
    pre_alerta_enviado = models.BooleanField(default=False)
 
    ultima_atualizacao = models.DateTimeField(auto_now=True)
 
    class Meta:
        ordering = ['-data_emissao', '-id']
        verbose_name = 'Processo'
        verbose_name_plural = 'Processos'
 
    def save(self, *args, **kwargs):
        hoje = timezone.now()
        ano = str(hoje.year)[-2:]
        mes = f"{hoje.month:02d}"
 
        if not self.numero_processo:
            ultimo = Processo.objects.filter(
                numero_processo__startswith=f"{ano}{mes}"
            ).order_by('-numero_processo').first()
 
            if ultimo and ultimo.numero_processo and len(ultimo.numero_processo) >= 7:
                sequencia = int(ultimo.numero_processo[-3:]) + 1
            else:
                sequencia = 1
 
            self.numero_processo = f"{ano}{mes}{sequencia:03d}"
 
        if not self.numero_fatura:
            prefixo = "IM" if self.tipo == "IMPORTACAO" else "EX"
 
            ultima_fatura = Processo.objects.filter(
                numero_fatura__startswith=prefixo
            ).order_by('-numero_fatura').first()
 
            if ultima_fatura and ultima_fatura.numero_fatura:
                try:
                    parte = ultima_fatura.numero_fatura.split('-')[0]
                    sequencia_fatura = int(parte[2:]) + 1
                except Exception:
                    sequencia_fatura = 1
            else:
                sequencia_fatura = 1
 
            self.numero_fatura = f"{prefixo}{sequencia_fatura:03d}-{ano}"
 
        super().save(*args, **kwargs)
 
    def total_faturado_brl(self):
        cotacoes = {c.moeda: c.valor for c in self.cotacoes.all()}
        total = Decimal("0.00")
 
        for item in self.itens.all():
            if item.moeda == "BRL":
                total += item.valor
            else:
                cotacao = cotacoes.get(item.moeda)
                if cotacao:
                    total += item.valor * cotacao
 
        return total
 
    def total_custo_brl(self):
        cotacoes = {c.moeda: c.valor for c in self.cotacoes.all()}
        total = Decimal("0.00")
 
        for conta in self.contas_pagar.all():
            if conta.moeda == "BRL":
                total += conta.valor
            else:
                cotacao = cotacoes.get(conta.moeda)
                if cotacao:
                    total += conta.valor * cotacao
 
        return total
 
    def total_recebido_brl(self):
        cotacoes = {c.moeda: c.valor for c in self.cotacoes.all()}
        total = Decimal("0.00")
 
        for conta in self.contas_receber.all():
            if conta.moeda == "BRL":
                total += conta.valor
            else:
                cotacao = cotacoes.get(conta.moeda)
                if cotacao:
                    total += conta.valor * cotacao
 
        return total
 
    def total_iof_brl(self):
        cotacoes = {c.moeda: c.valor for c in self.cotacoes.all()}
        total_estrangeiro = Decimal("0.00")
 
        for item in self.itens.all():
            if item.moeda != "BRL":
                cotacao = cotacoes.get(item.moeda)
                if cotacao:
                    total_estrangeiro += item.valor * cotacao
 
        iof = self.iof_percentual or Decimal("0.00")
        return total_estrangeiro * (iof / Decimal("100.00"))
 
    def total_faturado_com_iof_brl(self):
        return self.total_faturado_brl() + self.total_iof_brl()
 
    def lucro_brl(self):
        return self.total_faturado_com_iof_brl() - self.total_custo_brl()
 
    def __str__(self):
        return self.numero_processo or f"Processo {self.pk}"
 
 
class ItemFatura(models.Model):
    processo = models.ForeignKey(Processo, on_delete=models.CASCADE, related_name='itens')
    descricao = models.CharField(max_length=100)
    moeda = models.CharField(max_length=10, choices=MOEDA_CHOICES, default='BRL')
    valor = models.DecimalField(max_digits=14, decimal_places=2)
 
    class Meta:
        verbose_name = 'Item da Fatura'
        verbose_name_plural = 'Itens da Fatura'
 
    def __str__(self):
        return self.descricao
 
 
class CotacaoMoeda(models.Model):
    processo = models.ForeignKey(Processo, on_delete=models.CASCADE, related_name='cotacoes')
    moeda = models.CharField(max_length=10, choices=MOEDA_CHOICES)
    valor = models.DecimalField(max_digits=14, decimal_places=4)
 
    class Meta:
        verbose_name = 'Cotação de Moeda'
        verbose_name_plural = 'Cotações de Moeda'
 
    def __str__(self):
        return f"{self.moeda} - {self.valor}"
 
 
class ContaPagar(models.Model):
    processo = models.ForeignKey(Processo, on_delete=models.CASCADE, related_name='contas_pagar')
    descricao = models.CharField(max_length=100)
    fornecedor = models.CharField(max_length=150, blank=True, null=True)
    moeda = models.CharField(max_length=10, choices=MOEDA_CHOICES, default='BRL')
    valor = models.DecimalField(max_digits=14, decimal_places=2)
    vencimento = models.DateField(blank=True, null=True)
    pago = models.BooleanField(default=False)
    data_pagamento = models.DateField(blank=True, null=True)
 
    class Meta:
        verbose_name = 'Conta a Pagar'
        verbose_name_plural = 'Contas a Pagar'
 
    def __str__(self):
        return self.descricao
 
 
class ContaReceber(models.Model):
    processo = models.ForeignKey(Processo, on_delete=models.CASCADE, related_name='contas_receber')
    descricao = models.CharField(max_length=100)
    cliente = models.CharField(max_length=150, blank=True, null=True)
    moeda = models.CharField(max_length=10, choices=MOEDA_CHOICES, default='BRL')
    valor = models.DecimalField(max_digits=14, decimal_places=2)
    vencimento = models.DateField(blank=True, null=True)
    recebido = models.BooleanField(default=False)
    data_recebimento = models.DateField(blank=True, null=True)
    observacoes = models.TextField(blank=True, null=True)
 
    class Meta:
        verbose_name = 'Conta a Receber'
        verbose_name_plural = 'Contas a Receber'
 
    def __str__(self):
        return self.descricao
 
 
class DadosBancarios(models.Model):
    banco = models.CharField(max_length=100)
    agencia = models.CharField(max_length=20)
    conta_corrente = models.CharField(max_length=20)
    favorecido = models.CharField(max_length=150)
    cnpj = models.CharField(max_length=20)
 
    class Meta:
        verbose_name = 'Dado Bancário'
        verbose_name_plural = 'Dados Bancários'
 
    def __str__(self):
        return self.banco
 
 
class Cotacao(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    processo_gerado = models.OneToOneField(
        Processo,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='cotacao_origem'
    )
 
    referencia_cliente = models.CharField(max_length=100, blank=True, null=True)
    tipo = models.CharField(max_length=20, choices=TIPO_PROCESSO_CHOICES)
 
    moeda_principal = models.CharField(max_length=10, choices=MOEDA_CHOICES, default='BRL')
    tarifa_cotacao = models.DecimalField(max_digits=14, decimal_places=4, blank=True, null=True)
    data_cotacao = models.DateField(blank=True, null=True)
    iof_percentual = models.DecimalField(max_digits=5, decimal_places=2, default=0)
 
    pol = models.CharField(max_length=100, blank=True, null=True)
    destino = models.CharField(max_length=100, blank=True, null=True)
    transbordo = models.CharField(max_length=100, blank=True, null=True)
    booking = models.CharField(max_length=100, blank=True, null=True)
    transit_time = models.CharField(max_length=20, blank=True, null=True)
    armador = models.CharField(max_length=100, blank=True, null=True)
 
    saida = models.DateField(blank=True, null=True)
    previsao_chegada = models.DateField(blank=True, null=True)
 
    container_type = models.CharField(max_length=100, blank=True, null=True)
    navio = models.CharField(max_length=100, blank=True, null=True)
    place_of_delivery = models.CharField(max_length=100, blank=True, null=True)
    pickup_container = models.CharField(max_length=100, blank=True, null=True)
 
    status = models.CharField(max_length=20, choices=STATUS_COTACAO_CHOICES, default='EM_ANALISE')
    observacoes = models.TextField(blank=True, null=True)
    criado_em = models.DateTimeField(auto_now_add=True)
 
    class Meta:
        verbose_name = 'Cotação'
        verbose_name_plural = 'Cotações'
        ordering = ['-criado_em', '-id']
 
    def __str__(self):
        return f"Cotação - {self.cliente} - {self.get_tipo_display()}"
 
 
class ItemCotacao(models.Model):
    cotacao = models.ForeignKey('Cotacao', on_delete=models.CASCADE, related_name='itens_cotacao')
    descricao = models.CharField(max_length=100)
    moeda = models.CharField(max_length=10, choices=MOEDA_CHOICES, default='BRL')
    valor = models.DecimalField(max_digits=14, decimal_places=2)
 
    class Meta:
        verbose_name = 'Item da Cotação'
        verbose_name_plural = 'Itens da Cotação'
 
    def __str__(self):
        return self.descricao
 
 
class CustoCotacao(models.Model):
    cotacao = models.ForeignKey('Cotacao', on_delete=models.CASCADE, related_name='custos_cotacao')
    descricao = models.CharField(max_length=100)
    fornecedor = models.CharField(max_length=150, blank=True, null=True)
    moeda = models.CharField(max_length=10, choices=MOEDA_CHOICES, default='BRL')
    valor = models.DecimalField(max_digits=14, decimal_places=2)
 
    class Meta:
        verbose_name = 'Custo da Cotação'
        verbose_name_plural = 'Custos da Cotação'
 
    def __str__(self):
        return self.descricao
 
 
class CotacaoCambio(models.Model):
    cotacao = models.ForeignKey('Cotacao', on_delete=models.CASCADE, related_name='cotacoes_moeda')
    moeda = models.CharField(max_length=10, choices=MOEDA_CHOICES)
    valor = models.DecimalField(max_digits=14, decimal_places=4)
 
    class Meta:
        verbose_name = 'Câmbio da Cotação'
        verbose_name_plural = 'Câmbios da Cotação'
 
    def __str__(self):
        return f"{self.moeda} - {self.valor}"
 
 
class FollowUp(models.Model):
    processo = models.ForeignKey(Processo, on_delete=models.CASCADE, related_name='followups')
    descricao = models.TextField()
    data = models.DateField()
    concluido = models.BooleanField(default=False)
    criado_em = models.DateTimeField(auto_now_add=True)
 
    class Meta:
        verbose_name = 'Follow-up'
        verbose_name_plural = 'Follow-ups'
        ordering = ['-data', '-id']
 
    def __str__(self):
        return f"{self.processo} - {self.data}"
 
 
class TarefaOperacional(models.Model):
    processo = models.ForeignKey(Processo, on_delete=models.CASCADE, related_name='tarefas_operacionais')
    descricao = models.CharField(max_length=200)
    prazo = models.DateField(blank=True, null=True)
    responsavel = models.CharField(max_length=100, blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_TAREFA_CHOICES, default='PENDENTE')
    observacoes = models.TextField(blank=True, null=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)
 
    class Meta:
        ordering = ['prazo', '-criado_em']
        verbose_name = 'Tarefa Operacional'
        verbose_name_plural = 'Tarefas Operacionais'
 
    def __str__(self):
        return f"{self.processo} - {self.descricao}"
