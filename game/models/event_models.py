from django.db import models

class HistoricalEvent(models.Model):
    """Represents a historical event used in the trivia game."""
    event_description = models.CharField(max_length=255)
    event_year = models.IntegerField()
    category = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.event_description} ({self.start_year})"
