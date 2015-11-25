---
title: "pandocinject"
author:
    - name: Mark Sprevak
date: 25 November 2015
style: Notes
...

# pandocinject

Suppose that you have a list of items in a data file (yaml, json, bibtex, etc.). Suppose you would like to select some of those items, format them nicely, and inject them into a markdown document. You might have a file that includes a list of your talks, for example, and you want to select items from this list and format them for your CV or homepage.

Wouldn't it be nice to automate this? Wouldn't it be nice to describe the format directly in markdown? Wouldn't it be nice to do this without learning a funky selection/templating language (csl, SQL, bibtex)?

pandocinject enables you to do this. More accurately, pandocinject creates pandoc filters that do it. pandocinject is 100% Python. It allows you to select and format with Python functions.


# Installation

```
pip3 install git+https://github.com/msprev/pandocinject
```

*Requirements:*

* [pandoc][]
* [Python 3][]
* [pip][] (included in most Python 3 distributions)

*To upgrade existing installation:*

```
pip3 install --upgrade git+https://github.com/msprev/pandocinject
```

 [pandoc]: http://johnmacfarlane.net/pandoc/index.html
 [panzer]: https://github.com/msprev
 [pip]: https://pip.pypa.io/en/stable/index.html
 [python 3]: https://www.python.org/downloads/


# Worked example

Suppose you have a yaml file, `talks.yaml`, listing your talks:

``` yaml
- title: A walk in the park
  date:
    - year: 2015
    - month: January
    - day: 3
  venue: Central park
```

You want to select the talks from 2015, and format them nicely.

Let's write a little filter that uses pandocinject to do it.
Easy peasy.

## Step 1: Selector

First, write a function to select items from the last year.
Put this into a file `selector.py`.

``` python
from pandocinject import Selector

class LastYear(Selector):
    def select(self, entry):
        if entry['date']['year'] == 2015:
            return True
        return False
```

## Step 2: Formatter

Now, write a function to format this we way we want.
Put this into a file `formatter.py`:

``` python
from pandocinject import Formatter

class Homepage(Formatter):
    def add_entry(self, entry):
        return '"%s" was given by me on %d %s %d in %s' %
        (entry['title'],
         entry['date']['day'], entry['date']['month'], entry['date']['year'],
         entry['venue'])
```

## Step 3: The filter

Now, let's glue it together into a filter.
Put this into a file `inject-talks.py`:

``` python
#!/usr/bin/env python3

import pandocfilters
import importlib
from pandocinject import Injector

if __name__ == "__main__":
    s = importlib.import_module('selector')
    f = importlib.import_module('formatter')
    i = Injector('inject-talk', selector=s, formatter=f)
    pandocfilters.toJSONFilter(i.get_filter())
```

Remember to make your filter executable:

```
chmod +x inject-talks.py
```


## Step 4: Use the filter

Add the following `div` block to your markdown document where you want your talks to appear:

``` html
<div class="inject-talk" source="talks.yaml" select="LastYear" format="Homepage"></div>
```

Now call pandoc on your file with the filter:

```
pandoc test.md -t markdown --filter=./inject-talks.py
```

## The result

Here is the markdown output:

```
1. "A walk in the park", 3 January 2015 in Central Park

2. "A walk in the park", 3 January 2015 in Central Park
```

We had a simple formatter and selector.
But these components can be as complex, and utilise whatever features of Python, than you like.

You can see more complex versions that I use here:

- inject-student
- inject-talk
- inject-publication

# Injection syntax

You inject into markdown with a `div` or `span` with the class name of your filter.

``` html
<div class="inject-talk" source="talks.yaml" select="LastYear" format="Homepage"></div>
```

The element have three attributes: `source`, `select`, `format`:

1. `source`: source file(s) to read data from
2. `select`: function(s) that select items from your data
3. `format`: function that formats the data into pretty markdown

`div` elements inject block elements into markdown.
`span` element inject inline elements.
You should write your formatter appropriately to whether it is going to be used for injecting block or inline elements.
Note the default formatter (in the `Formatter` base class) creates block elements (loose numbered lists).

## `source`

The `source` attribute takes a list of space-separated file names or paths.
Files at the start are read before files at the end.
The type of the file is detected from the file name's extension.

Source file types that are currently supported include:

* yaml ('.yaml')
* json ('.json')
* bibtex ('.bib')

## `select`

The `select` attribute takes a list of space-separated of selectors.
Selectors can be of two types.

1. Select by class
2. Select by uuid or slug

### Select by class

``` html
<div class="inject-talk" source="talks.yaml" select="LastYear" format="Homepage"></div>
```

This selects the items using the class `LastYear`.
This class contains a method -- `select` -- that is run on each entry and decides yes or no, whether the entry should be included in the injected list.

Multiple classes may be listed in the `select` attribute.
An item is selected for inclusion only if selected by *all* of the classes.

``` html
<div class="inject-talk" source="talks.yaml" select="LastYear UK" format="Homepage"></div>
```

Here, an item is selected for inclusion only if both `LastYear` and `UK` classes select it.


### Select by uuid or slug


``` html
<div class="inject-talk" source="talks.yaml" select="uuid=6342F747-4294-4036-BE77-10364924164D" format="Homepage"></div>
<div class="inject-talk" source="talks.yaml" select="slug=my-great-talk" format="Homepage"></div>
```

Sometimes you want to pick out some arbitrary items for which there is no obvious pattern.
You can specify these items by two special attributes: uuid or slug.

Class selectors and uuid/slug selectors can be freely mixed.
If an item has been selected by its uuid/slug, it will be included before whether it has been selected by the class selectors.

## `format`

## `star`

# Selector and Formatter

You write a selector or formatter by subclassing `Selector` or `Formatter` in `pandocinject`.

You can take a look at the (very simple) base classes here:

* `Formatter`:
* `Selector`:

Each class has a small number of methods some of which you may wish to override when writing a formatter or selector.

## `Selector`

* `select(self, entry)`: returns `True` if `entry` is to be selected for injection into document, `False` otherwise

    - Base class behaviour: select every entry.

## `Formatter`

* `format_block(self, entries, starred)`: returns a markdown String for the entire injected block

    - `entries`: List of entries to be formatted, already been passed through `sort_entries`
    - `starred`: List of entries to be starred
    - Base class behaviour: Return a loose numbered list of entries each formatted by `add_entry`; star items by inserting a preceding asterisk

* `add_entry(self, entry)`: returns the markdown String for the formatted item `entry`

    - `entry`: Dictionary with key--values for the entry
    - Base class behaviour: Return Python's String representation of `entry`

* `sort_entries(self, entries)`: returns List of entries in order they should appear, first to last

    - `entries`: List of entries in the order read from source
    - Base class behaviour: Do nothing to the order of entries

# Similar

- gitit
    - The main advantage is that pandocinject allows you do everything with just pandoc + filters.
    You also don't need to learn any weird selection/formatting syntax. Just use Python to express
    what you want done.

- pandoc-citeproc
    -   very sophisticated, but requires you to know csl.

# Release notes

-   0.1 (24 November 2015):
    -   initial release

