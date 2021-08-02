
def tags_to_dict(tags):
    tag_dict = {}
    for tag in tags.values():
        tag_dict[tag.name] = tag.value
    return tag_dict


def print_dict(d, compact=False, indent=0):
    s = ''
    for key, value in d.items():
        if not isinstance(value, list):
            if not compact: s += '\t' * indent
            s += str(key)
            s += ':' if compact else '\n'
        if isinstance(value, dict):
            s += print_dict(value, indent=indent + 1)
        elif isinstance(value, list):
            for v in value:
                s += print_dict(v)
        else:
            if not compact: s += '\t' * (indent + 1)
            s += str(value)
        s += ' ' if compact else '\n'
    return s


def print_hbytes(bytes):
    exps = ['', 'K', 'M', 'G', 'T']
    div = 1024
    exp = 0

    while bytes > div:
        bytes /= div
        exp +=1
    return f'{bytes:.1f}{exps[exp]}B'

