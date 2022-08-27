from django.urls import path
from . import views

app_name = 'user'

urlpatterns = [
    path('', views.Index.as_view(), name='index'),
    path('login/', views.Login.as_view(), name='login'),
    path('logout/', views.Logout.as_view(), name='logout'),
    path('create/', views.UserCreate.as_view(), name='create'),
    path('<int:pk>/detail/', views.UserDetail.as_view(), name='detail'),
    path('<int:pk>/question/', views.UserQuestion.as_view(), name='question'),
    path('<int:pk>/bookmark/', views.UserBookmark.as_view(), name='bookmark'),
    path('<int:pk>/history/', views.UserHistory.as_view(), name='history'),
]