from django.db import models
from django.conf import settings  
from systemsetting.models import DailyOffer

class DailyOfferLog(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE) 
    offer = models.ForeignKey(DailyOffer, on_delete=models.CASCADE)
    clicked_at = models.DateTimeField(auto_now_add=True)
    rewarded = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username} - {self.offer.title}"
