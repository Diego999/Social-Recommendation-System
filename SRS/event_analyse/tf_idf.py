from tree_tagger import TreeTagger
from app_config import FRENCH_STOPWORDS_FILE


class TypeFeature(object):
    Description = 1
    Website = 2
    Category = 3


def load_stopwords():
    stopwords = list()
    with open(FRENCH_STOPWORDS_FILE, 'r') as f:
        for l in f.read().splitlines():
            stopwords.append(l.decode('utf-8'))
    return stopwords


class Document:
    """
    This class represent a document. This document could be a description or text parsing for a website
    """
    stopwords = load_stopwords()

    def __init__(self, text, id):
        self.id = id  # Useful to sort the document
        self.statistics = dict()
        self.tagger = TreeTagger()
        self.add_text(text)

    def __eq__(self, other):
        return self.id == other

    def __contains__(self, item):
        return item == self.id

    def __hash__(self):
        return self.id

    def __str__(self):
        return str(self.id)

    def get_id(self):
        return self.id

    def get_statistics(self):
        """
        Return a dictionary contains the number of occurrence for all terms
        """
        return self.statistics

    def add_text(self, text):
        """
        Add the text to the document and update the statistics
        """
        words = self.tagger.tag_text(text=text, all_tags=True)

        for w in words:
            if w not in Document.stopwords:
                if w in self.statistics:
                    self.statistics[w] += 1
                else:
                    self.statistics[w] = 1

    def get_tf(self, term):
        """
        Compute the tf of a specific term
        """
        if term in self.statistics:
            occurrence = self.statistics[term]
            all_occurrences = 0
            for v in self.statistics.values():
                all_occurrences += v
            return float(occurrence)/float(all_occurrences)
        else:
            return 0.0


class Corpus:
    """
    Class represents a corpus, that contains a set of documents
    """

    def __init__(self):
        self.documents = list()

    def __contains__(self, item):
        return item in self.documents

    def add_document(self, document):
        """
        Add a document in the corpus
        """
        self.documents.append(document)

    def get_document(self, doc_id):
        for doc in self.documents:
            if doc.get_id() == doc_id:
                return doc
        return None

    def get_idf(self, term):
        """
        Compute the idf of a specific term in the corpus
        """
        import numpy

        number_documents_with_term = 0
        for doc in self.documents:
            if doc.get_tf(term) != 0:
                number_documents_with_term += 1

        #  Mathematically the base of the function log is not important
        return numpy.log10(len(self.documents))/number_documents_with_term if number_documents_with_term != 0 else 1


class TfIdf:
    """
    Class make easier to compute the tf-idf
    """

    def __init__(self, corpus):
        self.total_number_documents = 0
        self.corpus = corpus
        self.term_tf_idf = dict(dict())

    def get_tf_idf(self, term, doc_id):
        """
        Compute the tf-idf of a term in the document
        term -> A word
        document -> A document class. If it contains an underscore, it's considered as a website thus the website weight factor is apply
        Return : tf-idf
        """

        if doc_id not in self.corpus:
            raise Exception("The document is no in the corpus !")

        if term in Document.stopwords:
            return 0.0

        doc = self.corpus.get_document(doc_id)

        if doc is None:
            return None

        tf = doc.get_tf(term)
        idf = self.corpus.get_idf(term)

        out = tf*idf
        type = TypeFeature.Website if '_' in str(doc.get_id()) else TypeFeature.Description

        if doc.get_id() not in self.term_tf_idf.keys():
            self.term_tf_idf[doc.get_id()] = dict()
            self.term_tf_idf[doc.get_id()][term] = (tf, out, type)
        else:
            self.term_tf_idf[doc.get_id()][term] = (tf, out, type)

        return out

    def get_all_tf_idf_sorted(self, id_doc=0):
        """
        Return all the tf-idf computed, by document and inverted-sorted
        Return : dict(OrderedDict())
        """
        from collections import OrderedDict
        out = OrderedDict()

        if id_doc == 0:
            for d in self.term_tf_idf.keys():
                out[d] = OrderedDict(sorted(self.term_tf_idf[d].items(), key=lambda x: x[1], reverse=True))
        elif id_doc not in self.term_tf_idf.keys():
            return out
        else:
            out = OrderedDict(sorted(self.term_tf_idf[id_doc].items(), key=lambda x: x[1], reverse=True))

        return out

