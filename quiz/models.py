from django.db import models
from users.models import User


class Quiz(models.Model):
    title = models.CharField(max_length=200)

    def __str__(self):
        return self.title


class Question(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name="questions")
    text = models.TextField()
    image = models.ImageField(upload_to="questions/", blank=True, null=True)  # ✅ question image

    def __str__(self):
        return self.text[:50]


class Answer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name="answers")
    text = models.CharField(max_length=255, blank=True, null=True)  # ✅ answer text
    image = models.ImageField(upload_to="answers/", blank=True, null=True)  # ✅ answer image
    is_correct = models.BooleanField(default=False)  # ✅ mark correct answer

    def __str__(self):
        return f"Answer to Q{self.question.id}: {self.text or 'Image Answer'}"


class UserAnswer(models.Model):
    user = models.ForeignKey("users.User", on_delete=models.CASCADE)
    question = models.ForeignKey("quiz.Question", on_delete=models.CASCADE)
    is_correct = models.BooleanField(default=False)  # ✅ only track if correct
    answered_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} - {self.question} ({'Correct' if self.is_correct else 'Wrong'})"

