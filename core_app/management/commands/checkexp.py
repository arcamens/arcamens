from django.core.management import BaseCommand
from core_app.models import User, Organization, EDisabledAccount
from django.conf import settings
from datetime import date

arcabot, _ = User.objects.get_or_create(
email=settings.ARCAMENS_BOT_EMAIL, name=settings.ARCAMENS_BOT_NAME)

class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        users = User.objects.filter(paid=True, expiration__gte=date.today())
        users.update(enabled=False)

        users = User.objects.filter(paid=True, expiration__gte=date.today())
        users = users.only('id')

        for ind in users:
            self.disable(ind)
        self.stdout.write('Checked expiration!')
    
    def disable(self, user):
        user.enabled = False
        user.save()

        reason = 'Your accounnt expiration has ran over!'
        event  = EDisabledAccount.objects.create(user=arcabot, reason=reason)
        event.dispatch(user)

    





