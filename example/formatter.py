from pandocinject import Formatter

class Homepage(Formatter):
    def format_entry(self, entry):
        text = str()
        text += '*' + entry['title'] + '*, '
        text += entry['venue'] + ', '
        text += str(entry['year'])
        return text
