from attendance.models import AttendanceActivity
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from datetime import date, datetime, timedelta
from attendance.models import EmployeeShiftDay
from attendance.views.views import *
from attendance.views.clock_in_out import *
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.parsers import JSONParser
from attendance.models import Attendance
from .serializers import AttendanceActivitySerializer, AttendanceLateComeEarlyOutSerializer, AttendanceOverTimeSerializer, AttendanceSerializer
# Create your views here.


class ClockInAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        employee, work_info = employee_exists(request)
        if employee and work_info is not None:
            shift = work_info.shift_id
            date_today = date.today()
            attendance_date = date_today
            day = date_today.strftime("%A").lower()
            day = EmployeeShiftDay.objects.get(day=day)
            now = datetime.now().strftime("%H:%M")
            now_sec = strtime_seconds(now)
            mid_day_sec = strtime_seconds("12:00")
            minimum_hour, start_time_sec, end_time_sec = shift_schedule_today(
                day=day, shift=shift
            )
            if start_time_sec > end_time_sec:
                # night shift
                # ------------------
                # Night shift in Horilla consider a 24 hours from noon to next day noon,
                # the shift day taken today if the attendance clocked in after 12 O clock.

                if mid_day_sec > now_sec:
                    # Here you need to create attendance for yesterday

                    date_yesterday = date_today - timedelta(days=1)
                    day_yesterday = date_yesterday.strftime("%A").lower()
                    day_yesterday = EmployeeShiftDay.objects.get(
                        day=day_yesterday)
                    minimum_hour, start_time_sec, end_time_sec = shift_schedule_today(
                        day=day_yesterday, shift=shift
                    )
                    attendance_date = date_yesterday
                    day = day_yesterday
            clock_in_attendance_and_activity(
                employee=employee,
                date_today=date_today,
                attendance_date=attendance_date,
                day=day,
                now=now,
                shift=shift,
                minimum_hour=minimum_hour,
                start_time=start_time_sec,
                end_time=end_time_sec,
            )
            return Response({"message": "Clocked-In"}, status=200)


class ClockOutAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        employee, work_info = employee_exists(request)
        shift = work_info.shift_id
        date_today = date.today()
        day = date_today.strftime("%A").lower()
        day = EmployeeShiftDay.objects.get(day=day)
        attendance = (
            Attendance.objects.filter(employee_id=employee)
            .order_by("id", "attendance_date")
            .last()
        )
        if attendance is not None:
            day = attendance.attendance_day
        now = datetime.now().strftime("%H:%M")
        minimum_hour, start_time_sec, end_time_sec = shift_schedule_today(
            day=day, shift=shift
        )
        early_out_instance = attendance.late_come_early_out.filter(
            type="early_out")
        if not early_out_instance.exists():
            early_out(
                attendance=attendance, start_time=start_time_sec, end_time=end_time_sec
            )

        clock_out_attendance_and_activity(
            employee=employee, date_today=date_today, now=now)

        return Response({"message": "Clocked-Out"}, status=200)


class AttendanceView(APIView):

    def get(self, request, pk=None, type=None):

        if type == 'ot':
            condition = AttendanceValidationCondition.objects.first()
            minot = strtime_seconds("00:30")
            if condition is not None:
                minot = strtime_seconds(condition.minimum_overtime_to_approve)
                attendances = Attendance.objects.filter(
                    attendance_overtime_approve=False,
                    overtime_second__gte=minot,
                    attendance_validated=True,
                )
        elif type == 'validated':
            attendances = Attendance.objects.filter(attendance_validated=True)
        elif type == 'non-validated':
            attendances = Attendance.objects.filter(attendance_validated=False)
        else:
            attendances = Attendance.objects.all()
        if pk:
            attendance = get_object_or_404(Attendance, pk=pk)
            serializer = AttendanceSerializer(attendance)
        else:
            serializer = AttendanceSerializer(attendances, many=True)
        return Response(serializer.data, status=200)

    def post(self, request):
        data = JSONParser().parse(request)
        serializer = AttendanceSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

    def put(self, request, pk):
        attendance = get_object_or_404(Attendance, pk=pk)
        data = JSONParser().parse(request)
        serializer = AttendanceSerializer(attendance, data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

    def delete(self, request, pk):
        attendance = get_object_or_404(Attendance, pk=pk)
        attendance.delete()
        return Response({'message': 'Attendance deleted successfully'}, status=204)


class AttendanceOverTimeView(APIView):
    def get(self, request, pk=None):
        if pk:
            attendance_ot = get_object_or_404(
            AttendanceOverTime, pk=pk) 
        else :
            attendance_ot = AttendanceOverTime.objects.all()
        serializer = AttendanceOverTimeSerializer(attendance_ot, many=False if pk else True)
        return Response(serializer.data, status=200)

    def post(self, request):
        serializer = AttendanceOverTimeSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=200)
        return Response(serializer.errors, status=400)

    def put(self, request, pk):
        attendance_ot = get_object_or_404(AttendanceOverTime, pk=pk)
        serializer = AttendanceOverTimeSerializer(
            instance=attendance_ot, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=200)
        return Response(serializer.errors, status=400)

    def delete(self, request, pk):
        attendance = get_object_or_404(AttendanceOverTime, pk=pk)
        attendance.delete()
        return Response({'message': 'Overtime deleted successfully'}, status=204)

class LateComeEarlyOutView(APIView):
    def get(self,request,pk=None):
        data = LateComeEarlyOutFilter(request.GET)
        serializer = AttendanceLateComeEarlyOutSerializer(data.qs,many=True)
        return Response(serializer.data,status=200)
    
    def delete(self,request,pk=None):
        attendance = get_object_or_404(AttendanceLateComeEarlyOut, pk=pk)
        attendance.delete()
        return Response({'message': 'Attendance deleted successfully'}, status=204)      

class AttendanceActivityView(APIView):
    def get(self,request,pk=None):
        data =AttendanceActivity.objects.all()
        serializer = AttendanceActivitySerializer(data,many=True)
        return Response(serializer.data,status=200)
    
   

        