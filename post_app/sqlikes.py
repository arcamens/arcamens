from sqlike.parser import SqLike, SqNode
from post_app.models import Post
from django.db.models import Q

class SqOwner(SqNode):
    def __init__(self):
        super(SqOwner, self).__init__(('o', 'owner'), self.query)

    def query(self, ind):
        q0 = Q(owner__name__icontains=ind)
        q1 = Q(owner__email__icontains=ind)
        return  q0 | q1

class SqNotOwner(SqOwner):
    def __init__(self):
        super(SqOwner, self).__init__(('!o', '!owner'), 
        lambda ind: ~self.query(ind))

class SqLiker(SqNode):
    def __init__(self):
        super(SqLiker, self).__init__(('le', 'liker'), self.query, chain=True)

    def query(self, ind):
        q0 = Q(likes__name__icontains=ind)
        q1 = Q(likes__email__icontains=ind)
        return q0 | q1

class SqNotLiker(SqLiker):
    def __init__(self):
        super(SqLiker, self).__init__(('!le', '!liker'), 
        lambda ind: ~self.query(ind), chain=True)


class SqCreatedGt(SqNode):
    def __init__(self):
        super(SqCreatedGt, self).__init__(('c>', 'created>'), self.query)

    def query(self, ind):
        return Q(created__gt=ind)

class SqCreatedLt(SqNode):
    def __init__(self):
        super(SqCreatedLt, self).__init__(('c<', 'created<'), self.query)

    def query(self, ind):
        return Q(created__lt=ind)

class SqCreated(SqNode):
    def __init__(self):
        super(SqCreated, self).__init__(('c', 'created'), self.query)

    def query(self, ind):
        return Q(created__date=ind)

class SqLabel(SqNode):
    def __init__(self):
        super(SqLabel, self).__init__(('l', 'label'), self.query)

    def query(self, ind):
        return Q(label__icontains=ind)

class SqNotLabel(SqLabel):
    def __init__(self):
        super(SqLabel, self).__init__(('!l', '!label'), 
        lambda ind: ~self.query(ind))

class SqData(SqNode):
    def __init__(self):
        super(SqData, self).__init__(('d', 'data'), self.query)

    def query(self, ind):
        return Q(data__icontains=ind)

class SqNotData(SqData):
    def __init__(self):
        super(SqData, self).__init__(('!d', '!data'), 
        lambda ind: ~self.query(ind))


class SqTag(SqNode):
    def __init__(self):
        super(SqTag, self).__init__(('t', 'tag'), self.query, chain=True)

    def query(self, ind):
         return Q(tags__name__icontains=ind)

class SqNotTag(SqTag):
    def __init__(self):
        super(SqTag, self).__init__(('!t', '!tag'), 
        lambda ind: ~self.query, chain=True)

class SqFile(SqNode):
    def __init__(self):
        super(SqFile, self).__init__(('f', 'file'), self.query, chain=True)

    def query(self, ind):
        return Q(postfilewrapper__file__icontains=ind)

class SqGroup(SqNode):
    def __init__(self):
        super(SqGroup, self).__init__(('g', 'group'), self.query)

    def query(self, ind):
        return Q(ancestor__name__icontains=ind)

class SqNotGroup(SqGroup):
    def __init__(self):
        super(SqGroup, self).__init__(('!g', '!group'), 
        lambda ind: ~self.query(ind))

class SqComment(SqNode):
    def __init__(self):
        super(SqComment, self).__init__(('s', 'comment'), self.query)

    def query(self, ind):
        q0 = Q(comments__title__icontains=ind) 
        q1 = Q(comments__data__icontains=ind)

class SqNotComment(SqComment):
    def __init__(self):
        super(SqComment, self).__init__(('!s', '!comment'), 
        lambda ind: ~self.query(ind))

class SqCommentOwner(SqNode):
    def __init__(self):
        super(SqCommentOwner, self).__init__(('so', 'comment.owner'), self.query)

    def query(self, ind):
        q0 = Q(comments__owner__name__icontains=ind)
        q1 = Q(comments__owner__email__icontains=ind)
        return q0 | q1

class SqNotCommentOwner(SqCommentOwner):
    def __init__(self):
        super(SqCommentOwner, self).__init__(('!so', '!comment.owner'), 
        lambda ind: ~self.query(ind))

class SqCommentTitle(SqNode):
    def __init__(self):
        super(SqCommentTitle, self).__init__(('st', 'comment.title'), self.query)

    def query(self, ind):
        return Q(comments__title__icontains=ind)

class SqNotCommentTitle(SqCommentTitle):
    def __init__(self):
        super(SqCommentTitle, self).__init__(('!st', '!comment.title'),
        lambda ind: ~self.query(ind))

class SqCommentData(SqNode):
    def __init__(self):
        super(SqCommentData, self).__init__(('sd', 'comment.data'), self.query)

    def query(self, ind):
        return Q(comments__data__icontains=ind)

class SqNotCommentData(SqCommentData):
    def __init__(self):
        super(SqCommentData, self).__init__(('!sd', '!comment.data'), 
        lambda ind: ~self.query(ind))


class SqCommentFile(SqNode):
    def __init__(self):
        super(SqCommentFile, self).__init__(('sf', 'comment.file'), self.query)

    def query(self, ind):
        return Q(comments__commentfilewrapper__file__icontains=ind)

class SqDefault(SqNode):
    def __init__(self):
        super(SqDefault, self).__init__((None, SqDefault), self.query)

    def query(self, ind):
        return Q(label__icontains=ind) | Q(data__icontains=ind)

class SqFork(SqNode):
    def __init__(self):
        super(SqFork, self).__init__(('k', 'fork'), self.query)

    def query(self, ind):
        q0 = Q(card_forks__children__label__icontains=ind)
        q1 = Q(card_forks__children__data__icontains=ind)
        q2 = Q(card_forks__label__icontains=ind)
        q3 = Q(card_forks__data__icontains=ind)
        return q0 | q1 | q2 | q3

class SqNotFork(SqFork):
    def __init__(self):
        super(SqFork, self).__init__(('!k', '!fork'), 
        lambda ind: ~self.query(ind))

class SqForkLabel(SqNode):
    def __init__(self):
        super(SqForkLabel, self).__init__(('kl', 'fork.label'), self.query)

    def query(self, ind):
        q0 = Q(card_forks__children__label__icontains=ind)
        q1 = Q(card_forks__label__icontains=ind)
        return q0 | q1

class SqNotForkLabel(SqForkLabel):
    def __init__(self):
        super(SqForkLabel, self).__init__(('!kl', '!fork.label'), 
        lambda ind: ~self.query(ind))

class SqForkData(SqNode):
    def __init__(self):
        super(SqForkData, self).__init__(('kd', 'fork.data'), self.query)

    def query(self, ind):
        q0 = Q(card_forks__children__data__icontains=ind)
        q1 = Q(card_forks__data__icontains=ind)
        return q0 | q1

class SqNotForkData(SqForkData):
    def __init__(self):
        super(SqForkData, self).__init__(('!kd', '!fork.data'), 
        lambda ind: ~self.query(ind))

class SqForkTag(SqNode):
    def __init__(self):
        super(SqForkTag, self).__init__(('kt', 'fork.tag'), 
        self.query, chain=True)

    def query(self, ind):
        q0 = Q(card_forks__children__tags__name__icontains=ind)
        q1 = Q(card_forks__tags__name__icontains=ind)
        return q0 | q1

class SqNotForkTag(SqForkTag):
    def __init__(self):
        super(SqForkTag, self).__init__(('!kt', '!fork.tag'),
        lambda ind: ~self.query(ind), chain=True)

class SqForkWorker(SqNode):
    def __init__(self):
        super(SqForkWorker, self).__init__(
        ('kw', 'fork.worker'), self.query, chain=True)

    def query(self, ind):
        q0 = Q(card_forks__children__workers__name__icontains=ind)
        q1 = Q(card_forks__workers__name__icontains=ind)
        return q0 | q1

class SqNotForkWorker(SqForkWorker):
    def __init__(self):
        super(SqForkWorker, self).__init__(('!kw', '!fork.worker'), 
        lambda ind: ~self.query(ind))

class SqPost(SqLike):
    def __init__(self):
        super(SqPost, self).__init__(Post, SqDefault(),
        SqOwner(), SqNotOwner(),
        SqFile(), SqLiker(), SqNotLiker(),
        SqCreatedGt(), SqCreatedLt(), SqCreated(),
        SqLabel(), SqNotLabel(), 
        SqData(), SqNotData(), 
        SqTag(), SqNotTag(), 
        SqComment(), SqNotComment(),
        SqCommentOwner(), SqNotCommentOwner(),
        SqCommentTitle(), SqNotCommentTitle(),
        SqCommentData(), SqNotCommentData(),
        SqFork(), SqNotFork(),
        SqForkLabel(), SqNotForkLabel(),
        SqForkData(), SqNotForkData(),
        SqForkTag(), SqNotForkTag(),
        SqForkWorker(), SqNotForkWorker(),
        SqCommentFile(), SqGroup(), SqNotGroup())




