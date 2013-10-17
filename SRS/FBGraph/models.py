from django.db import models

class User(models.Model):
    external_id = models.PositiveIntegerField()
    name = models.CharField(max_length=100)
    token = models.TextField()

    def __unicode__(self):
        return str(self.external_id) + '\t' + self.name + '\t' + self.token