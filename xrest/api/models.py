from django.db import models


# Create your models here.
class SomeFile(models.Model):
    file = models.FileField(max_length=100)
    name = models.CharField(max_length=100, default='')
    size = models.IntegerField(default=0)
    ext = models.CharField(max_length=100, default='')
    mime_type = models.CharField(max_length=100, default='')
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
