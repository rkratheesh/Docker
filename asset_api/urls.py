from django.urls import re_path
from .views import (
    AssetCategoryAPIView,
    AssetLotAPIView,
    AssetAPIView,
    AssetAssignmentAPIView,
    AssetRequestAPIView
)

urlpatterns = [
    re_path(r'^asset-categories/(?P<pk>\d+)?$', AssetCategoryAPIView.as_view(), name='asset-category-detail'),
    re_path(r'^asset-lots/(?P<pk>\d+)?$', AssetLotAPIView.as_view(), name='asset-lot-detail'),
    re_path(r'^assets/(?P<pk>\d+)?$', AssetAPIView.as_view(), name='asset-detail'),
    re_path(r'^asset-assignments/(?P<pk>\d+)?$', AssetAssignmentAPIView.as_view(), name='asset-assignment-detail'),
    re_path(r'^asset-requests/(?P<pk>\d+)?$', AssetRequestAPIView.as_view(), name='asset-request-detail'),
]