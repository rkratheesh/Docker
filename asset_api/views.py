from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from asset.models import (
    AssetCategory,
    AssetLot,
    Asset,
    AssetAssignment,
    AssetRequest
)
from .serializers import (
    AssetCategorySerializer,
    AssetLotSerializer,
    AssetSerializer,
    AssetAssignmentSerializer,
    AssetRequestSerializer
)
from rest_framework.pagination import PageNumberPagination


class AssetAPIView(APIView):
    def get(self, request, pk=None):
        if pk:
            asset = Asset.objects.get(pk=pk)
            serializer = AssetSerializer(asset)
            return Response(serializer.data)
        paginator = PageNumberPagination()
        assets = Asset.objects.all()
        page = paginator.paginate_queryset(assets, request)
        serializer = AssetSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)

    def post(self, request):
        serializer = AssetSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk):
        asset = Asset.objects.get(pk=pk)
        serializer = AssetSerializer(asset, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        asset = Asset.objects.get(pk=pk)
        asset.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class AssetCategoryAPIView(APIView):

    def get(self, request, pk=None):
        if pk:
            asset_category = AssetCategory.objects.get(pk=pk)
            serializer = AssetCategorySerializer(asset_category)
            return Response(serializer.data)
        paginator = PageNumberPagination()
        assets = AssetCategory.objects.all()
        page = paginator.paginate_queryset(assets, request)
        serializer = AssetCategorySerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)

    def post(self, request):
        serializer = AssetCategorySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk):
        asset_category = AssetCategory.objects.get(pk=pk)
        serializer = AssetCategorySerializer(asset_category, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        asset_category = AssetCategory.objects.get(pk=pk)
        asset_category.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class AssetLotAPIView(APIView):
    def get(self, request, pk=None):
        if pk:
            asset_lot = AssetLot.objects.get(pk=pk)
            serializer = AssetLotSerializer(asset_lot)
            return Response(serializer.data)
        paginator = PageNumberPagination()
        assets = AssetLot.objects.all()
        page = paginator.paginate_queryset(assets, request)
        serializer = AssetLotSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)

    def post(self, request):
        serializer = AssetLotSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk):
        asset_lot = AssetLot.objects.get(pk=pk)
        serializer = AssetLotSerializer(asset_lot, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        asset_lot = AssetLot.objects.get(pk=pk)
        asset_lot.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class AssetAssignmentAPIView(APIView):
    def get(self, request, pk=None):
        if pk:
            asset_assignment = AssetAssignment.objects.get(pk=pk)
            serializer = AssetAssignmentSerializer(asset_assignment)
            return Response(serializer.data)
        paginator = PageNumberPagination()
        assets = AssetAssignment.objects.all()
        page = paginator.paginate_queryset(assets, request)
        serializer = AssetAssignmentSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)

    def post(self, request):
        serializer = AssetAssignmentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk):
        asset_assignment = AssetAssignment.objects.get(pk=pk)
        serializer = AssetAssignmentSerializer(
            asset_assignment, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        asset_assignment = AssetAssignment.objects.get(pk=pk)
        asset_assignment.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class AssetRequestAPIView(APIView):
    def get(self, request, pk=None):
        if pk:
            asset_request = AssetRequest.objects.get(pk=pk)
            serializer = AssetRequestSerializer(asset_request)
            return Response(serializer.data)
        paginator = PageNumberPagination()
        assets = AssetRequest.objects.all()
        page = paginator.paginate_queryset(assets, request)
        serializer = AssetRequestSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)

    def post(self, request):
        serializer = AssetRequestSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk):
        asset_request = AssetRequest.objects.get(pk=pk)
        serializer = AssetRequestSerializer(asset_request, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        asset_request = AssetRequest.objects.get(pk=pk)
        asset_request.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
