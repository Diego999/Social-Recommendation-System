from facepy import GraphAPI
import json

class Graph:
    def __init__(self, token):
        self.graph = GraphAPI(token)

    def get_information(self, params):
        out = dict()
        for p in params:
            out[p] = self.graph.get(path='me/' + p, page=False)['data']

        return out
