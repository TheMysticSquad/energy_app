from django.views.generic import TemplateView
from django.urls import path, include

urlpatterns = [
    path("api/", include("api.urls")),
    path("", TemplateView.as_view(template_name="index.html")),  # React app entry
]
