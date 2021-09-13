from django.conf.urls import url
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework import permissions

from drf_yasg.views import get_schema_view
from drf_yasg import openapi

from .views import LinkViewSet

router = DefaultRouter()
router.register(r'links', LinkViewSet, basename='links')


schema_view = get_schema_view(
   openapi.Info(
      title="LinkShortener API",
      default_version='v1',
      description="Documentation for Rest API of the LinkShortener application.",
   ),
   public=True,
   permission_classes=[permissions.AllowAny],
)


urlpatterns = [
    path('', include(router.urls), name='api'),
    #url(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    url(r'^swagger/$', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
]
