from django.db import models
from FBGraph.models import User

class Category(models.Model):
    """
    Class representing a category of an event. External_id is related with the gokera.com categories and the name from the same website
    """
    external_id = models.PositiveIntegerField()
    name = models.CharField(max_length=50)

    def __unicode__(self):
        return str(self.external_id) + '\t' + self.name

class Event(models.Model):
    """
    Class representing an event of gokera.com. External_id, name, website, description are related with gokera.com.
    Category is related with the Category class. users_have_rated related with the relation many2many with a user. represented by the class Rating
    """
    category = models.ForeignKey(Category)
    external_id = models.PositiveIntegerField()
    name = models.CharField(max_length=100)
    website = models.URLField()
    description = models.TextField(max_length=1000)
    users_have_rated = models.ManyToManyField(User, through='Rating')
    features = models.ManyToManyField('Feature', through='EventFeature')# 'Feature' because the class is declared underneath

    def __unicode__(self):
        return str(self.external_id) + '\t' + self.category.name + '\t' + self.name + '\t' + self.website + '\t' + self.description

    def __hash__(self):
        return self.external_id

class Rating(models.Model):
    """
    Represent the relation many2many of the table Event & User. Contains the rating of the user about the associated event
    """
    event = models.ForeignKey(Event)
    user = models.ForeignKey(User)
    rating = models.IntegerField()

    def __unicode__(self):
        return str(self.event) + '\t' + str(self.user) + '\t' + 'LIKE' if self.rating == RatingValue.LIKE else 'DISLIKE'

class RatingValue:
    """
    All the possible values that a user can attribute to an event. If it's NEUTRAL, the link is supposed to be removed
    """
    LIKE = 1
    NEUTRAL = 0
    DISLIKE = -1

class Feature(models.Model):
    """
    Represent a feature linked with one or more events
    """
    name = models.CharField(max_length=100)

    def __unicode__(self):
        return self.name

class EventFeature(models.Model):
    """
    Association between an event and a feature
    """
    event = models.ForeignKey(Event)
    feature = models.ForeignKey(Feature)
    tf_idf = models.FloatField()

    def __unicode__(self):
        return self.event + '\t' + self.feature + '\t' + self.tf_idf