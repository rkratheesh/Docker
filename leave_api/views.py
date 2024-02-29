from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .serializers import *
from leave.models import LeaveRequest
from rest_framework.pagination import PageNumberPagination
from django.http import Http404
from django.contrib.auth.models import AnonymousUser
from django.http import QueryDict


class EmployeeAvailableLeaveGetAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        employee = request.user.employee_get
        available_leave = employee.available_leave.all()
        paginator = PageNumberPagination()
        page = paginator.paginate_queryset(available_leave, request)
        serializer = GetAvailableLeaveTypeSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)


class EmployeeLeaveRequestGetCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]
        
    def get(self, request):
        employee = request.user.employee_get
        leave_request = employee.leaverequest_set.all()
        paginator = PageNumberPagination()
        page = paginator.paginate_queryset(leave_request, request)
        serializer = userLeaveRequestGetAllSerilaizer(page, many=True)
        return paginator.get_paginated_response(serializer.data)
    
    def post(self, request):
        employee_id = request.user.employee_get.id
        data = request.data
        if isinstance(data, QueryDict):
            data = data.dict()
        data['employee_id'] = employee_id
        data['end_date'] = data.get('start_date') if not data.get('end_date') else data.get('end_date')
        serializer = LeaveRequestCreateUpdateSerializer(data=data) 
        if serializer.is_valid(): 
            leave_request = serializer.save()
            return Response(userLeaveRequestGetAllSerilaizer(leave_request).data, status=201)
        return Response(serializer.errors, status=400)


class EmployeeLeaveRequestUpdateDeleteAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get_leave_request(self, request, pk):
        try:
            return LeaveRequest.objects.get(pk=pk, employee_id=request.user.employee_get)
        except LeaveRequest.DoesNotExist as e:
            raise serializers.ValidationError(e)
    
    def get(self, request, pk):
        leave_request = self.get_leave_request(request, pk)
        serializer = UserLeaveRequestGetSerilaizer(leave_request)
        return Response(serializer.data, status=200)

    
    def put(self, request, pk):
        leave_request = self.get_leave_request(request, pk)
        employee_id = request.user.employee_get
        if leave_request.status == 'requested' and leave_request.employee_id == employee_id:
            data = request.data
            if isinstance(data, QueryDict):
                data = data.dict()
            data['employee_id'] = employee_id.id
            data['end_date'] = data.get('start_date') if not data.get('end_date') else data.get('end_date')
            serializer = LeaveRequestCreateUpdateSerializer(leave_request, data=data)
            if serializer.is_valid(): 
                leave_request = serializer.save()
                return Response(UserLeaveRequestGetSerilaizer(leave_request).data, status=201)
            return Response(serializer.errors, status=400)
        raise serializers.ValidationError({"error":"Access Denied.."})
        
        
    def delete(self, request, pk):
        leave_request = self.get_leave_request(request, pk)
        employee_id = request.user.employee_get
        if leave_request.status == 'requested'and leave_request.employee_id == employee_id:
            leave_request.delete()
            return Response({"message":"Leave request deleted successfully.."}, status=200)
        raise serializers.ValidationError({"error":"Access Denied.."})


class LeaveTypeGetCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        queryset = LeaveType.objects.all()
        paginator = PageNumberPagination()
        page = paginator.paginate_queryset(queryset, request)
        serializer = LeaveTypeAllGetSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)

    def post(self, request):
        serializer = LeaveTypeGetCreateSerilaizer(data=request.data)  
        if serializer.is_valid(): 
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)
    

class LeaveTypeGetUpdateDeleteAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get_leave_type(self, pk):
        try:
            return LeaveType.objects.get(pk=pk)
        except LeaveType.DoesNotExist as e:
            raise serializers.ValidationError(e)
        
    def get(self, request, pk):
        leave_type = self.get_leave_type(pk)
        serializer = LeaveTypeGetCreateSerilaizer(leave_type)
        return Response(serializer.data, status=200)
    
    def put(self, request, pk):
        leave_type = self.get_leave_type(pk)  
        serializer = LeaveTypeGetCreateSerilaizer(leave_type, data=request.data)
        if serializer.is_valid(): 
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)
    
    def delete(self, request, pk):
        leave_type = self.get_leave_type(pk)
        leave_type.delete()
        return Response(status=201)


class LeaveAllocationRequestGetCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get_user(self, request):
        user = request.user
        if isinstance(user, AnonymousUser):
            raise Http404("AnonymousUser")
        return user


    def get(self, request):
        allocation_requests = LeaveAllocationRequest.objects.all()
        paginator = PageNumberPagination()
        page = paginator.paginate_queryset(allocation_requests, request)
        serializer = LeaveAllocationRequestGetSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)

    def post(self, request):
        data = request.data.dict()
        data['created_by'] = self.get_user(request).id
        serializer = LeaveAllocationRequestCreateSerializer(data=data)
        if serializer.is_valid():
            allocation_request = serializer.save()
            return Response(LeaveAllocationRequestGetSerializer(allocation_request).data, status=201)
        return Response(serializer.errors, status=400)
    

class LeaveAllocationRequestGetUpdateDeleteAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get_user(self, request):
        user = request.user
        if isinstance(user, AnonymousUser):
            raise Http404("AnonymousUser")
        return user

    def get_allocation_request(self, pk):
        try:
            return LeaveAllocationRequest.objects.get(pk=pk)
        except LeaveAllocationRequest.DoesNotExist as e:
            raise serializers.ValidationError(e)


    def get(self, request, pk):
        allocation_request = self.get_allocation_request(pk)
        serializer = LeaveAllocationRequestGetSerializer(allocation_request)
        return Response(serializer.data, status=200) 

    def put(self, request, pk):
        data = request.data.dict()
        data['created_by'] = self.get_user(request).id
        serializer = LeaveAllocationRequestCreateSerializer(data=data)
        if serializer.is_valid():
            allocation_request = serializer.save()
            return Response(LeaveAllocationRequestGetSerializer(allocation_request).data, status=201)
        return Response(serializer.errors, status=400)

    def delete(self, request, pk):
        allocation_request = self.get_allocation_request(pk)
        allocation_request.delete()
        return Response(status=200)


class AssignLeaveGetCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        available_leave = AvailableLeave.objects.all()
        paginator = PageNumberPagination()
        page = paginator.paginate_queryset(available_leave, request)
        serializer = AssignLeaveGetSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)
        

    def post(self, request):
        serializer = AssignLeaveCreateSerializer(data=request.data)
        if serializer.is_valid():
            employee_ids = serializer.validated_data.get('employee_ids')
            leave_type_ids = serializer.validated_data.get('leave_type_ids')
            print('employee_ids', employee_ids)
            print('leave_type_ids', leave_type_ids)
            for employee_id in employee_ids:
                for leave_type_id in leave_type_ids:
                    if not AvailableLeave.objects.filter(employee_id=employee_id, leave_type_id=leave_type_id).exists():
                        AvailableLeave.objects.create(employee_id=employee_id, leave_type_id=leave_type_id, available_days=leave_type_id.total_days)
            return Response(status=201)
        return Response(serializer.errors, status=400)
    

class AssignLeaveGetUpdateDeleteAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get_available_leave(self, pk):
        try:
            return AvailableLeave.objects.get(pk=pk)
        except AvailableLeave.DoesNotExist as e:
            raise serializers.ValidationError(e)

    def get(self, request, pk):
        available_leave = self.get_available_leave(pk)
        serializer = AssignLeaveGetSerializer(available_leave)
        return Response(serializer.data, status=200)
    
    def put(self, request, pk):
        available_leave = self.get_available_leave(pk)
        serializer = AvailableLeaveUpdateSerializer(available_leave, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(status=201)
        return Response(serializer.errors, status=400)

    def delete(self, request, pk):
        available_leave = self.get_available_leave(pk)
        available_leave.delete()
        return Response(status=200)


class LeaveRequestGetCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        leave_request = LeaveRequest.objects.all().order_by('-id')
        paginator = PageNumberPagination()
        page = paginator.paginate_queryset(leave_request, request)
        serializer = LeaveRequestGetAllSerilaizer(page, many=True)
        return paginator.get_paginated_response(serializer.data)

    def post(self, request):
        data = request.data
        if isinstance(data, QueryDict):
            data = data.dict()
        data['end_date'] = data.get('start_date') if not data.get('end_date') else data.get('end_date')
        serializer = LeaveRequestCreateUpdateSerializer(data=data)
        if serializer.is_valid():
            leave_request = serializer.save()
            return Response(LeaveRequestGetSerilaizer(leave_request).data,status=201)
        return Response(serializer.errors, status=400)
    

class LeaveRequestGetUpdateDeleteAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get_leave_request(self, pk):
        try:
            return LeaveRequest.objects.get(pk=pk)
        except LeaveRequest.DoesNotExist as e:
            raise serializers.ValidationError(e)

    def get(self, request, pk):
        leave_request = self.get_leave_request(pk)
        serializer = LeaveRequestGetSerilaizer(leave_request)
        return Response(serializer.data, status=200)

    def put(self, request, pk):
        leave_request = self.get_leave_request(pk)
        if leave_request.status == 'requested':
            data = request.data
            if isinstance(data, QueryDict):
                data = data.dict()
            data['end_date'] = data.get('start_date') if not data.get('end_date') else data.get('end_date')
            serializer = LeaveRequestCreateUpdateSerializer(leave_request, data=data)
            if serializer.is_valid(): 
                leave_request = serializer.save()
                return Response(UserLeaveRequestGetSerilaizer(leave_request).data, status=201)
            return Response(serializer.errors, status=400)
        raise serializers.ValidationError({"error":"Access Denied.."})

    def delete(self, request, pk):
        leave_request = self.get_leave_request(pk)
        if leave_request.status == 'requested':
            leave_request.delete()
            return Response(status=200)
        raise serializers.ValidationError({"error":"Access Denied.."})
    

class LeaveAllocationRequestGetCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        leave_allocation_request = LeaveAllocationRequest.objects.all().order_by('-id')
        paginator = PageNumberPagination()
        page = paginator.paginate_queryset(leave_allocation_request, request)
        serializer = LeaveAllocationRequestGetSerilaizer(page, many=True)
        return paginator.get_paginated_response(serializer.data)

    def post(self, request):
        serializer = LeaveAllocationRequestSerilaizer(data=request.data)
        if serializer.is_valid():
            allocation_request = serializer.save()
            allocation_request.created_by = request.user.employee_get
            allocation_request.save()
            return Response(LeaveAllocationRequestGetSerilaizer(allocation_request).data, status=201)
        return Response(serializer.errors, status=400)


class LeaveAllocationRequestGetUpdateDeleteAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get_leave_allocation_request(self, pk):
        try:
            return LeaveAllocationRequest.objects.get(pk=pk)
        except LeaveAllocationRequest.DoesNotExist as e:
            raise serializers.ValidationError(e)
    
    def get(self, request, pk):
        allocation_request = self.get_leave_allocation_request(pk)
        serializer = LeaveAllocationRequestGetSerilaizer(allocation_request)
        return Response(serializer.data, status=200)
    

    def put(self, request, pk):
        allocation_request = self.get_leave_allocation_request(pk)
        if allocation_request.status == 'requested':
            serializer = LeaveAllocationRequestSerilaizer(allocation_request, data=request.data)
            if serializer.is_valid():
                allocation_request = serializer.save()
                allocation_request.created_by = request.user.employee_get
                allocation_request.save()
                return Response(LeaveAllocationRequestGetSerilaizer(allocation_request).data, status=201)
            return Response(serializer.errors, status=400)
        raise serializers.ValidationError({"error":"Access Denied.."})

                
    def delete(self, request, pk):
        allocation_request = self.get_leave_allocation_request(pk)
        if allocation_request.status == 'requested':
            allocation_request.delete()
            return Response(status=200)
        raise serializers.ValidationError({"error":"Access Denied.."})
    

class CompanyLeaveGetCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        company_leave = CompanyLeave.objects.all().order_by('-id')
        paginator = PageNumberPagination()
        page = paginator.paginate_queryset(company_leave, request)
        serializer = CompanyLeaveSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)


    def post(self, request):
        serializer = CompanyLeaveSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)
    

class CompanyLeaveGetUpdateDeleteAPIView(APIView):
    permission_classes = [IsAuthenticated]  

    def get_company_leave(self, pk):
        try:
            return CompanyLeave.objects.get(pk=pk)
        except CompanyLeave.DoesNotExist as e:
            raise serializers.ValidationError(e)

    def get(self, request, pk):
        company_leave = self.get_company_leave(pk)
        serializer = CompanyLeaveSerializer(company_leave)
        return Response(serializer.data, status=200)

    def put(self, request, pk):
        company_leave = self.get_company_leave(pk)
        serializer = CompanyLeaveSerializer(company_leave, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=200)
        return Response(serializer.errors, status=400)


    def delete(self, request, pk):
        company_leave = self.get_company_leave(pk)
        company_leave.delete()
        return Response(status=200)


class HolidayGetCreateAPIView(APIView):

    def get(self, request):
        holiday = Holiday.objects.all().order_by('-id')
        paginator = PageNumberPagination()
        page = paginator.paginate_queryset(holiday, request)
        serializer = HoildaySerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)

    def post(self, request):
        serializer = HoildaySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)
    
class HolidayGetUpdateDeleteAPIView(APIView):

    def get_holiday(self, pk):
        try:
            return Holiday.objects.get(pk=pk)
        except Holiday.DoesNotExist as e:
            raise serializers.ValidationError(e)

    def get(self, request, pk):
        holiday = self.get_holiday(pk)
        serializer = HoildaySerializer(holiday)
        return Response(serializer.data, status=200)
    
    def put(self, request, pk):
        holiday = self.get_holiday(pk)
        serializer = HoildaySerializer(holiday, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)
    
    def delete(self, request, pk):
        holiday = self.get_holiday(pk)
        holiday.delete()
        return Response(status=200)


class LeaveRequestApproveAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get_leave_request(self, pk):
        try:
            return LeaveRequest.objects.get(pk=pk)
        except LeaveRequest.DoesNotExist as e:
            raise serializers.ValidationError(e)

    def leave_approve_calculation(self, leave_request, available_leave):
        if leave_request.requested_days > available_leave.available_days:
            leave = leave_request.requested_days - available_leave.available_days
            leave_request.approved_available_days = available_leave.available_days
            available_leave.available_days = 0
            available_leave.carryforward_days = (
                available_leave.carryforward_days - leave
            )
            leave_request.approved_carryforward_days = leave
        else:
            temp = available_leave.available_days
            available_leave.available_days = temp - leave_request.requested_days
            leave_request.approved_available_days = leave_request.requested_days
        available_leave.save()

    def put(self, request, pk):   
        leave_request = self.get_leave_request(pk)
        serializer = LeaveRequestApproveSerializer(leave_request, data=request.data)
        if serializer.is_valid():
            available_leave = serializer.validated_data.get('available_leave')
            self.leave_approve_calculation(leave_request, available_leave)
            serializer.save()
            return Response(status=200)
        return Response(serializer.errors, status=400)


class LeaveRequestCancelRejectAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get_leave_request(self, pk):
        try:
            return LeaveRequest.objects.get(pk=pk)
        except LeaveRequest.DoesNotExist as e:
            raise serializers.ValidationError(e)
        
    def leave_calculation(self, leave_request, employee_id):
        leave_type_id = leave_request.leave_type_id
        available_leave = AvailableLeave.objects.get(
            leave_type_id=leave_type_id, employee_id=employee_id
        )
        available_leave.available_days += leave_request.approved_available_days
        available_leave.carryforward_days += leave_request.approved_carryforward_days
        available_leave.save()
        leave_request.approved_available_days = 0
        leave_request.approved_carryforward_days = 0
         
    def put(self, request, pk):
        leave_request = self.get_leave_request(pk)
        employee_id = request.user.employee_get
        serializer = LeaveRequestCancelRejectSerializer(leave_request, data=request.data)
        if serializer.is_valid():
            self. leave_calculation(leave_request, employee_id)
            serializer.save()
            return Response(status=200)
        return Response(serializer.errors, status=400)


class LeaveAllocationApproveAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get_leave_allocation_request(self, pk):
        try:
            return LeaveAllocationRequest.objects.get(pk=pk)
        except LeaveAllocationRequest.DoesNotExist as e:
            raise serializers.ValidationError(e)
    
    def approve_calculations(self, leave_allocation_request, employee_id):
        available_leave = AvailableLeave.objects.get_or_create(employee_id = employee_id, 
                                                               leave_type_id=leave_allocation_request.leave_type_id)[0]
        available_leave.available_days += leave_allocation_request.requested_days
        available_leave.save()
        
    def put(self, request, pk):
        leave_allocation_request = self.get_leave_allocation_request(pk)
        employee_id = request.user.employee_get
        serializer = LeaveAllocationRequestApproveSerializer(leave_allocation_request, data=request.data)
        if serializer.is_valid():
            self.approve_calculations(leave_allocation_request, employee_id)
            serializer.save()
            return Response(status=200)
        return Response(serializer.errors, status=400)
    

class LeaveAllocationRequestCancelAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get_leave_allocation_request(self, pk):
        try:
            return LeaveAllocationRequest.objects.get(pk=pk)
        except LeaveAllocationRequest.DoesNotExist as e:
            raise serializers.ValidationError(e)
        
    def reject_calculation(self, leave_allocation_request, employee_id):
        if leave_allocation_request.status == "approved":
            leave_type = leave_allocation_request.leave_type_id
            requested_days = leave_allocation_request.requested_days
            available_leave = AvailableLeave.objects.filter(
                leave_type_id=leave_type,
                employee_id=leave_allocation_request.employee_id,
            ).first()
            available_leave.available_days = max(
                0, available_leave.available_days - requested_days
            )
        available_leave.save()

    def put(self, request, pk):
        leave_allocation_request = self.get_leave_allocation_request(pk)
        employee_id = request.user.employee_get
        serializer = LeaveAllocationRequestCancelSerializer(leave_allocation_request, data=request.data)
        if serializer.is_valid():
            self.reject_calculation(leave_allocation_request, employee_id)
            serializer.save()
            return Response(status=200)
        return Response(serializer.errors, status=400)



