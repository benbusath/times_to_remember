from django.db import models
from django.contrib.auth.models import User
from game.models.event_models import HistoricalEvent

class Player(models.Model):
    """Represents a player participating in the game."""
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    username = models.CharField(max_length=50, unique=True)
    remaining_bounds = models.JSONField(default=list)  # Store player's bounds individually
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.username


class GameSession(models.Model):
    """Represents a single game session for a group of players."""
    players = models.ManyToManyField(Player)
    current_event = models.ForeignKey(HistoricalEvent, on_delete=models.SET_NULL, null=True, blank=True)
    category = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Game for {', '.join([player.username for player in self.players.all()])} - {self.category}"
