from django.urls import path
from . import views

app_name = 'nnkr'

urlpatterns = [
    path('', views.Index.as_view(),name='index'),
    path('detail/<int:pk>/', views.Detail.as_view(), name='detail'),
    path('create_question/', views.create_question, name='create_question'),
    path('create_comment/<int:pk>/', views.CreateComment.as_view(), name='create_comment'),
    path('vote/<int:pk>', views.vote, name="vote"),
    path('create_tag/<int:pk>/', views.CreateTag.as_view(), name='create_tag'),
    path('delete_tag/<int:q_pk>/<int:t_pk>/', views.delete_tag, name='delete_tag'),
    path('tag_question/<int:pk>/', views.TagQuestion.as_view(), name='tag_question'),
    path('bookmark/<int:q_pk>/', views.create_bookmark, name='bookmark'),
]
