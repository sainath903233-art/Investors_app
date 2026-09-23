# core/models.py
# Extra info attached to each user (like a linked row in Sequelize)

from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    # Each User has exactly one Profile
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    RISK_CHOICES = [
        ("conservative", "Conservative (careful)"),
        ("moderate", "Moderate (balanced)"),
        ("aggressive", "Aggressive (bold)"),
    ]
    risk_profile = models.CharField(max_length=20, choices=RISK_CHOICES, default="moderate")

    def __str__(self):
        return f"{self.user.username} ({self.risk_profile})"
