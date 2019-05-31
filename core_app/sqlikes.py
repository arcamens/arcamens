from sqlike.parser import SqLike, SqNode
from django.db.models import Q
from core_app.models import User, Tag

class SqTagDefault(SqNode):
    def __init__(self):
        super(SqTagDefault, self).__init__(None, self.query)

    def query(self, ind):
        return Q(name__icontains=ind) | Q(description__icontains=ind)

class SqEmail(SqNode):
    def __init__(self):
        super(SqEmail, self).__init__(('m', 'email'), self.query)

    def query(self, ind):
        return Q(email__icontains=ind)

class SqName(SqNode):
    def __init__(self):
        super(SqName, self).__init__(('n', 'name'), self.query)

    def query(self, ind):
        return Q(name__icontains=ind)

class SqDesc(SqNode):
    def __init__(self):
        super(SqDesc, self).__init__(('d', 'desc'), self.query)

    def query(self, ind):
        return Q(description__icontains=ind)

class SqnTag(SqNode):
    def __init__(self):
        super(SqnTag, self).__init__(('t', 'tag'), self.query, chain=True)

    def query(self, ind):
        return Q(tags__name__icontains=ind)

class SqUserDefault(SqNode):
    def __init__(self):
        super(SqUserDefault, self).__init__(None, self.query)

    def query(self, ind):
        return Q(email__icontains=ind) | Q(name__icontains=ind)

class SqUser(SqLike):
    def __init__(self):
        super(SqUser, self).__init__(User, SqUserDefault(),
        SqEmail(), SqName(), SqDesc(), SqnTag(), )

class SqTag(SqLike):
    def __init__(self):
        super(SqTag, self).__init__(Tag, SqTagDefault())



