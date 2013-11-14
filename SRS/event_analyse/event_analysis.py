from tf_idf import *


class EventAnalysis:
    """
    Class that contains all the necessary operation to process to a text analysis
    """

    @staticmethod
    def get_id_website(id_doc, is_website):
        """
        Apply the processing to have a website id
        """
        return id_doc if not is_website else id_doc + '_'

    def __init__(self):
        self.corpus = Corpus()
        self.is_corpus_complete = False
        self.tf_idf = None

    def add_document_in_corpus(self, text, id_doc):
        """
        The id is as follow :
        - A description : Event's id
        - A website : Event's id + "_"
        """
        self.corpus.add_document(Document(text.lower(), id_doc))

    def set_corpus_complete(self):
        """
        Define the corpus as complete to proceed to the next step with tf-idf
        """
        self.is_corpus_complete = True
        self.tf_idf = TfIdf(self.corpus)

    def compute_tf_idf(self, term, id_doc):
        """
        The id is as follow :
        - A description : Event's id
        - A website : Event's id + "_"
        """
        return self.tf_idf.get_tf_idf(term.lower(), id_doc)

    def get_tf_idf_the_k_most_important(self, k, id_doc):
        """
        Return a OrderedDict that contains the k most important term (sorted by frequences). If there are
        less terms as k, it returns the number of terms.
        """
        if not self.is_corpus_complete:
            raise Exception("The corpus is not complete ! Please call set_corpus_complete when you've filled it.")

        if k <= 0:
            raise Exception("The k is <= 0 !")

        from itertools import islice
        from collections import OrderedDict

        #Transform OrderedDict(key, tuple(double1, double2)) in OrderedDict(key, double2)
        return OrderedDict((x[0], (x[1][0], x[1][1], x[1][2])) for x in
                           islice(self.tf_idf.get_all_tf_idf_sorted(id_doc).items(), 0, k))
