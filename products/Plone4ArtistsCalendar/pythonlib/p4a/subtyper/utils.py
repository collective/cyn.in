
def dotted_name(obj):
    return obj.__module__ + '.' + obj.__name__

def name_to_class(name):
    pieces = name.split('.')
    ifacename = pieces[-1]
    pm = '.'.join(pieces[:-1])

    m = __import__(pm, globals(), locals(), pm)
    return getattr(m, ifacename)

