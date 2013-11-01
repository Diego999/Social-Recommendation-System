from django.db import models


class User(models.Model):
    """
    Class representing a Facebook User. Contains the external_id, related with Facebook id, a name and the last token
    """
    external_id = models.PositiveIntegerField()
    name = models.CharField(max_length=100)
    token = models.TextField()

    def __unicode__(self):
        return str(self.external_id) + '\t' + self.name + '\t' + self.token