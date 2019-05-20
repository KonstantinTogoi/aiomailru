import html.parser


class AuthPageParser(html.parser.HTMLParser):
    def __init__(self):
        super().__init__()
        self.inputs = {}
        self.url = ''

    def handle_startendtag(self, tag, attrs):
        attrs = dict(attrs)
        name = attrs.get('name', '')
        value = attrs.get('value', '')

        if name == 'Login':
            self.inputs['Login'] = value
        if name == 'Password':
            self.inputs['Password'] = value
        if name == 'Page':
            self.inputs['Page'] = value
        if name == 'FailPage':
            self.inputs['FailPage'] = value

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)

        if attrs.get('name') == 'Domain':
            self.inputs['Domain'] = attrs.get('value', '')

        if tag == 'form':
            self.url = attrs.get('action', '')
