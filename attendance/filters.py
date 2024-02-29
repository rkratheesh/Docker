"""
filters.py

This page is used to register filter for attendance models

"""
import uuid
import django_filters
from django.forms import DateTimeInput
from django import forms
from django.utils.translation import gettext_lazy as _
from django.db.models import Subquery, OuterRef
from horilla.filters import filter_by_name
from employee.models import Employee
from attendance.models import (
    Attendance,
    AttendanceOverTime,
    AttendanceLateComeEarlyOut,
    AttendanceActivity,
    strtime_seconds,
)
from base.filters import FilterSet


class DurationInSecondsFilter(django_filters.CharFilter):
    """
    Custom CharFilter class that applies specific filter process.
    """

    def filter(self, qs, value):
        """
        FilterSet filter method

        Args:
            qs (self): FilterSet instance
            value (str): duration formatted string

        Returns:
            qs: queryset object
        """
        if value:
            ftr = [3600, 60, 1]
            duration_sec = sum(a * b for a, b in zip(ftr, map(int, value.split(":"))))
            lookup = self.lookup_expr or "exact"
            return qs.filter(**{f"{self.field_name}__{lookup}": duration_sec})
        return qs


class AttendanceOverTimeFilter(FilterSet):
    """
    Filter set class for AttendanceOverTime model

    Args:
        FilterSet (class): custom filter set class to apply styling
    """

    MONTH_CHOICES = [
        ("January", _("January")),
        ("February", _("February")),
        ("March", _("March")),
        ("April", _("April")),
        ("May", _("May")),
        ("June", _("June")),
        ("July", _("July")),
        ("August", _("August")),
        ("September", _("September")),
        ("October", _("October")),
        ("November", _("November")),
        ("December", _("December")),
    ]
    search = django_filters.CharFilter(method=filter_by_name)

    worked_hours__gte = DurationInSecondsFilter(
        field_name="hour_account_second", lookup_expr="gte"
    )
    worked_hours__lte = DurationInSecondsFilter(
        field_name="hour_account_second", lookup_expr="lte"
    )
    pending_hours__lte = DurationInSecondsFilter(
        field_name="hour_pending_second", lookup_expr="lte"
    )
    pending_hours__gte = DurationInSecondsFilter(
        field_name="hour_pending_second", lookup_expr="gte"
    )
    overtime__gte = DurationInSecondsFilter(
        field_name="overtime_second", lookup_expr="gte"
    )
    overtime__lte = DurationInSecondsFilter(
        field_name="overtime_second", lookup_expr="lte"
    )
    month = django_filters.ChoiceFilter(choices=MONTH_CHOICES, lookup_expr="icontains")
    department_name = django_filters.CharFilter(
        field_name="employee_id__employee_work_info__department_id__department",
        lookup_expr="icontains",
    )

    class Meta:
        """
        Meta class to add additional options
        """

        model = AttendanceOverTime
        fields = [
            "employee_id",
            "month",
            "overtime",
            "worked_hours",
            "year",
            "department_name",
            "employee_id__employee_work_info__department_id",
            "employee_id__employee_work_info__company_id",
            "employee_id__employee_work_info__job_position_id",
            "employee_id__employee_work_info__location",
            "employee_id__employee_work_info__reporting_manager_id",
            "employee_id__employee_work_info__shift_id",
            "employee_id__employee_work_info__work_type_id",
        ]

    def __init__(self, data=None, queryset=None, *, request=None, prefix=None):
        super().__init__(data=data, queryset=queryset, request=request, prefix=prefix)
        for field in self.form.fields.keys():
            self.form.fields[field].widget.attrs["id"] = f"{uuid.uuid4()}"


class LateComeEarlyOutFilter(FilterSet):
    """
    LateComeEarlyOutFilter class
    """

    search = django_filters.CharFilter(method=filter_by_name)
    employee_id = django_filters.ModelMultipleChoiceFilter(
        queryset=Employee.objects.all(),
        widget=forms.SelectMultiple(),
    )
    attendance_date__gte = django_filters.DateFilter(
        field_name="attendance_id__attendance_date",
        lookup_expr="gte",
        widget=forms.DateInput(attrs={"type": "date"}),
    )
    attendance_date__lte = django_filters.DateFilter(
        field_name="attendance_id__attendance_date",
        lookup_expr="lte",
        widget=forms.DateInput(attrs={"type": "date"}),
    )
    attendance_clock_in__lte = django_filters.TimeFilter(
        field_name="attendance_id__attendance_clock_in",
        widget=forms.TimeInput(attrs={"type": "time"}),
        lookup_expr="lte",
    )
    attendance_clock_in__gte = django_filters.TimeFilter(
        field_name="attendance_id__attendance_clock_in",
        widget=forms.TimeInput(attrs={"type": "time"}),
        lookup_expr="gte",
    )
    attendance_clock_out__gte = django_filters.TimeFilter(
        field_name="attendance_id__attendance_clock_out",
        widget=forms.TimeInput(attrs={"type": "time"}),
        lookup_expr="gte",
    )
    attendance_clock_out__lte = django_filters.TimeFilter(
        field_name="attendance_id__attendance_clock_out",
        widget=forms.TimeInput(attrs={"type": "time"}),
        lookup_expr="lte",
    )
    attendance_clock_in = django_filters.TimeFilter(
        field_name="attendance_id__attendance_clock_in",
        widget=forms.TimeInput(attrs={"type": "time"}),
        lookup_expr="exact",
    )
    attendance_clock_out = django_filters.TimeFilter(
        field_name="attendance_id__attendance_clock_out",
        widget=forms.TimeInput(attrs={"type": "time"}),
        lookup_expr="exact",
    )
    attendance_date = django_filters.DateFilter(
        field_name="attendance_id__attendance_date",
        widget=forms.DateInput(attrs={"type": "date"}),
    )
    overtime_second__lte = DurationInSecondsFilter(
        field_name="attendance_id__overtime_second", lookup_expr="lte"
    )
    overtime_second__gte = DurationInSecondsFilter(
        field_name="attendance_id__overtime_second", lookup_expr="gte"
    )
    at_work_second__lte = DurationInSecondsFilter(
        field_name="attendance_id__at_work_second", lookup_expr="lte"
    )
    at_work_second__gte = DurationInSecondsFilter(
        field_name="attendance_id__at_work_second", lookup_expr="gte"
    )
    department = django_filters.CharFilter(
        field_name="employee_id__employee_work_info__department_id__department",
        lookup_expr="icontains",
    )
    year = django_filters.CharFilter(
        field_name="attendance_id__attendance_date", lookup_expr="year"
    )
    month = django_filters.CharFilter(
        field_name="attendance_id__attendance_date", lookup_expr="month"
    )
    week = django_filters.CharFilter(
        field_name="attendance_id__attendance_date", lookup_expr="week"
    )

    class Meta:
        """
        Meta class for additional options"""

        model = AttendanceLateComeEarlyOut
        fields = [
            "employee_id",
            "type",
            "attendance_id__minimum_hour",
            "attendance_id__attendance_worked_hour",
            "attendance_id__attendance_overtime_approve",
            "attendance_id__attendance_validated",
            "employee_id__employee_work_info__department_id",
            "employee_id__employee_work_info__company_id",
            "employee_id__employee_work_info__job_position_id",
            "employee_id__employee_work_info__location",
            "employee_id__employee_work_info__reporting_manager_id",
            "attendance_id__shift_id",
            "attendance_id__work_type_id",
            "attendance_date__gte",
            "attendance_date__lte",
            "attendance_clock_in__lte",
            "attendance_clock_in__gte",
            "attendance_clock_out__gte",
            "attendance_clock_out__lte",
            "attendance_clock_in",
            "attendance_clock_out",
            "attendance_date",
            "department",
            "year",
            "month",
            "week",
        ]

    def __init__(self, data=None, queryset=None, *, request=None, prefix=None):
        super().__init__(data=data, queryset=queryset, request=request, prefix=prefix)
        for field in self.form.fields.keys():
            self.form.fields[field].widget.attrs["id"] = f"{uuid.uuid4()}"


class AttendanceActivityFilter(FilterSet):
    """
    Filter set class for AttendanceActivity model

    Args:
        FilterSet (class): custom filter set class to apply styling
    """

    search = django_filters.CharFilter(method=filter_by_name)

    attendance_date = django_filters.DateFilter(
        field_name="attendance_date", widget=forms.DateInput(attrs={"type": "date"})
    )
    attendance_date_from = django_filters.DateFilter(
        field_name="attendance_date",
        lookup_expr="gte",
        widget=forms.DateInput(attrs={"type": "date"}),
    )
    attendance_date_till = django_filters.DateFilter(
        field_name="attendance_date",
        lookup_expr="lte",
        widget=forms.DateInput(attrs={"type": "date"}),
    )
    in_from = django_filters.DateFilter(
        field_name="clock_in",
        lookup_expr="gte",
        widget=forms.DateInput(attrs={"type": "time"}),
    )
    out_from = django_filters.DateFilter(
        field_name="clock_out",
        lookup_expr="gte",
        widget=forms.DateInput(attrs={"type": "time"}),
    )
    in_till = django_filters.DateFilter(
        field_name="clock_in",
        lookup_expr="lte",
        widget=forms.DateInput(attrs={"type": "time"}),
    )
    out_till = django_filters.DateFilter(
        field_name="clock_out",
        lookup_expr="lte",
        widget=forms.DateInput(attrs={"type": "time"}),
    )
    clock_in_date = django_filters.DateFilter(
        field_name="clock_in_date", widget=forms.DateInput(attrs={"type": "date"})
    )
    clock_out_date = django_filters.DateFilter(
        field_name="clock_out_date", widget=forms.DateInput(attrs={"type": "date"})
    )

    class Meta:
        """
        Meta class to add additional options
        """

        fields = [
            "employee_id",
            "attendance_date",
            "attendance_date_from",
            "attendance_date_till",
            "in_from",
            "in_till",
            "out_from",
            "shift_day",
            "out_till",
            "clock_in_date",
            "clock_out_date",
            "employee_id__employee_work_info__department_id",
            "employee_id__employee_work_info__company_id",
            "employee_id__employee_work_info__shift_id",
            "employee_id__employee_work_info__work_type_id",
            "employee_id__employee_work_info__job_position_id",
            "employee_id__employee_work_info__location",
            "employee_id__employee_work_info__reporting_manager_id",
        ]
        model = AttendanceActivity

    def __init__(self, data=None, queryset=None, *, request=None, prefix=None):
        super().__init__(data=data, queryset=queryset, request=request, prefix=prefix)
        for field in self.form.fields.keys():
            self.form.fields[field].widget.attrs["id"] = f"{uuid.uuid4()}"


class AttendanceFilters(FilterSet):
    """
    Filter set class for Attendance model

    Args:
        FilterSet (class): custom filter set class to apply styling
    """
    id = django_filters.NumberFilter(field_name="id")
    search = django_filters.CharFilter(method=filter_by_name)
    employee = django_filters.CharFilter(field_name="employee_id__id")
    date_attendance = django_filters.DateFilter(field_name="attendance_date")
    employee_id = django_filters.ModelMultipleChoiceFilter(
        queryset=Employee.objects.all(),
        widget=forms.SelectMultiple(),
    )

    attendance_date__gte = django_filters.DateFilter(
        field_name="attendance_date",
        lookup_expr="gte",
        widget=forms.DateInput(attrs={"type": "date"}),
    )
    attendance_date__lte = django_filters.DateFilter(
        field_name="attendance_date",
        lookup_expr="lte",
        widget=forms.DateInput(attrs={"type": "date"}),
    )

    attendance_clock_in__lte = django_filters.TimeFilter(
        field_name="attendance_clock_in",
        widget=forms.TimeInput(attrs={"type": "time"}),
        lookup_expr="lte",
    )
    attendance_clock_in__gte = django_filters.TimeFilter(
        field_name="attendance_clock_in",
        widget=forms.TimeInput(attrs={"type": "time"}),
        lookup_expr="gte",
    )
    attendance_clock_out__gte = django_filters.TimeFilter(
        field_name="attendance_clock_out",
        widget=forms.TimeInput(attrs={"type": "time"}),
        lookup_expr="gte",
    )
    attendance_clock_out__lte = django_filters.TimeFilter(
        field_name="attendance_clock_out",
        widget=forms.TimeInput(attrs={"type": "time"}),
        lookup_expr="lte",
    )
    attendance_clock_in = django_filters.TimeFilter(
        field_name="attendance_clock_in",
        widget=forms.TimeInput(attrs={"type": "time"}),
    )
    attendance_clock_out = django_filters.TimeFilter(
        field_name="attendance_clock_out",
        widget=forms.TimeInput(attrs={"type": "time"}),
    )

    attendance_date = django_filters.DateFilter(
        widget=forms.DateInput(attrs={"type": "date"}),
    )
    pending_hour__lte = DurationInSecondsFilter(
        method="filter_pending_hour",
    )
    pending_hour__gte = DurationInSecondsFilter(
        method="filter_pending_hour",
    )
    at_work_second__lte = DurationInSecondsFilter(
        field_name="at_work_second", lookup_expr="lte"
    )
    at_work_second__gte = DurationInSecondsFilter(
        field_name="at_work_second", lookup_expr="gte"
    )
    overtime_second__lte = DurationInSecondsFilter(
        field_name="overtime_second", lookup_expr="lte"
    )
    overtime_second__gte = DurationInSecondsFilter(
        field_name="overtime_second", lookup_expr="gte"
    )
    year = django_filters.CharFilter(field_name="attendance_date", lookup_expr="year")
    month = django_filters.CharFilter(field_name="attendance_date", lookup_expr="month")
    week = django_filters.CharFilter(field_name="attendance_date", lookup_expr="week")
    department = django_filters.CharFilter(
        field_name="employee_id__employee_work_info__department_id__department",
        lookup_expr="icontains",
    )

    def filter_pending_hour(self, queryset, name, value):
        if value is not None:
            value = strtime_seconds(value)
            filtered_attendance = []
            for attendance in queryset:
                minimum_hour_second = strtime_seconds(attendance.minimum_hour)
                worked_hour_second = attendance.at_work_second
                pending_hour_second = minimum_hour_second - worked_hour_second
                if name == "pending_hour__lte":
                    if value >= pending_hour_second:
                        filtered_attendance.append(attendance)
                else:
                    if value <= pending_hour_second:
                        filtered_attendance.append(attendance)
        return queryset.filter(
            id__in=[attendance.id for attendance in filtered_attendance]
        )

    class Meta:
        """
        Meta class to add additional options
        """

        model = Attendance
        fields = [
            "id",
            "employee_id",
            "employee_id__employee_work_info__department_id",
            "employee_id__employee_work_info__company_id",
            "employee_id__employee_work_info__job_position_id",
            "employee_id__employee_work_info__location",
            "employee_id__employee_work_info__reporting_manager_id",
            "attendance_date",
            "work_type_id",
            "shift_id",
            "minimum_hour",
            "attendance_validated",
            "attendance_clock_in",
            "attendance_clock_out",
            "at_work_second",
            "overtime_second",
            "late_come_early_out__type",
            "attendance_overtime_approve",
            "attendance_validated",
            "is_validate_request",
            "is_validate_request_approved",
            "at_work_second__lte",
            "at_work_second__gte",
            "overtime_second__lte",
            "overtime_second__gte",
            "overtime_second",
            "department",
        ]

        widgets = {
            "attendance_date": DateTimeInput(attrs={"type": "date"}),
        }

    def __init__(self, data=None, queryset=None, *, request=None, prefix=None):
        super().__init__(data=data, queryset=queryset, request=request, prefix=prefix)
        for field in self.form.fields.keys():
            self.form.fields[field].widget.attrs["id"] = f"{uuid.uuid4()}"


class LateComeEarlyOutReGroup:
    """
    Class to keep the field name for group by option
    """

    fields = [
        ("", "Select"),
        ("employee_id", "Employee"),
        ("type", "Type"),
        ("attendance_id.attendance_date", "Attendance Date"),
        ("attendance_id.shift_id", "Shift"),
        ("attendance_id.work_type_id", "Work Type"),
        ("attendance_id.minimum_hour", "Minimum Hour"),
        ("attendance_id.employee_id.country", "Country"),
        (
            "attendance_id.employee_id.employee_work_info.reporting_manager_id",
            "Reporting Manager",
        ),
        ("attendance_id.employee_id.employee_work_info.department_id", "Department"),
        (
            "attendance_id.employee_id.employee_work_info.job_position_id",
            "Job Position",
        ),
        (
            "attendance_id.employee_id.employee_work_info.employee_type_id",
            "Employment Type",
        ),
        ("attendance_id.employee_id.employee_work_info.company_id", "Company"),
    ]


class AttendanceReGroup:
    """
    Class to keep the field name for group by option
    """

    fields = [
        ("", "Select"),
        ("employee_id", "Employee"),
        ("attendance_date", "Attendance Date"),
        ("shift_id", "Shift"),
        ("work_type_id", "Work Type"),
        ("minimum_hour", "Minimum Hour"),
        ("employee_id.country", "Country"),
        ("employee_id.employee_work_info.reporting_manager_id", "Reporting Manager"),
        ("employee_id.employee_work_info.department_id", "Department"),
        ("employee_id.employee_work_info.job_position_id", "Job Position"),
        ("employee_id.employee_work_info.employee_type_id", "Employment Type"),
        ("employee_id.employee_work_info.company_id", "Company"),
    ]


class AttendanceOvertimeReGroup:
    """
    Class to keep the field name for group by option
    """

    fields = [
        ("", "Select"),
        ("employee_id", "Employee"),
        ("month", "Month"),
        ("year", "Year"),
        ("employee_id.country", "Country"),
        ("employee_id.employee_work_info.reporting_manager_id", "Reporting Manager"),
        ("employee_id.employee_work_info.shift_id", "Shift"),
        ("employee_id.employee_work_info.work_type_id", "Work Type"),
        ("employee_id.employee_work_info.department_id", "Department"),
        ("employee_id.employee_work_info.job_position_id", "Job Position"),
        ("employee_id.employee_work_info.employee_type_id", "Employment Type"),
        ("employee_id.employee_work_info.company_id", "Company"),
    ]


class AttendanceActivityReGroup:
    """
    Class to keep the field name for group by option
    """

    fields = [
        ("", "Select"),
        ("employee_id", "Employee"),
        ("attendance_date", "Attendance Date"),
        ("clock_in_date", "In Date"),
        ("clock_out_date", "Out Date"),
        ("shift_day", "Shift Day"),
        ("employee_id.country", "Country"),
        ("employee_id.employee_work_info.reporting_manager_id", "Reporting Manager"),
        ("employee_id.employee_work_info.shift_id", "Shift"),
        ("employee_id.employee_work_info.work_type_id", "Work Type"),
        ("employee_id.employee_work_info.department_id", "Department"),
        ("employee_id.employee_work_info.job_position_id", "Job Position"),
        ("employee_id.employee_work_info.employee_type_id", "Employment Type"),
        ("employee_id.employee_work_info.company_id", "Company"),
    ]


class AttendanceRequestReGroup:
    """
    Class to keep the field name for group by option
    """

    fields = [
        ("", "Select"),
        ("employee_id", "Employee"),
        ("attendance_day", "Attendance Date"),
        ("attendance_clock_in_date", "In Date"),
        ("attendance_clock_out_date", "Out Date"),
        ("employee_id.country", "Country"),
        ("employee_id.employee_work_info.reporting_manager_id", "Reporting Manager"),
        ("employee_id.employee_work_info.shift_id", "Shift"),
        ("employee_id.employee_work_info.work_type_id", "Work Type"),
        ("employee_id.employee_work_info.department_id", "Department"),
        ("employee_id.employee_work_info.job_position_id", "Job Position"),
        ("employee_id.employee_work_info.employee_type_id", "Employment Type"),
        ("employee_id.employee_work_info.company_id", "Company"),
    ]
