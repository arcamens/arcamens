from django.db import models
from django.db.models import Q
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse
from django.core.mail import send_mail
from django.conf import settings
import random

class RegisterProcessMixin:
    def save(self, *args, **kwargs):
        self.token = 'signup%s' % random.randint(1000, 10000)

        signup_url = reverse('site_app:enable-account', 
        kwargs={'user_id': self.user.id, 'token': self.token})

        self.signup_url = '%s%s' % (settings.LOCAL_ADDR, signup_url)

        send_mail('Confirm your account', '%s' % self.signup_url, 
        'noreply@arcamens.com', [self.user.email], fail_silently=False)
        super().save(*args, **kwargs)

class PasswordTicket(models.Model):
    token = models.CharField(null=True,
    blank=False, max_length=256)

    user = models.ForeignKey('core_app.User', null=True, 
    related_name='password_tickets', blank=True)

    # expiration = models.DateTimeField(blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True, null=True)

class RegisterProcess(RegisterProcessMixin, models.Model):
    # email = models.EmailField(max_length=70, 
    # null=True, blank=False)
    user = models.OneToOneField('core_app.User', null=True, 
    blank=True, related_name='register_process')

    # should have a count to avoid mail spam.
    token = models.CharField(null=True,
    blank=False, max_length=256)

    signup_url = models.CharField(null=True,
    blank=False, max_length=256)

    created = models.DateTimeField(auto_now_add=True, null=True)





