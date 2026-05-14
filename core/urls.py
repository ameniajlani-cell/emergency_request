from django.urls import path
from django.contrib.auth import views as auth_views

from .forms import LoginForm
from . import views

urlpatterns = [
    path('login/', auth_views.LoginView.as_view(
        template_name='login.html',
        authentication_form=LoginForm,
    ), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('', views.home, name='home'),
    path('create/', views.create_request, name='create_request'),
    path('update/<int:id>/', views.update_request, name='update_request'),
    path('delete/<int:id>/', views.delete_request, name='delete_request'),
    path('requesters/', views.requester_list, name='requester_list'),
    path('requesters/create/', views.requester_create, name='requester_create'),
    path('requesters/update/<int:id>/', views.requester_update, name='requester_update'),
    path('requesters/delete/<int:id>/', views.requester_delete, name='requester_delete'),
    path('emergency-types/', views.emergency_type_list, name='emergency_type_list'),
    path('emergency-types/create/', views.emergency_type_create, name='emergency_type_create'),
    path('emergency-types/update/<int:id>/', views.emergency_type_update, name='emergency_type_update'),
    path('emergency-types/delete/<int:id>/', views.emergency_type_delete, name='emergency_type_delete'),
    path('response-teams/', views.response_team_list, name='response_team_list'),
    path('response-teams/create/', views.response_team_create, name='response_team_create'),
    path('response-teams/update/<int:id>/', views.response_team_update, name='response_team_update'),
    path('response-teams/delete/<int:id>/', views.response_team_delete, name='response_team_delete'),
    path('assignments/', views.assignment_list, name='assignment_list'),
    path('assignments/create/', views.assignment_create, name='assignment_create'),
    path('assignments/update/<int:id>/', views.assignment_update, name='assignment_update'),
    path('assignments/delete/<int:id>/', views.assignment_delete, name='assignment_delete'),
]
