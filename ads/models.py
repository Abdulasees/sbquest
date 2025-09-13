from django.db import models
from users.models import User

class Ad(models.Model):
    title = models.CharField(max_length=255)
    image = models.ImageField(upload_to='ads/')
    link = models.URLField()
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.title

class AdView(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    ad = models.ForeignKey(Ad, on_delete=models.CASCADE)
    viewed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} viewed {self.ad}"
