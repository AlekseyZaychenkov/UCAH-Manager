from django.urls import path
from workspace_editor.views import homeView
from django.contrib import admin
from django.conf.urls import include


urlpatterns = [
    path('home', homeView, name="home"),
]

