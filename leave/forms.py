import re
import uuid
from django import forms
from django.forms import ModelForm
from django.forms.widgets import TextInput
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.template.loader import render_to_string
from employee.filters import EmployeeFilter
from employee.models import Employee
from base.methods import reload_queryset
from horilla_widgets.forms import HorillaForm
from horilla_widgets.widgets.horilla_multi_select_field import HorillaMultiSelectField
from horilla_widgets.widgets.select_widgets import HorillaMultiSelectWidget
from .models import (
    LeaveType,
    LeaveRequest,
    AvailableLeave,
    Holiday,
    CompanyLeave,
    LeaveAllocationRequest,
)
from .methods import (
    calculate_requested_days,
    leave_requested_dates,
    holiday_dates_list,
    company_leave_dates_list,
)


CHOICES = [("yes", _("Yes")), ("no", _("No"))]


class ModelForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        reload_queryset(self.fields)
        for field_name, field in self.fields.items():
            widget = field.widget

            if isinstance(widget, (forms.DateInput)):
                field.widget.attrs.update({"class": "oh-input oh-calendar-input w-100"})
            elif isinstance(
                widget, (forms.NumberInput, forms.EmailInput, forms.TextInput)
            ):
                field.widget.attrs.update(
                    {"class": "oh-input w-100", "placeholder": field.label}
                )
            elif isinstance(widget, (forms.Select,)):
                field.widget.attrs.update(
                    {"class": "oh-select oh-select-2 select2-hidden-accessible"}
                )
            elif isinstance(widget, (forms.Textarea)):
                field.widget.attrs.update(
                    {
                        "class": "oh-input w-100",
                        "placeholder": field.label,
                        "rows": 2,
                        "cols": 40,
                    }
                )
            elif isinstance(
                widget,
                (
                    forms.CheckboxInput,
                    forms.CheckboxSelectMultiple,
                ),
            ):
                field.widget.attrs.update({"class": "oh-switch__checkbox"})


class ConditionForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        reload_queryset(self.fields)
        for field_name, field in self.fields.items():
            widget = field.widget
            if isinstance(widget, (forms.Select,)):
                field.widget.attrs[
                    "style"
                ] = "width:100%; height:50px;border: 1px solid hsl(213deg,22%,84%);border-radius: 0rem;padding: 0.8rem 1.25rem;"
            elif isinstance(widget, (forms.DateInput)):
                field.widget.attrs.update({"class": "oh-input oh-calendar-input w-100"})
            elif isinstance(
                widget, (forms.NumberInput, forms.EmailInput, forms.TextInput)
            ):
                field.widget.attrs.update(
                    {"class": "oh-input w-100", "placeholder": field.label}
                )
            elif isinstance(widget, (forms.Textarea)):
                field.widget.attrs.update(
                    {
                        "class": "oh-input w-100",
                        "placeholder": field.label,
                        "rows": 2,
                        "cols": 40,
                    }
                )
            elif isinstance(
                widget,
                (
                    forms.CheckboxInput,
                    forms.CheckboxSelectMultiple,
                ),
            ):
                field.widget.attrs.update({"class": "oh-switch__checkbox"})


class LeaveTypeForm(ConditionForm):
    require_approval = forms.CharField(
        label="Require Approval", widget=forms.RadioSelect(choices=CHOICES)
    )
    require_attachment = forms.CharField(
        label="Require Attachment", widget=forms.RadioSelect(choices=CHOICES)
    )
    exclude_company_leave = forms.CharField(
        label="Exclude Company Leave", widget=forms.RadioSelect(choices=CHOICES)
    )
    exclude_holiday = forms.CharField(
        label="Exclude Holiday", widget=forms.RadioSelect(choices=CHOICES)
    )

    class Meta:
        model = LeaveType
        fields = "__all__"
        labels = {
            "name": _("Name"),
        }
        widgets = {
            "color": TextInput(attrs={"type": "color", "style": "height:40px;"}),
            "period_in": forms.HiddenInput(),
            "total_days": forms.HiddenInput(),
        }

    def clean(self):
        cleaned_data = super().clean()
        if "employee_id" in self.errors:
            del self.errors["employee_id"]
        if "exceed_days" in self.errors:
            del self.errors["exceed_days"]
        return cleaned_data

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class UpdateLeaveTypeForm(ConditionForm):
    require_approval = forms.CharField(
        label="Require Approval", widget=forms.RadioSelect(choices=CHOICES)
    )
    require_attachment = forms.CharField(
        label="Require Attachment", widget=forms.RadioSelect(choices=CHOICES)
    )
    exclude_company_leave = forms.CharField(
        label="Exclude Company Leave", widget=forms.RadioSelect(choices=CHOICES)
    )
    exclude_holiday = forms.CharField(
        label="Exclude Holiday", widget=forms.RadioSelect(choices=CHOICES)
    )

    def __init__(self, *args, **kwargs):
        super(UpdateLeaveTypeForm, self).__init__(*args, **kwargs)

        empty_fields = []
        for field_name, field_value in self.instance.__dict__.items():
            if field_value is None or field_value == "":
                if field_name.endswith("_id"):
                    foreign_key_field_name = re.sub("_id$", "", field_name)
                    empty_fields.append(foreign_key_field_name)
                empty_fields.append(field_name)

        for index, visible in enumerate(self.visible_fields()):
            if list(self.fields.keys())[index] in empty_fields:
                visible.field.widget.attrs[
                    "style"
                ] = "display:none;width:100%; height:50px;border: 1px solid hsl(213deg,22%,84%);border-radius: 0rem;padding: 0.8rem 1.25rem;"
                visible.field.widget.attrs["data-hidden"] = True

    class Meta:
        model = LeaveType
        fields = "__all__"
        exclude = ["period_in", "total_days"]
        widgets = {
            "color": TextInput(attrs={"type": "color", "style": "height:40px;"}),
        }

    def clean(self):
        cleaned_data = super().clean()
        if "exceed_days" in self.errors:
            del self.errors["exceed_days"]
        return cleaned_data

def cal_effective_requested_days(start_date,end_date,leave_type_id,requested_days):
    requested_dates = leave_requested_dates(start_date, end_date)
    holidays = Holiday.objects.all()
    holiday_dates = holiday_dates_list(holidays)
    company_leaves = CompanyLeave.objects.all()
    company_leave_dates = company_leave_dates_list(company_leaves, start_date)
    if (
        leave_type_id.exclude_company_leave == "yes"
        and leave_type_id.exclude_holiday == "yes"
    ):
        total_leaves = list(set(holiday_dates + company_leave_dates))
        total_leave_count = sum(
            requested_date in total_leaves for requested_date in requested_dates
        )
        requested_days = requested_days - total_leave_count
    else:
        holiday_count = 0
        if leave_type_id.exclude_holiday == "yes":
            for requested_date in requested_dates:
                if requested_date in holiday_dates:
                    holiday_count += 1
            requested_days = requested_days - holiday_count
        if leave_type_id.exclude_company_leave == "yes":
            company_leave_count = sum(
                requested_date in company_leave_dates
                for requested_date in requested_dates
            )
            requested_days = requested_days - company_leave_count
    return requested_days

class LeaveRequestCreationForm(ModelForm):
    start_date = forms.DateField(widget=forms.DateInput(attrs={"type": "date"}))
    end_date = forms.DateField(widget=forms.DateInput(attrs={"type": "date"}))

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get("start_date")
        end_date = cleaned_data.get("end_date")
        employee_id = cleaned_data.get("employee_id")
        leave_type_id = cleaned_data.get("leave_type_id")
        start_date_breakdown = cleaned_data.get("start_date_breakdown")
        end_date_breakdown = cleaned_data.get("end_date_breakdown")
        attachment = cleaned_data.get("attachment")
        overlapping_requests = LeaveRequest.objects.filter(
            employee_id=employee_id, start_date__lte=end_date, end_date__gte=start_date
        )
        if leave_type_id.require_attachment == "yes":
            if attachment is None:
                raise forms.ValidationError(
                    _("An attachment is required for this leave request")
                )
        if not start_date <= end_date:
            raise forms.ValidationError(
                _("End date should not be less than start date.")
            )
        if start_date == end_date:
            if start_date_breakdown != end_date_breakdown:
                raise forms.ValidationError(
                    _("There is a mismatch in the breakdown of the start date and end date.")
                )
        if not AvailableLeave.objects.filter(
            employee_id=employee_id, leave_type_id=leave_type_id
        ).exists():
            raise forms.ValidationError(_("Employee has no leave type.."))

        if overlapping_requests.exists():
            raise forms.ValidationError(
                _("Employee has already a leave request for this date range..")
            )

        available_leave = AvailableLeave.objects.get(
            employee_id=employee_id, leave_type_id=leave_type_id
        )
        total_leave_days = (
            available_leave.available_days + available_leave.carryforward_days
        )
        requested_days = calculate_requested_days(
            start_date, end_date, start_date_breakdown, end_date_breakdown
        )
        effective_requested_days = cal_effective_requested_days(start_date=start_date,end_date=end_date,leave_type_id=leave_type_id,requested_days=requested_days)
        if not effective_requested_days <= total_leave_days:
            raise forms.ValidationError(_("Employee doesn't have enough leave days.."))

        return cleaned_data

    def as_p(self, *args, **kwargs):
        """
        Render the form fields as HTML table rows with Bootstrap styling.
        """
        context = {"form": self}
        table_html = render_to_string("attendance_form.html", context)
        return table_html

    class Meta:
        model = LeaveRequest
        fields = [
            "employee_id",
            "leave_type_id",
            "start_date",
            "start_date_breakdown",
            "end_date",
            "end_date_breakdown",
            "description",
            "attachment",
        ]


class LeaveRequestUpdationForm(ModelForm):
    start_date = forms.DateField(widget=forms.DateInput(attrs={"type": "date"}))
    end_date = forms.DateField(widget=forms.DateInput(attrs={"type": "date"}))

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get("start_date")
        end_date = cleaned_data.get("end_date")
        employee_id = cleaned_data.get("employee_id")
        leave_type_id = cleaned_data.get("leave_type_id")
        start_date_breakdown = cleaned_data.get("start_date_breakdown")
        end_date_breakdown = cleaned_data.get("end_date_breakdown")
        overlapping_requests = LeaveRequest.objects.filter(
            employee_id=employee_id, start_date__lte=end_date, end_date__gte=start_date
        ).exclude(id=self.instance.id)
        if not start_date <= end_date:
            raise forms.ValidationError(
                _("End date should not be less than start date.")
            )
        if start_date == end_date:
            if start_date_breakdown != end_date_breakdown:
                raise forms.ValidationError(
                    _("There is a mismatch in the breakdown of the start date and end date.")
                )
        if not AvailableLeave.objects.filter(
            employee_id=employee_id, leave_type_id=leave_type_id
        ).exists():
            raise forms.ValidationError(_("Employee has no leave type.."))
        if overlapping_requests.exists():
            raise forms.ValidationError(
                _("Employee has already a leave request for this date range..")
            )
        available_leave = AvailableLeave.objects.get(
            employee_id=employee_id, leave_type_id=leave_type_id
        )
        total_leave_days = (
            available_leave.available_days + available_leave.carryforward_days
        )
        requested_days = calculate_requested_days(
            start_date, end_date, start_date_breakdown, end_date_breakdown
        )
        effective_requested_days = cal_effective_requested_days(start_date=start_date,end_date=end_date,leave_type_id=leave_type_id,requested_days=requested_days)
        if not effective_requested_days <= total_leave_days:
            raise forms.ValidationError(_("Employee doesn't have enough leave days.."))

        return cleaned_data

    def as_p(self, *args, **kwargs):
        """
        Render the form fields as HTML table rows with Bootstrap styling.
        """
        context = {"form": self}
        table_html = render_to_string("attendance_form.html", context)
        return table_html

    class Meta:
        model = LeaveRequest
        fields = [
            "leave_type_id",
            "employee_id",
            "start_date",
            "start_date_breakdown",
            "end_date",
            "end_date_breakdown",
            "description",
            "attachment",
            "status",
        ]


class AvailableLeaveForm(ModelForm):
    leave_type_id = forms.ModelChoiceField(
        queryset=LeaveType.objects.all(),
        widget=forms.SelectMultiple,
        empty_label=None,
    )
    employee_id = forms.ModelChoiceField(
        queryset=Employee.objects.all(),
        widget=forms.SelectMultiple,
        empty_label=None,
    )

    class Meta:
        model = AvailableLeave
        fields = ["leave_type_id", "employee_id"]


class HolidayForm(ModelForm):
    start_date = forms.DateField(
        widget=forms.DateInput(attrs={"type": "date"}),
    )
    end_date = forms.DateField(
        widget=forms.DateInput(attrs={"type": "date"}),
    )

    def clean_end_date(self):
        start_date = self.cleaned_data.get("start_date")
        end_date = self.cleaned_data.get("end_date")

        if start_date and end_date and end_date < start_date:
            raise ValidationError(
                _("End date should not be earlier than the start date.")
            )

        return end_date

    class Meta:
        model = Holiday
        fields = "__all__"
        labels = {
            "name": _("Name"),
        }


class LeaveOneAssignForm(ModelForm):
    employee_id = forms.ModelChoiceField(
        queryset=Employee.objects.all(),
        widget=forms.SelectMultiple,
        empty_label=None,
    )

    class Meta:
        model = AvailableLeave
        fields = ["employee_id"]


class AvailableLeaveUpdateForm(ModelForm):
    class Meta:
        model = AvailableLeave
        fields = ["available_days", "carryforward_days"]


class CompanyLeaveForm(ModelForm):
    class Meta:
        model = CompanyLeave
        fields = "__all__"


class UserLeaveRequestForm(ModelForm):
    start_date = forms.DateField(widget=forms.DateInput(attrs={"type": "date"}))
    end_date = forms.DateField(widget=forms.DateInput(attrs={"type": "date"}))
    description = forms.CharField(label=_("Description"), widget=forms.Textarea)

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get("start_date")
        end_date = cleaned_data.get("end_date")
        employee_id = cleaned_data.get("employee_id")
        start_date_breakdown = cleaned_data.get("start_date_breakdown")
        end_date_breakdown = cleaned_data.get('end_date_breakdown')
        leave_type_id = cleaned_data.get("leave_type_id")
        overlapping_requests = LeaveRequest.objects.filter(
            employee_id=employee_id,
            start_date__lte=end_date,
            end_date__gte=start_date
        ).exclude(
            id=self.instance.id,
            status__in=['cancelled_and_rejected', 'rejected']
        )
        if start_date == end_date:
            if start_date_breakdown != end_date_breakdown:
                raise forms.ValidationError(
                    _("There is a mismatch in the breakdown of the start date and end date.")
                )
        if not start_date <= end_date:
            raise forms.ValidationError(
                _("End date should not be less than start date.")
            )
        if overlapping_requests.exists():
            raise forms.ValidationError(
                _("Employee has already a leave request for this date range..")
            )
        requested_days = calculate_requested_days(
            start_date, end_date, start_date_breakdown, end_date_breakdown
        )
        available_leave = AvailableLeave.objects.get(
            employee_id=employee_id, leave_type_id=leave_type_id
        )
        total_leave_days = (
            available_leave.available_days + available_leave.carryforward_days
        )
        effective_requested_days = cal_effective_requested_days(start_date=start_date,end_date=end_date,leave_type_id=leave_type_id,requested_days=requested_days)
        if not effective_requested_days <= total_leave_days:
            raise forms.ValidationError(_("Employee doesn't have enough leave days.."))
        return cleaned_data

    def __init__(self, *args, employee=None, **kwargs):
        super(UserLeaveRequestForm, self).__init__(*args, **kwargs)

    def as_p(self, *args, **kwargs):
        """
        Render the form fields as HTML table rows with Bootstrap styling.
        """
        context = {"form": self}
        table_html = render_to_string("attendance_form.html", context)
        return table_html

    class Meta:
        model = LeaveRequest
        fields = [
            "employee_id",
            "leave_type_id",
            "start_date",
            "start_date_breakdown",
            "end_date",
            "end_date_breakdown",
            "description",
            "attachment",
        ]
        widgets = {
            "employee_id": forms.HiddenInput(),
            'leave_type_id': forms.HiddenInput()     
        }


excluded_fields = [
    "id",
    "approved_available_days",
    "approved_carryforward_days",
    "created_at",
    "attachment",
]


class AvailableLeaveColumnExportForm(forms.Form):
    model_fields = AvailableLeave._meta.get_fields()
    field_choices = [
        (field.name, field.verbose_name)
        for field in model_fields
        if hasattr(field, "verbose_name") and field.name not in excluded_fields
    ]
    selected_fields = forms.MultipleChoiceField(
        choices=field_choices,
        widget=forms.CheckboxSelectMultiple,
        initial=[
            "employee_id",
            "leave_type_id",
            "available_days",
            "carryforward_days",
            "total_leave_days",
        ],
    )


class HolidaysColumnExportForm(forms.Form):
    model_fields = Holiday._meta.get_fields()
    field_choices = [
        (field.name, field.verbose_name)
        for field in model_fields
        if hasattr(field, "verbose_name") and field.name not in excluded_fields
    ]
    selected_fields = forms.MultipleChoiceField(
        choices=field_choices,
        widget=forms.CheckboxSelectMultiple,
        initial=[
            "name",
            "start_date",
            "end_date",
            "recurring",
        ],
    )


class RejectForm(forms.Form):
    reason = forms.CharField(
        label=_("Rejection Reason"),
        widget=forms.Textarea(attrs={"rows": 4, "class": "p-4 oh-input w-100"}),
    )

    class Meta:
        model = LeaveRequest
        fields = ["reject_reason"]


class UserLeaveRequestCreationForm(ModelForm):
    start_date = forms.DateField(widget=forms.DateInput(attrs={"type": "date"}))
    end_date = forms.DateField(widget=forms.DateInput(attrs={"type": "date"}))

    def as_p(self, *args, **kwargs):
        """
        Render the form fields as HTML table rows with Bootstrap styling.
        """
        context = {"form": self}
        table_html = render_to_string("attendance_form.html", context)
        return table_html
    
    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get("start_date")
        end_date = cleaned_data.get("end_date")
        employee_id = cleaned_data.get("employee_id")
        leave_type_id = cleaned_data.get("leave_type_id")
        start_date_breakdown = cleaned_data.get("start_date_breakdown")
        end_date_breakdown = cleaned_data.get('end_date_breakdown')
        overlapping_requests = LeaveRequest.objects.filter(
            employee_id=employee_id, start_date__lte=end_date, end_date__gte=start_date
        )

        if not start_date <= end_date:
            raise forms.ValidationError(
                _("End date should not be less than start date.")
            )
        if start_date == end_date:
            if start_date_breakdown != end_date_breakdown:
                raise forms.ValidationError(
                    _("There is a mismatch in the breakdown of the start date and end date.")
                )
        if not AvailableLeave.objects.filter(
            employee_id=employee_id, leave_type_id=leave_type_id
        ).exists():
            raise forms.ValidationError(_("Employee has no leave type.."))

        if overlapping_requests.exists():
            raise forms.ValidationError(
                _("Employee has already a leave request for this date range..")
            )

        available_leave = AvailableLeave.objects.get(
            employee_id=employee_id, leave_type_id=leave_type_id
        )
        total_leave_days = (
            available_leave.available_days + available_leave.carryforward_days
        )
        requested_days = (end_date - start_date).days + 1
        cleaned_data["requested_days"] = requested_days

        if not requested_days <= total_leave_days:
            raise forms.ValidationError(_("Employee doesn't have enough leave days.."))

        return cleaned_data

    class Meta:
        model = LeaveRequest
        fields = [
            "leave_type_id",
            "employee_id",
            "start_date",
            "start_date_breakdown",
            "end_date",
            "end_date_breakdown",
            "description",
            "attachment",
            "requested_days",
        ]
        widgets = {
            "employee_id": forms.HiddenInput(),
            'requested_days': forms.HiddenInput()     
        }


class LeaveAllocationRequestForm(ModelForm):
    def as_p(self, *args, **kwargs):
        """
        Render the form fields as HTML table rows with Bootstrap styling.
        """
        context = {"form": self}
        table_html = render_to_string("attendance_form.html", context)
        return table_html

    class Meta:
        model = LeaveAllocationRequest
        fields = [
            "leave_type_id",
            "employee_id",
            "requested_days",
            "description",
            "attachment",
        ]


class LeaveAllocationRequestRejectForm(forms.Form):
    reason = forms.CharField(
        label=_("Rejection Reason"),
        widget=forms.Textarea(attrs={"rows": 4, "class": "p-4 oh-input w-100"}),
    )

    class Meta:
        model = LeaveAllocationRequest
        fields = ["reject_reason"]


class LeaveRequestExportForm(forms.Form):
    model_fields = LeaveRequest._meta.get_fields()
    field_choices = [
        (field.name, field.verbose_name)
        for field in model_fields
        if hasattr(field, "verbose_name") and field.name not in excluded_fields
    ]

    selected_fields = forms.MultipleChoiceField(
        choices=field_choices,
        widget=forms.CheckboxSelectMultiple,
        initial=[
            "employee_id",
            "leave_type_Assignid",
            "start_date",
            "start_date_breakdown",
            "end_date",
            "end_date_breakdown",
            "requested_days",
            "description",
            "status",
        ],
    )



class AssignLeaveForm(HorillaForm):
    """
    Form for Payslip
    """
    leave_type_id = forms.ModelChoiceField(
        queryset=LeaveType.objects.all(),
        widget=forms.SelectMultiple(attrs={"class": "oh-select oh-select-2 mb-2","required": True}),
        empty_label=None,
        label="Leave Type",
        required=False,
    )
    employee_id = HorillaMultiSelectField(
        queryset=Employee.objects.all(),
        widget=HorillaMultiSelectWidget(
            filter_route_name="employee-widget-filter",
            filter_class=EmployeeFilter,
            filter_instance_contex_name="f",
            filter_template_path="employee_filters.html",
            required = True,
        ),
        label="Employee",
    )

    def clean(self):
        cleaned_data = super().clean()
        employee_id = cleaned_data.get("employee_id")
        leave_type_id = cleaned_data.get("leave_type_id")

        if not employee_id :
            raise forms.ValidationError(
                {
                    "employee_id": "This field is required"
                }
            )
        if not leave_type_id :
            raise forms.ValidationError(
                {
                    "leave_type_id": "This field is required"
                }
            )
        return cleaned_data

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        reload_queryset(self.fields)
        self.fields["employee_id"].widget.attrs.update(
            {"required": True, "id": uuid.uuid4()}
        ),
        self.fields['leave_type_id'].label = "Leave Type"

