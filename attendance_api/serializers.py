from rest_framework import serializers
from attendance.models import *

class AttendanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attendance
        fields = '__all__'
  
class AttendanceOverTimeSerializer(serializers.ModelSerializer):
    class Meta:
        model = AttendanceOverTime
        fields = '__all__'
  
class AttendanceLateComeEarlyOutSerializer(serializers.ModelSerializer):
    class Meta:
        model = AttendanceLateComeEarlyOut
        fields = '__all__'

class AttendanceActivitySerializer(serializers.ModelSerializer):
    class Meta:
        model = AttendanceActivity
        fields = "__all__"
  