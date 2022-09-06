from django.urls import path
from . import views

app_name = 'nnkr'

urlpatterns = [
    path('', views.Top.as_view(),name='top'),
    path('index/', views.Index.as_view(),name='index'),
    path('tag_index/', views.TagIndex.as_view(),name='tag_index'),
    path('tag/<int:pk>/', views.TagQuestion.as_view(), name='tag_question'),
    path('faq/', views.FAQ.as_view(),name='faq'),
    path('create_lobbychat/', views.CreateLobbychat.as_view(), name='create_lobbychat'),
    path('create_question/', views.CreateQuestion.as_view(), name='create_question'),
    path('delete_question/<int:pk>/', views.delete_question, name='delete_question'),
    path('question/<int:pk>/', views.Detail.as_view(), name='detail'),
    path('question/<int:pk>/create_choice/', views.CreateChoice.as_view(), name='create_choice'),
    path('question/<int:pk>/create_comment/', views.CreateComment.as_view(), name='create_comment'),
    path('question/<int:q_pk>/update_comment/<int:pk>/', views.UpdateComment.as_view(), name='update_comment'),
    path('question/<int:pk>/create_comment_liek/<int:c_pk>/', views.create_comment_like, name='create_comment_like'),
    path('question/<int:pk>/vote/<int:c_pk>/', views.vote, name="vote"),
    path('question/<int:pk>/secret_vote/<int:c_pk>/', views.secret_vote, name="secret_vote"),
    path('question/<int:pk>/create_tag/', views.CreateTag.as_view(), name='create_tag'),
    path('question/<int:pk>/delete_tag/<int:t_pk>/', views.delete_tag, name='delete_tag'),
    path('question/<int:pk>/create_bookmark/', views.create_bookmark, name='create_bookmark'),
    path('question/<int:pk>/delete_bookmark/', views.delete_bookmark, name='delete_bookmark'),
    path('question/<int:pk>/create_liker/', views.CreateLiker.as_view(), name='create_liker'),
    path('question/<int:pk>/delete_liker/', views.delete_liker, name='delete_liker'),
    path('question/<int:pk>/create_disliker/', views.CreateDisliker.as_view(), name='create_disliker'),
]
