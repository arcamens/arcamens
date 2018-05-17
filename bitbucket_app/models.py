from django.utils.translation import ugettext_lazy as _
from core_app.models import Event
from django.db import models

class BitbucketHook(models.Model):
    """
    """

    organization = models.ForeignKey('core_app.Organization', null=True, blank=True,
    related_name='bitbucket_hooks')

    address = models.CharField(null=True, 
    help_text='Example: https://bitbucket.org/team/project/',
    blank=False, default='', max_length=626)

class EBitbucketCommit(Event):
    # Not sure if i should have abitbuckethooker 
    # foreignkey here. The user actor will
    # be the bitbucket addon.
    # We need to add commit_id too, for updating
    # in case the commit is deleted(not sure yet though).
    hook = models.ForeignKey('BitbucketHook', null=True, blank=True)

    url = models.CharField(null=True, blank=False, 
    max_length=626)

    note = models.OneToOneField('note_app.Note', null=True, blank=True,
    related_name='commit')

    html_template = 'bitbucket_app/e-bitbucket-commit.html'








