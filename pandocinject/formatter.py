###################################
#  Base class for all formatters  #
###################################

class Formatter(object):

    def format_block(self, entries, starred):
        """
        format a list of entries
        """
        out = str()
        for e in entries:
            # add each entry in loose numbered list
            out += '1.  '
            # star start of item
            if e in starred:
                out += '\* '
            out += self.add_entry(e)
            out += '\n\n'
        return out

    def add_entry(self, entry):
        """
        format a single entry
        """
        # return a string representation of entry
        return str(entry)

    def sort_entries(self, entries):
        """
        sort a list of entries
        """
        # don't do anything
        return entries
