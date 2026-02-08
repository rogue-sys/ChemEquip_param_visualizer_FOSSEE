from django.db import models
from django.contrib.auth.models import User

class Dataset(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    filename = models.CharField(max_length=255)
    summary = models.JSONField()
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.filename} ({self.user.username})"
