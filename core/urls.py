from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('log-activity/', views.log_activity, name='log_activity'), 
    path('history/', views.history, name='history'),
    path('trends/', views.monthly_trends, name='trends'),
]