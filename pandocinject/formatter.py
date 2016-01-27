###################################
#  Base class for all formatters  #
###################################

class Formatter(object):

    def __init__(self):
        # the format of the strings that this formatter object yields
        # values may be any of pandoc's output formats ('-o')
        # e.g. 'html', 'org'
        self.output_format = 'markdown'

    def format_block(self, entries, starred):
        """
        format a block containing entries
        """
        out = str()
        for e in entries:
            # add each entry in loose numbered list
            out += '1.  '
            # star start of item
            if e in starred:
                out += '\* '
            out += self.format_entry(e)
            out += '\n\n'
        return out

    def format_entry(self, entry):
        """
        format a single entry
        """
        # return a string representation of entry
        return str(entry)

    def sort_entries(self, entries):
        """
        return entries to be formatted from first to list
        """
        # don't do anything
        return entries
