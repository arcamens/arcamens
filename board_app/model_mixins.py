from django.core.urlresolvers import reverse
from core_app import ws

class PinMixin(object):
    def get_absolute_url(self):
        if self.board:
            return reverse('list_app:list-lists', 
                kwargs={'board_id': self.board.id})
        elif self.card:
            return reverse('card_app:view-data', 
                kwargs={'card_id': self.card.id})
        else:
            return reverse('card_app:list-cards', 
                kwargs={'list_id': self.list.id})

    def get_target_name(self):
        if self.board:
            return self.board.name
        elif self.card:
            return self.card.label
        else:
            return self.list.name

class BoardMixin:
    def ws_alert(self):
        ws.client.publish('board%s' % self.id, 
            'alert-event', 0, False)

    def ws_sound(self):
        ws.client.publish('board%s' % self.id, 
            'sound', 0, False)

    @classmethod
    def get_user_boards(cls, user):
        boards = user.boards.filter(organization=user.default)
        return boards

    def get_ancestor_url(self):
        return reverse('board_app:list-boards')

class EBindBoardUserMixin(object):
    pass

class EUnbindBoardUserMixin(object):
    pass

class EUpdateBoardMixin(object):
    pass

class ECreateBoardMixin(object):
    pass


