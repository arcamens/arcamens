from re import split

def search_tokens(data):
    tokens     = split(' *\+ *', data)
    chks, tags = [], []

    for ind in tokens:
        if ind.startswith('#'):
            tags.append(ind.strip('#'))
        else:
            chks.append(ind)
    return chks, tags
