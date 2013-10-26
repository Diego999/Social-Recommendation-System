from HTMLParser import HTMLParser
import re

class HTMLParserByTag(HTMLParser):
    """This class allows you to catch any unique element in a HTML document.
    For example, if you have the following document : <p>123<span>456</span>789</p> and you want to fetch all p elements,
    you'll have the following result : 123789.
    When you've created an object, don't forger to initialize it before feeding it !

    If you've a problem with the accent, try this :
    parser = HTMLParserByTag()
    parser.initialize(...)
    parser.unescape(urllib2.urlopen("...").read().decode('ascii', 'ignore'))
    """

    def __init__(self):
        HTMLParser.__init__(self)
        self.tag = ''
        self.stack = None
        self.keep_data = None
        self.data = None

    def initialize(self, tag):
        """Initialize the object for a new feed"""
        self.tag = tag
        self.stack = list()
        self.keep_data = False
        self.data = list()

    def get_data(self):
        """Return all the pasing result."""
        return ' '.join(self.data)

    def handle_starttag(self, tag, attrs):
        if tag == self.tag or len(self.stack) > 0:
            self.stack.append(tag)
            self.keep_data = tag == self.tag

    def handle_endtag(self, tag):
        if len(self.stack) > 0 and self.stack[-1] == tag:
            self.stack.pop()

            self.keep_data = len(self.stack) > 0 and self.stack[-1] == self.tag

    def handle_data(self, data):
        if self.keep_data:
            out = re.sub(r' +', ' ', re.sub(r'([.,!\|?\n])', '', data)).lstrip().rstrip()
            if len(out) > 0:
                self.data.append(out)