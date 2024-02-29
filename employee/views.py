"""
views.py

This module contains the view functions for handling HTTP requests and rendering
responses in your application.

Each view function corresponds to a specific URL route and performs the necessary
actions to handle the request, process data, and generate a response.

This module is part of the recruitment project and is intended to
provide the main entry points for interacting with the application's functionality.
"""

import os
import json
import calendar
from datetime import datetime, timedelta, date
from collections import defaultdict
from urllib.parse import parse_qs
import pandas as pd
from django.db.models import Q
from django.db.models import F, ProtectedError
from django.conf import settings
from django.contrib import messages
from django.core.paginator import Paginator
from django.shortcuts import render, redirect
from django.utils.translation import gettext as __
from django.contrib.auth.models import User
from django.views.decorators.http import require_http_methods
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse, QueryDict
from asset.models import AssetAssignment, AssetRequest
from django.utils.translation import gettext_lazy as _
from attendance.models import Attendance, AttendanceOverTime
from notifications.signals import notify
from horilla.decorators import (
    permission_required,
    login_required,
    hx_request_required,
    manager_can_enter,
)
from base.models import (
    Department,
    JobPosition,
    JobRole,
    RotatingShiftAssign,
    RotatingWorkTypeAssign,
    ShiftRequest,
    WorkType,
    EmployeeShift,
    EmployeeType,
    Company,
    WorkTypeRequest,
)
from base.methods import (
    filtersubordinates,
    filtersubordinatesemployeemodel,
    get_key_instances,
    sortby,
)
from employee.filters import EmployeeFilter, EmployeeReGroup
from employee.forms import (
    EmployeeExportExcelForm,
    EmployeeForm,
    EmployeeBankDetailsForm,
    EmployeeWorkInformationForm,
    EmployeeWorkInformationUpdateForm,
    EmployeeBankDetailsUpdateForm,
    excel_columns,
)
from employee.models import Employee, EmployeeWorkInformation, EmployeeBankDetails
from payroll.models.models import Contract
from pms.models import Feedback
from recruitment.models import Candidate


# Create your views here.
@login_required
def get_language_code(request):
    language_code = request.LANGUAGE_CODE
    return JsonResponse({"language_code": language_code})


@login_required
def employee_profile(request):
    """
    This method is used to view own profile of employee.
    """
    user = request.user
    employee = request.user.employee_get
    user_leaves = employee.available_leave.all()
    employee = Employee.objects.filter(employee_user_id=user).first()
    assets = AssetAssignment.objects.filter(assigned_to_employee_id=employee)
    feedback_own = Feedback.objects.filter(employee_id=employee, archive=False)
    today = datetime.today()
    return render(
        request,
        "employee/profile/profile_view.html",
        {
            "employee": employee,
            "user_leaves": user_leaves,
            "assets": assets,
            "self_feedback": feedback_own,
            "current_date": today,
        },
    )


@login_required
def self_info_update(request):
    """
    This method is used to update own profile of an employee.
    """
    user = request.user
    employee = Employee.objects.filter(employee_user_id=user).first()
    bank_form = EmployeeBankDetailsForm(
        instance=EmployeeBankDetails.objects.filter(employee_id=employee).first()
    )
    form = EmployeeForm(instance=Employee.objects.filter(employee_user_id=user).first())
    if request.POST:
        if request.POST.get("employee_first_name") is not None:
            instance = Employee.objects.filter(employee_user_id=request.user).first()
            form = EmployeeForm(request.POST, instance=instance)
            if form.is_valid():
                instance = form.save(commit=False)
                instance.employee_user_id = user
                instance.save()
                messages.success(request, _("Profile updated."))
        elif request.POST.get("any_other_code1") is not None:
            instance = EmployeeBankDetails.objects.filter(employee_id=employee).first()
            bank_form = EmployeeBankDetailsForm(request.POST, instance=instance)
            if bank_form.is_valid():
                instance = bank_form.save(commit=False)
                instance.employee_id = employee
                instance.save()
                messages.success(request, _("Bank details updated."))
    return render(
        request,
        "employee/profile/profile.html",
        {
            "form": form,
            "bank_form": bank_form,
        },
    )


@login_required
@manager_can_enter("employee.view_employee")
def employee_view_individual(request, obj_id, **kwargs):
    """
    This method is used to view profile of an employee.
    """
    employee = Employee.objects.get(id=obj_id)
    employee_leaves = employee.available_leave.all()
    user = Employee.objects.filter(employee_user_id=request.user).first()
    if user and user.reporting_manager.filter(
        employee_id=employee
    ).exists() or request.user.has_perm("employee.view_employee"):
        return render(
            request,
            "employee/view/individual.html",
            {
                "employee": employee,
                "employee_leaves": employee_leaves,
            },
        )
    return HttpResponseRedirect(
        request.META.get("HTTP_REFERER", "/employee/employee-view")
    )


@login_required
def contract_tab(request, obj_id, **kwargs):
    """
    This method is used to view profile of an employee.
    """
    employee = Employee.objects.get(id=obj_id)
    employee_leaves = employee.available_leave.all()
    user = Employee.objects.filter(employee_user_id=request.user).first()
    contracts = Contract.objects.filter(employee_id=obj_id)
    return render(
        request,
        "tabs/personal-tab.html",
        {
            "employee": employee,
            "employee_leaves": employee_leaves,
            "contracts": contracts,
        },
    )


@login_required
def asset_tab(request, emp_id):
    """
    This function is used to view asset tab of an employee in employee individual view.
    Parameters:
    request (HttpRequest): The HTTP request object.
    emp_id (int): The id of the employee.

    Returns: return asset-tab template

    """
    assets_requests = AssetRequest.objects.filter(
        requested_employee_id=emp_id, asset_request_status="Requested"
    )
    assets = AssetAssignment.objects.filter(assigned_to_employee_id=emp_id)
    context = {
        "assets": assets,
        "requests": assets_requests,
        "employee": emp_id,
    }
    return render(request, "tabs/asset-tab.html", context=context)


@login_required
def profile_asset_tab(request, emp_id):
    """
    This function is used to view asset tab of an employee in employee profile view.

    Parameters:
    request (HttpRequest): The HTTP request object.
    emp_id (int): The id of the employee.

    Returns: return profile-asset-tab template

    """
    assets = AssetAssignment.objects.filter(assigned_to_employee_id=emp_id)
    context = {
        "assets": assets,
    }
    return render(request, "tabs/profile-asset-tab.html", context=context)


@login_required
def asset_request_tab(request, emp_id):
    """
    This function is used to view asset request tab of an employee in employee individual view.

    Parameters:
    request (HttpRequest): The HTTP request object.
    emp_id (int): The id of the employee.

    Returns: return asset-request-tab template

    """
    assets_requests = AssetRequest.objects.filter(requested_employee_id=emp_id)
    context = {
        "asset_requests": assets_requests,
    }
    return render(request, "tabs/asset-request-tab.html", context=context)


@login_required
def performance_tab(request, emp_id):
    """
    This function is used to view performance tab of an employee in employee individual & profile view.

    Parameters:
    request (HttpRequest): The HTTP request object.
    emp_id (int): The id of the employee.

    Returns: return performance-tab template

    """
    feedback_own = Feedback.objects.filter(employee_id=emp_id, archive=False)
    today = datetime.today()
    context = {
        "self_feedback": feedback_own,
        "current_date": today,
    }
    return render(request, "tabs/performance-tab.html", context=context)


@login_required
def profile_attendance_tab(request):
    """
    This function is used to view attendance tab of an employee in profile view.

    Parameters:
    request (HttpRequest): The HTTP request object.
    emp_id (int): The id of the employee.

    Returns: return asset-request-tab template

    """
    user = request.user
    employee = user.employee_get
    employee_attendances = employee.employee_attendances.all()
    context = {
        "attendances": employee_attendances,
    }
    return render(request, "tabs/profile-attendance-tab.html", context)


@login_required
@manager_can_enter("employee.view_employee")
def attendance_tab(request, emp_id):
    """
    This function is used to view attendance tab of an employee in individual view.

    Parameters:
    request (HttpRequest): The HTTP request object.
    emp_id (int): The id of the employee.

    Returns: return attendance-tab template
    """

    requests = Attendance.objects.filter(
        is_validate_request=True,
        employee_id=emp_id,
    )
    validate_attendances = Attendance.objects.filter(
        attendance_validated=False, employee_id=emp_id
    )
    accounts = AttendanceOverTime.objects.filter(employee_id=emp_id)

    context = {
        "requests": requests,
        "accounts": accounts,
        "validate_attendances": validate_attendances,
    }
    return render(request, "tabs/attendance-tab.html", context=context)


@login_required
def shift_tab(request, emp_id):
    """
    This function is used to view shift tab of an employee in employee individual & profile view.

    Parameters:
    request (HttpRequest): The HTTP request object.
    emp_id (int): The id of the employee.

    Returns: return shift-tab template
    """

    work_type_requests = WorkTypeRequest.objects.filter(employee_id=emp_id)
    rshift_assign = RotatingShiftAssign.objects.filter(
        is_active=True, employee_id=emp_id
    )
    rwork_type_assign = RotatingWorkTypeAssign.objects.filter(employee_id=emp_id)
    shift_requests = ShiftRequest.objects.filter(employee_id=emp_id)

    context = {
        "work_data": work_type_requests,
        "rshift_assign": rshift_assign,
        "rwork_type_assign": rwork_type_assign,
        "shift_data": shift_requests,
        "employee": emp_id,
    }
    return render(request, "tabs/shift-tab.html", context=context)


@login_required
@require_http_methods(["POST"])
def employee_profile_bank_details(request):
    """
    This method is used to fill self bank details
    """
    employee = request.user.employee_get
    instance = EmployeeBankDetails.objects.filter(employee_id=employee).first()
    form = EmployeeBankDetailsUpdateForm(request.POST, instance=instance)
    if form.is_valid():
        bank_info = form.save(commit=False)
        bank_info.employee_id = employee
        bank_info.save()
        messages.success(request, _("Bank details updated"))
    return HttpResponseRedirect(request.META.get("HTTP_REFERER"))


@login_required
@permission_required("employee.view_profile")
def employee_profile_update(request):
    """
    This method is used update own profile of the requested employee
    """

    employee_user = request.user
    employee = Employee.objects.get(employee_user_id=employee_user)
    if employee_user.has_perm("employee.change_profile"):
        if request.method == "POST":
            form = EmployeeForm(request.POST, request.FILES, instance=employee)
            if form.is_valid():
                form.save()
                messages.success(request, _("Profile updated."))
    return redirect("/employee/employee-profile")


@login_required
@permission_required("delete_group")
@require_http_methods(["POST"])
def employee_user_group_assign_delete(_, obj_id):
    """
    This method is used to delete user group assign
    """
    user = User.objects.get(id=obj_id)
    user.groups.clear()
    return redirect("/employee/employee-user-group-assign-view")


def paginator_qry(qryset, page_number):
    """
    This method is used to paginate query set
    """
    paginator = Paginator(qryset, 50)
    qryset = paginator.get_page(page_number)
    return qryset


@login_required
@manager_can_enter("employee.view_employee")
def employee_view(request):
    """
    This method is used to render template for view all employee
    """
    view_type = request.GET.get("view")
    previous_data = request.GET.urlencode()
    page_number = request.GET.get("page")
    filter_obj = EmployeeFilter(
        request.GET, queryset=Employee.objects.all()
    )
    export_form = EmployeeExportExcelForm()
    employees = filtersubordinatesemployeemodel(
        request, filter_obj.qs, "employee.view_employee"
    )
    data_dict = parse_qs(previous_data)
    get_key_instances(Employee, data_dict)
    emp = Employee.objects.all()
    return render(
        request,
        "employee_personal_info/employee_view.html",
        {
            "data": paginator_qry(employees, page_number),
            "pd": previous_data,
            "f": filter_obj,
            "export_filter": EmployeeFilter(queryset=employees),
            "export_form": export_form,
            "view_type": view_type,
            "filter_dict": data_dict,
            "emp": emp,
            "gp_fields": EmployeeReGroup.fields,
        },
    )


@login_required
@permission_required("employee.add_employee")
def employee_view_new(request):
    """
    This method is used to render form to create a new employee.
    """
    form = EmployeeForm()
    work_form = EmployeeWorkInformationForm()
    bank_form = EmployeeBankDetailsForm()
    filter_obj = EmployeeFilter(queryset=Employee.objects.all())
    return render(
        request,
        "employee/create_form/form_view.html",
        {"form": form, "work_form": work_form, "bank_form": bank_form, "f": filter_obj},
    )


@login_required
@manager_can_enter("employee.change_employee")
def employee_view_update(request, obj_id, **kwargs):
    """
    This method is used to render update form for employee.
    """
    user = Employee.objects.filter(employee_user_id=request.user).first()
    employee = Employee.objects.filter(id=obj_id).first()
    if user and user.reporting_manager.filter(
        employee_id=employee
    ).exists() or request.user.has_perm("employee.change_employee"):
        form = EmployeeForm(instance=employee)
        work_form = EmployeeWorkInformationForm(
            instance=EmployeeWorkInformation.objects.filter(
                employee_id=employee
            ).first()
        )
        bank_form = EmployeeBankDetailsForm(
            instance=EmployeeBankDetails.objects.filter(employee_id=employee).first()
        )
        if request.POST:
            if request.POST.get("employee_first_name") is not None:
                form = EmployeeForm(request.POST, instance=employee)
                if form.is_valid():
                    form.save()
                    messages.success(
                        request, _("Employee personal information updated.")
                    )
            elif request.POST.get("reporting_manager_id") is not None:
                instance = EmployeeWorkInformation.objects.filter(
                    employee_id=employee
                ).first()
                work_form = EmployeeWorkInformationUpdateForm(
                    request.POST, instance=instance
                )
                if work_form.is_valid():
                    instance = work_form.save(commit=False)
                    instance.employee_id = employee
                    instance.save()
                    notify.send(
                        request.user.employee_get,
                        recipient=instance.employee_id.employee_user_id,
                        verb="Your work details has been updated.",
                        verb_ar="تم تحديث تفاصيل عملك.",
                        verb_de="Ihre Arbeitsdetails wurden aktualisiert.",
                        verb_es="Se han actualizado los detalles de su trabajo.",
                        verb_fr="Vos informations professionnelles ont été mises à jour.",
                        redirect="/employee/employee-profile",
                        icon="briefcase",
                    )
                    messages.success(request, _("Employee work information updated."))
            elif request.POST.get("any_other_code1"):
                instance = EmployeeBankDetails.objects.filter(
                    employee_id=employee
                ).first()
                bank_form = EmployeeBankDetailsUpdateForm(
                    request.POST, instance=instance
                )
                if bank_form.is_valid():
                    instance = bank_form.save(commit=False)
                    instance.employee_id = employee
                    instance.save()
                    messages.success(request, _("Employee bank details updated."))
        return render(
            request,
            "employee/update_form/form_view.html",
            {"form": form, "work_form": work_form, "bank_form": bank_form},
        )
    return HttpResponseRedirect(
        request.META.get("HTTP_REFERER", "/employee/employee-view")
    )


@login_required
@require_http_methods(["POST"])
@permission_required("employee.change_employee")
def update_profile_image(request, obj_id):
    """
    This method is used to upload a profile image
    """
    try:
        employee = Employee.objects.get(id=obj_id)
        img = request.FILES["employee_profile"]
        employee.employee_profile = img
        employee.save()
        messages.success(request, _("Profile image updated."))
    except Exception:
        messages.error(request, _("No image chosen."))
    response = render(
        request,
        "employee/profile/profile_modal.html",
    )
    return HttpResponse(
        response.content.decode("utf-8") + "<script>location.reload();</script>"
    )


@login_required
@require_http_methods(["POST"])
def update_own_profile_image(request):
    """
    This method is used to update own profile image from profile view form
    """
    employee = request.user.employee_get
    img = request.FILES.get("employee_profile")
    employee.employee_profile = img
    employee.save()
    messages.success(request, _("Profile image updated."))
    response = render(
        request,
        "employee/profile/profile_modal.html",
    )
    return HttpResponse(
        response.content.decode("utf-8") + "<script>location.reload();</script>"
    )


@login_required
@require_http_methods(["DELETE"])
@permission_required("employee.change_employee")
def remove_profile_image(request, obj_id):
    """
    This method is used to remove uploaded image
    Args: obj_id : Employee model instance id
    """
    employee = Employee.objects.get(id=obj_id)
    if employee.employee_profile.name == "":
        messages.info(request, _("No profile image to remove."))
        response = render(
            request,
            "employee/profile/profile_modal.html",
        )
        return HttpResponse(
            response.content.decode("utf-8") + "<script>location.reload();</script>"
        )
    file_path = employee.employee_profile.path
    absolute_path = os.path.join(settings.MEDIA_ROOT, file_path)
    os.remove(absolute_path)
    employee.employee_profile = None
    employee.save()
    messages.success(request, _("Profile image removed."))
    response = render(
        request,
        "employee/profile/profile_modal.html",
    )
    return HttpResponse(
        response.content.decode("utf-8") + "<script>location.reload();</script>"
    )


@login_required
@require_http_methods(["DELETE"])
def remove_own_profile_image(request):
    """
    This method is used to remove own profile image
    """
    employee = request.user.employee_get
    if employee.employee_profile.name == "":
        messages.info(request, _("No profile image to remove."))
        response = render(
            request,
            "employee/profile/profile_modal.html",
        )
        return HttpResponse(
            response.content.decode("utf-8") + "<script>location.reload();</script>"
        )
    file_path = employee.employee_profile.path
    absolute_path = os.path.join(settings.MEDIA_ROOT, file_path)
    os.remove(absolute_path)
    employee.employee_profile = None
    employee.save()

    messages.success(request, _("Profile image removed."))
    response = render(
        request,
        "employee/profile/profile_modal.html",
    )
    return HttpResponse(
        response.content.decode("utf-8") + "<script>location.reload();</script>"
    )


@login_required
@manager_can_enter("employee.change_employee")
@require_http_methods(["POST"])
def employee_update_personal_info(request, obj_id=None):
    """
    This method is used to update employee's personal info.
    """
    employee = Employee.objects.filter(id=obj_id).first()
    form = EmployeeForm(request.POST, instance=employee)
    if form.is_valid():
        form.save()
        if obj_id is None:
            messages.success(request, _("New Employee Added."))
            form = EmployeeForm(request.POST, instance=form.instance)
            work_form = EmployeeWorkInformationForm(
                instance=EmployeeWorkInformation.objects.filter(
                    employee_id=employee
                ).first()
            )
            bank_form = EmployeeBankDetailsForm(
                instance=EmployeeBankDetails.objects.filter(
                    employee_id=employee
                ).first()
            )
            return redirect(
                f"employee-view-update/{form.instance.id}/",
                data={"form": form, "work_form": work_form, "bank_form": bank_form},
            )
        return HttpResponse(
            """
                <div class="oh-alert-container">
                    <div class="oh-alert oh-alert--animated oh-alert--success">
                        Personal Info updated
                    </div> 
                </div>
                
        """
        )
    if obj_id is None:
        return render(
            request,
            "employee/create_form/form_view.html",
            {
                "form": form,
            },
        )
    errors = "\n".join(
        [
            f"<li>{form.fields.get(field, field).label}: {', '.join(errors)}</li>"
            for field, errors in form.errors.items()
        ]
    )
    return HttpResponse(f'<ul class="alert alert-danger">{errors}</ul>')


@login_required
@manager_can_enter("employee.change_employeeworkinformation")
@require_http_methods(["POST"])
def employee_update_work_info(request, obj_id=None):
    """
    This method is used to update employee work info
    """
    employee = Employee.objects.filter(id=obj_id).first()
    form = EmployeeWorkInformationForm(
        request.POST,
        instance=EmployeeWorkInformation.objects.filter(employee_id=employee).first(),
    )
    form.fields["employee_id"].required = False
    form.employee_id = employee
    if form.is_valid() and employee is not None:
        work_info = form.save(commit=False)
        work_info.employee_id = employee
        work_info.save()
        return HttpResponse(
            """
            
                <div class="oh-alert-container">
                    <div class="oh-alert oh-alert--animated oh-alert--success">
                        Personal Info updated
                    </div> 
                </div>
                
        """
        )
    errors = "\n".join(
        [
            f"<li>{form.fields.get(field, field).label}: {', '.join(errors)}</li>"
            for field, errors in form.errors.items()
        ]
    )
    return HttpResponse(f'<ul class="alert alert-danger">{errors}</ul>')


@login_required
@manager_can_enter("employee.change_employeebankdetails")
@require_http_methods(["POST"])
def employee_update_bank_details(request, obj_id=None):
    """
    This method is used to render form to create employee's bank information.
    """
    employee = Employee.objects.filter(id=obj_id).first()
    form = EmployeeBankDetailsForm(
        request.POST,
        instance=EmployeeBankDetails.objects.filter(employee_id=employee).first(),
    )
    if form.is_valid() and employee is not None:
        bank_info = form.save(commit=False)
        bank_info.employee_id = employee
        bank_info.save()
        return HttpResponse(
            """
            <div class="oh-alert-container">
                <div class="oh-alert oh-alert--animated oh-alert--success">
                    Bank details updated
                </div> 
            </div>
        """
        )
    errors = "\n".join(
        [
            f"<li>{form.fields.get(field, field).label}: {', '.join(errors)}</li>"
            for field, errors in form.errors.items()
        ]
    )
    return HttpResponse(f'<ul class="alert alert-danger">{errors}</ul>')


@login_required
@manager_can_enter("employee.view_employee")
def employee_filter_view(request):
    """
    This method is used to filter employee.
    """
    previous_data = request.GET.urlencode()
    field = request.GET.get("field")
    employees = EmployeeFilter(request.GET).qs
    if request.GET.get("is_active") != "False":
        employees=employees.filter(is_active=True)
    employees = filtersubordinatesemployeemodel(
        request, employees, "employee.view_employee"
    )
    page_number = request.GET.get("page")
    view = request.GET.get("view")
    data_dict = parse_qs(previous_data)
    get_key_instances(Employee, data_dict)
    template = "employee_personal_info/employee_card.html"
    if view == "list":
        template = "employee_personal_info/employee_list.html"
    if field != "" and field is not None:
        field_copy = field.replace(".", "__")
        employees = employees.order_by(field_copy)
        employees = employees.exclude(employee_work_info__isnull=True)
        template = "employee_personal_info/group_by.html"

    return render(
        request,
        template,
        {
            "data": paginator_qry(employees, page_number),
            "f": EmployeeFilter(request.GET),
            "pd": previous_data,
            "field": field,
            "filter_dict": data_dict,
        },
    )


@login_required
@manager_can_enter("employee.view_employee")
@hx_request_required
def employee_card(request):
    """
    This method renders card template to view all employees.
    """
    previous_data = request.GET.urlencode()
    search = request.GET.get("search")
    if isinstance(search, type(None)):
        search = ""
    employees = filtersubordinatesemployeemodel(
        request, Employee.objects.all(), "employee.view_employee"
    )
    if request.GET.get("is_active") is None:
        filter_obj = EmployeeFilter(
            request.GET,
            queryset=employees.filter(
                employee_first_name__icontains=search, is_active=True
            ),
        )
    else:
        filter_obj = EmployeeFilter(
            request.GET,
            queryset=employees.filter(employee_first_name__icontains=search),
        )
    page_number = request.GET.get("page")
    employees = sortby(request, filter_obj.qs, "orderby")
    return render(
        request,
        "employee_personal_info/employee_card.html",
        {
            "data": paginator_qry(employees, page_number),
            "f": filter_obj,
            "pd": previous_data,
        },
    )


@login_required
@manager_can_enter("employee.view_employee")
@hx_request_required
def employee_list(request):
    """
    This method renders template to view all employees
    """
    previous_data = request.GET.urlencode()
    search = request.GET.get("search")
    if isinstance(search, type(None)):
        search = ""
    if request.GET.get("is_active") is None:
        filter_obj = EmployeeFilter(
            request.GET,
            queryset=Employee.objects.filter(
                employee_first_name__icontains=search, is_active=True
            ),
        )
    else:
        filter_obj = EmployeeFilter(
            request.GET,
            queryset=Employee.objects.filter(employee_first_name__icontains=search),
        )
    employees = filtersubordinatesemployeemodel(
        request, filter_obj.qs, "employee.view_employee"
    )
    employees = sortby(request, employees, "orderby")
    page_number = request.GET.get("page")
    return render(
        request,
        "employee_personal_info/employee_list.html",
        {
            "data": paginator_qry(employees, page_number),
            "f": filter_obj,
            "pd": previous_data,
        },
    )


@login_required
@hx_request_required
@manager_can_enter("employee.view_employee")
def employee_update(request, obj_id):
    """
    This method is used to update employee if the form is valid
    args:
        obj_id : employee id
    """
    employee = Employee.objects.get(id=obj_id)
    form = EmployeeForm(instance=employee)
    work_info = EmployeeWorkInformation.objects.filter(employee_id=employee).first()
    bank_info = EmployeeBankDetails.objects.filter(employee_id=employee).first()
    work_form = EmployeeWorkInformationForm()
    bank_form = EmployeeBankDetailsUpdateForm()
    if work_info is not None:
        work_form = EmployeeWorkInformationForm(instance=work_info)
    if bank_info is not None:
        bank_form = EmployeeBankDetailsUpdateForm(instance=bank_info)
    if request.method == "POST":
        if request.user.has_perm("employee.change_employee"):
            form = EmployeeForm(request.POST, request.FILES, instance=employee)
            if form.is_valid():
                form.save()
                messages.success(request, _("Employee updated."))
    return render(
        request,
        "employee_personal_info/employee_update_form.html",
        {"form": form, "work_form": work_form, "bank_form": bank_form},
    )


@login_required
@permission_required("employee.delete_employee")
@require_http_methods(["POST"])
def employee_delete(request, obj_id):
    """
    This method is used to delete employee
    args:
        id  : employee id
    """

    try:
        view = request.POST.get("view")
        employee = Employee.objects.get(id=obj_id)
        user = employee.employee_user_id
        user.delete()
        messages.success(request, _("Employee deleted"))
    except Employee.DoesNotExist:
        messages.error(request, _("Employee not found."))
    except ProtectedError as e:
        model_verbose_names_set = set()
        for obj in e.protected_objects:
            model_verbose_names_set.add(__(obj._meta.verbose_name.capitalize()))
        model_names_str = ", ".join(model_verbose_names_set)
        messages.error(
            request, _("This employee already related in {}.".format(model_names_str))
        )
    return HttpResponseRedirect(request.META.get("HTTP_REFERER", f"/view={view}"))


@login_required
@permission_required("employee.delete_employee")
def employee_bulk_delete(request):
    """
    This method is used to delete set of Employee instances
    """
    ids = request.POST["ids"]
    ids = json.loads(ids)
    for employee_id in ids:
        try:
            employee = Employee.objects.get(id=employee_id)
            user = employee.employee_user_id
            user.delete()
            messages.success(
                request, _("%(employee)s deleted.") % {"employee": employee}
            )
        except Employee.DoesNotExist:
            messages.error(request, _("Employee not found."))
        except ProtectedError:
            messages.error(
                request, _("You cannot delete %(employee)s.") % {"employee": employee}
            )

    return JsonResponse({"message": "Success"})


@login_required
@permission_required("employee.delete_employee")
@require_http_methods(["POST"])
def employee_bulk_archive(request):
    """
    This method is used to archive bulk of Employee instances
    """
    ids = request.POST["ids"]
    ids = json.loads(ids)
    is_active = False
    if request.GET.get("is_active") == "True":
        is_active = True
    for employee_id in ids:
        employee = Employee.objects.get(id=employee_id)
        employee.is_active = is_active
        employee.employee_user_id.is_active = is_active
        employee.save()
        message = _("archived")
        if is_active:
            message = _("un-archived")
        messages.success(request, f"{employee} is {message}")
    return JsonResponse({"message": "Success"})


@login_required
@permission_required("employee.delete_employee")
def employee_archive(request, obj_id):
    """
    This method is used to archive employee instance
    Args:
            obj_id : Employee instance id
    """
    employee = Employee.objects.get(id=obj_id)
    employee.is_active = not employee.is_active
    employee.employee_user_id.is_active = not employee.is_active
    employee.save()
    message = "Employee un-archived"
    if not employee.is_active:
        message = _("Employee archived")
    messages.success(request, message)
    return HttpResponseRedirect(request.META.get("HTTP_REFERER"))


@login_required
@manager_can_enter("employee.view_employee")
def employee_search(request):
    """
    This method is used to search employee
    """
    search = request.GET["search"]
    view = request.GET["view"]
    previous_data = request.GET.urlencode()
    employees = EmployeeFilter(request.GET).qs
    if search == "":
        employees = employees.filter(is_active=True)
    page_number = request.GET.get("page")
    template = "employee_personal_info/employee_card.html"
    if view == "list":
        template = "employee_personal_info/employee_list.html"
    employees = filtersubordinatesemployeemodel(
        request, employees, "employee.view_employee"
    )
    employees = sortby(request, employees, "orderby")
    data_dict = parse_qs(previous_data)
    get_key_instances(Employee, data_dict)
    return render(
        request,
        template,
        {
            "data": paginator_qry(employees, page_number),
            "pd": previous_data,
            "filter_dict": data_dict,
        },
    )


@login_required
@manager_can_enter("employee.add_employeeworkinformation")
@require_http_methods(["POST"])
def employee_work_info_view_create(request, obj_id):
    """
    This method is used to create employee work information from employee single view template
    args:
        obj_id : employee instance id
    """

    employee = Employee.objects.get(id=obj_id)
    form = EmployeeForm(instance=employee)

    work_form = EmployeeWorkInformationUpdateForm(request.POST)

    bank_form = EmployeeBankDetailsUpdateForm()
    bank_form_instance = EmployeeBankDetails.objects.filter(
        employee_id=employee
    ).first()
    if bank_form_instance is not None:
        bank_form = EmployeeBankDetailsUpdateForm(
            instance=employee.employee_bank_details
        )

    if work_form.is_valid():
        work_info = work_form.save(commit=False)
        work_info.employee_id = employee
        work_info.save()
        messages.success(request, _("Created work information"))
    return render(
        request,
        "employee_personal_info/employee_update_form.html",
        {"form": form, "work_form": work_form, "bank_form": bank_form},
    )


@login_required
@manager_can_enter("employee.change_employeeworkinformation")
@require_http_methods(["POST"])
def employee_work_info_view_update(request, obj_id):
    """
    This method is used to update employee work information from single view template
    args:
        obj_id  : employee work information id
    """

    work_information = EmployeeWorkInformation.objects.get(id=obj_id)
    form = EmployeeForm(instance=work_information.employee_id)
    bank_form = EmployeeBankDetailsUpdateForm(
        instance=work_information.employee_id.employee_bank_details
    )
    work_form = EmployeeWorkInformationUpdateForm(
        request.POST,
        instance=work_information,
    )
    if work_form.is_valid():
        work_form.save()
        messages.success(request, _("Work Information Updated Successfully"))
    return render(
        request,
        "employee_personal_info/employee_update_form.html",
        {"form": form, "work_form": work_form, "bank_form": bank_form},
    )


@login_required
@manager_can_enter("employee.add_employeebankdetails")
@require_http_methods(["POST"])
def employee_bank_details_view_create(request, obj_id):
    """
    This method used to create bank details object from the view template
    args:
        obj_id : employee instance id
    """
    employee = Employee.objects.get(id=obj_id)
    form = EmployeeForm(instance=employee)
    bank_form = EmployeeBankDetailsUpdateForm(request.POST)
    work_form_instance = EmployeeWorkInformation.objects.filter(
        employee_id=employee
    ).first()
    work_form = EmployeeWorkInformationUpdateForm()
    if work_form_instance is not None:
        work_form = EmployeeWorkInformationUpdateForm(instance=work_form_instance)
    if bank_form.is_valid():
        bank_instance = bank_form.save(commit=False)
        bank_instance.employee_id = employee
        bank_instance.save()
        messages.success(request, _("Bank Details Created Successfully"))
    return render(
        request,
        "employee_personal_info/employee_update_form.html",
        {"form": form, "work_form": work_form, "bank_form": bank_form},
    )


@login_required
@manager_can_enter("employee.change_employeebankdetails")
@require_http_methods(["POST"])
def employee_bank_details_view_update(request, obj_id):
    """
    This method is used to update employee bank details.
    """
    employee_bank_instance = EmployeeBankDetails.objects.get(id=obj_id)
    form = EmployeeForm(instance=employee_bank_instance.employee_id)
    work_form = EmployeeWorkInformationUpdateForm(
        instance=employee_bank_instance.employee_id.employee_work_info
    )
    bank_form = EmployeeBankDetailsUpdateForm(
        request.POST, instance=employee_bank_instance
    )
    if bank_form.is_valid():
        bank_instance = bank_form.save(commit=False)
        bank_instance.employee_id = employee_bank_instance.employee_id
        bank_instance.save()
        messages.success(request, _("Bank Details Updated Successfully"))
    return render(
        request,
        "employee_personal_info/employee_update_form.html",
        {"form": form, "work_form": work_form, "bank_form": bank_form},
    )


@login_required
@permission_required("employee.delete_employeeworkinformation")
@require_http_methods(["POST", "DELETE"])
def employee_work_information_delete(request, obj_id):
    """
    This method is used to delete employee work information
    args:
        obj_id : employee work information id
    """
    try:
        employee_work = EmployeeWorkInformation.objects.get(id=obj_id)
        employee_work.delete()
        messages.success(request, _("Employee work information deleted"))
    except EmployeeWorkInformation.DoesNotExist:
        messages.error(request, _("Employee work information not found."))
    except ProtectedError:
        messages.error(request, _("You cannot delete this Employee work information"))

    return redirect("/employee/employee-work-information-view")


@login_required
@permission_required("employee.add_employee")
def employee_import(request):
    """
    This method is used to create employee and corresponding user.
    """
    if request.method == "POST":
        file = request.FILES["file"]
        # Read the Excel file into a Pandas DataFrame
        data_frame = pd.read_excel(file)
        # Convert the DataFrame to a list of dictionaries
        employee_dicts = data_frame.to_dict("records")
        # Create or update Employee objects from the list of dictionaries
        error_list = []
        for employee_dict in employee_dicts:
            try:
                phone = employee_dict["phone"]
                email = employee_dict["email"]
                employee_full_name = employee_dict["employee_full_name"]
                existing_user = User.objects.filter(username=email).first()
                if existing_user is None:
                    employee_first_name = employee_full_name
                    employee_last_name = ""
                    if " " in employee_full_name:
                        (
                            employee_first_name,
                            employee_last_name,
                        ) = employee_full_name.split(" ", 1)

                    user = User.objects.create_user(
                        username=email,
                        email=email,
                        password=str(phone).strip(),
                        is_superuser=False,
                    )
                    employee = Employee()
                    employee.employee_user_id = user
                    employee.employee_first_name = employee_first_name
                    employee.employee_last_name = employee_last_name
                    employee.email = email
                    employee.phone = phone
                    employee.save()
            except Exception:
                error_list.append(employee_dict)
        return HttpResponse(
            """
    <div class='alert-success p-3 border-rounded'>
        Employee data has been imported successfully.
    </div>
            
    """
        )
    data_frame = pd.DataFrame(columns=["employee_full_name", "email", "phone"])
    # Export the DataFrame to an Excel file
    response = HttpResponse(content_type="application/ms-excel")
    response["Content-Disposition"] = 'attachment; filename="employee_template.xlsx"'
    data_frame.to_excel(response, index=False)
    return response


@login_required
@permission_required("employee.add_employee")
def employee_export(_):
    """
    This method is used to export employee data to xlsx
    """
    # Get the list of field names for your model
    field_names = [f.name for f in Employee._meta.get_fields() if not f.auto_created]
    field_names.remove("employee_user_id")
    field_names.remove("employee_profile")
    field_names.remove("additional_info")
    field_names.remove("is_active")

    # Get the existing employee data and convert it to a DataFrame
    employee_data = Employee.objects.values_list(*field_names)
    data_frame = pd.DataFrame(list(employee_data), columns=field_names)

    # Export the DataFrame to an Excel file

    response = HttpResponse(content_type="application/ms-excel")
    response["Content-Disposition"] = 'attachment; filename="employee_export.xlsx"'
    data_frame.to_excel(response, index=False)

    return response


def convert_nan(field, dicts):
    """
    This method is returns None or field value
    """
    field_value = dicts.get(field)
    try:
        float(field_value)
        return None
    except ValueError:
        return field_value


def work_info_import(request):
    """
    This method is used to import Employee instances and creates related objects
    """
    data_frame = pd.DataFrame(
        columns=[
            "badge_id",
            "first_name",
            "last_name",
            "phone",
            "email",
            "gender",
            "department",
            "job_position",
            "job_role",
            "work_type",
            "shift",
            "employee_type",
            "reporting_manager",
            "company",
            "location",
            "date_joining",
            "contract_end_date",
            "basic_salary",
            "salary_hour",
        ]
    )
    # Export the DataFrame to an Excel file
    response = HttpResponse(content_type="application/ms-excel")
    response["Content-Disposition"] = 'attachment; filename="work_info_template.xlsx"'
    data_frame.to_excel(response, index=False)

    if request.method == "POST" and request.FILES.get("file") is not None:
        file = request.FILES["file"]
        data_frame = pd.read_excel(file)
        work_info_dicts = data_frame.to_dict("records")
        error_lists = []
        for work_info in work_info_dicts:
            try:
                email = work_info["email"]
                phone = work_info["phone"]
                first_name = work_info["first_name"]
                last_name = work_info["last_name"]
                badge_id = convert_nan("badge_id", work_info)
                department = convert_nan("department", work_info)
                job_position = convert_nan("job_position", work_info)
                job_role = convert_nan("job_role", work_info)
                work_type = convert_nan("work_type", work_info)
                employee_type = convert_nan("employee_type", work_info)
                reporting_manager = convert_nan("reporting_manager", work_info)
                company = convert_nan("company", work_info)
                location = convert_nan("location", work_info)
                shift = convert_nan("shift", work_info)
                date_joining = convert_nan("date_joining", work_info)
                contract_end_date = convert_nan("contract_end_date", work_info)
                basic_salary = convert_nan("basic_salary", work_info)
                gender = work_info.get("gender")
                user = User.objects.filter(username=email).first()
                if user is None:
                    user = User.objects.create_user(
                        username=email,
                        email=email,
                        password=str(phone).strip(),
                        is_superuser=False,
                    )

                    employee_obj = Employee.objects.filter(
                        employee_first_name=first_name, employee_last_name=last_name
                    ).first()
                    if employee_obj is None:
                        employee_obj = Employee()
                    employee_obj.employee_user_id = user
                    employee_obj.badge_id = badge_id
                    employee_obj.employee_first_name = first_name
                    employee_obj.employee_last_name = last_name
                    employee_obj.email = email
                    employee_obj.phone = phone
                    employee_obj.gender = gender.lower()
                    employee_obj.save()
                    department_obj = Department.objects.filter(
                        department=department
                    ).first()
                    if department_obj is None:
                        department_obj = Department()
                        department_obj.department = department
                        department_obj.save()

                    job_position_obj = JobPosition.objects.filter(
                        department_id=department_obj, job_position=job_position
                    ).first()
                    if job_position_obj is None:
                        job_position_obj = JobPosition()
                        job_position_obj.department_id = department_obj
                        job_position_obj.job_position = job_position
                        job_position_obj.save()

                    job_role_obj = JobRole.objects.filter(
                        job_role=job_role, job_position_id=job_position_obj
                    ).first()
                    if job_role_obj is None:
                        job_role_obj = JobRole()
                        job_role_obj.job_position_id = job_position_obj
                        job_role_obj.job_role = job_role
                        job_role_obj.save()

                    work_type_obj = WorkType.objects.filter(work_type=work_type).first()
                    if work_type_obj is None:
                        work_type_obj = WorkType()
                        work_type_obj.work_type = work_type
                        work_type_obj.save()

                    shift_obj = EmployeeShift.objects.filter(
                        employee_shift=shift
                    ).first()
                    if shift_obj is None:
                        shift_obj = EmployeeShift()
                        shift_obj.employee_shift = shift
                        shift_obj.save()
                    employee_type_obj = EmployeeType.objects.filter(
                        employee_type=employee_type
                    ).first()
                    if employee_type_obj is None:
                        employee_type_obj = EmployeeType()
                        employee_type_obj.employee_type = employee_type
                        employee_type_obj.save()
                    manager_fname, manager_lname = "", ""
                    if isinstance(reporting_manager, str) and " " in reporting_manager:
                        manager_fname, manager_lname = reporting_manager.split(" ", 1)
                    reporting_manager_obj = Employee.objects.filter(
                        employee_first_name=manager_fname,
                        employee_last_name=manager_lname,
                    ).first()
                    company_obj = Company.objects.filter(company=company).first()
                    employee_work_info = EmployeeWorkInformation.objects.filter(
                        employee_id=employee_obj
                    ).first()
                    if employee_work_info is None:
                        employee_work_info = EmployeeWorkInformation()
                    employee_work_info.employee_id = employee_obj
                    employee_work_info.email = email
                    employee_work_info.department_id = department_obj
                    employee_work_info.job_position_id = job_position_obj
                    employee_work_info.job_role_id = job_role_obj
                    employee_work_info.employee_type_id = employee_type_obj
                    employee_work_info.reporting_manager_id = reporting_manager_obj
                    employee_work_info.company_id = company_obj
                    employee_work_info.shift_id = shift_obj
                    employee_work_info.location = location
                    employee_work_info.date_joining = date_joining
                    employee_work_info.contract_end_date = contract_end_date
                    employee_work_info.basic_salary = basic_salary
                    employee_work_info.save()
            except Exception:
                error_lists.append(work_info)
        if error_lists:
            res = defaultdict(list)
            for sub in error_lists:
                for key in sub:
                    res[key].append(sub[key])
            # df = pd.DataFrame(res)
            data_frame = pd.DataFrame(error_lists, columns=error_lists[0].keys())
            # Create an HTTP response object with the Excel file
            response = HttpResponse(content_type="application/ms-excel")
            response["Content-Disposition"] = 'attachment; filename="ImportError.xlsx"'
            data_frame.to_excel(response, index=False)
            return response
        return HttpResponse("Imported successfully")
    return response


def work_info_export(request):
    """
    This method is used to export employee data to xlsx
    """
    employees_data = {}
    selected_columns = []
    form = EmployeeExportExcelForm()
    employees = EmployeeFilter(request.GET).qs
    selected_fields = request.GET.getlist("selected_fields")
    if not selected_fields:
        selected_fields = form.fields["selected_fields"].initial
        ids = request.GET.get("ids")
        id_list = json.loads(ids)
        employees = Employee.objects.filter(id__in=id_list)
    for field in excel_columns:
        value = field[0]
        key = field[1]
        if value in selected_fields:
            selected_columns.append((value, key))
    for column_value, column_name in selected_columns:
        nested_attributes = column_value.split("__")
        employees_data[column_name] = []
        for employee in employees:
            value = employee
            for attr in nested_attributes:
                value = getattr(value, attr, None)
                if value is None:
                    break
            data = str(value) if value is not None else ""
            if data == "True":
                data = _("Yes")
            elif data == "False":
                data = _("No")
            employees_data[column_name].append(data)

    data_frame = pd.DataFrame(data=employees_data)
    response = HttpResponse(content_type="application/ms-excel")
    response["Content-Disposition"] = 'attachment; filename="employee_export.xlsx"'
    data_frame.to_excel(response, index=False)

    return response


def birthday():
    """
    This method is used to find upcoming birthday and returns the queryset
    """
    today = datetime.now().date()
    last_day_of_month = calendar.monthrange(today.year, today.month)[1]
    employees = Employee.objects.filter(
        dob__day__gte=today.day,
        dob__month=today.month,
        dob__day__lte=last_day_of_month,
    ).order_by(F("dob__day").asc(nulls_last=True))

    for employee in employees:
        employee.days_until_birthday = employee.dob.day - today.day
    return employees


@login_required
def get_employees_birthday(_):
    """
    This method is used to render all upcoming birthday employee details to fill the dashboard.
    """
    employees = birthday()
    birthdays = []
    for emp in employees:
        name = f"{emp.employee_first_name} {emp.employee_last_name}"
        dob = emp.dob.strftime("%d %b %Y")
        days_till_birthday = emp.days_until_birthday
        if days_till_birthday == 0:
            days_till_birthday = "Today"
        elif days_till_birthday == 1:
            days_till_birthday = "Tomorrow"
        else:
            days_till_birthday = f"In {days_till_birthday} Days"
        try:
            path = emp.employee_profile.url
        except:
            path = f"https://ui-avatars.com/api/?\
                name={emp.employee_first_name}+{emp.employee_last_name}&background=random"
        birthdays.append(
            {
                "profile": path,
                "name": name,
                "dob": dob,
                "daysUntilBirthday": days_till_birthday,
            }
        )
    return JsonResponse({"birthdays": birthdays})


@login_required
@manager_can_enter("employee.view_employee")
def dashboard(request):
    """
    This method is used to render individual dashboard for employee module
    """
    upcoming_birthdays = birthday()
    employees = Employee.objects.all()
    employees = filtersubordinates(request, employees, "employee.view_employee")
    active_employees = employees.filter(is_active=True)
    inactive_employees = employees.filter(is_active=False)
    active_ratio = 0
    inactive_ratio = 0
    if employees.exists():
        active_ratio = f"{(len(active_employees) / len(employees)) * 100:.1f}"
        inactive_ratio = f"{(len(inactive_employees) / len(employees)) * 100:.1f}"

    return render(
        request,
        "employee/dashboard/dashboard_employee.html",
        {
            "birthdays": upcoming_birthdays,
            "active_employees": len(active_employees),
            "inactive_employees": len(inactive_employees),
            "total_employees": len(employees),
            "active_ratio": active_ratio,
            "inactive_ratio": inactive_ratio,
        },
    )


@login_required
def dashboard_employee(request):
    """
    Active and in-active employee dashboard
    """
    labels = [
        _("Active"),
        _("In-Active"),
    ]
    employees = Employee.objects.all()
    response = {
        "dataSet": [
            {
                "label": _("Employees"),
                "data": [
                    len(employees.filter(is_active=True)),
                    len(employees.filter(is_active=False)),
                ],
            },
        ],
        "labels": labels,
    }
    return JsonResponse(response)


@login_required
def dashboard_employee_gender(request):
    """
    This method is used to filter out gender vise employees
    """
    labels = [_("Male"), _("Female"), _("Other")]
    employees = Employee.objects.filter(is_active=True)

    response = {
        "dataSet": [
            {
                "label": _("Employees"),
                "data": [
                    len(employees.filter(gender="male")),
                    len(employees.filter(gender="female")),
                    len(employees.filter(gender="other")),
                ],
            },
        ],
        "labels": labels,
    }
    return JsonResponse(response)


@login_required
def dashboard_employee_department(request):
    """
    This method is used to find the count of employees corresponding to the departments
    """
    labels = []
    count = []
    departments = Department.objects.all()
    for dept in departments:
        labels.append(dept.department)
        count.append(
            len(
                Employee.objects.filter(
                    employee_work_info__department_id__department=dept,is_active=True
                )
            )
        )
    response = {
        "dataSet": [{"label": "Department", "data": count}],
        "labels": labels,
        "message": _("No Data Found..."),
    }
    return JsonResponse(response)


@login_required
def dashboard_employee_tiles(request):
    """
    This method returns json response.
    """
    data = {}
    # active employees count
    data["total_employees"] = Employee.objects.filter(is_active=True).count()
    # filtering newbies
    data["newbies_today"] = Candidate.objects.filter(
        joining_date__range=[date.today(), date.today() + timedelta(days=1)]
    ).count()
    try:
        data[
            "newbies_today_percentage"
        ] = f"""{
        (EmployeeWorkInformation.objects.filter(
            date_joining__range=[date.today(), date.today() + timedelta(days=1)]
            ).count() / Employee.objects.filter(
                employee_work_info__isnull=False).count()
                ) * 100:.2f}%"""
    except Exception:
        data["newbies_today_percentage"] = 0
    # filtering newbies on this week

    data["newbies_week"] = Candidate.objects.filter(
        joining_date__range=[
            date.today() - timedelta(days=date.today().weekday()),
            date.today() + timedelta(days=6 - date.today().weekday()),
        ]
    ).count()
    try:
        data[
            "newbies_week_percentage"
        ] = f"""{(
            EmployeeWorkInformation.objects.filter(
            date_joining__range=[date.today() - timedelta(days=7), date.today()]
            ).count() / Employee.objects.filter(
            employee_work_info__isnull=False
            ).count()
            ) * 100:.2f}%"""

    except Exception:
        data["newbies_week_percentage"] = 0
    return JsonResponse(data)


@login_required
def widget_filter(request):
    """
    This method is used to return all the ids of the employees
    """
    ids = EmployeeFilter(request.GET).qs.values_list("id", flat=True)
    return JsonResponse({"ids": list(ids)})


@login_required
def employee_select(request):
    """
    This method is used to return all the id of the employees to select the employee row
    """
    page_number = request.GET.get("page")

    employees = Employee.objects.all()
    if page_number == "all":
        employees = Employee.objects.filter(is_active=True)

    employee_ids = [str(emp.id) for emp in employees]
    total_count = employees.count()

    context = {"employee_ids": employee_ids, "total_count": total_count}

    return JsonResponse(context, safe=False)


@login_required
def employee_select_filter(request):
    """
    This method is used to return all the ids of the filtered employees
    """
    page_number = request.GET.get("page")
    filtered = request.GET.get("filter")
    filters = json.loads(filtered) if filtered else {}

    if page_number == "all":
        employee_filter = EmployeeFilter(filters, queryset=Employee.objects.all())

        # Get the filtered queryset
        filtered_employees = employee_filter.qs

        employee_ids = [str(emp.id) for emp in filtered_employees]
        total_count = filtered_employees.count()

        context = {"employee_ids": employee_ids, "total_count": total_count}

        return JsonResponse(context)
