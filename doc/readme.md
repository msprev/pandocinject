# pandocinject

Suppose that you have items stored in a data file (yaml, json, bibtex, etc.). Suppose you would like to choose some of those items, format them nicely, and inject them into a markdown document. Suppose you want to choose which particular items you want, and which particular pretty formatting, from inside your markdown document. You might have a file that includes a list of your talks, for example, and you want to select items from this list and format them for your CV or homepage.

Wouldn't it be nice to automate this? Wouldn't it be nice to describe the format you want in markdown rather than some weird formatting language? Wouldn't it be nice to do all this without learning a weird selection/formatting language (csl, SQL, bibtex)?

pandocinject enables you to do this. More accurately, pandocinject is a cookie cutter that creates pandoc filters that do this. It is 100% based on Python.

# Example

Suppose you have a yaml file, `talks.yaml`, listing your talks:

``` yaml

```

You want to select the talks from last year, and format them like this:

Add the following `div` block to your markdown document where you want your talks to appear:

``` html
<div class="inject-talk" source="talks.yaml" select="LastYear" format="Homepage"></div>
```


`inject-talks.py`:


``` python
#!/usr/bin/env python3

from pandocfilters import toJSONFilter
from importlib import import_module
from pandocinject import Injector

if __name__ == "__main__":
    s = import_module('selector')
    f = import_module('formatter')
    i = Injector('inject-talk', selector=s, formatter=f)
    toJSONFilter(i.get_filter())
```


# Installation

# source

Source files that are currently supported:

* yaml
* json
* bibtex

# select

## Select by uuid or slug

## Select by class

# format

# star

# Selector class

``` python
class Selector(object):

    def select(self, e):
        return True
```

# Formatter class

``` python
class Formatter(object):

    def format(self, entries, starred):
        """
        format a list of entries
        """
        # 1. start with blank string
        out = str()
        # 2. add each entry
        for e in entries:
            # each as loose numbered item
            out += '1.  '
            # star start of item
            if e in starred:
                out += '\* '
            out += self.add_entry(e)
            # double cr to make a loose list
            out += '\n\n'
        # 3. don't append anything
        return out

    def add_entry(self, e):
        """
        format a single entry
        """
        # return a string representation of entry
        return str(e)

    def sort_entries(self, entries):
        """
        sort a list of entries
        """
        # don't do anything
        return entries
```

# Similar projects

- gitit
    - The main advantage is that pandocinject allows you do everything with just pandoc + filters.
    You also don't need to learn any weird selection/formatting syntax. Just use Python to express
    what you want done.

- pandoc-citeproc
    -   very sophisticated, but requires you to know csl.
