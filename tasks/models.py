from django.db import models
from quiz.models import Quiz  # ✅ keep quiz link for public tasks
from django.conf import settings


class Task(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    reward_sb = models.PositiveIntegerField()
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    quiz = models.ForeignKey(Quiz, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.title


class VisitorTask(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)  # ✅ replaces user
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    assigned_date = models.DateField()                           # ✅ for tracking daily slots
    half_day = models.IntegerField(default=0)                    # 0 = morning, 1 = evening slot
    completed = models.BooleanField(default=False)
    assigned_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    reward_given = models.BooleanField(default=False)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'task', 'assigned_date', 'half_day'],
                name='unique_task_per_user_per_slot'
            )
        ]

    def __str__(self):
        return f"{self.user.username} - {self.task.title} ({self.assigned_date}, half={self.half_day})"
