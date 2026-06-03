from django.db import models


class DataSource(models.Model):
    code = models.CharField(max_length=30)
    type = models.CharField(max_length=20)
    url = models.URLField()
    description = models.CharField(max_length=255, null=True)

    def __str__(self):
        return self.code


class Story(models.Model):
    data_source = models.ForeignKey(DataSource, on_delete=models.PROTECT)
    text = models.TextField()
    original_url = models.URLField(null=True)
    retrieved = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.data_source.code}: {self.text[:50]}"