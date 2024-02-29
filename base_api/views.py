import json
from rest_framework.views import APIView
from rest_framework.response import Response
from base.filters import ShiftRequestFilter
from base.views import is_reportingmanger, shift_request_export

from employee_api.methods import groupby_queryset
from .serializers import CompanySerializer, DepartmentSerializer, EmployeeShiftDaySerializer, EmployeeShiftScheduleSerializer, EmployeeShiftSerializer, JobPositionSerializer, JobRoleSerializer, RotatingShiftAssignSerializer, RotatingShiftSerializer, RotatingWorkTypeAssignSerializer, RotatingWorkTypeSerializer, ShiftRequestSerializer, WorkTypeRequestSerializer, WorkTypeSerializer
from base.models import Department, EmployeeShift, EmployeeShiftDay, EmployeeShiftSchedule, JobPosition, JobRole, Company, RotatingShift, RotatingShiftAssign, RotatingWorkType, RotatingWorkTypeAssign, ShiftRequest, WorkType, WorkTypeRequest
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend


def object_check(cls, pk):
    try:
        obj = cls.objects.get(id=pk)
        return obj
    except cls.DoesNotExist:
        return None


def object_delete(cls, pk):
    try:
        cls.objects.get(id=pk).delete()
        return "", 200
    except Exception as e:
        return {"error": str(e)}, 400


class JobPositionView(APIView):
    serializer_class = JobPositionSerializer
    # #permission_classes = [IsAuthenticated]

    def get(self, request, pk=None):
        if pk:
            job_position = object_check(JobPosition, pk)
            if job_position is None:
                return Response({"error": "Job position not found "}, status=404)
            serializer = self.serializer_class(job_position)
            return Response(serializer.data, status=200)

        job_positions = JobPosition.objects.all()
        paginater = PageNumberPagination()
        page = paginater.paginate_queryset(job_positions, request)
        serializer = self.serializer_class(page, many=True)
        return paginater.get_paginated_response(serializer.data)

    def put(self, request, pk):
        job_position = object_check(JobPosition, pk)
        if job_position is None:
            return Response({"error": "Job position not found "}, status=404)
        serializer = self.serializer_class(job_position, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=200)
        return Response(serializer.errors, status=400)

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

    def delete(self, request, pk):
        job_position = object_check(JobPosition, pk)
        if job_position is None:
            return Response({"error": "Job position not found "}, status=404)
        response, status_code = object_delete(JobPosition, pk)
        return Response(response, status=status_code)


class DepartmentView(APIView):
    serializer_class = DepartmentSerializer
    # permission_classes = [IsAuthenticated]

    def get(self, request, pk=None):
        if pk:
            department = object_check(Department, pk)
            if department is None:
                return Response({"error": "Department not found "}, status=404)
            serializer = self.serializer_class(department)
            return Response(serializer.data, status=200)

        departments = Department.objects.all()
        paginator = PageNumberPagination()
        page = paginator.paginate_queryset(departments, request)
        serializer = self.serializer_class(page, many=True)
        return paginator.get_paginated_response(serializer.data)

    def put(self, request, pk):
        department = object_check(Department, pk)
        if department is None:
            return Response({"error": "Department not found "}, status=404)
        serializer = self.serializer_class(department, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=200)
        return Response(serializer.errors, status=400)

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

    def delete(self, request, pk):
        department = object_check(Department, pk)
        if department is None:
            return Response({"error": "Department not found "}, status=404)
        response, status_code = object_delete(Department, pk)
        return Response(response, status=status_code)


class JobRoleView(APIView):
    serializer_class = JobRoleSerializer
    # permission_classes = [IsAuthenticated]

    def get(self, request, pk=None):
        if pk:
            job_role = object_check(JobRole, pk)
            if job_role is None:
                return Response({"error": "Job role not found "}, status=404)
            serializer = self.serializer_class(job_role)
            return Response(serializer.data, status=200)

        job_roles = JobRole.objects.all()
        paginator = PageNumberPagination()
        page = paginator.paginate_queryset(job_roles, request)
        serializer = self.serializer_class(page, many=True)
        return paginator.get_paginated_response(serializer.data)

    def put(self, request, pk):
        job_role = object_check(JobRole, pk)
        if job_role is None:
            return Response({"error": "Job role not found "}, status=404)
        serializer = self.serializer_class(job_role, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=200)
        return Response(serializer.errors, status=400)

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

    def delete(self, request, pk):
        job_role = object_check(JobRole, pk)
        if job_role is None:
            return Response({"error": "Job role not found "}, status=404)
        response, status_code = object_delete(JobRole, pk)
        return Response(response, status=status_code)


class CompanyView(APIView):
    serializer_class = CompanySerializer
    # #permission_classes = [IsAuthenticated]

    def get(self, request, pk=None):
        if pk:
            company = object_check(Company, pk)
            if company is None:
                return Response({"error": "Company not found "}, status=404)
            serializer = self.serializer_class(company)
            return Response(serializer.data, status=200)

        companies = Company.objects.all()
        paginator = PageNumberPagination()
        page = paginator.paginate_queryset(companies, request)
        serializer = self.serializer_class(page, many=True)
        return paginator.get_paginated_response(serializer.data)

    def put(self, request, pk):
        company = object_check(Company, pk)
        if company is None:
            return Response({"error": "Company not found "}, status=404)
        serializer = self.serializer_class(company, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=200)
        return Response(serializer.errors, status=400)

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

    def delete(self, request, pk):
        company = object_check(Company, pk)
        if company is None:
            return Response({"error": "Company not found "}, status=400)
        response, status_code = object_delete(Company, pk)
        return Response(response, status=status_code)


class WorkTypeView(APIView):
    serializer_class = WorkTypeSerializer

    def get(self, request, pk=None):
        if pk:
            work_type = object_check(WorkType, pk)
            if work_type is None:
                return Response({"error": "WorkType not found"}, status=404)
            serializer = self.serializer_class(work_type)
            return Response(serializer.data, status=200)

        work_types = WorkType.objects.all()
        serializer = self.serializer_class(work_types, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=200)
        return Response(serializer.errors, status=400)

    def put(self, request, pk):
        work_type = object_check(WorkType, pk)
        if work_type is None:
            return Response({"error": "WorkType not found"}, status=404)
        serializer = self.serializer_class(work_type, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=200)
        return Response(serializer.errors, status=400)

    def delete(self, request, pk):
        work_type = object_check(WorkType, pk)
        if work_type is None:
            return Response({"error": "WorkType not found"}, status=404)
        response, status_code = object_delete(WorkType, pk)
        return Response(response, status=status_code)


class RotatingWorkTypeView(APIView):
    serializer_class = RotatingWorkTypeSerializer

    def get(self, request, pk=None):
        if pk:
            rotating_work_type = object_check(RotatingWorkType, pk)
            if rotating_work_type is None:
                return Response({"error": "RotatingWorkType not found"}, status=404)
            serializer = self.serializer_class(rotating_work_type)
            return Response(serializer.data, status=200)

        rotating_work_types = RotatingWorkType.objects.all()
        serializer = self.serializer_class(rotating_work_types, many=True)
        return Response(serializer.data, status=200)

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

    def put(self, request, pk):
        rotating_work_type = object_check(RotatingWorkType, pk)
        if rotating_work_type is None:
            return Response({"error": "RotatingWorkType not found"}, status=404)
        serializer = self.serializer_class(
            rotating_work_type, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=200)
        return Response(serializer.errors, status=400)

    def delete(self, request, pk):
        rotating_work_type = object_check(RotatingWorkType, pk)
        if rotating_work_type is None:
            return Response({"error": "RotatingWorkType not found"}, status=404)
        response, status_code = object_delete(RotatingWorkType, pk)
        return Response(response, status=status_code)


class RotatingWorkTypeAssignView(APIView):
    serializer_class = RotatingWorkTypeAssignSerializer

    def get(self, request, pk=None):
        if pk:
            rotating_work_type_assign = object_check(
                RotatingWorkTypeAssign, pk)
            if rotating_work_type_assign is None:
                return Response({"error": "RotatingWorkTypeAssign not found"}, status=404)
            serializer = self.serializer_class(rotating_work_type_assign)
            return Response(serializer.data, status=200)

        rotating_work_type_assigns = RotatingWorkTypeAssign.objects.all()
        serializer = self.serializer_class(
            rotating_work_type_assigns, many=True)
        return Response(serializer.data, status=200)

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

    def put(self, request, pk):
        rotating_work_type_assign = object_check(RotatingWorkTypeAssign, pk)
        if rotating_work_type_assign is None:
            return Response({"error": "RotatingWorkTypeAssign not found"}, status=404)
        serializer = self.serializer_class(
            rotating_work_type_assign, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=200)
        return Response(serializer.errors, status=400)

    def delete(self, request, pk):
        rotating_work_type_assign = object_check(RotatingWorkTypeAssign, pk)
        if rotating_work_type_assign is None:
            return Response({"error": "RotatingWorkTypeAssign not found"}, status=404)
        response, status_code = object_delete(RotatingWorkTypeAssign, pk)
        return Response(response, status=status_code)


class EmployeeShiftDayView(APIView):
    serializer_class = EmployeeShiftDaySerializer

    def get(self, request, pk=None):
        if pk:
            employee_shift_day = object_check(EmployeeShiftDay, pk)
            if employee_shift_day is None:
                return Response({"error": "EmployeeShiftDay not found"}, status=404)
            serializer = self.serializer_class(employee_shift_day)
            return Response(serializer.data, status=200)

        employee_shift_days = EmployeeShiftDay.objects.all()
        serializer = self.serializer_class(employee_shift_days, many=True)
        return Response(serializer.data, status=200)

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

    def put(self, request, pk):
        employee_shift_day = object_check(EmployeeShiftDay, pk)
        if employee_shift_day is None:
            return Response({"error": "EmployeeShiftDay not found"}, status=404)
        serializer = self.serializer_class(
            employee_shift_day, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=200)
        return Response(serializer.errors, status=400)

    def delete(self, request, pk):
        employee_shift_day = object_check(EmployeeShiftDay, pk)
        if employee_shift_day is None:
            return Response({"error": "EmployeeShiftDay not found"}, status=404)
        response, status_code = object_delete(EmployeeShiftDay, pk)
        return Response(response, status=status_code)


class EmployeeShiftView(APIView):
    serializer_class = EmployeeShiftSerializer

    def get(self, request, pk=None):
        if pk:
            employee_shift = object_check(EmployeeShift, pk)
            if employee_shift is None:
                return Response({"error": "EmployeeShift not found"}, status=404)
            serializer = self.serializer_class(employee_shift)
            return Response(serializer.data, status=200)

        employee_shifts = EmployeeShift.objects.all()
        serializer = self.serializer_class(employee_shifts, many=True)
        return Response(serializer.data, status=200)

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

    def put(self, request, pk):
        employee_shift = object_check(EmployeeShift, pk)
        if employee_shift is None:
            return Response({"error": "EmployeeShift not found"}, status=404)
        serializer = self.serializer_class(employee_shift, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=200)
        return Response(serializer.errors, status=400)

    def delete(self, request, pk):
        employee_shift = object_check(EmployeeShift, pk)
        if employee_shift is None:
            return Response({"error": "EmployeeShift not found"}, status=404)
        response, status_code = object_delete(EmployeeShift, pk)
        return Response(response, status=status_code)


class EmployeeShiftScheduleView(APIView):
    serializer_class = EmployeeShiftScheduleSerializer

    def get(self, request, pk=None):
        if pk:
            employee_shift_schedule = object_check(EmployeeShiftSchedule, pk)
            if employee_shift_schedule is None:
                return Response({"error": "EmployeeShiftSchedule not found"}, status=404)
            serializer = self.serializer_class(employee_shift_schedule)
            return Response(serializer.data, status=200)

        employee_shift_schedules = EmployeeShiftSchedule.objects.all()
        serializer = self.serializer_class(employee_shift_schedules, many=True)
        return Response(serializer.data, status=200)

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

    def put(self, request, pk):
        employee_shift_schedule = object_check(EmployeeShiftSchedule, pk)
        if employee_shift_schedule is None:
            return Response({"error": "EmployeeShiftSchedule not found"}, status=404)
        serializer = self.serializer_class(
            employee_shift_schedule, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=200)
        return Response(serializer.errors, status=400)

    def delete(self, request, pk):
        employee_shift_schedule = object_check(EmployeeShiftSchedule, pk)
        if employee_shift_schedule is None:
            return Response({"error": "EmployeeShiftSchedule not found"}, status=404)
        response, status_code = object_delete(EmployeeShiftSchedule, pk)
        return Response(response, status=status_code)


class RotatingShiftView(APIView):
    serializer_class = RotatingShiftSerializer

    def get(self, request, pk=None):
        if pk:
            rotating_shift = object_check(RotatingShift, pk)
            if rotating_shift is None:
                return Response({"error": "RotatingShift not found"}, status=404)
            serializer = self.serializer_class(rotating_shift)
            return Response(serializer.data, status=200)

        rotating_shifts = RotatingShift.objects.all()
        serializer = self.serializer_class(rotating_shifts, many=True)
        return Response(serializer.data, status=200)

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

    def put(self, request, pk):
        rotating_shift = object_check(RotatingShift, pk)
        if rotating_shift is None:
            return Response({"error": "RotatingShift not found"}, status=404)
        serializer = self.serializer_class(rotating_shift, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=200)
        return Response(serializer.errors, status=400)

    def delete(self, request, pk):
        rotating_shift = object_check(RotatingShift, pk)
        if rotating_shift is None:
            return Response({"error": "RotatingShift not found"}, status=404)
        response, status_code = object_delete(RotatingShift, pk)
        return Response(response, status=status_code)


class RotatingShiftAssignView(APIView):
    serializer_class = RotatingShiftAssignSerializer

    def get(self, request, pk=None):
        if pk:
            rotating_shift_assign = object_check(RotatingShiftAssign, pk)
            if rotating_shift_assign is None:
                return Response({"error": "RotatingShiftAssign not found"}, status=404)
            serializer = self.serializer_class(rotating_shift_assign)
            return Response(serializer.data, status=200)

        rotating_shift_assigns = RotatingShiftAssign.objects.all()
        serializer = self.serializer_class(rotating_shift_assigns, many=True)
        return Response(serializer.data, status=200)

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

    def put(self, request, pk):
        rotating_shift_assign = object_check(RotatingShiftAssign, pk)
        if rotating_shift_assign is None:
            return Response({"error": "RotatingShiftAssign not found"}, status=404)
        serializer = self.serializer_class(
            rotating_shift_assign, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=200)
        return Response(serializer.errors, status=400)

    def delete(self, request, pk):
        rotating_shift_assign = object_check(RotatingShiftAssign, pk)
        if rotating_shift_assign is None:
            return Response({"error": "RotatingShiftAssign not found"}, status=404)
        response, status_code = object_delete(RotatingShiftAssign, pk)
        return Response(response, status=status_code)


class WorkTypeRequestView(APIView):
    serializer_class = WorkTypeRequestSerializer

    def get(self, request, pk=None):
        if pk:
            work_type_request = object_check(WorkTypeRequest, pk)
            if work_type_request is None:
                return Response({"error": "WorkTypeRequest not found"}, status=404)
            serializer = self.serializer_class(work_type_request)
            return Response(serializer.data, status=200)

        work_type_requests = WorkTypeRequest.objects.all()
        serializer = self.serializer_class(work_type_requests, many=True)
        return Response(serializer.data, status=200)

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

    def put(self, request, pk):
        work_type_request = object_check(WorkTypeRequest, pk)
        if work_type_request is None:
            return Response({"error": "WorkTypeRequest not found"}, status=404)
        serializer = self.serializer_class(
            work_type_request, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=200)
        return Response(serializer.errors, status=400)

    def delete(self, request, pk):
        work_type_request = object_check(WorkTypeRequest, pk)
        if work_type_request is None:
            return Response({"error": "WorkTypeRequest not found"}, status=404)
        response, status_code = object_delete(WorkTypeRequest, pk)
        return Response(response, status=status_code)


class ShiftRequestView(APIView):
    serializer_class = ShiftRequestSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = ShiftRequestFilter

    def get(self, request, pk=None):
        if pk:
            shift_request = object_check(ShiftRequest, pk)
            if shift_request is None:
                return Response({"error": "ShiftRequest not found"}, status=404)
            serializer = self.serializer_class(shift_request)
            return Response(serializer.data, status=200)

        shift_requests = ShiftRequest.objects.all()
        shift_requests_filter_queryset = self.filterset_class(
            request.GET, queryset=shift_requests).qs
        paginator = PageNumberPagination()
        page = paginator.paginate_queryset(
            shift_requests_filter_queryset, request)
        serializer = self.serializer_class(page, many=True)
        return paginator.get_paginated_response(serializer.data)

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

    def put(self, request, pk):
        shift_request = object_check(ShiftRequest, pk)
        if shift_request is None:
            return Response({"error": "ShiftRequest not found"}, status=404)
        serializer = self.serializer_class(shift_request, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=200)
        return Response(serializer.errors, status=400)

    def delete(self, request, pk):
        shift_request = object_check(ShiftRequest, pk)
        if shift_request is None:
            return Response({"error": "ShiftRequest not found"}, status=404)
        response, status_code = object_delete(ShiftRequest, pk)
        return Response(response, status=status_code)


class RotatingWorkTypeView(APIView):
    serializer_class = RotatingWorkTypeSerializer

    def get(self, request, pk=None):
        if pk:
            rotating_work_type = object_check(RotatingWorkType, pk)
            if rotating_work_type is None:
                return Response({"error": "RotatingWorkType not found"}, status=404)
            serializer = self.serializer_class(rotating_work_type)
            return Response(serializer.data, status=200)

        rotating_work_types = RotatingWorkType.objects.all()
        serializer = self.serializer_class(rotating_work_types, many=True)
        return Response(serializer.data, status=200)

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

    def put(self, request, pk):
        rotating_work_type = object_check(RotatingWorkType, pk)
        if rotating_work_type is None:
            return Response({"error": "RotatingWorkType not found"}, status=404)
        serializer = self.serializer_class(
            rotating_work_type, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=200)
        return Response(serializer.errors, status=400)

    def delete(self, request, pk):
        rotating_work_type = object_check(RotatingWorkType, pk)
        if rotating_work_type is None:
            return Response({"error": "RotatingWorkType not found"}, status=404)
        response, status_code = object_delete(RotatingWorkType, pk)
        return Response(response, status=status_code)


class ShiftRequestGroupByView(APIView):
    def get(self, request, class_name):
        group_by_fields = {"employee_id", "requested_date",
                           "shift_id",  "previous_shift_id"}
        field_name = class_name if class_name in group_by_fields else None
        if field_name is None:
            return Response({"error": "Not found"}, status=400)
        model = ShiftRequest
        response = groupby_queryset(
            model, field_name, request)
        return Response(response.data, status=200)


class ShiftRequestApproveView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        shift_request = ShiftRequest.objects.get(id=pk)
        if (
            is_reportingmanger(request, shift_request)
            or request.user.has_perm("approve_shiftrequest")
            or request.user.has_perm("change_shiftrequest")
            and not shift_request.approved
        ):
            """
            here the request will be approved, can send mail right here
            """
            if not shift_request.is_any_request_exists():
                shift_request.approved = True
                shift_request.canceled = False
                shift_request.save()
                return Response({"status": "success"}, status=200)
        return Response({"error": "No permission "}, status=400)


class ShiftRequestBulkApproveView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        ids = request.data["ids"]
        length = len(ids)
        count = 0
        for id in ids:
            shift_request = ShiftRequest.objects.get(id=id)
            if (
                is_reportingmanger(request, shift_request)
                or request.user.has_perm("approve_shiftrequest")
                or request.user.has_perm("change_shiftrequest")
                and not shift_request.approved
            ):
                """
                here the request will be approved, can send mail right here
                """
                shift_request.approved = True
                shift_request.canceled = False
                employee_work_info = shift_request.employee_id.employee_work_info
                employee_work_info.shift_id = shift_request.shift_id
                employee_work_info.save()
                shift_request.save()
                count += 1
        if length == count:
            return Response({"status": "success"}, status=200)
        return Response({"status": "failed"}, status=400)


class ShiftRequestCancelView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):

        shift_request = ShiftRequest.objects.get(id=pk)
        if (
            is_reportingmanger(request, shift_request)
            or request.user.has_perm("base.cancel_shiftrequest")
            or shift_request.employee_id == request.user.employee_get
            and shift_request.approved == False
        ):
            shift_request.canceled = True
            shift_request.approved = False
            shift_request.employee_id.employee_work_info.shift_id = (
                shift_request.previous_shift_id
            )
            shift_request.employee_id.employee_work_info.save()
            shift_request.save()
            return Response({"status": "success"}, status=200)
        return Response({"status": "failed"}, status=400)


class ShiftRequestBulkCancelView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        ids = request.data.get("ids", None)
        length = len(ids)
        count = 0
        for id in ids:
            shift_request = ShiftRequest.objects.get(id=id)
            if (
                is_reportingmanger(request, shift_request)
                or request.user.has_perm("base.cancel_shiftrequest")
                or shift_request.employee_id == request.user.employee_get
                and shift_request.approved == False
            ):
                shift_request.canceled = True
                shift_request.approved = False
                shift_request.employee_id.employee_work_info.shift_id = (
                    shift_request.previous_shift_id
                )
                shift_request.employee_id.employee_work_info.save()
                shift_request.save()
                count += 1
        if length == count:
            return Response({"status": "success"}, status=200)
        return Response({"status": "failed"}, status=400)


class ShiftRequestDeleteView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request,pk=None):
        if pk is None:
            try:
                ids = request.data["ids"]
                shift_requests = ShiftRequest.objects.filter(id__in=ids)
                shift_requests.delete()
            except Exception as e:
                return Response({"status":"failed","error":str(e)},status=400)
            return Response({"status":"success"},status=200)
        try:
            shift_request = ShiftRequest.objects.get(id=pk)
            shift_request.delete()
        except ShiftRequest.DoesNotExist:
            return Response({"status":"failed","error":"Shift request does not exists"},status=400)
        return Response({"status":"deleted"},status=200)


class ShiftRequestExportView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self,request):
        return shift_request_export(request)
