from django.core.management import BaseCommand
from core_app.models import User
from django.core.mail import send_mail
from django.core.urlresolvers import reverse
from card_app.models import Card, EArrivedCardDeadline
from django.db.models import Q, F
from django.utils import timezone
from django.conf import settings

arcabot, _ = User.objects.get_or_create(
email=settings.ARCAMENS_BOT_EMAIL, name=settings.ARCAMENS_BOT_NAME)

class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        now   = timezone.now()
        query = Q(deadline__lte=now)  & Q(expired=False) & Q(done=False)
        cards = Card.objects.filter(query)
        cards = cards.only('id', 'label', 'workers')
    
        for ind in cards:
            self.run_timeout(ind)

        # Set all them as expired.
        cards = Card.objects.filter(query)
        cards.update(expired=True)

        self.stdout.write('Checked deadlines!')
    
    def run_timeout(self, card):
        url    = '%s%s' % (settings.LOCAL_ADDR, 
        reverse('card_app:card-link', kwargs={'card_id': card.id}))
        emails = card.workers.values_list('email')
    
        send_mail('Task deadline has arrived', '%s %s' % (card.label, url),
                'noreply@arcamens.com', emails, fail_silently=False)

        event = EArrivedCardDeadline.objects.create(deadline=card.deadline,
        organization=card.ancestor.ancestor.organization, card=card, 
        ancestor=card.ancestor, board=card.ancestor.ancestor, user=arcabot)
    
        event.dispatch(*card.workers.all(), *card.ancestor.ancestor.members.all())
    

