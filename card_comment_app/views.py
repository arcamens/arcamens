from django.views.generic import View
from django.shortcuts import render, redirect
from board_app.views import GuardianView
import board_app.models
import card_app.models
from . import models
from . import forms

class ListCardComments(GuardianView):
    """
    """

    def get(self, request, card_id):
        card    = card_app.models.Card.objects.get(id=card_id)
        records = card.cardcomment_set.order_by('-created')
        return render(request, 'comment_app/list-comments.html', 
        {'form':forms.CardCommentForm(), 'card': card, 'records': records})

class CreateCardComment(GuardianView):
    def post(self, request, card_id):
        user = core_app.models.User.objects.get(id=self.user_id)
        card = card_app.models.Card.objects.get(id=card_id)
        records = card.cardcomment_set.order_by('-created')
        form = forms.CardCommentForm(request.POST, request.FILES)

        if not form.is_valid():
            return render(request, 'comment_app/list-comments.html',
                {'form': form, 'card':card, 'records': records}, status=400)
        record      = form.save(commit = False)
        record.card = card
        record.user = user
        record.save()

        user = core_app.models.User.objects.get(id=self.user_id)
        event = models.ECreateCardComment.objects.create(organization=user.default,
        child=card, comment=record, user=user)
        event.users.add(*card.ancestor.ancestor.members.all())

        return redirect('comment_app:list-comments', 
        card_id=card.id)

class ECreateCardComment(GuardianView):
    """
    """

    def get(self, request, event_id):
        event = models.ECreateCardComment.objects.get(id=event_id)
        return render(request, 'comment_app/e-create-comment.html', 
        {'event':event})










