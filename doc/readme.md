---
title: "pandocinject"
author:
    - name: Mark Sprevak
date: 27 January 2016
style: Notes
...

# pandocinject

Imagine you have a list of items in a structured data file (yaml, json, bibtex, etc.).
    You want to select some of the items, format them nicely, and inject the result into a markdown/html/docx/etc document.
    For example, you might have a file that includes a list of your talks, and you want to select some of the items, sort them, and format them neatly for a CV on your website.

Wouldn't it be nice to do this without learning a funky template/style/query language?
    Wouldn't it be nice to say the output you want directly in markdown/html/org/etc.?
    And wouldn't it be nice to use a simple language like Python to do the selecting and formatting logic?

pandocinject does this.
    Or rather, pandocinject creates pandoc filters do to this.
    Creating these filters is trivial.
    Some worked examples are given below.

pandocinject is 100% Python.
    Using pandocinject only requires a basic knowledge of Python.
    There are no funky template/style/query languages (SQL, csl, biblatex, etc.) to learn.


# Installation

```
pip3 install git+https://github.com/msprev/pandocinject
```

*Requirements:*

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

Suppose you have your talks in a yaml file, `talks.yaml`:

``` yaml
- title: "A walk in the park"
  year: 2015
  venue: Central park

- title: "Another walk"
  year: 2016
  venue: London Park
```

You want to select the talks from 2015, and format them nicely.

Let's write a filter that uses pandocinject to do it.
Easy peasy.

## Step 1: Write the selector logic

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

## Step 2: Write the formatter logic

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

## Step 3: Put them together to create a filter

Put this into a file `inject-talks.py`, in the same directory as the others:

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

## The result

Add this `div` to your markdown document where you want your talks to appear:

``` html
The talks I have this week include:

<div class="inject-talk" source="talks.yaml" select="LastYear" format="Homepage"></div>
```

Now call pandoc with the filter:

```
pandoc test.md -t markdown --filter=./inject-talks.py
```

Here is the markdown output:

```
The talks I have this week include:

1. "A walk in the park", 3 January 2015 in Central Park

2. "A walk in the park", 3 January 2015 in Central Park
```

What about html? No problem:

```
pandoc test.md -t html --filter=./inject-talks.py
```

Here is the html output:

```
The talks I have this week include:

1. "A walk in the park", 3 January 2015 in Central Park

2. "A walk in the park", 3 January 2015 in Central Park
```

# Other examples

You can see more worked examples of formatters and selectors here:

- inject-student
- inject-talk
- inject-publication

# Documentation

## Input document

You inject into pandoc's input file by using a `div` or `span` with the class name of your filter in that file.

``` html
<div class="inject-talk" source="talks.yaml" select="LastYear" format="Homepage"></div>
<span class="inject-publication-info" source="publications.yaml" select="uuid=6342F747-4294-4036-BE77-10364924164D" format="Abstract"></div>
```

- `div` tags are for injecting blocks
- `span` tags are for injecting inline elements

Your formatter will likely behave differently depending on whether it is intended to be used for injecting block or inline elements.
Note that the default formatter (in base class `Formatter`) creates block elements (loose numbered lists).

The tag has three attributes that control what gets injected: `source`, `select`, `format`:

1. `source`: source file(s) to read data from (yaml/bibtex/etc.)
2. `select`: Python classes that select items from the data
3. `format`: Python class that formats the data into a string


### `source`

The `source` attribute takes a list of space-separated file names or paths.
Files at the start are read before files at the end.
The file type is inferred from the file name's extension.

File types currently supported include:

* yaml (`'.yaml'`)
* json (`'.json'`)
* bibtex (`'.bib'`)

### `select`

The `select` attribute takes a list of space-separated of selectors.
Selectors can be of two types.

1. Select by class
2. Select by uuid or slug

#### Select by class

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


#### Select by uuid or slug


``` html
<div class="inject-talk" source="talks.yaml" select="uuid=6342F747-4294-4036-BE77-10364924164D" format="Homepage"></div>
<div class="inject-talk" source="talks.yaml" select="slug=my-great-talk" format="Homepage"></div>
```

Sometimes you want to pick out some arbitrary items for which there is no obvious pattern.
You can specify these items by two special attributes: uuid or slug.

Class selectors and uuid/slug selectors can be freely mixed.
If an item has been selected by its uuid/slug, it will be included before whether it has been selected by the class selectors.

### `format`

## Input document metadata

### `star`

Sometimes you may want to mark out certain entries as special in the document.
    For example, you may wish to star certain entries if they appear in the document.

If the input document contains a metadata variable `star`, this variable is read as a list of uuids or slugs.
    Any items with those identifiers will be starred if injected.

``` yaml
star:
    - "6342F747-4294-4036-BE77-10364924164D"
    - "my-new-york-talk"
```

What being starred means, is determined by the formatter used for injection.
The default formatter prepends an asterisk ('`* `') to the item.


## Python selector/formatter

You write a selector or formatter by subclassing `Selector` or `Formatter` as imported from module `pandocinject`.

The base classes are very simple:

* `Formatter`:
* `Selector`:

Each class has a small number of methods some of which you may wish to override when writing a formatter or selector.

## `Selector`

* `select(self, entry)`: returns `True` if `entry` is to be selected for injection into document, `False` otherwise

    - Base class behaviour: select every entry.

## `Formatter`

* `output_format`: String specifying the format of the strings that this formatter object returns. Values could be any of pandoc's output formats (`'-o'`) (e.g. `'html'`, `'org'`).
    - Default: `'markdown'`

* `format_block(self, entries, starred)`: returns a String for the entire injected block

    - `entries`: List of entries to be formatted, already been passed through `sort_entries`
    - `starred`: List of entries to be starred
    - Default: Return a loose numbered list of entries each formatted by `add_entry`; star items by inserting a preceding asterisk

* `format_entry(self, entry)`: returns the markdown String for the formatted item `entry`

    - `entry`: Dictionary with key--values for the entry
    - Default: Return Python's String representation of `entry`

* `sort_entries(self, entries)`: returns List of entries in order they should appear, first to last

    - `entries`: List of entries in the order read from source
    - Default: Do nothing to the order of entries

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

