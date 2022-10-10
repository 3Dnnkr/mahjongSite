from django.urls import path
from . import views

app_name = 'kntu'

urlpatterns = [
    path('preview/', views.paifu_preview, name='preview'),
    path('create_exam/', views.CreateExam.as_view(), name='create_exam'),
    path('update_exam/<uuid:pk>/', views.UpdateExam.as_view(), name='update_exam'),
    path('delete_exam/<uuid:pk>/', views.delete_exam, name='delete_exam'),
    path('index/', views.Index.as_view(), name='index'),
    path('exam/<uuid:pk>/', views.Detail.as_view(), name='detail'),
    path('create_comment/<int:pk>/', views.CreateComment.as_view(), name="create_comment"),
    path('update_comment/<int:pk>/', views.UpdateComment.as_view(), name='update_comment'),
    path('create_comment_like/<int:pk>/', views.create_comment_like, name='create_comment_like'),
]