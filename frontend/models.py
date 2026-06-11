from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

from django.contrib.auth.models import User

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """
    ensure a UserProfile is created whenever a User is created.
    """
    if created:
        UserProfile.objects.get_or_create(user=instance)

def user_profile_default_value():
    return {
        'new_tabs': True
    }

class UserProfile(models.Model):
    DEFAULT_SETTINGS = dict(new_tabs=True)

    user = models.OneToOneField(User, related_name='profile',
                                on_delete=models.CASCADE)
    settings = models.JSONField('settings',
                                default=user_profile_default_value)

    def __str__(self):
        return 'Profile of user: {}'.format(self.user.username)

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
        return f"{self.data_source.code} #{self.id}: {self.title[:50]}"


class Vote(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    story = models.ForeignKey(Story, on_delete=models.CASCADE)
    direction = models.SmallIntegerField(choices={-1: "down", 1 : "up"})
    time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        if self.direction > 0:
            sign = "+"
        else:
            sign = ""
        return f"{sign}{self.direction} by {self.user} on {self.story}"

    @classmethod
    def by_user_and_stories(cls, user_id, story_ids):
        """
        returns associative array of story_id => vote.
        """
        votes = Vote.objects.filter(user_id=user_id,
                                    story_id__in=story_ids)
        if votes:
            votes_collated = {vote.story_id: vote for vote in votes}
            return votes_collated
        else:
            return {}

    class Meta:
        indexes = [
            models.Index(fields=["story_id", "user_id"]),
        ]
