from re import split

def splittokens(data):
    tokens     = split(' *\+ *', data)
    chks, tags = [], []

    for ind in tokens:
        if ind.startswith('#'):
            tags.append(ind.strip('#'))
        else:
            chks.append(ind)
    return chks, tags

