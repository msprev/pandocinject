###################################
#  Base class for all formatters  #
###################################

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
