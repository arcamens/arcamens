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
        pair = pair.split(':')
        q = self.fields.get(pair[0], self.default)
        sql = q(pair[-1])
        return sql

def splittokens(data):
    tokens     = split(' *\+ *', data)
    chks, tags = [], []

    for ind in tokens:
        if ind.startswith('#'):
            tags.append(ind.strip('#'))
        else:
            chks.append(ind)
    return chks, tags


