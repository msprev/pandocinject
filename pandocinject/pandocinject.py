import importlib
import os
import re
import string
from pandocfilters import *
from pandocinject.reader import read_source
from pandocinject.pandoc import text2json
from pandocinject.simplebool import BooleanEvaluator

ENCODING = 'utf-8'

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
                ast = text2json(text, text_format, ['--smart'])[1]
                # if inline element:
                if key == 'Span' and len(ast) > 0:
                    # inject contents of first block element
                    return ast[0]['c']
                return ast
        return expand


def get_args(raw_args):
    def get_arg(raw_args, name):
        for a in raw_args:
            if a[0] == name:
                return a[1]
        return str()
    args = dict()
    args['source'] = get_arg(raw_args, 'source')
    args['selector'] = get_arg(raw_args, 'select')
    args['formatter'] = get_arg(raw_args, 'format')
    return args

def load_source(arg_val, cache):
    entries = list()
    filenames = arg_val.split()
    for fname in filenames:
        if fname in cache:
            incoming = cache[fname]
        else:
            ftype = os.path.splitext(fname)[1].lower()
            incoming = read_source(ftype, fname)
            cache[fname] = incoming
        entries.extend(incoming)
    log('INFO', '%d entries loaded' % len(entries))
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

def select_entries(entries, selector_module, arg_val):
    if not arg_val:
        return entries
    # 1. split into list of non-logical words
    word_str = arg_val
    REMOVE = [r'\band\b', r'\bAND\b', r'\bor\b', r'\bOR\b', r'\bnot\b', r'\bNOT\b', r'\(', r'\)']
    for pat in REMOVE:
        word_str = re.sub(pat, ' ', word_str)
    words = word_str.split()
    # 2. get a list of letters
    letters = list(string.ascii_lowercase + string.ascii_uppercase)
    if len(words) > len(letters):
        log('ERROR', 'Exceeded number of selectors supported in boolean expression')
        return []
    # 3. assign a letter to each word
    translation_table = dict()
    translated = arg_val
    for i, w in enumerate(words):
        translation_table[w] = letters[i]
        translated = re.sub(r'\b' + w + r'\b', translation_table[w], translated)
    # 4. assign a function to each letter
    function_table = dict()
    for w in words:
        # - function: select by uuid or slug
        if w.split('=', 1)[0] in ['uuid', 'slug']:
            key = w.split('=', 1)[0]
            val = w.split('=', 1)[1]
            function_table[translation_table[w]] = \
                lambda e: True if key in e and e[key] == val else False
            continue
        # - function: select by named class selector
        try:
            s = getattr(selector_module, w)()
        except (AttributeError, IndexError):
            log('ERROR', 'selector "%s" not found' % w)
            return []
        function_table[translation_table[w]] = s.select
    # 5. create an evaluator
    b = BooleanEvaluator(translated, function_table)
    out = [e for e in entries if b.evaluate(e)]
    return out

def format_entries(entries, formatter_module, arg_val, starred):
    log('INFO', '- %d entries sent to formatter' % len(entries))
    try:
        f = getattr(formatter_module, arg_val)()
    except (AttributeError, IndexError):
        log('ERROR', 'formatter "%s" not found' % arg_val)
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
