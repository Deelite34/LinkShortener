from django.urls import path
from . import views

urlpatterns = [
    path('get/', views.get_view),
    path('post/', views.post_view)
]
