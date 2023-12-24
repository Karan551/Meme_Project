from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name="index"),  # Register User api
    path("login/", views.login, name="login"),  # Login api
    path("memes/", views.get_memes, name="memes"),
    path("logout/", views.logout, name="logout"),  # logout api
]
