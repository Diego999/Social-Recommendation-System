from django.db import models

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

    def __unicode__(self):
        return str(self.external_id) + '\t' + self.category.name + '\t' + self.name + '\t' + self.website + '\t' \
               + self.description