# Create your models here.
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
import random

class SystemLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='system_logs')
    cpu_usage = models.FloatField()
    ram_usage = models.FloatField()
    disk_usage = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    def __str__(self):
        return f"CPU:{self.cpu_usage}% RAM:{self.ram_usage}%"

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    latitude = models.FloatField(default=0.0)
    longitude = models.FloatField(default=0.0)
    latest_cpu = models.FloatField(default=0.0)
    latest_ram = models.FloatField(default=0.0)
    latest_disk = models.FloatField(default=0.0)
    latest_disk_total = models.FloatField(null=True, blank=True)
    latest_disk_free = models.FloatField(null=True, blank=True)

    def __str__(self):
        return self.user.username

CITIES = [
    (40.7128, -74.0060),  # New York
    (34.0522, -118.2437), # Los Angeles
    (51.5074, -0.1278),   # London
    (48.8566, 2.3522),    # Paris
    (35.6895, 139.6917),  # Tokyo
    (39.9042, 116.4074),  # Beijing
    (19.0760, 72.8777),   # Mumbai
    (28.6139, 77.2090),   # New Delhi
    (23.0225, 72.5714),   # Ahmedabad
    (-33.8688, 151.2093), # Sydney
    (-23.5505, -46.6333), # Sao Paulo
    (55.7558, 37.6173),   # Moscow
    (1.3521, 103.8198),   # Singapore
]

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        lat, lon = random.choice(CITIES)
        lat += random.uniform(-0.05, 0.05)
        lon += random.uniform(-0.05, 0.05)
        UserProfile.objects.create(user=instance, latitude=lat, longitude=lon)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if hasattr(instance, 'userprofile'):
        instance.userprofile.save()
    else:
        lat, lon = random.choice(CITIES)
        lat += random.uniform(-0.05, 0.05)
        lon += random.uniform(-0.05, 0.05)
        UserProfile.objects.create(user=instance, latitude=lat, longitude=lon)