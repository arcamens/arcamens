from django import forms
from django.db.models import Q
from datetimewidget.widgets import DateTimeWidget
from core_app.forms import FileAttachment
from sqlike.forms import SqLikeForm
from . import models
from django.utils import timezone

class DeadlineMixinForm:
    def clean(self):
        super(DeadlineMixinForm, self).clean()
        deadline = self.cleaned_data.get('deadline')

        # Check if one of the parents has a deadline set
        # in that case it cant have a none deadline.
        cards = self.instance.path.filter(deadline__isnull=False)
        elem  = cards.first()
        ERR2  = ("Can't remove deadline!"
        "Doesn't meet parent: {label} " "Deadline: {deadline}")

        if elem and not deadline: 
            raise forms.ValidationError(ERR2.format(
                label=elem.label, deadline=elem.deadline))
        elif not deadline: 
            return

        if deadline < timezone.now():
            raise forms.ValidationError('Invalid deadline')

        # Check if one of the children has a none deadline
        # in that case he has to go and set the deadline.
        cards = self.instance.children.filter(Q(
        deadline=None) | Q(deadline__gt=deadline))

        elem = cards.first()
        ERR0 = ("Can't set deadline!"
        "Doesn't meet fork: {label} " "Deadline: {deadline}")

        if elem: raise forms.ValidationError(ERR0.format(
        label=elem.label, deadline=elem.deadline))

        # Check if one of the parent deadlines doesnt meet
        # the desired deadline. The parent deadline has to be
        # equal or greater to the set deadline.
        cards = self.instance.path.filter(Q(deadline__lt=deadline))
        elem  = cards.first()
        ERR1  = ("Can't set deadline!"
        "It doesn't meet parent: {label} " "Deadline: {deadline}")

        if elem: raise forms.ValidationError(ERR1.format(
        label=elem.label, deadline=elem.deadline))

class UserSearchForm(SqLikeForm, forms.Form):
    pattern = forms.CharField(required=False,
    help_text='Example: tag:arcamens + tag:bug-hunter')

class DeadlineForm(DeadlineMixinForm, forms.ModelForm):
    class Meta:
        model   = models.Card
        fields  = ('deadline', )
        widgets = {
            'deadline': DateTimeWidget(usel10n = True, 
                 bootstrap_version=3)
        }

class CardSearchForm(SqLikeForm, forms.Form):
    done = forms.BooleanField(required=False)

    pattern = forms.CharField(required=False, 
    help_text='Example: owner:oliveira + tag:bug')

class CardPriorityForm(SqLikeForm, forms.Form):
    pattern = forms.CharField(required=False, 
    help_text='Example: owner:oliveira + tag:bug')

class ConnectCardForm(SqLikeForm, forms.Form):
    pattern = forms.CharField(required=False, 
    help_text='Example: owner:oliveira + tag:bug')

class ConnectPostForm(SqLikeForm, forms.Form):
    pattern = forms.CharField(required=False, 
    help_text='Example: owner:oliveira + tag:bug')

class TagSearchForm(SqLikeForm, forms.Form):
    pattern = forms.CharField(required=False, 
    help_text='Example: fake-bug')

class ListSearchform(SqLikeForm, forms.Form):
    pattern = forms.CharField(required=False, 
    help_text='Ex: arcamens + todo ...')

class GroupSearchform(SqLikeForm, forms.Form):
    pattern = forms.CharField(required=False, 
    help_text='Ex: arcamens + backlog ...')

class CardAttentionForm(forms.Form):
    message = forms.CharField(
    required=False, widget=forms.Textarea,
    help_text='(Optional) Hey, do you remember \
    you have a job?')

class AlertCardWorkersForm(forms.Form):
    message = forms.CharField(
    required=False, widget=forms.Textarea,
    help_text='I need this task done a!')

class GlobalCardFilterForm(SqLikeForm, forms.ModelForm):
    class Meta:
        model  = models.GlobalCardFilter
        exclude = ('user', 'organization')

class CardFilterForm(SqLikeForm, forms.ModelForm):
    class Meta:
        model  = models.CardFilter
        exclude = ('user', 'organization', 
        'board', 'list')

class CardForm(forms.ModelForm):
    class Meta:
        model  = models.Card
        fields = ('label', 'data')

class CardFileWrapperForm(FileAttachment, forms.ModelForm):
    class Meta:
        model  = models.CardFileWrapper
        exclude = ('card', )



