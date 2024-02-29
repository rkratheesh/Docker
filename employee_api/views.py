import base64
import pandas as pd
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.pagination import PageNumberPagination
from django.http import FileResponse, Http404, HttpResponse
from employee.filters import EmployeeFilter
from employee.models import Employee, EmployeeBankDetails, EmployeeWorkInformation
from employee.views import work_info_export, work_info_import
from employee_api.methods import groupby_queryset
from .serializers import EmployeeBankDetailsSerializer, EmployeeBulkUpdateSerializer, EmployeeSerializer, EmployeeWorkInformationSerializer
from django_filters.rest_framework import DjangoFilterBackend


class EmployeeAPIView(APIView):
    filter_backends = [DjangoFilterBackend]
    filterset_class = EmployeeFilter

    def get(self, request, pk=None):
        if pk:
            try:
                employee = Employee.objects.get(pk=pk)
            except Employee.DoesNotExist:
                return Response({"error": "Employee does not exist"}, status=status.HTTP_404_NOT_FOUND)

            serializer = EmployeeSerializer(employee)
            return Response(serializer.data)

        paginator = PageNumberPagination()
        employees_queryset = Employee.objects.all()
        employees_filter_queryset = self.filterset_class(
            request.GET, queryset=employees_queryset).qs
        page = paginator.paginate_queryset(employees_filter_queryset, request)
        serializer = EmployeeSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)

    def post(self, request):
        serializer = EmployeeSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk):
        try:
            employee = Employee.objects.get(pk=pk)
        except Employee.DoesNotExist:
            return Response({"error": "Employee does not exist"}, status=status.HTTP_404_NOT_FOUND)

        serializer = EmployeeSerializer(employee, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        try:
            employee = Employee.objects.get(pk=pk)
        except Employee.DoesNotExist:
            return Response({"error": "Employee does not exist"}, status=status.HTTP_404_NOT_FOUND)

        employee.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class EmployeeBankDetailsAPIView(APIView):

    def get(self, request, pk=None):

        if pk:
            try:
                bank_detail = EmployeeBankDetails.objects.get(pk=pk)
            except EmployeeBankDetails.DoesNotExist:
                return Response({"error": "Bank details do not exist"}, status=status.HTTP_404_NOT_FOUND)

            serializer = EmployeeBankDetailsSerializer(bank_detail)
            return Response(serializer.data)
        paginator = PageNumberPagination()
        employee_bank_details = EmployeeBankDetails.objects.all()
        page = paginator.paginate_queryset(employee_bank_details, request)
        serializer = EmployeeBankDetailsSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)

    def post(self, request):
        serializer = EmployeeBankDetailsSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk):
        try:
            bank_detail = EmployeeBankDetails.objects.get(pk=pk)
        except EmployeeBankDetails.DoesNotExist:
            return Response({"error": "Bank details do not exist"}, status=status.HTTP_404_NOT_FOUND)

        serializer = EmployeeBankDetailsSerializer(
            bank_detail, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        try:
            bank_detail = EmployeeBankDetails.objects.get(pk=pk)
        except EmployeeBankDetails.DoesNotExist:
            return Response({"error": "Bank details do not exist"}, status=status.HTTP_404_NOT_FOUND)

        bank_detail.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class EmployeeWorkInformationAPIView(APIView):
    def get(self, request, pk=None):
        if pk:
            try:
                work_info = EmployeeWorkInformation.objects.get(pk=pk)
                serializer = EmployeeWorkInformationSerializer(work_info)
                return Response(serializer.data)
            except EmployeeWorkInformation.DoesNotExist:
                raise Http404
        paginator = PageNumberPagination()
        work_info = EmployeeWorkInformation.objects.all()
        page = paginator.paginate_queryset(work_info, request)
        serializer = EmployeeWorkInformationSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)

    def post(self, request):
        serializer = EmployeeWorkInformationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk):
        try:
            work_info = EmployeeWorkInformation.objects.get(pk=pk)
        except EmployeeWorkInformation.DoesNotExist:
            raise Http404
        serializer = EmployeeWorkInformationSerializer(
            work_info, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        try:
            work_info = EmployeeWorkInformation.objects.get(pk=pk)
        except EmployeeWorkInformation.DoesNotExist:
            raise Http404
        work_info.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class EmployeeGroupByView(APIView):
    def get(self, request, class_name):
        group_by_fields = {"department_id", "company_id",
                          "job_position_id","job_role_id", "reporting_manager_id"}
        field_name =class_name if class_name in group_by_fields else None
        if field_name is None:
            return Response({"error":"Not found"},status=400)
        model = EmployeeWorkInformation
        response = groupby_queryset(
            model, field_name, request)
        return Response(response.data, status=200)


class EmployeeWorkInfoExportView(APIView):
    def get(self, request):
        return work_info_export(request)


class EmployeeWorkInfoImportView(APIView):
    def get(self, request):
        return work_info_import(request)


class EmployeeBulkUpdateView(APIView):
    def put(self, request):
        employee_ids = request.data.get('ids', [])
        employees = Employee.objects.filter(id__in=employee_ids)
        employee_work_info = EmployeeWorkInformation.objects.filter(
            employee_id__in=employees)
        employee_data = request.data.get('employee_data', {})
        work_info_data = request.data.get("employee_work_info", {})

        fields_to_remove = [
            "badge_id",
            "employee_first_name",
            "employee_last_name",
            "is_active",
            "email",
            "phone",
            "employee_bank_details__account_number",
        ]
        for field in fields_to_remove:
            employee_data.pop(field, None)
            work_info_data.pop(field, None)

        try:
            employees.update(**employee_data)
            employee_work_info.update(**work_info_data)
        except Exception as e:
            return Response({"error": str(e)}, status=400)
        return Response({"status": "success"}, status=200)
