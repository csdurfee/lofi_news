from django.db import models

class DataSource(models.Model):
    code = models.CharField(max_length=30)
    type = models.CharField(max_length=20)
    url = models.URLField()
    description = models.CharField(max_length=255, null=True)
    last_checked = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return f"{self.code}: {self.url[:50]}"

class Story(models.Model):
    data_source = models.ForeignKey(DataSource, on_delete=models.PROTECT)
    title = models.CharField(max_length=100)
    text = models.TextField()
    original_url = models.URLField(null=True)
    retrieved = models.DateTimeField(auto_now_add=True)
    raw_data = models.JSONField()

    def __str__(self):
        return f"{self.data_source.code}: {self.title[:50]}"

    def can_up(self):
        # TODO implement this
        return True

    def can_down(self):
        # TODO implement this
        return True