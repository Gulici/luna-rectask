from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    """
    Custom user model extending Django's AbstractUser.
    Allows for future extensions such as additional fields.
    """

    def __str__(self):
        return self.username


class HydroponicSystem(models.Model):
    """
    Model representing a hydroponic system owned by a user.
    Each system is uniquely associated with a user.
    """

    name = models.CharField(max_length=100, db_index=True)
    owner = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="systems", db_index=True
    )
    created_date = models.DateTimeField(auto_now_add=True, db_index=True)

    def __str__(self):
        return f"{self.name} (Owner: {self.owner.username})"


class Measurement(models.Model):
    """
    Model representing a measurement recorded for a hydroponic system.
    Each measurement contains pH, temperature, and TDS (Total Dissolved Solids).
    """

    system = models.ForeignKey(
        HydroponicSystem, on_delete=models.CASCADE, related_name="measurements", db_index=True
    )
    ph = models.FloatField()
    temperature = models.FloatField()
    tds = models.IntegerField()
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)

    def __str__(self):
        return (
            f"Measurement for {self.system.name} | "
            f"pH: {self.ph}, Temp: {self.temperature}°C, "
            f"TDS: {self.tds} ppm"
        )

    class Meta:
        ordering = ["-timestamp"]
        indexes = [
            models.Index(fields=["timestamp"]),
            models.Index(fields=["system", "timestamp"]),
        ]
