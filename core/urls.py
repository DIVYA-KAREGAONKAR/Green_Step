from django.urls import path
from django.contrib.auth import views as auth_views  # <--- ADD THIS LINE
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('log-activity/', views.log_activity, name='log_activity'),
    path('trends/', views.monthly_trends, name='trends'),
    path('history/', views.history, name='history'),
    
    # Auth Routes
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
]