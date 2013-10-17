from django.db import models
from FBGraph.models import User

class Category(models.Model):
    external_id = models.PositiveIntegerField()
    name = models.CharField(max_length=50)

    def __unicode__(self):
        return str(self.external_id) + '\t' + self.name

class Event(models.Model):
    category = models.ForeignKey(Category)
    external_id = models.PositiveIntegerField()
    name = models.CharField(max_length=100)
    website = models.URLField()
    description = models.TextField(max_length=1000)
    users_have_rated = models.ManyToManyField(User, through='Rating')

    def __unicode__(self):
        return str(self.external_id) + '\t' + self.category.name + '\t' + self.name + '\t' + self.website + '\t' + self.description

class Rating(models.Model):
    event = models.ForeignKey(Event)
    user = models.ForeignKey(User)
    rating = models.IntegerField()

    def __unicode__(self):
        return str(self.event) + '\t' + str(self.user) + '\t' + 'LIKE' if self.rating == RatingValue.LIKE else 'DISLIKE'

class RatingValue:
    LIKE = 1
    NEUTRAL = 0
    DISLIKE = -1
