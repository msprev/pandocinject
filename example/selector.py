from pandocinject import Selector

class Since2012(Selector):
    def select(self, entry):
        return True if entry['year'] > 2012 else False
