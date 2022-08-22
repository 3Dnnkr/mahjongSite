from django.urls import path
from . import views

app_name = 'user'

urlpatterns = [
    path('', views.UserIndex.as_view(), name='index'),
    path('login/', views.Login.as_view(), name='login'),
    path('logout/', views.Logout.as_view(), name='logout'),
    path('create/', views.UserCreate.as_view(), name='create'),
    path('detail/<int:pk>/', views.UserUpdate.as_view(), name='detail'),
    path('question/<int:pk>/', views.UserQuestionIndex.as_view(), name='question'),
]