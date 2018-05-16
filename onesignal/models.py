from django.db import models

# Create your models here.
class GroupSignal(models.Model):
    class Meta:
        abstract = True

    def dispatch(self, notification, exclude=[]):
        message = notification.fmt_message()

    def push(self, devices=[]):
        pass

class Notification:
    def fmt_message(self):
        pass

class SignalToken(models.Model):
    token = models.CharField(null=True, blank=True, max_length=256)

class Device(models.Model):
    signal_token = models.OneToOneField('onesignal.SignalToken', 
    null=True, blank=True, related_name='device')
    uuid = models.CharField(null=True, blank=True, max_length=256)

    class Meta:
        abstract = True

    def init_onesignal(self):
        context = {'ONE_SIGNAL_APPID': settings.ONE_SIGNAL_APPID}
        tmp     = get_template('onesignal/init_onesignal.html')
        html    = tmp.render(context)
        return html

