from django.db import models
from django.contrib.postgres.fields import JSONField

class FXTable(models.Model):
    created = models.DateTimeField("created", auto_now=True)
    kind = models.TextField()
    payload = JSONField()
    completed = models.DateTimeField(null=True)
    completion_payload = JSONField(null=True)
    