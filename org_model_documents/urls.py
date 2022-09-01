from django.conf.urls import url
from rest_framework import routers

from org_model_documents.api import DocumentCreateView

router = routers.SimpleRouter()

urlpatterns = [
    url(r"upload-documents", DocumentCreateView.as_view()),
]
