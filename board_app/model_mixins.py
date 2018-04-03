from django.core.urlresolvers import reverse
from wsbells.models import QueueWS

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

    def get_link_url(self):
        if self.board:
            return reverse('board_app:board-link', 
                kwargs={'board_id': self.board.id})
        elif self.card:
            return reverse('card_app:card-link', 
                kwargs={'card_id': self.card.id})
        else:
            return reverse('list_app:list-link', 
                kwargs={'list_id': self.list.id})

    def get_target_name(self):
        if self.board:
            return self.board.name
        elif self.card:
            return self.card.label
        else:
            return self.list.name

class BoardMixin(QueueWS):
    @classmethod
    def get_user_boards(cls, user):
        boards = user.boards.filter(organization=user.default)
        return boards

    def get_ancestor_url(self):
        return reverse('board_app:list-boards')

    def get_link_url(self):
        return reverse('board_app:board-link', 
                    kwargs={'board_id': self.id})

    def __str__(self):
        return self.name

class EBindBoardUserMixin(object):
    pass

class EUnbindBoardUserMixin(object):
    pass

class EUpdateBoardMixin(object):
    pass

class ECreateBoardMixin(object):
    pass






