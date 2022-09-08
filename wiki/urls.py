from django.urls import path
from . import views

app_name = 'wiki'

urlpatterns = [
    path('', views.Index.as_view(),name='index'),
    path('detail/<int:pk>/', views.Detail.as_view(),name='detail'),
    path('create_article/', views.CreateArticle.as_view(),name='create_article'),
]
