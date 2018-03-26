from re import split

class SqLike:
    def __init__(self, fields, default):
        self.fields         = fields
        self.default = default

    def build(self, data):
        tokens = split(' *\+ *', data)
        sql    = []
        for ind in tokens:
            sql.append(self.fmt(ind))
        return sql

    def fmt(self, pair):
        pair = pair.split(':', 2)
        q    = self.fields[pair[0]] if len(pair) > 1 \
        else self.default

        return q(pair[-1])

def splittokens(data):
    tokens     = split(' *\+ *', data)
    chks, tags = [], []

    for ind in tokens:
        if ind.startswith('#'):
            tags.append(ind.strip('#'))
        else:
            chks.append(ind)
    return chks, tags


