from django.db import models
from users.models import User
from quiz.models import Quiz  # ✅ Importing the Quiz model


class Task(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    reward_sb = models.PositiveIntegerField()
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    quiz = models.ForeignKey(Quiz, on_delete=models.SET_NULL, null=True, blank=True)  # ✅ Optional quiz link

    def __str__(self):
        return self.title


class UserTask(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    completed = models.BooleanField(default=False)
    assigned_at = models.DateTimeField(null=True, blank=True)   # ✅ New field for slot assignment
    completed_at = models.DateTimeField(null=True, blank=True)  # ✅ Only set when user finishes
    reward_given = models.BooleanField(default=False)           # ✅ New field to track reward status

    def __str__(self):
        return f"{self.user} - {self.task}"
