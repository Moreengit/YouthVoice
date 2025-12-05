from django.db import models
from django.contrib.auth.models import User
import json 
from pathlib import Path 
import json
from pathlib import Path

loc_path = Path(__file__).parent / "data" / "locations.json"

# Create your models here.
with open(loc_path, "r") as f:
    loc_data = json.load(f)

print(loc_data)
class Profile(models.Model):
    ROLE_CHOICES = [
        ('resident', 'Resident'),
        ('leader', 'Leader'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)

    county = models.CharField(max_length=100)
    constituency = models.CharField(max_length=100)
    ward = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.user.username}'s profile"
