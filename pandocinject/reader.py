##############################
#  readers for source files  #
##############################

ENCODING = 'utf-8'

def read_source(filetype, filename):
    if filetype == '.yaml':
        return read_yaml(filename)
    elif filetype == '.bib':
        return read_bibtex(filename)
    return []

def read_yaml(filename):
    import yaml
    with open(filename, 'r', encoding=ENCODING) as f:
        return yaml.load(f)

def read_bibtex(filename):
    import bibtexparser
    from bibtexparser.bparser import BibTexParser

    def customizations(record):
        """
        custom transformation applied during parsing
        """
        record = bibtexparser.customization.convert_to_unicode(record)
        # Split author field from separated by 'and' into a list of "Name, Surname".
        record = bibtexparser.customization.author(record)
        # Split editor field from separated by 'and' into a list of "Name, Surname".
        record = editor_split(record)
        return record

    def editor_split(record):
        """
        custom transformation
        - split editor field into a list of "Name, Surname"
        :record: dict -- the record
        :returns: dict -- the modified record
        """
        if "editor" in record:
            if record["editor"]:
                record["editor"] = getnames([i.strip() for i in record["editor"].replace('\n', ' ').split(" and ")])
            else:
                del record["editor"]
        return record

    with open(filename) as f:
        parser = BibTexParser()
        parser.customization = customizations
        return bibtexparser.load(f, parser=parser).entries

