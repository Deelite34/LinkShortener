from django.urls import path
from .views import IndexView, RedirectView

urlpatterns = [
    path('', IndexView.as_view(), name="index"),
    path('l/<str:url_output>/', RedirectView.as_view(), name="redirect"),
]
