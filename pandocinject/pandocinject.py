import importlib
import os
from pandocfilters import *
from pandocinject.reader import read_source
from pandocinject.pandoc import markdown2json

ENCODING = 'utf-8'
FIELD_SELECTORS = ['uuid', 'slug']

class Injector(object):

    def __init__(self, k, formatter=None, selector=None):
        self.kind = k
        self.source_cache = dict()
        if formatter:
            self.formatter = formatter
        else:
            log('WARNING', 'No formatter specified, reverting to default')
            self.formatter = importlib.import_module('formatter')
        if selector:
            self.selector = selector
        else:
            log('WARNING', 'No selector specified, reverting to default')
            self.selector = importlib.import_module('selector')

    def get_filter(self):
        def expand(key, value, format, meta):
            if (key == 'Div' or key == 'Span') and "FILTER-inject" in value[0][1]:
                args = get_args(value[0][2])
                # if args['kind'] != self.kind:
                #     return
                entries = load_source(args['source'], self.source_cache)
                starred = get_starred_entries(entries, meta)
                entries = select_entries(entries, self.selector, args['selector'])
                text = format_entries(entries, self.formatter, args['formatter'], starred)
                ast = markdown2json(text, ['--smart'])
                # if inline element:
                if key == 'Span' and len(ast) > 0:
                    # inject contents of first block element
                    return ast[0]['c']
                return ast
        return expand


def get_args(raw_args):
    def get_vals(raw_args, name):
        for a in raw_args:
            if a[0] == name:
                return a[1].split()
        return []
    args = dict()
    args['source'] = get_vals(raw_args, 'source')
    args['kind'] = get_vals(raw_args, 'kind')
    args['selector'] = get_vals(raw_args, 'select')
    args['formatter'] = get_vals(raw_args, 'format')
    if not args['kind']:
        log('WARNING', 'no "kind" specified, reverting to default')
        args['kind'] = ['default']
    if len(args['kind']) > 1:
        log('WARNING', 'only one kind allowed -- ignoring all except first')
    if len(args['formatter']) > 1:
        log('WARNING', 'only one formmatter allowed -- ignoring all except first')
    return args

def load_source(filenames, cache):
    entries = list()
    for fname in filenames:
        if fname in cache:
            incoming = cache[fname]
        else:
            ftype = os.path.splitext(fname)[1]
            incoming = read_source(ftype, fname)
            cache[fname] = incoming
        entries.extend(incoming)
    return entries

def get_starred_entries(entries, meta):
    if not entries:
        return []
    if 'star' not in meta or meta['star']['t'] != 'MetaList':
        return []
    starred = list()
    s_ids = [stringify(s) for s in meta['star']['c']]
    for e in entries:
        if ('uuid' in e and e['uuid'] in s_ids) \
        or ('slug' in e and e['slug'] in s_ids):
            starred.append(e)
    return starred

def select_entries(entries, selector, args):

    def by_field(entries, args):
        out = list()
        for f in FIELD_SELECTORS:
            hitlist = [a.split(f + '=', 1)[1] for a in args if a.startswith(f + '=')]
            selected = [e for e in entries if f in e and e[f] in hitlist]
            out.extend(selected)
        return out

    def by_class(entries, selector, args):
        out = list()
        classnames = [a for a in args if not '=' in a]
        classes = list()
        for n in classnames:
            try:
                classes.append(getattr(selector, n))
            except AttributeError:
                log('ERROR', 'selector "%s" not found' % n)
                continue
        ss = [c() for c in classes]
        for s in ss:
            entries = [e for e in entries if s.select(e) == True]
        return entries

    if not entries:
        return []
    l1 = by_field(entries, args)
    l2 = by_class(entries, selector, args)
    return l1 + l2

def format_entries(entries, formatter, classnames, starred):
    try:
        f = getattr(formatter, classnames[0])()
    except (AttributeError, IndexError):
        log('ERROR', 'formatter "%s" not found' % classnames[0])
        return []
    return f.format(list(f.sort_entries(entries)), starred)

def log(level, msg):
    import os
    import sys
    if 'PANZER_SHARED' in os.environ:
        sys.path.append(os.path.join(os.environ['PANZER_SHARED'], 'python'))
        import panzertools
        panzertools.log(level, msg)
    else:
        print(level + ': ' + msg, file=sys.stderr)
