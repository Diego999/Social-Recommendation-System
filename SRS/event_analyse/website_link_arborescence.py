from HTMLParser import HTMLParser
import urlparse
import urllib2
from urllib2 import HTTPError, URLError
from httplib import BadStatusLine


class HashTableUrl:
    """
    Class used for the class TreeNode & HTMLParserLink. This class allows you to have all unique urls in a specified
    website. The hash function is simply f(x)=x, a url is suppose to be unique, so no problem !
    """
    def __init__(self):
        self.list = list()

    def add(self, url):
        if url not in self.list:
            self.list.append(url)

    def __contains__(self, item):
        return item in self.list

    def get_urls(self):
        return self.list


class HTMLParserLink(HTMLParser):
    """
    This class parses a website and fetch all the href of a tag <a>. Then it cleans this url and add in the list of the
    current node and the hash table urls if and only if it's not already in. This purpose is to have unique set of urls
    for a specified website.
    """
    @staticmethod
    def remove_last_slash(url):
        return url if len(url) == 0 or url[-1] != '/' else url[:-1]

    @staticmethod
    def clean_path(path):
        if len(path) == 0 or len(path) == 1:
            return ''

        if path.count('/') == 1:
            return ''

        return path[0:path.rfind('/')]

    @staticmethod
    def remove_sharp(url):
        return url[0:url.find('#')] if url.count('#') > 0 else url

    def __init__(self, url, hash_table_urls):
        HTMLParser.__init__(self)
        parse = urlparse.urlparse(url)
        self.hash_table_urls = hash_table_urls
        self.netloc = parse.netloc
        self.root_url = parse.scheme + '://' + HTMLParserLink.remove_last_slash(parse.netloc)
        self.parent = HTMLParserLink.remove_last_slash(self.root_url + HTMLParserLink.clean_path(parse.path))
        self.links = list()

    def handle_starttag(self, tag, attrs):
        if tag == 'a' and len(attrs) > 0 and attrs[0][0] == 'href' and len(attrs[0][1]) > 0:
            link = attrs[0][1]  # href attribute
            parent = self.parent
            parse = urlparse.urlparse(link)
            mime = None

            if parse.scheme == '':
                # All relative cases
                if link[0] == '.' and link[1] == '.' and link[2] == '/':
                    parent = HTMLParserLink.clean_path(self.parent)
                    link = link[3:]
                elif link[0] == '.' and link[1] == '/':
                    link = link[2:]
                elif link[0] == '/':
                    parent = self.root_url
                    link = link[1:]

                # Transform the relative path to an absolute one and update the parser and the mime type
                # (didn't know before)
                link = parent + '/' + link
                if link[-1] != '/':
                    try:
                        response = urllib2.urlopen(link)
                        mime = response.info()['Content-Type']
                        link = HTMLParserLink.remove_sharp(response.geturl())
                    except (HTTPError, URLError, ValueError) as e:
                        return
                parse = urlparse.urlparse(link)

            # We keep the link if and only if :
            # - the domain is the same (we are not interested to leave the website)
            # - The link is not already in the children links of the parent and the hash table
            # - The contain is HTML
            if parse.netloc == self.netloc:
                link = HTMLParserLink.remove_sharp(link)
                if link not in self.hash_table_urls and link not in self.links:
                    try:
                        mime = mime if mime is not None else urllib2.urlopen(link).info()['Content-Type']
                        if 'text/html' in mime:
                            self.links.append(link)
                            self.hash_table_urls.add(link)
                    except (HTTPError, URLError, ValueError) as e:
                        pass

    def get_links(self):
        """
        Return the children links of the parent
        """
        return self.links


class TreeNode:
    """
    Class that represents a url for a tree structure. It will parse recursively a website with a specified depth
    and update the hash table.
    """
    prefix_tag = '\t'

    def __init__(self, url, depth, hash_table_urls):
        self.url = url
        self.parser = HTMLParserLink(url, hash_table_urls)
        self.urls = list()
        self.depth = depth
        self.can_process = depth > 0
        self.hash_table_urls = hash_table_urls

        if self.can_process:
            self.process()

    def process(self):
        if self.can_process:
            self.urls = list()
            try:
                self.parser.feed(self.parser.unescape(urllib2.urlopen(self.url).read().decode('utf-8')))
                for link in self.parser.get_links():
                    self.urls.append(TreeNode(link, self.depth-1, self.hash_table_urls))
            except (HTTPError, URLError, ValueError, BadStatusLine) as e:
                pass

    # DEBUG
    """def display(self, prefix=''):
        for u in self.urls:
            print prefix + u.url
            u.display(prefix + TreeNode.prefix_tag)"""

