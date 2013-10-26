class Document:
    """This class represent a document. This document could be a description or text parsing for a website"""

    def __init__(self, text, id):
        self.id = id
        self.statistics = dict()
        self.add_text(text)

    def __eq__(self, other):
        return self.id == other.id

    def __contains__(self, item):
        return item == self.id

    def __hash__(self):
        return self.id

    def __str__(self):
        return str(self.id)

    def get_statistics(self):
        """Return a dictionary contains the number of occurrence for all terms"""
        return self.statistics

    def add_text(self, text):
        """Add the text to the document and update the statistics"""
        words = text.split()
        for w in words:
            if w in self.statistics:
                self.statistics[w] += 1
            else:
                self.statistics[w] = 1

    def get_tf(self, term):
        """Compute the tf of a specific term"""
        if term in self.statistics:
            occurrence = self.statistics[term]
            all_occurrences = 0
            for v in self.statistics.values():
                all_occurrences += v
            return float(occurrence)/float(all_occurrences)
        else:
            return 0

class Corpus:
    """Class reprensents a corpus, that contains a set of documents"""
    def __init__(self):
        self.documents = list()

    def __contains__(self, item):
        return item in self.documents

    def add_document(self, document):
        """Add a document in the corpus"""
        self.documents.append(document)

    def get_idf(self, term):
        """Compute the idf of a specific term in the corpus"""
        import math

        number_documents_with_term = 0
        for doc in self.documents:
            if doc.get_tf(term) != 0:
                number_documents_with_term += 1

        #Mathematically the base of the function log is not important
        return math.log(len(self.documents), 2)/number_documents_with_term if number_documents_with_term != 0 else 1

class TfIdf:
    """Class make easier to compute the tf-idf"""
    def __init__(self, corpus, stopwords):
        self.total_number_documents = 0
        self.stopwords = list()
        self.corpus = corpus
        self.term_tf_idf = dict(dict())

        with open(stopwords, 'r') as f:
            for l in f.read().splitlines():
                self.stopwords.append(l)

    def get_tf_idf(self, term, document):
        """Compute the tf-idf of a term in the document
        term -> A word
        document -> A document class
        Return : tf-idf
        """
        if document not in self.corpus:
            raise Exception("The document is no in the corpus !")

        if term in self.stopwords:
            return 0

        tf = document.get_tf(term)
        idf = self.corpus.get_idf(term)

        out = tf*idf

        if document not in self.term_tf_idf.keys():
            self.term_tf_idf[document] = dict()
            self.term_tf_idf[document][term] = out
        else:
            self.term_tf_idf[document][term] = out
        return out

    def get_all_tf_idf_sorted(self):
        """Return all the tf-idf computed, by document and inverted-sorted
        Return : dict(OrderedDict())"""
        from collections import OrderedDict
        out = dict()
        for d in self.term_tf_idf.keys():
            out[d] = OrderedDict(sorted(self.term_tf_idf[d].items(), key=lambda x: x[1], reverse=True))
        return out
