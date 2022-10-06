from django.urls import path
from . import views

app_name = 'kntu'

urlpatterns = [
    path('paifu_preview/', views.paifu_preview, name='paifu_preview'),
]