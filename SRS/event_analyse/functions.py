import urllib2
from config import IMPORTANT_WEBSITE_TAGS

from html_parser_by_tag import HTMLParserByTag
from models import Event

def event_website_analyse():
    events = Event.objects.exclude(website='')

    parser = HTMLParserByTag()
    for e in events:
        html = parser.unescape(urllib2.urlopen(e.website).read().decode('ascii', 'ignore'))
        for t in IMPORTANT_WEBSITE_TAGS:
            parser.initialize(t)
            parser.feed(html)
            parsed_text = parser.get_data()

            """TODO"""
