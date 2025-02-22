from django.db import models
from django.contrib.auth.models import AbstractUser

# custom user 
class User(AbstractUser):
    
    def __str__(self):
        return self.username


class HydroponicSystem(models.Model):
    name = models.CharField(max_length=100)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='systems')
    created_date = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.name} Owned by {self.owner.username}"
        
    
class Measurement(models.Model):
    system = models.ForeignKey(HydroponicSystem, on_delete=models.CASCADE, related_name='measurements')
    ph = models.FloatField()
    temperature = models.FloatField()
    tds = models.IntegerField()
    timestamp = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Measurement for {self.system.name} | pH: {self.ph}, Temp: {self.temperature}°C, TDS: {self.tds} ppm"