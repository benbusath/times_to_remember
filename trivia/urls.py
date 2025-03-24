# trivia/urls.py
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),         # Admin site URL
    path('', include('game.urls')),          # Include URLs from the 'game' app
]