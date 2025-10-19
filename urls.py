# utility_cis/urls.py
from django.contrib import admin
from django.urls import path, include
from rest_framework import routers
from metering.views import MeterViewSet
from consumers.views import ConsumerViewSet
from billing.views import BillingViewSet
from vendors.views import VendorViewSet

router = routers.DefaultRouter()
router.register(r"meters", MeterViewSet)
router.register(r"consumers", ConsumerViewSet)
router.register(r"billing", BillingViewSet)
router.register(r"vendors", VendorViewSet)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include(router.urls)),
    path("api/auth/", include("rest_framework.urls")),  # browsable auth
]
