from django.db import models

# Create your models here.
class DataSource(models.Model):
    code = models.CharField(max_length=30)
    type = models.CharField(max_length=20)
    url = models.URLField()
    description = models.CharField(max_length=255, null=True)


class Story(models.Model):
    data_source = models.ForeignKey(DataSource, on_delete=models.PROTECT)
    text = models.TextField()
    retrieved = models.DateTimeField(auto_now_add=True)
    

