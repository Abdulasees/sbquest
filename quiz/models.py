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
    visitor_id = models.CharField(max_length=64, db_index=True)  # track anonymous users
    question = models.ForeignKey("quiz.Question", on_delete=models.CASCADE)
    is_correct = models.BooleanField(default=False)
    answered_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('visitor_id', 'question')  # one answer per visitor per question

    def __str__(self):
        return f"{self.visitor_id} - {self.question} ({'Correct' if self.is_correct else 'Wrong'})"


