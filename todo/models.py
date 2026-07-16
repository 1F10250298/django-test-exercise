from django.db import models
from django.utils import timezone


# Create your models here.
class Task(models.Model):
    title = models.CharField(max_length=100)
    completed = models.BooleanField(default=False)
    posted_at = models.DateTimeField(default=timezone.now)
    due_at = models.DateTimeField(null=True, blank=True)
    close_comment = models.CharField(max_length=200, blank=True, default='')

    def save(self, *args, **kwargs):
        if not self.title or self.title.strip() == '':
            self.title = '無題のタスク'
        super().save(*args, **kwargs)

    def is_overdue(self, dt):
        if self.due_at is None:
            return False
        return self.due_at < dt
