from rest_framework import serializers
from base.models import Department, JobPosition

from employee.models import Employee, EmployeeBankDetails, EmployeeWorkInformation
from employee_api.methods import get_next_badge_id


class EmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = "__all__"

    def create(self, validated_data):
        validated_data['badge_id'] = get_next_badge_id()
        return super().create(validated_data)


class EmployeeWorkInformationSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmployeeWorkInformation
        fields = "__all__"


class EmployeeBankDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmployeeBankDetails
        fields = '__all__'


class EmployeeBulkUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        # fields = [
        #     'employee_last_name',
        #     'address',
        #     'country',
        #     'state',
        #     'city',
        #     'zip',
        #     'dob',
        #     'gender',
        #     'qualification',
        #     'experience',
        #     'marital_status',
        #     'children',
        # ]
        fields = [
            'employee_last_name',
            
        ]
