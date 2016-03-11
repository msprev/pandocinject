============
pandocinject
============

:Author: true
:Date:   11 March 2016

pandocinject
============

Imagine you have a list of items in a structured data file (yaml, json,
bibtex, etc.). You want to select some of the items, format them nicely,
and inject the result into a markdown/html/docx/etc document. For
example, you might have a file that includes a list of your talks, and
you want to select some of the items, sort them, and format them neatly
for your website.

Wouldn’t it be nice to do this without learning a funky
template/style/query language? Wouldn’t it be nice to say the output you
want directly in your favourite format (markdown/html/org/etc.)? And
wouldn’t it be nice to use a simple language like Python to do the logic
of selecting and formatting?

pandocinject does all this. Or rather, pandocinject creates pandoc
filters do to this. Creating these filters is trivial. A worked example
is given below.

pandocinject is 100% Python. Using it only requires a basic knowledge of
Python. There are no funky template/style/query languages (SQL, csl,
biblatex, etc.) to learn.

Installation
============

::

    pip3 install git+https://github.com/msprev/pandocinject

*Requirements:*

-  `Python 3 <https://www.python.org/downloads/>`__
-  `pip <https://pip.pypa.io/en/stable/index.html>`__ (included in most
   Python 3 distributions)

*To upgrade existing installation:*

::

    pip3 install --upgrade git+https://github.com/msprev/pandocinject

Worked example
==============

Suppose you have your talks in a yaml file, ``talks.yaml``:

.. code:: yaml

    - title: "My first walk"
      year: 2012
      venue: Edinburgh meadows

    - title: "A walk in the park"
      year: 2013
      venue: London Park

    - title: "Another walk"
      year: 2014
      venue: Central park

    - title: "Walking again"
      year: 2015
      venue: London Park

You want to select the talks after 2012, and format them nicely.

Easy. Let’s write a filter.

Step 1: Write the selector logic
--------------------------------

First, write a function to select items after 2012. Put this into a file
``selector.py``.

.. code:: python

    from pandocinject import Selector

    class Since2012(Selector):
        def select(self, entry):
            return True if entry['year'] > 2012 else False

Step 2: Write the formatter logic
---------------------------------

Now, write a function to format this we way we want. Put this into a
file ``formatter.py``:

.. code:: python

    from pandocinject import Formatter

    class Homepage(Formatter):
        def format_entry(self, entry):
            text = '*' + entry['title'] + '*, '
            text += entry['venue'] + ', '
            text += str(entry['year'])
            return text

Step 3: Put them together to create a filter
--------------------------------------------

Put this into a file ``inject-talks.py``, in the same directory as the
others:

.. code:: python

    #!/usr/bin/env python3

    import importlib
    from pandocfilters import toJSONFilter
    from pandocinject import Injector

    if __name__ == "__main__":
        s = importlib.import_module('selector')
        f = importlib.import_module('formatter')
        i = Injector('inject-talk', selector_module=s, formatter_module=f)
        toJSONFilter(i.get_filter())

Remember to make your filter executable:

::

    chmod +x inject-talks.py

The result
----------

Add this ``div`` to your markdown document where you want your talks to
appear:

.. code:: html

    The talks I have given since 2012 include:

    <div class="inject-talk" source="talks.yaml" select="Since2012" format="Homepage"></div>

Now call pandoc with the filter:

::

    pandoc test.md -t markdown --filter=./inject-talks.py

Here is the markdown output:

.. code:: markdown

    The talks I have given since 2012 include:

    1.  *A walk in the park*, London Park, 2013

    2.  *Another walk*, Central park, 2014

    3.  *Walking again*, London Park, 2015

What about html output for a webpage? No problem:

::

    pandoc test.md -t html --filter=./inject-talks.py

Here is the html output:

.. code:: html

    <p>The talks I have given since 2012 include:</p>
    <ol style="list-style-type: decimal">
    <li><p><em>A walk in the park</em>, London Park, 2013</p></li>
    <li><p><em>Another walk</em>, Central park, 2014</p></li>
    <li><p><em>Walking again</em>, London Park, 2015</p></li>
    </ol>

.. raw:: html

   <!-- ## Other examples -->

.. raw:: html

   <!-- You can see more worked examples of formatters and selectors here: -->

.. raw:: html

   <!-- - inject-student -->

.. raw:: html

   <!-- - inject-talk -->

.. raw:: html

   <!-- - inject-publication -->

Documentation
=============

Input document
--------------

You inject into pandoc’s input file by using a ``div`` or ``span`` with
the class name of your filter in that file.

.. code:: html

    <div class="inject-talk" source="talks.yaml" select="LastYear" format="Homepage"></div>
    <span class="inject-ref" source="pubs.yaml" select="SingleAuthor" format="Keywords"></div>

-  ``div`` tags are for injecting data formatted as a block
-  ``span`` tags are for injecting data formatted as an inline element

Your formatter will likely behave differently depending on whether it is
intended to be used for injecting block or inline elements. Note that
the default formatter (in base class ``Formatter``) injects block
elements (loose numbered lists).

The ``div`` or ``span`` tag has three attributes that control what gets
injected: ``source``, ``select``, ``format``:

1. ``source``: source file(s) from which to read data
2. ``select``: boolean string of Python classes to select items from the
   data
3. ``format``: Python class to format those items into a string

``source``
~~~~~~~~~~

The ``source`` attribute takes a list of space-separated file names or
paths. Files at the start are read before files at the end. The file
type is inferred from the file name’s extension.

File types currently supported:

-  yaml (``'.yaml'``)
-  json (``'.json'``)
-  bibtex (``'.bib'``)

``select``
~~~~~~~~~~

The ``select`` attribute takes a boolean expression involving names of
Python classes – ‘selector’ classes. You can create these classes by
subclassing ``Selector`` from module ``pandocinject`` and changing the
result to suit your needs.

``select`` may consist of the name of a single selector class or a
boolean expression that involves the names of multiple classes. A
space-separated list is equivalent to a boolean expression where each
item is joined with ``AND``.

.. code:: html

    <div class="inject-talk" source="talks.yaml" select="JointAuthor" format="Homepage"></div>
    <div class="inject-talk" source="talks.yaml" select="Paper LastYear" format="Homepage"></div>
    <div class="inject-talk" source="talks.yaml" select="(LastYear OR Forthcoming) AND Paper AND NOT JointAuthor" format="Homepage"></div>

Valid boolean operators include:

-  ``AND``, ``and``
-  ``OR``, ``or``
-  ``NOT``, ``not``

Brackets can be used to group expressions.

Sometimes you want to select a particular item. You do not need to write
a custom selector class to do this. panzerinject will create a selector
for a single item on the fly based on two identifying attributes:
``uuid`` and ``slug``.

.. code:: html

    <div class="inject-talk" source="talks.yaml" select="uuid=6342F747-4294-4036-BE77-10364924164D" format="Homepage"></div>
    <div class="inject-talk" source="talks.yaml" select="slug=my-great-talk" format="Homepage"></div>

In order for this to work, your item must have an ``uuid`` or ``slug``
attribute.

uuid/slug selectors can be freely mixed with other selectors in boolean
expressions.

``format``
~~~~~~~~~~

The ``format`` attribute takes the name of a Python class – the
‘formatter’ class. You can create a formatter class by subclassing
``Formatter`` from module ``pandocinject`` and tweaking the result to
suit your needs.

.. code:: html

    <div class="inject-talk" source="talks.yaml" select="JointAuthor" format="Homepage"></div>
    <div class="inject-talk" source="talks.yaml" select="JointAuthor" format="CV"></div>
    <span class="inject-talk" source="talks.yaml" select="JointAuthor" format="Abstract"></div>

Input document metadata
-----------------------

``star``
~~~~~~~~

Sometimes you may want to mark out certain entries as special. For
example, you may wish to star certain entries when they appear in the
document.

If the input document contains a metadata variable ``star``, which
contains a list of uuids or slugs, any items with those identifiers will
be starred if injected.

.. code:: yaml

    star:
        - "6342F747-4294-4036-BE77-10364924164D"
        - "my-new-york-talk"

What ‘being starred’ means is determined by the formatter class. The
default formatter prepends an asterisk (‘``*``’) to a starred item.

Python classes
--------------

``Injector``
------------

Objects from this class create pandoc filters. You need to instantiate
one of these to create a pandoc filter.

-  ``Injector(name, selector_module, formatter_module)``:

   -  Returns:

      -  An Injector object

   -  Arguments:

      -  ``name``: name of ``class`` of ``<div>`` or ``<span>`` tags
         where injector will insert text
      -  ``selector_module``: module with the selector classes for the
         injector
      -  ``formatter_module``: module with formatter classes for the
         injector

   -  Default:

      -  ``selector_module``: Default (base) class: selects everything
         in source file
      -  ``formatter_module``: Default (base) class: formats entries as
         loose numbered list

-  ``get_filter(self)``:

   -  Returns:

      -  Function that is a pandoc filter; can be passed to
         ``toJSONFilter``

``Selector``
------------

You write a selector or formatter by subclassing ``Selector`` or
``Formatter`` as imported from module ``pandocinject``.

These classes have methods that you are likely to wish to override for
your own formatter or selector.

-  ``select(self, entry)``:

   -  Returns:

      -  ``True`` if ``entry`` is to be selected for injection into
         document, ``False`` otherwise

   -  Arguments:

      -  ``entry``: Item (dictionary) to assess for selection

   -  Default:

      -  Return ``True``

``Formatter``
-------------

-  ``output_format``: Format of the string that ``format_block`` returns

   -  Value:

      -  Any of pandoc’s output formats (``'-o'``) (e.g. ``'html'``,
         ``'org'``).

   -  Default:

      -  ``'markdown'``

-  ``format_block(self, entries, starred)``:

   -  Returns:

      -  Formatted version of ``entries`` (string)

   -  Arguments:

      -  ``entries``: List of items (sorted)
      -  ``starred``: List of items to star

   -  Default:

      -  Return a markdown string with loose numbered list of entries,
         each formatted by ``format_entry``; star items by inserting a
         preceding asterisk

-  ``format_entry(self, entry)``:

   -  Returns:

      -  Formatted version of ``entry`` (string)

   -  Arguments:

      -  ``entry``: Item (dictionary) to be formatted

   -  Default:

      -  Return Python’s string representation of ``entry``

-  ``sort_entries(self, entries)``:

   -  Returns:

      -  List of items in order they should be formatted, first to last

   -  Arguments:

      -  ``entries``: List of items to sort

   -  Default:

      -  Return ``entries`` unchanged

Similar
=======

A large number of tools can accomplish the same. But here there are no
funky template/style/query languages (SQL, csl, biblatex, etc.) to
learn. The main feature of pandocinject is it provides a simple, general
way to mine lists of items and inject the result into pandoc’s abstract
syntax tree.

Release notes
=============

-  1.0 (28 January 2016):

   -  implement boolean language for ``select`` attribute
   -  documentation complete
   -  clean up

-  0.1 (24 November 2015):

   -  initial release
