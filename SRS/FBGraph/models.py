from django.db import models
import time


class User(models.Model):
    """
    Class representing a Facebook User. Contains the external_id, related with Facebook id, a name and the last token
    """
    external_id = models.PositiveIntegerField()
    name = models.CharField(max_length=100)
    token = models.TextField()

    def __unicode__(self):
        return str(self.external_id) + '\t' + self.name + '\t' + self.token


class FBUser:
    """
    Class that represents a Facebook user with fields uid, name and interests
    """

    def __init__(self, uid, name, interests):
        self.uid = uid
        self.name = name
        self.interests = [] if len(interests) == 0 else interests.split(',')
        for i in range(0, len(self.interests)):
            self.interests[i] = self.interests[i]
        self.groups = []
        self.pages = []
        self.posts = []
        self.average_between_posts = None
        self.first_activity = None
        self.average_absolute_deviation_between_posts = None

    def get_average_between_post(self):
        """
        Return the average time between each messages posted in seconds
        """
        if self.average_between_posts is None:
            self.first_activity = sorted([p.get_created_time() for p in self.posts])[0]
            now = int(time.time())
            self.average_between_posts = float(now - self.first_activity)/float(len(self.posts))
        return self.average_between_posts

    def get_average_absolute_deviation(self, graph):
        """
        Return the average absolute deviation time between each messages posted in seconds
        """
        from Graph import Graph

        if self.average_absolute_deviation_between_posts is None:
            if self.average_between_posts is None:
                self.get_average_between_post()
            avg = self.average_between_posts

            months = []
            month_in_secs = 60*60*24*30  # We approximate with 30 days in a month
            i = self.first_activity
            now = int(time.time())
            while i < now:
                months.append((i, i+month_in_secs))
                i += month_in_secs

            self.average_absolute_deviation_between_posts = 0
            for m in months:
                data = graph.fetch_user_posts_and_comments(graph.get_graph(), self.uid, m[0], m[1])
                nb_msg = len(data[0][u'fql_result_set']) + len(data[1][u'fql_result_set'])
                self.average_absolute_deviation_between_posts += abs((float(month_in_secs)/float(nb_msg) if nb_msg != 0 else 0) - avg)
                time.sleep(1)
            self.average_absolute_deviation_between_posts /= float(len(months))
        return self.average_absolute_deviation_between_posts

    def add_post(self, post):
        self.posts.append(post)

    def add_group(self, group):
        self.groups.append(group)

    def add_page(self, page):
        self.pages.append(page)

    def __unicode__(self):
        return self.uid + '\t' + self.name + '\t' + self.interests + '\t' + self.groups + '\t' + self.pages + '\t' + self.posts

    def get_uid(self):
        return self.uid

    def get_name(self):
        return self.name

    def get_interests(self):
        return self.interests

    def get_posts(self):
        return self.posts

    def get_pages(self):
        return self.pages

    def get_groups(self):
        return self.groups


class Group:
    """
    Class that represents a group in Facebook
    """

    def __init__(self, name, description):
        self.name = name
        self.description = description.replace('\n', ' ').replace('\\', ' ').replace('/', ' ')

    def __unicode__(self):
        return self.name + '\t' + self.description

    def get_name(self):
        return self.name

    def get_description(self):
        return self.description


class Page:
    """
    Class that represents a page fan in Facebook
    """

    def __init__(self, name, description):
        self.name = name
        self.description = description.replace('\n', ' ').replace('\\', ' ').replace('/', ' ')

    def __unicode__(self):
        return self.name + '\t' + self.description

    def get_name(self):
        return self.name

    def get_description(self):
        return self.description


class Post:
    """
    Class that represents a post/comment fan in Facebook
    """

    def __init__(self, message, created_time):
        self.message = message.replace('\n', ' ').replace('\\', ' ').replace('/', ' ')
        self.created_time = created_time

    def __unicode__(self):
        return self.message + '\t' + self.created_time

    def get_message(self):
        return self.message

    def get_created_time(self):
        return self.created_time