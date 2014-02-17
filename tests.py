import unittest
import math
from event_analyse.tf_idf import *
from event_analyse.website_link_arborescence import *


def is_equal(a, b):
    return math.fabs(a-b) < 10**-6


class TestTfIdf(unittest.TestCase):

    def setUp(self):
        # With stopwords
        self.corpus = Corpus()
        self.corpus.add_document(Document("allo attendu test", 1))
        self.corpus.add_document(Document("allo attendu test", 2))
        self.corpus.add_document(Document("attendu", 3))
        self.corpus.add_document(Document("allo test", 4))
        self.corpus.add_document(Document("manger poire", 5))
        self.tf_idf = TfIdf(self.corpus)

        # Without stopwords
        self.corpus = Corpus()
        self.corpus.add_document(Document("manger pomme demain", 1))
        self.corpus.add_document(Document("boire eau demain", 2))
        self.corpus.add_document(Document("hier acheter papillon", 3))
        self.corpus.add_document(Document("absolument papillon", 4))
        self.corpus.add_document(Document("manger poire", 5))
        self.tf_idf2 = TfIdf(self.corpus)

    def test_compute_tf_idf_with_stopwords(self):
        self.assertTrue(is_equal(self.tf_idf.get_tf_idf("test", 1), 0.232990001))
        self.assertTrue(is_equal(self.tf_idf.get_tf_idf("poire", 5), 0.349485002))

    def test_compute_tf_idf_without_stopwords(self):
        self.assertTrue(is_equal(self.tf_idf2.get_tf_idf("papillon", 3), 0.116495001))
        self.assertTrue(is_equal(self.tf_idf2.get_tf_idf("poire", 5), 0.349485002))


class TestUrlExtractor(unittest.TestCase):

    def setUp(self):
        self.unique_urls = HashTableUrl()

    def test_recursion_one(self):
        TreeNode('http://www.cartor.ch'.encode('utf-8'), 1, self.unique_urls)
        supposed_url = ['http://www.cartor.ch/newList/', 'http://www.cartor.ch/pres/',
                        'http://www.cartor.ch/newList/?mod=1', 'http://www.cartor.ch/search/', 'http://www.cartor.ch/']
        out = True
        for u in self.unique_urls.get_urls():
            out = u in supposed_url
            if not out:
                break
        self.assertTrue(out)

    def test_recursion_two(self):
        TreeNode('http://www.cartor.ch'.encode('utf-8'), 2, self.unique_urls)
        supposed_url = ['http://www.cartor.ch/newList/', 'http://www.cartor.ch/pres/',
                        'http://www.cartor.ch/newList/?mod=1', 'http://www.cartor.ch/search/',
                        'http://www.cartor.ch/', 'http://www.cartor.ch/index.php',
                        'http://www.cartor.ch/pres/index.php', 'http://www.cartor.ch/pres/iphone.php',
                        'http://www.cartor.ch/pres/android.php']
        out = True
        for u in self.unique_urls.get_urls():
            out = u in supposed_url
            if not out:
                break
        self.assertTrue(out)

    def test_recursion_three(self):
        TreeNode('http://www.cartor.ch'.encode('utf-8'), 3, self.unique_urls)
        supposed_url = ['http://www.cartor.ch/newList/', 'http://www.cartor.ch/pres/',
                        'http://www.cartor.ch/newList/?mod=1', 'http://www.cartor.ch/search/',
                        'http://www.cartor.ch/', 'http://www.cartor.ch/index.php',
                        'http://www.cartor.ch/pres/index.php', 'http://www.cartor.ch/pres/iphone.php',
                        'http://www.cartor.ch/pres/android.php']
        out = True
        for u in self.unique_urls.get_urls():
            out = u in supposed_url
            if not out:
                break
        self.assertTrue(out)

    def test_recursion_four(self):
        TreeNode('http://www.cartor.ch'.encode('utf-8'), 4, self.unique_urls)
        supposed_url = ['http://www.cartor.ch/newList/', 'http://www.cartor.ch/pres/',
                        'http://www.cartor.ch/newList/?mod=1', 'http://www.cartor.ch/search/',
                        'http://www.cartor.ch/', 'http://www.cartor.ch/index.php',
                        'http://www.cartor.ch/pres/index.php', 'http://www.cartor.ch/pres/iphone.php',
                        'http://www.cartor.ch/pres/android.php']
        out = True
        for u in self.unique_urls.get_urls():
            out = u in supposed_url
            if not out:
                break
        self.assertTrue(out)

if __name__ == '__main__':
    unittest.main()