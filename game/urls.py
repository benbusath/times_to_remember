# game/urls.py
from django.urls import path
from . import views  # Import views from the current directory (game/views.py)

urlpatterns = [
    path('', views.index, name='index'),  # This maps to the index view in game/views.py
    # Add other URL patterns as needed for your game app
]