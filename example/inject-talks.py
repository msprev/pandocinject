#!/usr/bin/env python3

import importlib
from pandocfilters import toJSONFilter
from pandocinject import Injector

if __name__ == "__main__":
    s = importlib.import_module('selector')
    f = importlib.import_module('formatter')
    i = Injector('inject-talk', selector_module=s, formatter_module=f)
    toJSONFilter(i.get_filter())
