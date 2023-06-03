from django.urls import path
from rest_framework import routers

from . import views

router = routers.SimpleRouter()
router.register(r'tags', views.TagViewSet)
router.register(r'clients', views.ClientViewSet)
router.register(r'mailings', views.MailingViewSet)
urlpatterns = []

urlpatterns += router.urls
