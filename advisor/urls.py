from django.urls import path, include
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path('start-recording/', views.start_recording, name='start_recording'),
    path('stop-recording/', views.stop_recording, name='stop_recording'),
    path('analyze-gameplay/', views.analyze_gameplay, name='analyze_gameplay'),
]
