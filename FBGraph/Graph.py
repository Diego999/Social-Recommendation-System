from facepy import GraphAPI
from models import FBUser, Post, Page, Group


class Graph:
    def __init__(self, token):
        self.graph = GraphAPI(token)
        self.me = None
        self.friends = []

    def fetch_information(self):
        """
        Return the data of the user and his friends
        """
        self.init_me()
        self.init_friends()

        self.init_my_groups()
        self.init_my_friends_groups()

        self.init_my_pages()
        self.init_my_friends_pages()

        self.init_my_posts()
        self.init_my_friends_posts()

        return self.me, self.friends

    def get_graph(self):
        return self.graph

    def init_my_posts(self):
        data = Graph.fetch_user_posts_and_comments(self.graph, 'me()')
        for p in data[0][u'fql_result_set']:
            self.me.add_post(Post(p[u'message'], p[u'created_time']))
        for p in data[1][u'fql_result_set']:
            self.me.add_post(Post(p[u'text'], p[u'time']))

    def init_my_friends_posts(self):
        for i in range(0, len(self.friends)):
            data = Graph.fetch_user_posts_and_comments(self.graph, self.friends[i].get_uid())
            for p in data[0][u'fql_result_set']:
                self.friends[i].add_post(Post(p[u'message'], p[u'created_time']))
            for p in data[1][u'fql_result_set']:
                self.friends[i].add_post(Post(p[u'text'], p[u'time']))

    def init_my_pages(self):
        for p in Graph.fetch_user_pages(self.graph, 'me()'):
            self.me.add_page(Page(p[u'name'], p[u'description']))

    def init_my_friends_pages(self):
        for i in range(0, len(self.friends)):
            for p in Graph.fetch_user_pages(self.graph, self.friends[i].get_uid()):
                self.friends[i].add_page(Page(p[u'name'], p[u'description']))

    def init_my_groups(self):
        for g in Graph.fetch_user_groups(self.graph, 'me()'):
            self.me.add_group(Group(g[u'name'], g[u'description']))

    def init_my_friends_groups(self):
        for i in range(0, len(self.friends)):
            for g in Graph.fetch_user_groups(self.graph, self.friends[i].get_uid()):
                self.friends[i].add_group(Group(g[u'name'], g[u'description']))

    def init_friends(self):
        for l in Graph.fetch_user_information(self.graph, False):
                    self.friends.append(FBUser(l[u'uid'], l[u'name'], l[u'interests']))

    def init_me(self):
        t = Graph.fetch_user_information(self.graph, True)
        self.me = FBUser(t[u'uid'], t[u'name'], t[u'interests'])

    def get_me(self):
        """
        Return basic data (dictionary) from Facebook Graph with /me
        """
        return self.graph.get('me')

    @staticmethod
    def fetch_user_groups(graph, uid):
        return graph.fql('{"groups_friends":"SELECT name, description FROM group WHERE gid IN (SELECT gid FROM group_member WHERE uid  = %s) LIMIT 10000"}' % uid)[u'data'][0][u'fql_result_set']

    @staticmethod
    def fetch_user_pages(graph, uid):
        return graph.fql('{"pages_friends":"SELECT name, description FROM page WHERE page_id IN(SELECT page_id FROM page_fan WHERE uid = %s) LIMIT 10000"}' % uid)[u'data'][0][u'fql_result_set']

    @staticmethod
    def fetch_user_posts_and_comments(graph, uid, start_time=None, end_time=None):
        return graph.fql("""
        {
        "posts":"SELECT post_id, message, created_time FROM stream WHERE source_id = %s and actor_id = %s %s LIMIT 10000",
        "comments":"SELECT text, time FROM comment WHERE post_id IN (SELECT post_id FROM #posts) and fromid = %s %s LIMIT 10000"
        }
        """ % (uid,
               uid,
               ('and created_time >= %s and created_time <= %s' % (start_time, end_time)) if start_time is not None and end_time is not None else '',
               uid,
               ('and time >= %s and time <= %s' % (start_time, end_time)) if start_time is not None and end_time is not None else ''
               ))[u'data']

    @staticmethod
    def fetch_user_information(graph, me=False):
        if me:
            return graph.fql('{"me":"SELECT uid,name,interests FROM user WHERE uid = me()  LIMIT 10000"}')[u'data'][0][u'fql_result_set'][0]
        else:
            return graph.fql('{"friends":"SELECT uid,name,interests FROM user WHERE uid IN (SELECT uid1 FROM friend WHERE uid2 = me()) LIMIT 10000"}')[u'data'][0][u'fql_result_set']