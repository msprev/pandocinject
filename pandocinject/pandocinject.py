import importlib
import os
from pandocfilters import *
from pandocinject.reader import read_source
from pandocinject.pandoc import text2json

ENCODING = 'utf-8'
FIELD_SELECTORS = ['uuid', 'slug']

class Injector(object):

    def __init__(self, name, selector_module=None, formatter_module=None):
        self.match_on = name
        self.source_cache = dict()
        if selector_module:
            self.selector_module = selector_module
        else:
            log('WARNING', 'No selector module specified, reverting to default')
            self.selector_module = importlib.import_module('selector')
        if formatter_module:
            self.formatter_module = formatter_module
        else:
            log('WARNING', 'No formatter module specified, reverting to default')
            self.formatter_module = importlib.import_module('formatter')

    def get_filter(self):
        def expand(key, value, format, meta):
            if (key == 'Div' or key == 'Span') and self.match_on in value[0][1]:
                args = get_args(value[0][2])
                entries = load_source(args['source'], self.source_cache)
                starred = get_starred_entries(entries, meta)
                entries = select_entries(entries, self.selector_module, args['selector'])
                (text, text_format) = format_entries(entries, self.formatter_module, args['formatter'], starred)
                ast = text2json(text, text_format, ['--smart'])
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
    args['selector'] = get_vals(raw_args, 'select')
    args['formatter'] = get_vals(raw_args, 'format')
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

def select_entries(entries, selector_module, args):

    def by_field(entries, args):
        out = list()
        for f in FIELD_SELECTORS:
            hitlist = [a.split(f + '=', 1)[1] for a in args if a.startswith(f + '=')]
            selected = [e for e in entries if f in e and e[f] in hitlist]
            out.extend(selected)
        return out

    def by_class(entries, selector_module, args):
        classnames = [a for a in args if not '=' in a]
        if not classnames:
            return []
        classes = list()
        for n in classnames:
            try:
                classes.append(getattr(selector_module, n))
            except AttributeError:
                log('ERROR', 'selector "%s" not found' % n)
                continue
        ss = [c() for c in classes]
        if not ss:
            return []
        for s in ss:
            entries = [e for e in entries if s.select(e) == True]
        return entries

    if not entries:
        return []
    l1 = by_field(entries, args)
    l2 = by_class(entries, selector_module, args)
    return l1 + l2

def format_entries(entries, formatter_module, classnames, starred):
    try:
        f = getattr(formatter_module, classnames[0])()
    except (AttributeError, IndexError):
        log('ERROR', 'formatter "%s" not found' % classnames[0])
        return ('', 'markdown')
    text = f.format_block(list(f.sort_entries(entries)), starred)
    text_format = f.output_format
    return (text, text_format)

def log(level, msg):
    import os
    import sys
    if 'PANZER_SHARED' in os.environ:
        sys.path.append(os.path.join(os.environ['PANZER_SHARED'], 'python'))
        import panzertools
        panzertools.log(level, msg)
    else:
        print(level + ': ' + msg, file=sys.stderr)
