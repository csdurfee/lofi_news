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

class Channel(models.Model):
    code = models.CharField(max_length=30)
    description = models.CharField(max_length=100)

    def __str__(self):
        return f"[{self.code}] {self.description[:50]}"

class DataSource(models.Model):
    code = models.CharField(max_length=30)
    type = models.CharField(max_length=20)
    url = models.URLField()
    description = models.CharField(max_length=255, null=True)
    last_checked = models.DateTimeField(auto_now_add=True, null=True)
    channel = models.ForeignKey(Channel, on_delete=models.PROTECT, null=True)

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

    @classmethod
    def saved(cls, user_id, limit=10, last_id=None):
        """
        Return items saved (TODO: consolidate with unskipped?) 
        """
        saved = Vote.objects.filter(user=user_id,
                                    direction=Vote.Direction.UP) \
                                    .values_list('story_id', flat=True)
        query = Story.objects.filter(id__in=saved)
        if last_id:
            query = query.filter(id__lt=last_id)

        query = query.order_by("-id") \
                    .select_related("data_source")
        return list(query[:limit])


    @classmethod
    def unskipped(cls, user_id=None, order_by="-id",
                        limit=10, sources=None, last_id=None):
        """
        get stories that the user hasn't skipped yet

        if no user id, get all stories that match other criteria

        this needs to potentially handle:
            after_id => last story seen (for pagination)
            data_source => list of sources to filter to
            saved => include saved ones?
            skipped => include skipped ones?
            order_by => direction to sort
        """

        # get skipped
        if user_id:
            skipped = Vote.objects.filter(user=user_id,
                                        direction=Vote.Direction.DOWN) \
                                    .values_list('story_id', flat=True)

            query = Story.objects.exclude(id__in=skipped)
        else:
            query = Story.objects

        if sources:
            query = query.filter(data_source__in=sources)

        if last_id:
            # fixme: this depends on order-by
            query = query.filter(id__lt=last_id)

        query = query.order_by(order_by) \
            .select_related('data_source')

        return list(query[:limit])


class Vote(models.Model):
    class Direction(models.IntegerChoices):
        DOWN = -1, "down"
        UP = 1, "up"

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    story = models.ForeignKey(Story, on_delete=models.CASCADE)
    direction = models.SmallIntegerField(choices=Direction)
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
