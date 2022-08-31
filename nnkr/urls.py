from django.urls import path
from . import views

app_name = 'nnkr'

urlpatterns = [
    path('', views.Top.as_view(),name='top'),
    path('index/', views.Index.as_view(),name='index'),
    path('tag_question/<int:pk>/', views.TagQuestion.as_view(), name='tag_question'),
    path('create_question/', views.create_question, name='create_question'),
    path('question/<int:pk>/', views.Detail.as_view(), name='detail'),
    path('question/<int:pk>/create_comment/', views.CreateComment.as_view(), name='create_comment'),
    path('question/<int:pk>/create_comment_liek/<int:c_pk>/', views.create_comment_like, name='create_comment_like'),
    path('question/<int:pk>/vote/', views.vote, name="vote"),
    path('question/<int:pk>/secret_vote/', views.secret_vote, name="secret_vote"),
    path('question/<int:pk>/create_tag/', views.CreateTag.as_view(), name='create_tag'),
    path('question/<int:pk>/delete_tag/<int:t_pk>/', views.delete_tag, name='delete_tag'),
    path('question/<int:pk>/create_bookmark/', views.create_bookmark, name='create_bookmark'),
    path('question/<int:pk>/delete_bookmark/', views.delete_bookmark, name='delete_bookmark'),
]
