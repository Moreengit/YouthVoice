from django.db import models
from django.contrib.auth.models import User
import json
from pathlib import Path

loc_path = Path(__file__).parent / "data" / "kenya_locations.json"

class Profile(models.Model):
    ROLE_CHOICES = [
        ('resident', 'Resident'),
        ('leader', 'Leader'),
    ]

    # Load JSON once
    with open(loc_path, "r") as f:
        loc_data = json.load(f)

    COUNTY_CHOICES = [
        (county["name"], county["name"])
        for county in loc_data["counties"]
    ]

    CONSTITUENCY_CHOICES = []
    for county in loc_data["counties"]:
        for const in county["constituencies"]:
            CONSTITUENCY_CHOICES.append((const["name"], const["name"]))
    
    

    WARD_CHOICES = []
    for county in loc_data["counties"]:
        for const in county["constituencies"]:
            for ward in const["wards"]:
                WARD_CHOICES.append((ward, ward))

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    county = models.CharField(max_length=100, choices=COUNTY_CHOICES)
    constituency = models.CharField(max_length=100, choices=CONSTITUENCY_CHOICES )
    ward = models.CharField(max_length=100, choices=WARD_CHOICES)

    def __str__(self):
        return f"{self.user.username}'s profile"



class Idea(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    image = models.ImageField(upload_to='ideas/', blank=True, null=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ideas')
    county = models.CharField(max_length=100)
    constituency = models.CharField(max_length=100)
    ward = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    def total_votes(self):
        return self.vote_set.count()

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-created_at']

    STATUS_CHOICES = [
        ('open', 'Open'),
        ('in_progress', 'In Progress'),
        ('done', 'Done'),
    ]

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')


    


class Vote(models.Model):
    idea = models.ForeignKey(Idea, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('idea', 'user') 

    def __str__(self):
        return f"{self.user} voted on {self.idea}"





class Sponsorship(models.Model):
    TIER_CHOICES = [
        ('bronze', 'Bronze - KES 100'),
        ('silver', 'Silver - KES 500'),
        ('gold', 'Gold - KES 1000+'),
    ]

    name = models.CharField(max_length=100, blank=True)
    phone_number = models.CharField(max_length=15)
    amount = models.PositiveIntegerField()
    tier = models.CharField(max_length=10, choices=TIER_CHOICES)
    message = models.TextField(blank=True)
    mpesa_receipt_number = models.CharField(max_length=50, blank=True, null=True)
    status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending'),
            ('completed', 'Completed'),
            ('failed', 'Failed'),
        ],
        default='pending'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name or 'Anonymous'} - KES {self.amount}"

    class Meta:
        ordering = ['-created_at']

