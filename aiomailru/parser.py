from collections import defaultdict
import html.parser


class AuthPageParser(html.parser.HTMLParser):
    """Authorization page parser."""

    def __init__(self):
        super().__init__()
        self.inputs = {}
        self.url = ''

    @property
    def form(self):
        return self.url, self.inputs

    def handle_starttag(self, tag, attrs):
        attrs = defaultdict(str, attrs)

        if tag == 'input':
            if attrs['type'] != 'submit':
                self.inputs[attrs['name']] = attrs['value']
        elif tag == 'form':
            if attrs['method'] == 'post':
                self.url = attrs['action']
