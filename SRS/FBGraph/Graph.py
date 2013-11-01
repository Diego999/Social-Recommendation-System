from facepy import GraphAPI


class Graph:
    def __init__(self, token):
        self.graph = GraphAPI(token)

    def get_information(self, params):
        """
        Return a dictionary with the given params and the related information asked about Facebook Graph
        """
        out = dict()
        for p in params:
            out[p] = self.graph.get('me/' + p)['data']
        return out

    def get_me(self):
        """
        Return basic data (dictionary) from Facebook Graph with /me
        """
        return self.graph.get('me')