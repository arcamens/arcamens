from re import split

from django.db.models import Q
from functools import reduce
from operator import and_, or_
from re import split

class SqNode:
    def __init__(self, tokens, rule, op=and_, chain=False):
        self.rule = rule
        self.tokens = tokens
        self.op = op
        self.seq = [Q()]
        self.chain = chain

    def add(self, value):
        self.seq.append(self.rule(value))

    def run(self, queryset):
        if not self.chain:
            return queryset.filter(reduce(self.op, self.seq))

        for ind in self.seq:
            queryset = queryset.filter(ind)
        return queryset

class SqLike:
    def __init__(self, node, *args, op=and_):
        self.args    = args
        self.node    = node
        self.op      = op
        self.sql     = {}

        for indi in args:
            for indj in indi.tokens:
                self.sql[indj] = indi

    def feed(self, data):
        pairs = split(' *\+ *', data)
        pairs = map(lambda ind: ind.split(':', 2), pairs)

        for ind in pairs:
            self.build(ind)

    def build(self, pair):
        pair[0]  = pair[0].strip().rstrip()
        pair[-1] = pair[-1].strip().rstrip()

        if len(pair) > 1:
            self.sql[pair[0]].add(pair[1])
        else:
            self.node.add(pair[0])

    def run(self, queryset):
        for ind in self.args:
            queryset = ind.run(queryset)
        return self.node.run(queryset)

