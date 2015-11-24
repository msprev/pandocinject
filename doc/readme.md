# inject-yaml

Injects information from yaml files, formatted by custom functions

- source: names of yaml files to read
- kind: name of module for select/format functions
- select: names of functions to use to filter source list
- format: name of function to use to format list

Example:

    <div class="FILTER-inject" source="test.yaml" kind="event" select="Article SingleAuthor" format="CV"></div>

-- filter transforms to ->>>:

# source

list of files, separated by spaces, of yaml

# kind

# select

# format

# star
