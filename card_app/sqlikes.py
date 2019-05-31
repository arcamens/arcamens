from card_app.models import Card
from sqlike.parser import SqLike, SqNode
from django.db.models import Q, F

class SqDefault(SqNode):
    def __init__(self):
        super(SqDefault, self).__init__(None, self.query)

    def query(self, ind):
        q0 = Q(label__icontains=ind) 
        q1 = Q(data__icontains=ind) 
        return q0 | q1

class SqOwner(SqNode):
    def __init__(self):
        super(SqOwner, self).__init__(('o', 'owner'), self.query)

    def query(self, ind):
        q0 = Q(owner__name__icontains=ind) 
        q1 = Q(owner__email__icontains=ind)
        return q0 | q1

class SqNotOwner(SqOwner):
    def __init__(self):
        super(SqOwner, self).__init__(('!o', '!owner'), 
        lambda ind: ~self.query(ind))

class SqWorker(SqNode):
    def __init__(self):
        super(SqWorker, self).__init__(('w', 'worker'), 
        self.query, chain=True)

    def query(self, ind):
        q0 = Q(workers__name__icontains=ind) 
        q1 = Q(workers__email__icontains=ind)
        return q0 | q1

class SqNotWorker(SqWorker):
    def __init__(self):
        super(SqWorker, self).__init__(('!w', '!worker'), 
        lambda ind: ~self.query(ind), chain=True)

class SqAssigner(SqNode):
    def __init__(self):
        super(SqAssigner, self).__init__(('a', 'assigner'), self.query)
    
    def query(self, ind):        
        q0 = Q(cardtaskship__assigner__name__icontains=ind) 
        q1 = Q(cardtaskship__assigner__email__icontains=ind)
        return q0 | q1

class SqNotAssigner(SqAssigner):
    def __init__(self):
        super(SqAssigner, self).__init__(('!a', '!assigner'),
        lambda ind: ~self.query(ind))

class SqFile(SqNode):
    def __init__(self):
        super(SqFile, self).__init__(('f', 'file'), 
        self.query, chain=True)

    def query(self, ind):
         return Q(cardfilewrapper__file__icontains=ind)

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
        lambda ind: ~self.label(ind))

class SqDeadlineGt(SqNode):
    def __init__(self):
        super(SqDeadlineGt, self).__init__(('dl>', 'deadline>'), self.query)

    def query(self, ind):
        return Q(deadline__gt=ind)

class SqDeadlineLt(SqNode):
    def __init__(self):
        super(SqDeadlineLt, self).__init__(('dl<', 'deadline<'), self.query)

    def query(self, ind):
        return Q(deadline__lt=ind)
    
class SqDeadline(SqNode):
    def __init__(self):
        super(SqDeadlineLt, self).__init__(('dl', 'deadline'), self.query)

    def query(self, ind):
        return Q(deadline__date=ind)

class SqData(SqNode):
    def __init__(self):
        super(SqData, self).__init__(('d', 'data'), self.query)

    def query(self, ind):
        return Q(data__icontains=ind)

class SqNotData(SqData):
    def __init__(self):
        super(SqData, self).__init__(('!d', '!data'), 
        lambda ind: ~self.query(ind))

class SqNote(SqNode):
    def __init__(self):
        super(SqNote, self).__init__(('n', 'note'), 
        self.query, chain=True)

    def query(self, ind):
        return Q(notes__data__icontains=ind)

class SqNotNote(SqNote):
    def __init__(self):
        super(SqNote, self).__init__(('!n', '!note'), 
        lambda ind: ~self.query(ind))
    
class SqTag(SqNode):
    def __init__(self):
        super(SqTag, self).__init__(('t', 'tag'), 
        self.query, chain=True)

    def query(self, ind):
        return Q(tags__name__icontains=ind)

class SqNotTag(SqTag):
    def __init__(self):
        super(SqTag, self).__init__(('!t', '!tag'), 
        lambda ind: ~self.query(ind), chain=True)
    
class SqList(SqNode):
    def __init__(self):
        super(SqList, self).__init__(('i', 'list'), self.query)

    def query(self, ind):
        return Q(ancestor__name__icontains=ind)

class SqNotList(SqList):
    def __init__(self):
        super(SqList, self).__init__(('!i', '!list'), 
        lambda ind: self.query(ind))

class SqBoard(SqNode):
    def __init__(self):
        super(SqBoard, self).__init__(('b', 'board'), self.query)

    def query(self, ind):
        return Q(ancestor__ancestor__name__icontains=ind)

class SqNotBoard(SqBoard):
    def __init__(self):
        super(SqBoard, self).__init__(('!b', '!board'), 
        lambda ind: ~self.query(ind))

class SqNoteOwner(SqNode):
    def __init__(self):
        super(SqNoteOwner, self).__init__(('no', 'note.owner'), self.query)

    def query(self, ind):
        q0 = Q(notes__owner__name__icontains=ind) 
        q1 = Q(notes__owner__email__icontains=ind)

        return q0 | q1

class SqNotNoteOwner(SqNoteOwner):
    def __init__(self):
        super(SqNoteOwner, self).__init__(('!no', '!note.owner'), 
        lambda ind: ~self.query)

class SqNoteFile(SqNode):
    def __init__(self):
        super(SqNoteFile, self).__init__(('nf', 'note.file'), 
        self.query, chain=True)

    def query(self, ind):
        return Q(notes__notefilewrapper__file__icontains=ind)

class SqFork(SqNode):
    def __init__(self):
        super(SqFork, self).__init__(('k', 'fork'), self.query)

    def query(self, ind):
        q0 = Q(children__label__icontains=ind)
        q1 = Q(children__data__icontains=ind)
        return q0 | q1

class SqNotFork(SqFork):
    def __init__(self):
        super(SqFork, self).__init__(('!k', '!fork'), 
        lambda ind: ~self.query(ind))

class SqForkLabel(SqNode):
    def __init__(self):
        super(SqForkLabel, self).__init__(('kl', 'fork.label'), self.query)

    def query(self, ind):
        return Q(children__label__icontains=ind)

class SqNotForkLabel(SqForkLabel):
    def __init__(self):
        super(SqForkLabel, self).__init__(('!kl', '!fork.label'), 
        lambda ind: ~self.query(ind))

class SqForkData(SqNode):
    def __init__(self):
        super(SqForkData, self).__init__(('kd', 'fork.data'), self.query)

    def query(self, ind):
        return Q(children__data__icontains=ind)

class SqNotForkData(SqForkData):
    def __init__(self):
        super(SqForkData, self).__init__(('!kd', '!fork.data'), 
        lambda ind: ~self.query(ind))

class SqForkTag(SqNode):
    def __init__(self):
        super(SqForkTag, self).__init__(('kt', 'fork.tag'), 
        self.query, chain=True)

    def query(self, ind):
        return Q(children__tags__name__icontains=ind)

class SqNotForkTag(SqForkTag):
    def __init__(self):
        super(SqForkTag, self).__init__(('!kt', '!fork.tag'), 
        lambda ind: ~self.query(ind), chain=True)

class SqForkWorker(SqNode):
    def __init__(self):
        super(SqForkWorker, self).__init__(('kw', 'fork.worker'), 
        self.query, chain=True)

    def query(self, ind):
        q0 = Q(children__workers__name__icontains=ind)
        q1 = Q(children__workers__email__icontains=ind)
        return q0 | q1

class SqNotForkWorker(SqForkWorker):
    def __init__(self):
        super(SqForkWorker, self).__init__(('!kw', '!fork.worker'), 
        lambda ind: ~self.query(ind), chain=True)

class SqParent(SqNode):
    def __init__(self):
        super(SqParent, self).__init__(('!p', '!parent'), self.query)

    def query(self, ind):
        q0 = Q(path__label__icontains=ind)
        q1 = Q(path__data__icontains=ind)
        return q0 | q1

class SqParentLabel(SqNode):
    def __init__(self):
        super(SqParentLabel, self).__init__(('pl', 'parent.label'), self.query)

    def query(self, ind):
        return Q(path__label__icontains=ind)

class SqNotParentLabel(SqParentLabel):
    def __init__(self):
        super(SqParentLabel, self).__init__(('!pl', '!parent.label'), 
        lambda ind: ~self.query(ind))

class SqParentData(SqNode):
    def __init__(self):
        super(SqParentData, self).__init__(('pd', 'parent.data'), self.query)

    def query(self, ind):
        return Q(path__data__icontains=ind)

class SqNotParentData(SqParentData):
    def __init__(self):
        super(SqParentData, self).__init__(('!pd', '!parent.data'), 
        lambda ind: ~self.query(ind))

class SqParentTag(SqNode):
    def __init__(self):
        super(SqParentTag, self).__init__(('pt', 'parent.tag'), 
        self.query, chain=True)

    def query(self, ind):
        return Q(path__tags__name__icontains=ind)

class SqNotParentTag(SqParentTag):
    def __init__(self):
        super(SqParentTag, self).__init__(('!pt', '!parent.tag'), 
        lambda ind: ~self.query(ind), chain=True)

class SqParentWorker(SqNode):
    def __init__(self):
        super(SqParentWorker, self).__init__(('pw', 'parent.worker'), 
        self.query, chain=True)

    def query(self, ind):
        q0 = Q(path__workers__name__icontains=ind)
        q1 = Q(path__workers__email__icontains=ind)

        return q0 | q1

class SqNotParentWorker(SqParentWorker):
    def __init__(self):
        super(SqParentWorker, self).__init__(('!pw', '!parent.worker'), 
        lambda ind: ~self.query(ind), chain=True)

class SqCard(SqLike):
    def __init__(self):
        super(SqCard, self).__init__(Card, 
        SqDefault(), SqOwner(), SqNotOwner(),
        SqWorker(), SqNotWorker(),        
        SqAssigner(), SqNotAssigner(),
        SqFile(), SqCreatedGt(), SqCreatedLt(),
        SqCreated(), SqLabel(), SqNotLabel(),
        SqDeadlineGt(), SqDeadlineLt(),
        SqData(), SqNotData(),  
        SqNote(), SqNotNote(),
        SqTag(), SqNotTag(),
        SqList(), SqNotList(),
        SqNoteOwner(), SqNotNoteOwner(),
        SqFork(), SqNotFork(), 
        SqForkLabel(), SqNotForkLabel(),
        SqForkData(), SqNotForkData(),
        SqForkTag(), SqNotForkTag(),
        SqForkWorker(), SqNotForkWorker(),
        SqParent(), SqParentLabel(),
        SqParentData(), SqNotParentData(),
        SqParentTag(), SqNotParentTag(),
        SqParentWorker(), SqNotParentWorker(),
        SqNoteFile(), SqBoard(), SqNotBoard())
        

