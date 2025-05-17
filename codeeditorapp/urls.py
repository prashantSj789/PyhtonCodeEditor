from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='codeeditorapp'),
    path('run/', views.run_code, name='run_code'),
]