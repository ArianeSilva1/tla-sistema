from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.utils import timezone
from django.conf import settings

from core.models import Processo


class Command(BaseCommand):
    help = 'Envia alertas operacionais automáticos'

    def handle(self, *args, **options):
        hoje = timezone.now().date()
        processos = Processo.objects.all()
        enviados = 0

        for p in processos:
            mensagem = None

            # 🚨 1. Booking pendente próximo do embarque
            if p.etd and not p.booking:
                dias = (p.etd - hoje).days
                if dias <= 5:
                    mensagem = f'''
Processo: {p.numero_processo}
Cliente: {p.cliente}
⚠️ Booking pendente
ETD: {p.etd}
'''

            # 🚨 2. SI não enviado
            elif not p.si_enviado:
                mensagem = f'''
Processo: {p.numero_processo}
Cliente: {p.cliente}
⚠️ SI não enviado
'''

            # 🚨 3. Pré-alerta não enviado
            elif not p.pre_alerta_enviado:
                mensagem = f'''
Processo: {p.numero_processo}
Cliente: {p.cliente}
⚠️ Pré-alerta pendente
'''

            # 🚨 4. Processo atrasado
            elif p.etd and p.etd < hoje and p.status_operacional != 'EMBARCADO':
                mensagem = f'''
Processo: {p.numero_processo}
Cliente: {p.cliente}
🚨 PROCESSO ATRASADO
ETD: {p.etd}
'''

            if mensagem:
                send_mail(
                    subject=f'🚨 Alerta Operacional - Processo {p.numero_processo}',
                    message=mensagem,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=['operacional@tlamultimodal.com'],
                    fail_silently=False,
                )
                enviados += 1

        self.stdout.write(self.style.SUCCESS(f'{enviados} alertas enviados!'))