from django.db import models
from django.conf import settings  # Correct way to reference User model


# Main Daily Offer
class DailyOffer(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    reward_sb = models.IntegerField(default=0)  # Reward points (only if all answers correct)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


# Questions related to each Daily Offer
class DailyOfferQuestion(models.Model):
    daily_offer = models.ForeignKey(DailyOffer, on_delete=models.CASCADE, related_name='questions')
    question_text = models.CharField(max_length=500, blank=True, null=True)
    question_image = models.ImageField(upload_to="questions/", blank=True, null=True)  # ✅ allow image

    def __str__(self):
        return f"{self.daily_offer.title} - {self.question_text or 'Image Question'}"


# Answers related to each question
class DailyOfferAnswer(models.Model):
    question = models.ForeignKey(DailyOfferQuestion, on_delete=models.CASCADE, related_name='answers')
    answer_text = models.CharField(max_length=300, blank=True, null=True)
    answer_image = models.ImageField(upload_to="answers/", blank=True, null=True)  # ✅ allow image
    is_correct = models.BooleanField(default=False)  # ✅ mark correct one

    def __str__(self):
        return self.answer_text or f"Image Answer {self.id}"


# Tracks the daily fresh assignment of offers to users
class DailyOfferAssignment(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    offer = models.ForeignKey(DailyOffer, on_delete=models.CASCADE)
    assigned_date = models.DateField()
    half_day = models.IntegerField(default=0)  # 0 = morning, 1 = afternoon
    completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)
    reward_given = models.BooleanField(default=False)
    failed = models.BooleanField(default=False)  # ✅ track if user failed (wrong answer)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'offer', 'assigned_date', 'half_day'],
                name='unique_offer_per_user_per_day_half'
            )
        ]

    def __str__(self):
        return f"{self.user.username} - {self.offer.title} ({self.assigned_date}, half={self.half_day})"
