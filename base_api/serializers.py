from rest_framework import serializers
from base.models import Company, Department, EmployeeShift, EmployeeShiftDay, EmployeeShiftSchedule, JobPosition, JobRole, RotatingShift, RotatingShiftAssign, RotatingWorkType, RotatingWorkTypeAssign, ShiftRequest, WorkType, WorkTypeRequest


class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = "__all__"


class JobPositionSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobPosition
        fields = "__all__"


class JobRoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobRole
        fields = "__all__"


class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = "__all__"

    def create(self, validated_data):
        comapny_id = validated_data.pop('company_id', [])
        obj = Department(**validated_data)
        obj.save()
        obj.company_id.set(comapny_id)
        return obj


class WorkTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkType
        fields = '__all__'


class RotatingWorkTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = RotatingWorkType
        fields = '__all__'


class RotatingWorkTypeAssignSerializer(serializers.ModelSerializer):
    class Meta:
        model = RotatingWorkTypeAssign
        fields = '__all__'


class EmployeeShiftDaySerializer(serializers.ModelSerializer):
    class Meta:
        model = EmployeeShiftDay
        fields = '__all__'


class EmployeeShiftSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmployeeShift
        fields = '__all__'


class EmployeeShiftScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmployeeShiftSchedule
        fields = '__all__'


class RotatingShiftSerializer(serializers.ModelSerializer):
    class Meta:
        model = RotatingShift
        fields = '__all__'


class RotatingShiftAssignSerializer(serializers.ModelSerializer):
    class Meta:
        model = RotatingShiftAssign
        fields = '__all__'


class WorkTypeRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkTypeRequest
        fields = '__all__'


class ShiftRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShiftRequest
        fields = '__all__'
