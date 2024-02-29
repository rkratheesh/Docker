import json
import datetime
from urllib.parse import parse_qs
from itertools import tee
from django.http import HttpResponse, JsonResponse
from django.db.utils import IntegrityError
from django.db.models import Q
from django.forms import modelformset_factory
from django.contrib import messages
from django.core.paginator import Paginator
from django.utils.translation import gettext_lazy as _
from django.shortcuts import get_object_or_404, render, redirect
from horilla.decorators import manager_can_enter
from horilla.decorators import login_required, hx_request_required
from notifications.signals import notify
from base.methods import get_key_instances
from base.models import Department, JobPosition
from employee.models import Employee, EmployeeWorkInformation
from pms.filters import (
    KeyResultFilter,
    ObjectiveFilter,
    FeedbackFilter,
    ObjectiveReGroup,
)
from django.db.models import ProtectedError
from pms.models import (
    EmployeeKeyResult,
    EmployeeObjective,
    Comment,
    Feedback,
    QuestionTemplate,
    Question,
    Answer,
    Period,
    QuestionOptions,
    KeyResultFeedback,
)
from .forms import (
    QuestionForm,
    ObjectiveForm,
    KeyResultForm,
    FeedbackForm,
    ObjectiveCommentForm,
    PeriodForm,
    QuestionTemplateForm,
)


@login_required
@manager_can_enter(perm="pms.add_employeeobjective")
def objective_creation(request):
    """
    This view is for objective creation , and returns a objective form.
    Returns:
        GET:
            objective form, period, department, job position, employee, department
        POST:
            Objective created, and returnes to key result creation function
    """

    employees = Employee.objects.all()
    departments = Department.objects.all()
    job_positions = JobPosition.objects.all()
    periods = Period.objects.all()
    employee = request.user.employee_get
    objective_form = ObjectiveForm(employee=employee)
    context = {
        "employee": employees,
        "department": departments,
        "job_position": job_positions,
        "period": periods,
        "objective_form": objective_form,
    }

    if request.method == "POST":
        objective_type = request.POST.get("objective_type")
        if objective_type == "individual":
            # if the objective is for a individual
            form_objectives = ObjectiveForm(request.POST)
            if form_objectives.is_valid():
                objective = form_objectives.save()
                obj_id = objective.id
                obj_type = "individual"
                messages.success(request, _("Objective created"))
                notify.send(
                    request.user.employee_get,
                    recipient=objective.employee_id.employee_user_id,
                    verb="You got an OKR!.",
                    verb_ar="لقد حققت هدفًا ونتيجة رئيسية!",
                    verb_de="Du hast ein Ziel-Key-Ergebnis erreicht!",
                    verb_es="¡Has logrado un Resultado Clave de Objetivo!",
                    verb_fr="Vous avez atteint un Résultat Clé d'Objectif !",
                    redirect=f"/pms/objective-detailed-view/{obj_id}",
                    icon="list-circle",
                )
                return redirect(key_result_creation, obj_id, obj_type)
            else:
                context["objective_form"] = form_objectives
        elif objective_type == "job_position" or objective_type == "department":
            # if the objective is based on particular job position or department
            form_objectives = ObjectiveForm(request.POST)
            obj_type = "multiple"
            if form_objectives.is_valid():
                objective_type = form_objectives.cleaned_data[objective_type]
                # to get all employee workinformation
                employee_work_informations = (
                    objective_type.employeeworkinformation_set.all()
                )
                # getting all the employees in the job position or department and assigning then the objective to them
                objective_ids = []
                for employee in employee_work_informations:
                    form_objectives = ObjectiveForm(request.POST)
                    form = form_objectives.save(commit=False)
                    form.employee_id = employee.employee_id
                    form.save()
                    notify.send(
                        request.user.employee_get,
                        recipient=form.employee_id.employee_user_id,
                        verb="You got an OKR!.",
                        verb_ar="لقد حققت هدفًا ونتيجة رئيسية!",
                        verb_de="Du hast ein Ziel-Key-Ergebnis erreicht!",
                        verb_es="¡Has logrado un Resultado Clave de Objetivo!",
                        verb_fr="Vous avez atteint un Résultat Clé d'Objectif !",
                        redirect=f"/pms/objective-detailed-view/{form.id}",
                        icon="list-circle",
                    )
                    objective_ids.append(form.id)
                obj_id = str(objective_ids)
                messages.success(request, _("Objectives created"))
                return redirect(key_result_creation, obj_id, obj_type)
            else:
                context["objective_form"] = form_objectives
        elif objective_type == "none":
            form_objectives = ObjectiveForm(request.POST)
            context["objective_form"] = form_objectives
    return render(request, "okr/objective_creation.html", context=context)


@login_required
@hx_request_required
@manager_can_enter(perm="pms.change_employeeobjective")
def objective_update(request, obj_id):
    """
    This view takes one arguments, id , and returns a HttpResponse object.,using htmx
    Args:
        id (int): Primary key of EmployeeObjective.
    Returns:
        A HttpResponse object with the content Form errors.
    """
    instance = EmployeeObjective.objects.get(id=obj_id)
    objective_form = ObjectiveForm(instance=instance)
    context = {"objective_form": objective_form}
    if request.method == "POST":
        objective_form = ObjectiveForm(request.POST, instance=instance)
        if objective_form.is_valid():
            objective_form.save()
            if not instance.employee_id.id == int(request.POST.get("employee_id")):
                notify.send(
                    request.user.employee_get,
                    recipient=instance.employee_id.employee_user_id,
                    verb="You got an OKR!.",
                    verb_ar="لقد حققت هدفًا ونتيجة رئيسية!",
                    verb_de="Du hast ein Ziel-Key-Ergebnis erreicht!",
                    verb_es="¡Has logrado un Resultado Clave de Objetivo!",
                    verb_fr="Vous avez atteint un Résultat Clé d'Objectif !",
                    redirect=f"/pms/objective-detailed-view/{instance.id}",
                    icon="eye-outline",
                )
            messages.info(
                request,
                _("Objective %(objective)s Updated")
                % {"objective": instance.objective},
            )
            response = render(request, "okr/objective_update.html", context)
            return HttpResponse(
                response.content.decode("utf-8") + "<script>location.reload();</script>"
            )
        else:
            context["objective_form"] = objective_form
    return render(request, "okr/objective_update.html", context)


@login_required
@manager_can_enter(perm="pms.delete_employeeobjective")
def objective_delete(request, obj_id):
    """
    This view takes one arguments, id and returns redirecting to a view.
    Args:
        id (int) : primarykey of the EmployeeObjective.
    Returns:
        Redirect to Objective_list_view".
    """
    try:
        objective = EmployeeObjective.objects.get(id=obj_id)
        if objective.status == "Not Started" or objective.status == "Closed":
            objective.delete()
            messages.success(
                request,
                _("Objective %(objective)s deleted")
                % {"objective": objective.objective},
            )
        else:
            messages.warning(
                request,
                _("You can't delete objective %(objective)s with status %(status)s")
                % {"objective": objective.objective, "status": objective.status},
            )
    except EmployeeObjective.DoesNotExist:
        messages.error(request, _("Objective not found."))
    return redirect(objective_list_view)


def objective_filter_pagination(request, objective_own, objective_all):
    """
    This view takes two arguments, all_objective,own_objecitve and returns some objects.
    Args:
        all_objective (queryset) : Queryset of objectives
        own_objective (queryset) : Queryset of objectives
    Returns:
        All the filtered and paginated object will return.
    """
    previous_data = request.GET.urlencode()
    initial_data = {"archive": False}  # set initial value of archive filter to False
    field = request.GET.get("field")
    if request.GET.get("status") != "Closed":
        objective_own = objective_own
        objective_all = objective_all
    objective_filter_own = ObjectiveFilter(
        request.GET or initial_data, queryset=objective_own
    )
    objective_filter_all = ObjectiveFilter(
        request.GET or initial_data, queryset=objective_all
    ).qs
    if field != "" and field is not None:
        field_copy = field.replace(".", "__")
        objective_filter_all = objective_filter_all.order_by(field_copy)

    objective_paginator_own = Paginator(objective_filter_own.qs, 50)
    objective_paginator_all = Paginator(objective_filter_all, 50)
    page_number = request.GET.get("page")
    objectives_own = objective_paginator_own.get_page(page_number)
    objectives_all = objective_paginator_all.get_page(page_number)
    now = datetime.datetime.now()
    data_dict = parse_qs(previous_data)
    get_key_instances(EmployeeObjective, data_dict)
    context = {
        "superuser": "true",
        "own_objectives": objectives_own,
        "all_objectives": objectives_all,
        "objective_filer_form": objective_filter_own.form,
        "pg": previous_data,
        "current_date": now,
        "filter_dict": data_dict,
        "gp_fields": ObjectiveReGroup.fields,
        "field": field,
    }
    return context


@login_required
def objective_list_view(request):
    """
    This view is used to show all the objectives  and returns some objects.
    Returns:
        Objects based on userlevel.
    """
    user = request.user
    employee = Employee.objects.filter(employee_user_id=user).first()
    is_manager = Employee.objects.filter(
        employee_work_info__reporting_manager_id=employee
    )

    if request.user.has_perm("pms.view_employeeobjective"):
        objective_own = EmployeeObjective.objects.filter(
            employee_id=employee
        ) | EmployeeObjective.objects.filter(emp_obj_id__employee_id=employee)
        objective_own = objective_own.distinct()
        objective_all = EmployeeObjective.objects.all()
        context = objective_filter_pagination(request, objective_own, objective_all)

    elif is_manager:
        # if user is a manager
        employees_ids = [employee.id for employee in is_manager]
        objective_own = EmployeeObjective.objects.filter(
            employee_id=employee
        ) | EmployeeObjective.objects.filter(emp_obj_id__employee_id=employee)
        objective_own = objective_own.distinct()
        objective_all = EmployeeObjective.objects.filter(
            employee_id__in=employees_ids
        ) | EmployeeObjective.objects.filter(emp_obj_id__employee_id__in=employees_ids)
        objective_all = objective_all.distinct()
        context = objective_filter_pagination(request, objective_own, objective_all)
    else:
        # for normal user
        objective_own = EmployeeObjective.objects.filter(
            employee_id=employee
        ) | EmployeeObjective.objects.filter(emp_obj_id__employee_id=employee)
        objective_own = objective_own.distinct()
        objective_all = EmployeeObjective.objects.none()
        context = objective_filter_pagination(request, objective_own, objective_all)
    if objective_all.exists() or objective_own.exists():
        template = "okr/objective_list_view.html"
    else:
        template = "okr/objective_empty.html"
    return render(request, template, context)


@login_required
# @hx_request_required
def objective_list_search(request):
    """
    This view is used to to search objective,  returns searched and filtered objects.
    Returns:
        All the filtered and searched object will based on userlevel.
    """
    search_val = request.GET.get("search")
    if search_val is None:
        search_val = ""
    
    user = request.user
    employee = Employee.objects.filter(employee_user_id=user).first()
    is_manager = Employee.objects.filter(
        employee_work_info__reporting_manager_id=employee
    )

    if request.user.has_perm("pms.view_employeeobjective"):
        # based on permission
        objective_own = EmployeeObjective.objects.filter(
            employee_id=request.user.employee_get
        ).filter(objective__icontains=search_val)
        objective_all = EmployeeObjective.objects.filter(
            objective__icontains=search_val
        )
        context = objective_filter_pagination(request, objective_own, objective_all)

    elif is_manager:
        # if user is a manager
        employees_ids = [employee.id for employee in is_manager]
        objective_own = EmployeeObjective.objects.filter(employee_id=employee).filter(
            objective__icontains=search_val
        )
        objective_all = EmployeeObjective.objects.filter(
            employee_id__in=employees_ids
        ).filter(objective__icontains=search_val)
        context = objective_filter_pagination(request, objective_own, objective_all)

    else:
        # for normal user
        objective_own = EmployeeObjective.objects.filter(employee_id=employee).filter(
            objective__icontains=search_val
        )
        objective_all = EmployeeObjective.objects.none()
        context = objective_filter_pagination(request, objective_own, objective_all)
    template = "okr/objective_list.html"
    if request.GET.get("field") != "" and request.GET.get("field") is not None:
        template = "okr/group_by.html"
    return render(request, template, context)


def objective_history(emp_obj_id):
    """
    This view is used to get history of EmployeeObjective,  return objects.
    Args:
        id (int): Primarykey of EmployeeObjective.
    Returns:
        All the history of EmployeeObjective.
    """

    def pair_history(iterable):
        """this function return two history pair"""
        a, b = tee(iterable)
        next(b, None)
        return zip(a, b)

    changed_key_results = []

    def key_result_history(key_result):
        """key result history"""
        key_result_iterator = (
            key_result.history.all().order_by("history_date").iterator()
        )
        for record_pair in pair_history(key_result_iterator):
            old_record, new_record = record_pair
            delta = new_record.diff_against(old_record)
            history_user_id = delta.new_record.history_user
            history_change_date = delta.new_record.history_date
            employee = Employee.objects.filter(employee_user_id=history_user_id).first()
            key_result = delta.new_record.key_result
            changed_key_results.append(
                {
                    "delta": delta,
                    "changed_user": employee,
                    "changed_date": history_change_date,
                    "k_r":key_result,
                }
            )

    obj_objective = EmployeeObjective.objects.get(id=emp_obj_id)
    all_key_results = EmployeeKeyResult.objects.filter(
        employee_objective_id=obj_objective
    )

    for key_result in all_key_results:
        # loop each key result and generate it's history
        key_result_history(key_result)
    changed_key_results.reverse()
    return changed_key_results


@login_required
def objective_detailed_view(request, emp_obj_id, **kwargs):
    """
    this function is used to update the key result of objectives
        args:
            emp_obj_id(int) : pimarykey of EmployeeObjective
        return:
            objects to objective_detailed_view
    """

    objective = EmployeeObjective.objects.get(id=emp_obj_id)
    key_results = EmployeeKeyResult.objects.filter(employee_objective_id=objective)
    comments = Comment.objects.filter(employee_objective_id=objective)
    key_results_all = objective.emp_obj_id.all()
    # progress of objective calculation
    total_kr = key_results_all.count()
    try:
        progress = int(sum(kr.progress_percentage for kr in key_results_all) / (total_kr))
    except (ZeroDivisionError, TypeError):
        progress = 0

    objective_form = ObjectiveForm(instance=objective)
    history = objective_history(emp_obj_id)
    now = datetime.datetime.now()
    context = {
        "employee_key_results": key_results,
        "employee_objective": objective,
        "comments": comments,
        "historys": history,
        "progress": progress,
        "objective_form": objective_form,
        "key_result_form": KeyResultForm,
        "objective_key_result_status": EmployeeKeyResult.STATUS_CHOICES,
        "comment_form": ObjectiveCommentForm,
        "current_date": now,
    }
    return render(request, "okr/objective_detailed_view.html", context)


@login_required
@hx_request_required
def objective_detailed_view_activity(request, id):
    """
    This view is used to show objective activity template ,using htmx
    Args:
        id (int): Primary key of EmployeeObjective.
    Returns:
        it will return history,comment object to objective_detailed_view_activity.
    """

    history = objective_history(id)
    objective = EmployeeObjective.objects.get(id=id)
    comments = Comment.objects.filter(employee_objective_id=objective)
    context = {
        "historys": history,
        "comments": comments,
    }
    return render(request, "okr/objective_detailed_view_activity.html", context)


@login_required
@hx_request_required
def objective_detailed_view_comment(request, id):
    """
    This view is used to create comment object for objective activity, using htmx
    Args:
        id (int): Primary key of EmployeeObjective.
    Returns:
        it will redirect to objective_detailed_view_activity.
    """
    comment_form = ObjectiveCommentForm(request.POST)
    if comment_form.is_valid():
        objective = EmployeeObjective.objects.get(id=id)
        form = comment_form.save(commit=False)
        form.employee_id = request.user.employee_get
        form.employee_objective_id = objective
        form.save()

        return redirect(objective_detailed_view_activity, id)
    return redirect(objective_detailed_view_activity, id)


@login_required
@hx_request_required
def objective_detailed_view_objective_status(request, id):
    """
    This view is used to  update status of objective in objective detailed view,  redirect to objective_detailed_view_activity. using htmx
    Args:
        obj_id (int): Primarykey of EmployeeObjective.
    Returns:
        All the filtered and searched object will based on userlevel.
    """

    objective = EmployeeObjective.objects.get(id=id)
    status = request.POST.get("objective_status")
    objective.status = status
    objective.save()
    messages.info(
        request,
        _("Objective %(objective)s status updated")
        % {"objective": objective.objective},
    )
    return redirect(objective_detailed_view_activity, id)


@login_required
@hx_request_required
def objective_detailed_view_key_result_status(request, obj_id, kr_id):
    """
    This view is used to  update status of key result in objective detailed view,  redirect to objective_detailed_view_activity. using htmx
    Args:
        obj_id (int): Primarykey of EmployeeObjective.
        kr_id (int): Primarykey of EmployeeKeyResult.
    Returns:
        All the filtered and searched object will based on userlevel.
    """

    status = request.POST.get("key_result_status")
    employee_key_result = EmployeeKeyResult.objects.get(id=kr_id)

    current_value = employee_key_result.current_value
    target_value = employee_key_result.target_value

    if current_value >= target_value:
        employee_key_result.status = "Closed"
    else:
        employee_key_result.status = status
    employee_key_result.save()
    messages.info(request, _("Status has been updated"))
    # return redirect(objective_detailed_view_activity, id=obj_id)
    response = redirect(objective_detailed_view_activity, id=obj_id)
    return HttpResponse(
        response.content.decode("utf-8") + "<script>location.reload();</script>"
    )


@login_required
@hx_request_required
def objective_detailed_view_current_value(request, kr_id):
    """
    This view is used to update current value of key result,  return redirect to view . using htmx
    Args:
        kr_id (int): Primarykey of EmployeeKeyresult.
    Returns:
        All the history of EmployeeObjective.
    """
    if request.method == "POST":
        current_value = request.POST.get("current_value")
        employee_key_result = EmployeeKeyResult.objects.get(id=kr_id)
        target_value = employee_key_result.target_value
        objective_id = employee_key_result.employee_objective_id.id
        if int(current_value) < target_value:
            employee_key_result.current_value = current_value
            employee_key_result.save()
            messages.info(
                request,
                _("Current value of %(employee_key_result)s updated")
                % {"employee_key_result": employee_key_result},
            )
            return redirect(objective_detailed_view_activity, objective_id)

        elif int(current_value) == target_value:
            employee_key_result.current_value = current_value
            employee_key_result.status = "Closed"
            employee_key_result.save()
            messages.info(
                request,
                _("Current value of %(employee_key_result)s updated")
                % {"employee_key_result": employee_key_result},
            )
            # return redirect(objective_detailed_view_activity, objective_id)
            response = redirect(objective_detailed_view_activity, objective_id)
            return HttpResponse(
                response.content.decode("utf-8") + "<script>location.reload();</script>"
            )

        elif int(current_value) > target_value:
            messages.warning(request, _("Current value is greater than target value"))
            return redirect(objective_detailed_view_activity, objective_id)
        messages.error(request, _("Error occurred during current value updation"))
        return redirect(objective_detailed_view_activity, objective_id)


@login_required
def objective_archive(request, id):
    """
    this function is used to archive the objective
        args:
            id(int) : pimarykey of EmployeeObjective
        return:
            redirect to objective_list_view
    """
    objective = EmployeeObjective.objects.get(id=id)
    if objective.archive:
        objective.archive = False
        objective.save()
        messages.info(request, _("Objective un-archived successfully!."))
    elif not objective.archive:
        objective.archive = True
        objective.save()
        messages.info(request, _("Objective archived successfully!."))
    return redirect(f"/pms/objective-list-view?{request.environ['QUERY_STRING']}")


@login_required
@manager_can_enter(perm="pms.add_employeekeyresult")
def key_result_view(request):
    """
    This view is used to view key result,
    Args:
        request: Request object.
    Returns:
        if errorr occur it will return errorr message.
    """
    key_results = KeyResultFilter(request.GET).qs
    context = {
        "key_results": key_results,
        "objective_key_result_status": EmployeeKeyResult.STATUS_CHOICES,
    }
    return render(request, "okr/key_result/key_result_view.html", context=context)


@login_required
@manager_can_enter(perm="pms.add_employeekeyresult")
def key_result_creation(request, obj_id, obj_type):
    """
    This view is used to create key result,
    Args:
        id (int): Primarykey of EmployeeObjective.
        obj_type (str): type  of objecitve
    Returns:
        if errorr occur it will return errorr message .
    """

    employee = request.user.employee_get
    if obj_type == "individual":
        objective = EmployeeObjective.objects.filter(id=int(obj_id))
        start_date = None
        end_date = None
        for obj in objective:
            start_date = obj.start_date
            end_date = obj.end_date
        key_result_form = KeyResultForm(
            employee=employee, initial={"start_date": start_date, "end_date": end_date}
        )
    else:
        objective_ids = json.loads(obj_id)
        for objective_id in objective_ids:
            objective = EmployeeObjective.objects.filter(id=objective_id).first()
            start_date = objective.start_date
            end_date = objective.end_date
        key_result_form = KeyResultForm(
            employee=employee, initial={"start_date": start_date, "end_date": end_date}
        )
    context = {
        "key_result_form": key_result_form,
        "objective_id": obj_id,
        "objective_type": obj_type,
    }
    if obj_type == "multiple":
        # for job position or department  the context should have all the related object ids
        value = context.pop("objective_id")
        context["objective_ids"] = value
    if request.method == "POST":
        if obj_type == "individual":
            employee_objective_id = EmployeeObjective.objects.get(id=int(obj_id))
            form_key_result = KeyResultForm(
                request.POST, initial={"employee_objective_id": employee_objective_id}
            )
            if form_key_result.is_valid():
                form = form_key_result.save(commit=False)
                form.start_value = form.current_value
                form.employee_objective_id = employee_objective_id
                form.save()
                messages.success(request, _("Key result created"))
                return redirect(objective_detailed_view, obj_id)
            else:
                context["key_result_form"] = form_key_result

        elif obj_type == "multiple":
            # If the objective is for job postion or department
            # The id will be list of objective id
            objective_ids = json.loads(obj_id)
            for objective_id in objective_ids:
                objective = EmployeeObjective.objects.filter(id=objective_id).first()
                form_key_result = KeyResultForm(
                    request.POST, initial={"employee_objective_id": objective}
                )
                if form_key_result.is_valid():
                    form = form_key_result.save(commit=False)
                    form.start_value = form.current_value
                    form.employee_id = objective.employee_id
                    form.employee_objective_id = objective
                    form.save()
                else:
                    context["key_result_form"] = form_key_result
                    return render(
                        request, "okr/key_result/key_result_creation.html", context
                    )
            messages.success(request, _("Key results created"))
            return redirect(objective_list_view)
    return render(request, "okr/key_result/key_result_creation.html", context)


@login_required
@hx_request_required
@manager_can_enter(perm="pms.add_employeekeyresult")
def key_result_creation_htmx(request, id):
    """
    This view is used to create key result in objective detailed view,  using htmx
    Args:
        id (int): Primarykey of EmployeeObjective.
        obj_type (str): type  of objecitve
    Returns:
        if errorr occure it will return errorr message .
    """
    object = EmployeeObjective.objects.filter(id=id)
    start_date = None
    end_date = None
    for obj in object:
        start_date = obj.start_date
        end_date = obj.end_date
    key_result_form = KeyResultForm(
        initial={"start_date": start_date, "end_date": end_date}
    )
    context = {"key_result_form": key_result_form, "objecitve_id": id}
    objective = EmployeeObjective.objects.get(id=id)
    if request.method == "POST":
        initial_data = {"employee_objective_id": objective}
        form_key_result = KeyResultForm(request.POST, initial=initial_data)
        if form_key_result.is_valid():
            form = form_key_result.save(commit=False)
            form.start_value = form.current_value
            form.employee_objective_id = objective
            form.save()
            messages.success(request, _("Key result created"))
            response = render(
                request, "okr/key_result/key_result_creation_htmx.html", context
            )
            return HttpResponse(
                response.content.decode("utf-8") + "<script>location.reload();</script>"
            )
        context["key_result_form"] = form_key_result
    return render(request, "okr/key_result/key_result_creation_htmx.html", context)


@login_required
@hx_request_required
@manager_can_enter(perm="pms.update_employeekeyresult")
def key_result_update(request, id):
    """
    This view is used to update key result, using htmx
    Args:
        id (int): Primarykey of EmployeeKeyResult.
    Returns:
        success or errors message.
    """

    key_result = EmployeeKeyResult.objects.get(id=id)
    key_result_form = KeyResultForm(instance=key_result)
    context = {"key_result_form": key_result_form, "key_result_id": key_result.id}
    if request.method == "POST":
        key_result_form = KeyResultForm(request.POST, instance=key_result)
        key_result_form.initial[
            "employee_objective_id"
        ] = (
            key_result.employee_objective_id
        )  # adding intial objective value to the form
        if key_result_form.is_valid():
            key_result_form.save()
            messages.info(request, _("Key result updated"))
            response = render(request, "okr/key_result/key_result_update.html", context)
            return HttpResponse(
                response.content.decode("utf-8") + "<script>location.reload();</script>"
            )
        else:
            context["key_result_form"] = key_result_form
    return render(request, "okr/key_result/key_result_update.html", context)


# feedback section
def send_feedback_notifications(request, form):
    # Send notification to employee
    if form.employee_id:
        employee = form.employee_id
        notify.send(
            request.user.employee_get,
            recipient=employee.employee_user_id,
            verb="You have received feedback!",
            verb_ar="لقد تلقيت ملاحظات!",
            verb_de="Sie haben Feedback erhalten!",
            verb_es="¡Has recibido retroalimentación!",
            verb_fr="Vous avez reçu des commentaires !",
            redirect=f"/pms/feedback-detailed-view/{form.id}",
            icon="chatbox-ellipses",
        )

    # Send notification to manager
    if form.manager_id:
        manager = form.manager_id
        notify.send(
            request.user.employee_get,
            recipient=manager.employee_user_id,
            verb="You have been assigned as a manager in a feedback!",
            verb_ar="لقد تم تعيينك كمدير في ملاحظة!",
            verb_de="Sie wurden als Manager in einem Feedback zugewiesen!",
            verb_es="¡Has sido asignado como manager en un feedback!",
            verb_fr="Vous avez été désigné comme manager dans un commentaire !",
            redirect=f"/pms/feedback-detailed-view/{form.id}",
            icon="chatbox-ellipses",
        )

    # Send notification to subordinates
    if form.subordinate_id:
        subordinates = form.subordinate_id.all()
        for subordinate in subordinates:
            notify.send(
                request.user.employee_get,
                recipient=subordinate.employee_user_id,
                verb="You have been assigned as a subordinate in a feedback!",
                verb_ar="لقد تم تعيينك كمرؤوس في ملاحظة!",
                verb_de="Sie wurden als Untergebener in einem Feedback zugewiesen!",
                verb_es="¡Has sido asignado como subordinado en un feedback!",
                verb_fr="Vous avez été désigné comme subordonné dans un commentaire !",
                redirect=f"/pms/feedback-detailed-view/{form.id}",
                icon="chatbox-ellipses",
            )

    # Send notification to colleagues
    if form.colleague_id:
        colleagues = form.colleague_id.all()
        for colleague in colleagues:
            notify.send(
                request.user.employee_get,
                recipient=colleague.employee_user_id,
                verb="You have been assigned as a colleague in a feedback!",
                verb_ar="لقد تم تعيينك كزميل في ملاحظة!",
                verb_de="Sie wurden als Kollege in einem Feedback zugewiesen!",
                verb_es="¡Has sido asignado como colega en un feedback!",
                verb_fr="Vous avez été désigné comme collègue dans un commentaire !",
                redirect=f"/pms/feedback-detailed-view/{form.id}",
                icon="chatbox-ellipses",
            )


@login_required
@manager_can_enter(perm="pms.add_feedback")
def feedback_creation(request):
    """
    This view is used to create feedback object.
    Returns:
        it will return feedback creation html.
    """
    employee = request.user.employee_get
    # if employe
    form = FeedbackForm(employee=employee)
    context = {
        "feedback_form": form,
    }
    if request.method == "POST":
        form = FeedbackForm(request.POST)
        if form.is_valid():
            if key_result_ids := request.POST.getlist("employee_key_results_id"):
                for key_result_id in key_result_ids:
                    key_result = EmployeeKeyResult.objects.get(id=key_result_id)
                    feedback_form = form.save()
                    feedback_form.employee_key_results_id.add(key_result)
            instance = form.save()
            messages.success(request, _("Feedback created successfully."))
            send_feedback_notifications(request, form=instance)
            return redirect(feedback_list_view)
        else:
            context["feedback_form"] = form
    return render(request, "feedback/feedback_creation.html", context)


@login_required
@manager_can_enter(perm="pms.add_feedback")
def feedback_creation_ajax(request):
    """
    This view is used to create feedback object.
    Returns:
        it will return feedback creation html.
    """
    # this ajax request is used to get the Key result and manager of the choosen employee
    is_ajax = request.headers.get("X-Requested-With") == "XMLHttpRequest"
    if is_ajax:
        if request.method == "POST":
            employee_id = request.POST.get("employee_id")
            key_results = EmployeeKeyResult.objects.filter(
                employee_id=employee_id
            ).values()
            employee_work_info = EmployeeWorkInformation.objects.filter(
                employee_id__id=employee_id
            ).first()
            reporting_manager_id = employee_work_info.reporting_manager_id
            if reporting_manager_id:
                reporting_manager = {
                    "id": reporting_manager_id.id or None,
                    "employee_first_name": reporting_manager_id.employee_first_name
                    or None,
                    "employee_last_name": reporting_manager_id.employee_last_name
                    or None,
                }
            else:
                reporting_manager = None
            return JsonResponse(
                {
                    "key_results": list(key_results),
                    "reporting_manager": reporting_manager,
                }
            )
        return JsonResponse({"status": "Invalid request"}, status=400)


@login_required
@hx_request_required
@manager_can_enter(perm="pms.change_feedback")
def feedback_update(request, id):
    """
    This view is used to  update the feedback.
    Args:
        id(int) : primarykey of the feedback.
    Returns:
        it will redirect to  feedback_detailed_view.
    """

    feedback = Feedback.objects.get(id=id)
    form = FeedbackForm(instance=feedback)
    feedback_started = Answer.objects.filter(feedback_id=feedback)
    context = {"feedback_form": form}
    if feedback_started:
        messages.error(request, _("Ongoing feedback is not editable!."))
        response = render(request, "feedback/feedback_update.html", context)
        return HttpResponse(
            response.content.decode("utf-8") + "<script>location.reload();</script>"
        )

    if request.method == "POST":
        form = FeedbackForm(request.POST, instance=feedback)
        if form.is_valid():
            form = form.save()
            messages.info(request, _("Feedback updated successfully!."))
            send_feedback_notifications(request, form)
            response = render(request, "feedback/feedback_update.html", context)
            return HttpResponse(
                response.content.decode("utf-8") + "<script>location.reload();</script>"
            )
        else:
            context["feedback_form"] = form
    return render(request, "feedback/feedback_update.html", context)


@login_required
def filter_pagination_feedback(
    request, self_feedback, requested_feedback, all_feedback
):
    """
    This view is used to filter or search the feedback object  ,

    Args:
        self_feedback (queryset): self feedback filtered queryset.
        requested_feedback (queryset): requested feedback filtered queryset.
        all_feedback (queryset): all feedback filtered queryset.

    Returns:
        it will return the filtered and searched object.

    """
    previous_data = request.GET.urlencode()
    initial_data = {"archive": False}  # set initial value of archive filter to False
    feedback_filter_own = FeedbackFilter(
        request.GET or initial_data, queryset=self_feedback
    )
    feedback_filter_requested = FeedbackFilter(
        request.GET or initial_data, queryset=requested_feedback
    )
    feedback_filter_all = FeedbackFilter(
        request.GET or initial_data, queryset=all_feedback
    )

    feedback_paginator_own = Paginator(feedback_filter_own.qs, 50)
    feedback_paginator_requested = Paginator(feedback_filter_requested.qs, 50)
    feedback_paginator_all = Paginator(feedback_filter_all.qs, 50)
    page_number = request.GET.get("page")

    feedbacks_own = feedback_paginator_own.get_page(page_number)
    feedbacks_requested = feedback_paginator_requested.get_page(page_number)
    feedbacks_all = feedback_paginator_all.get_page(page_number)
    now = datetime.datetime.now()
    data_dict = parse_qs(previous_data)
    get_key_instances(Feedback, data_dict)
    context = {
        "superuser": "true",
        "self_feedback": feedbacks_own,
        "requested_feedback": feedbacks_requested,
        "all_feedbacks": feedbacks_all,
        "feedback_filter_form": feedback_filter_own.form,
        "pg": previous_data,
        "current_date": now,
        "filter_dict": data_dict,
    }
    return context


@login_required
# @hx_request_required
def feedback_list_search(request):
    """
    This view is used to filter or search the feedback object  ,
    Args:
    Returns:
        it will return the filtered and searched object.
    """
    feedback = request.GET.get("search")  # if the search is none the filter will works
    if feedback is None:
        feedback = ""
    employee_id = Employee.objects.get(employee_user_id=request.user)
    self_feedback = Feedback.objects.filter(employee_id=employee_id).filter(
        review_cycle__icontains=feedback
    )

    requested_feedback_ids = []
    requested_feedback_ids.extend(
        [i.id for i in Feedback.objects.filter(manager_id=employee_id)]
    )
    requested_feedback_ids.extend(
        [i.id for i in Feedback.objects.filter(colleague_id=employee_id)]
    )
    requested_feedback_ids.extend(
        [i.id for i in Feedback.objects.filter(subordinate_id=employee_id)]
    )

    requested_feedback = Feedback.objects.filter(pk__in=requested_feedback_ids).filter(
        review_cycle__icontains=feedback
    )
    all_feedback = Feedback.objects.all().filter(review_cycle__icontains=feedback)

    reporting_manager_to = employee_id.reporting_manager.all()
    if request.user.has_perm("pms.view_feedback"):
        context = filter_pagination_feedback(
            request, self_feedback, requested_feedback, all_feedback
        )
    elif reporting_manager_to:
        employees_id = [i.id for i in reporting_manager_to]
        all_feedback = Feedback.objects.filter(employee_id__in=employees_id).filter(
            review_cycle__icontains=feedback
        )
        context = filter_pagination_feedback(
            request, self_feedback, requested_feedback, all_feedback
        )
    else:
        all_feedback = Feedback.objects.none()
        context = filter_pagination_feedback(
            request, self_feedback, requested_feedback, all_feedback
        )

    return render(request, "feedback/feedback_list.html", context)


@login_required
def feedback_list_view(request):
    """
    This view is used to filter or search the feedback object  ,
    Args:
    Returns:
        it will return the filtered and searched object.
    """
    user = request.user
    employee = Employee.objects.filter(employee_user_id=user).first()
    feedback_requested_ids = Feedback.objects.filter(
        Q(manager_id=employee) | Q(colleague_id=employee) | Q(subordinate_id=employee)
    ).values_list("id", flat=True)
    feedback_own = Feedback.objects.filter(employee_id=employee).filter(archive=False)
    feedback_requested = Feedback.objects.filter(pk__in=feedback_requested_ids).filter(
        archive=False
    )
    feedback_all = Feedback.objects.all().filter(archive=False)
    employees = Employee.objects.filter(
        employee_work_info__reporting_manager_id=employee
    )  # checking the user is reporting manager or not
    feedback_available = Feedback.objects.all()
    if request.user.has_perm("pms.view_feedback"):
        context = filter_pagination_feedback(
            request, feedback_own, feedback_requested, feedback_all
        )
    elif employees:
        # based on the reporting manager
        feedback_all = Feedback.objects.filter(employee_id__in=employees)
        context = filter_pagination_feedback(
            request, feedback_own, feedback_requested, feedback_all
        )
    else:
        feedback_all = Feedback.objects.none()
        context = filter_pagination_feedback(
            request, feedback_own, feedback_requested, feedback_all
        )
    if feedback_available.exists():
        template = "feedback/feedback_list_view.html"
    else:
        template = "feedback/feedback_empty.html"
    return render(request, template, context)


@login_required
def feedback_detailed_view(request, id, **kwargs):
    """
    This view is used to for detailed view of feedback,
    Args:
        id(int) : primarykey of the feedback
    Returns:
        it will return the feedback object to feedback_detailed_view template .
    """
    feedback = Feedback.objects.get(id=id)
    current_date = datetime.datetime.now()
    context = {
        "feedback": feedback,
        "feedback_status": Feedback.STATUS_CHOICES,
        "current_date": current_date,
    }
    return render(request, "feedback/feedback_detailed_view.html", context)


def feedback_detailed_view_answer(request, id, emp_id):
    """
    This view is used show  answer ,
    Args:
        id(int) : primarykey of the feedback.
        emp_id(int) : primarykey of the Employee.
    Returns:
        it will return the answers .
    """
    employee = Employee.objects.filter(id=emp_id).first()
    feedback = Feedback.objects.filter(id=id).first()
    answers = Answer.objects.filter(employee_id=employee, feedback_id=feedback)
    context = {
        "answers": answers,
    }
    return render(request, "feedback/feedback_detailed_view_answer.html", context)


@login_required
def feedback_answer_get(request, id, **kwargs):
    """
    This view is used to render the feedback questions ,
    Args:
        id(int) : primarykey of the feedback.
    Returns:
        it will redirect to feedaback_answer.html .
    """

    user = request.user
    employee = Employee.objects.filter(employee_user_id=user).first()
    feedback = Feedback.objects.get(id=id)
    answer = Answer.objects.filter(feedback_id=feedback, employee_id=employee)
    question_template = feedback.question_template_id
    questions = question_template.question.all()
    options = QuestionOptions.objects.all()
    feedback_employees = (
        [feedback.employee_id]
        + [feedback.manager_id]
        + list(feedback.colleague_id.all())
        + list(feedback.subordinate_id.all())
    )
    if not employee in feedback_employees:
        messages.info(request, _("You are not allowed to answer"))
        return redirect(feedback_list_view)

    # Employee does not have an answer object
    for employee in feedback_employees:
        has_answer = Answer.objects.filter(
            employee_id=employee, feedback_id=feedback
        ).exists()
        has_answer = has_answer and has_answer
    if has_answer:
        feedback.status = "Closed"
        feedback.save()

    # Check if the feedback has already been answered
    if answer:
        messages.info(request, _("Feedback already answered"))
        return redirect(feedback_list_view)

    context = {
        "questions": questions,
        "options": options,
        "feedback": feedback,
    }

    return render(request, "feedback/answer/feedback_answer.html", context)


@login_required
def feedback_answer_post(request, id):
    """
    This view is used to create feedback answer ,
    Args:
        id(int) : primarykey of the feedback.
    Returns:
        it will redirect to feedback_list_view if the form was success full.
    """

    user = request.user
    employee = Employee.objects.filter(employee_user_id=user).first()
    feedback = Feedback.objects.get(id=id)
    question_template = feedback.question_template_id
    questions = question_template.question.all()

    if request.method == "POST":
        for question in questions:
            if request.POST.get(f"answer{question.id}"):
                answer = request.POST.get(f"answer{question.id}")
                Answer.objects.get_or_create(
                    answer={"answer": answer},
                    question_id=question,
                    feedback_id=feedback,
                    employee_id=employee,
                )
                feedback.status = "On Track"
                feedback.save()
        for key_result in feedback.employee_key_results_id.all():
            if request.POST.get(f"key_result{key_result.id}"):
                answer = request.POST.get(f"key_result{key_result.id}")
                KeyResultFeedback.objects.get_or_create(
                    answer={"answer": answer},
                    key_result_id=key_result,
                    feedback_id=feedback,
                    employee_id=request.user.employee_get,
                )
        messages.success(
            request,
            _("Feedback %(review_cycle)s has been answered successfully!.")
            % {"review_cycle": feedback.review_cycle},
        )
        return redirect(feedback_list_view)


@login_required
def feedback_answer_view(request, id, **kwargs):
    """
    This view is used to  view the feedback for employee.
    Args:
        id(int) : primarykey of the feedback.
    Returns:
        it will return feedback answer object to feedback_answer_view.
    """

    user = request.user
    employee = Employee.objects.filter(employee_user_id=user).first()
    feedback = Feedback.objects.get(id=id)
    answers = Answer.objects.filter(feedback_id=feedback, employee_id=employee)
    key_result_feedback = KeyResultFeedback.objects.filter(
        feedback_id=feedback, employee_id=employee
    )

    if not answers:
        messages.info(request, _("Feedback is not answered yet"))
        return redirect(feedback_list_view)

    context = {
        "answers": answers,
        "feedback_id": feedback,
        "key_result_feedback": key_result_feedback,
    }
    return render(request, "feedback/answer/feedback_answer_view.html", context)


@login_required
@manager_can_enter(perm="pms.delete_feedback")
def feedback_delete(request, id):
    """
    This view is used to  delete the feedback.
    Args:
        id(int) : primarykey of the feedback.
    Returns:
        it will redirect to  feedback_list_view.
    """
    try:
        feedback = Feedback.objects.filter(id=id).first()
        answered = Answer.objects.filter(feedback_id=feedback).first()
        if (
            feedback.status == "Closed"
            or feedback.status == "Not Started"
            and not answered
        ):
            feedback.delete()
            messages.success(
                request,
                _("Feedback %(review_cycle)s deleted successfully!")
                % {"review_cycle": feedback.review_cycle},
            )

        else:
            messages.warning(
                request,
                _("You can't delete feedback %(review_cycle)s with status %(status)s")
                % {"review_cycle": feedback.review_cycle, "status": feedback.status},
            )
            return redirect(feedback_list_view)

    except Feedback.DoesNotExist:
        messages.error(request, _("Feedback not found."))
    except ProtectedError:
        messages.error(request, _("Related entries exists"))
    return redirect(feedback_list_view)


@login_required
@hx_request_required
def feedback_detailed_view_status(request, id):
    """
    This view is used to  update status of feedback.
    Args:
        obj_id (int): Primarykey of feedback.
    Returns:
         message to the view
    """
    status = request.POST.get("feedback_status")
    feedback = get_object_or_404(Feedback, id=id)
    answer = Answer.objects.filter(feedback_id=feedback)
    if status == "Not Started" and answer:
        messages.warning(request, _("Feedback is already started"))
        return render(request, "messages.html")
    feedback.status = status
    feedback.save()
    if (feedback.status) == status:
        messages.info(
            request, _("Feedback status updated to  %(status)s") % {"status": _(status)}
        )
        return render(request, "messages.html")
    messages.info(
        request,
        _("Error occurred during status update to %(status)s") % {"status": _(status)},
    )
    return render(request, "message.html")


@login_required
def feedback_archive(request, id):
    """
    this function is used to archive the feedback for employee
    args:
        id(int): primarykey of feedback
    """

    feedback = Feedback.objects.get(id=id)
    if feedback.archive:
        feedback.archive = False
        feedback.save()
        messages.info(request, _("Feedback un-archived successfully!."))
    elif not feedback.archive:
        feedback.archive = True
        feedback.save()
        messages.info(request, _("Feedback archived successfully!."))
    return redirect(feedback_list_view)


@login_required
def feedback_status(request):
    """this function is used to un-archive the feedback
    args:
        id(int): primarykey of feedback
        emp_id(int): primarykey of feedback
    """

    is_ajax = request.headers.get("X-Requested-With") == "XMLHttpRequest"
    if is_ajax:
        if request.method == "POST":
            employee_id = request.POST.get("employee_id")
            feedback_id = request.POST.get("feedback_id")
            feedback = Feedback.objects.get(id=feedback_id)
            employee = Employee.objects.filter(id=employee_id).first()
            answer = Answer.objects.filter(employee_id=employee, feedback_id=feedback)
            status = _("Completed") if answer else _("Not-completed")
            return JsonResponse({"status": status})
        return JsonResponse({"status": "Invalid request"}, status=400)


@login_required
@manager_can_enter(perm="pms.add_question")
def question_creation(request, id):
    """
    This view is used to  create  question object.
    Args:
        id(int) : primarykey of the question template.

    Returns:
        it will redirect to  question_template_detailed_view.
    """
    if request.method == "POST":
        form = QuestionForm(request.POST)
        question_template = QuestionTemplate.objects.get(id=id)
        feedback_ongoing = Feedback.objects.filter(
            question_template_id=question_template
        ).first()
        if feedback_ongoing:
            messages.info(request, _("Question template is used in feedback."))
            return redirect(question_template_detailed_view, id)
        if form.is_valid():
            obj_question = form.save(commit=False)
            obj_question.template_id = question_template
            obj_question.save()

            if obj_question.question_type == "4":
                # checking the question type is multichoice
                option_a = request.POST.get("option_a")
                option_b = request.POST.get("option_b")
                option_c = request.POST.get("option_c")
                option_d = request.POST.get("option_d")
                QuestionOptions(
                    question_id=obj_question,
                    option_a=option_a,
                    option_b=option_b,
                    option_c=option_c,
                    option_d=option_d,
                ).save()
                messages.success(request, _("Question created successfully."))
                return redirect(question_template_detailed_view, id)
            messages.success(request, _("Question created successfully."))
            return redirect(question_template_detailed_view, id)
        else:
            messages.error(request, _("Error occurred during question creation!"))
            return redirect(question_template_detailed_view, id)


@login_required
def question_view(request, id):
    """
    This view is used to  view  question object.
    Args:
        id(int) : primarykey of the question template.
    Returns:
        it will redirect to  question_template_detailed_view.
    """
    question_template = QuestionTemplate.objects.get(id=id)
    question_formset = modelformset_factory(Question, form=QuestionForm, extra=0)

    questions = question_template.question.all()
    formset = question_formset(queryset=questions)
    options = []
    question_types = ["text", "ratings", "boolean", "Multi-choices", "likert"]

    for question in questions:
        question_options = QuestionOptions.objects.filter(question_id=question)
        options.extend(question_options)
    context = {
        "question_template": question_template,
        "questions": questions,
        "question_options": options,
        "question_types": question_types,
        "formset": formset,
    }
    return render(
        request,
        "feedback/question_template/question_template_detailed_view.html",
        context,
    )


@login_required
@manager_can_enter(perm="pms.change_question")
def question_update(request, temp_id, q_id):
    """
    This view is used to  update  question object.
    Args:
        id (int): primarykey of question
        temp_id (int): primarykey of question_template
    Returns:
        it will redirect to  question_template_detailed_view.

    """
    if request.method == "POST":
        question = Question.objects.get(id=q_id)
        form = QuestionForm(request.POST, instance=question)
        if form.is_valid():
            question_type = form.cleaned_data["question_type"]
            if question_type == "4":
                # if question is Multi-choices
                option_a = form.cleaned_data["option_a"]
                option_b = form.cleaned_data["option_b"]
                option_c = form.cleaned_data["option_c"]
                option_d = form.cleaned_data["option_d"]
                options, created = QuestionOptions.objects.get_or_create(
                    question_id=question
                )
                options.option_a = option_a
                options.option_b = option_b
                options.option_c = option_c
                options.option_d = option_d
                options.save()
                form.save()
                messages.info(request, _("Question updated successfully."))
                return redirect(question_template_detailed_view, temp_id)
            else:
                form.save()
                question_options = QuestionOptions.objects.filter(question_id=question)
                if question_options:
                    question_options.delete()
                messages.info(request, _("Question updated successfully."))
                return redirect(question_template_detailed_view, temp_id)
        else:
            # Form submission had errors
            messages.error(
                request,
                "\n".join(
                    [
                        f"{field}: {error}"
                        for field, errors in form.errors.items()
                        for error in errors
                    ]
                ),
            )
            return redirect(question_template_detailed_view, temp_id)


@login_required
@manager_can_enter(perm="pms.delete_question")
def question_delete(request, id):
    """
    This view is used to  delete  question object.
    Args:
        id (int): primarykey of question
    Returns:
        it will redirect to  question_template_detailed_view.
    """

    try:
        # Code that may trigger the FOREIGN KEY constraint failed error
        question = Question.objects.filter(id=id).first()
        temp_id = question.template_id.id
        QuestionOptions.objects.filter(question_id=question).delete()
        question.delete()
        messages.success(request, _("Question deleted successfully!"))
        return redirect(question_template_detailed_view, temp_id)

    except IntegrityError:
        # Code to handle the FOREIGN KEY constraint failed error
        messages.error(
            request, _("Failed to delete question: Question template is in use.")
        )

    except Question.DoesNotExist:
        messages.error(request, _("Question not found."))
    except ProtectedError:
        messages.error(request, _("Related entries exists"))
    return redirect(question_template_detailed_view, temp_id)


@login_required
@manager_can_enter(perm="pms.add_questiontemplate")
def question_template_creation(request):
    """
    This view is used to  create   question template object.
    Args:
    Returns:
        it will redirect to  question_template_detailed_view.
    """
    if request.method == "POST":
        form = QuestionTemplateForm(request.POST)
        if form.is_valid():
            instance = form.save()
            return redirect(question_template_detailed_view, instance.id)
        else:
            messages.error(
                request,
                "\n".join(
                    [
                        f"{field}: {error}"
                        for field, errors in form.errors.items()
                        for error in errors
                    ]
                ),
            )
            return redirect(question_template_view)


@login_required
@manager_can_enter(perm="pms.view_questiontemplate")
def question_template_view(request):
    """
    This view is used to  view  question template  object.
    Returns:
        it will redirect to  question_template_detailed_view.
    """
    question_templates = QuestionTemplate.objects.all()
    context = {"form": QuestionTemplateForm, "question_templates": question_templates}
    if question_templates.exists():
        template = "feedback/question_template/question_template_view.html"
    else:
        template = "feedback/question_template/question_template_empty.html"
    return render(request, template, context)


@login_required
@manager_can_enter(perm="pms.view_questiontemplate")
def question_template_detailed_view(request, template_id, **kwargs):
    """
    This view is used to  view question template object.
    Args:
        id (int): primarykey of question template
        temp_id (int): primarykey of question_template
    Returns:
        it will redirect to  question_template_detailed_view.
    """

    question_template = QuestionTemplate.objects.get(id=template_id)
    questions = question_template.question.all()
    question_types = ["text", "ratings", "boolean", "multi-choices", "likert"]
    options = QuestionOptions.objects.filter(question_id__in=questions)

    # passing individual form
    question_form_list = [QuestionForm(instance=question) for question in questions]
    context = {
        "question_template": question_template,
        "questions": questions,
        "question_options": options,
        "question_types": question_types,
        "form": QuestionForm,
        "form_list": question_form_list,
    }
    return render(
        request,
        "feedback/question_template/question_template_detailed_view.html",
        context,
    )


@login_required
@manager_can_enter(perm="pms.change_questiontemplate")
def question_template_update(request, template_id):
    """
    This view is used to  update  question template object.
    Args:
        id (int): primarykey of question template
    Returns:
        it will redirect to  question_template_view.

    """
    question_template = QuestionTemplate.objects.filter(id=template_id).first()
    question_update_form = QuestionTemplateForm(instance=question_template)
    context = {"question_update_form": question_update_form}
    if request.method == "POST":
        form = QuestionTemplateForm(request.POST, instance=question_template)
        if form.is_valid():
            form.save()
            messages.info(request, _("Question template updated"))
            return redirect(question_template_view)
        context["question_update_form"] = form
    return render(
        request, "feedback/question_template/question_template_update.html", context
    )


@login_required
@manager_can_enter(perm="pms.delete_questiontemplate")
def question_template_delete(request, template_id):
    """
    This view is used to  delete  question template object.
    Args:
        id (int): primarykey of question template
    Returns:
        it will redirect to  question_template_view.
    """
    try:
        question_template = QuestionTemplate.objects.get(id=template_id)
        if Feedback.objects.filter(question_template_id=question_template):
            messages.info(request, _("This template is using in a feedback"))
            return redirect(question_template_view)
        question_template.delete()
        messages.success(request, _("The question template is deleted successfully !."))
    except QuestionTemplate.DoesNotExist:
        messages.error(request, _("question template not found."))
    except ProtectedError:
        messages.error(request, _("Related entries exists"))
    return redirect(question_template_view)


@login_required
@manager_can_enter(perm="pms.view_period")
def period_view(request):
    """
    This view is used to view period objects.
    Returns:
        it will return to period_view.
    """

    periods = Period.objects.all()
    context = {
        "periods": periods,
    }
    if periods.exists():
        template = "period/period_view.html"
    else:
        template = "period/period_empty.html"
    return render(request, template, context)


@login_required
@manager_can_enter(perm="pms.add_period")
@hx_request_required
def period_create(request):
    """
    This view is used to create period objects.
    Returns:
        it will redirect to period_view.
    """
    context = {"form": PeriodForm()}
    if request.method == "POST":
        form = PeriodForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, _("Period creation was Successful "))
            response = render(request, "period/period_create.html", context)
            return HttpResponse(
                response.content.decode("utf-8") + "<script>location.reload();</script>"
            )
        else:
            context["form"] = form
    return render(request, "period/period_create.html", context)


@login_required
@manager_can_enter(perm="pms.change_period")
def period_update(request, period_id):
    """
    This view is used to update period objects.
    Args:
        id (int): primarykey of period
    Returns:
        it will redirect to period_view.
    """

    period = Period.objects.filter(id=period_id).first()
    form = PeriodForm(instance=period)
    context = {"form": form}
    if request.method == "POST":
        form = PeriodForm(request.POST, instance=period)
        if form.is_valid():
            form.save()
            messages.info(request, _("Period updated  Successfully. "))
            response = render(request, "period/period_update.html", context)
            return HttpResponse(
                response.content.decode("utf-8") + "<script>location.reload();</script>"
            )
        else:
            context["form"] = form
    return render(request, "period/period_update.html", context)


@login_required
@manager_can_enter(perm="pms.delete_period")
def period_delete(request, period_id):
    """
    This view is used to delete period objects.
    Args:
        id (int): primarykey of period
    Returns:
        it will redirect to period_view.
    """
    try:
        obj_period = Period.objects.get(id=period_id)
        obj_period.delete()
        messages.info(request, _("Period deleted successfully."))
    except Period.DoesNotExist:
        messages.error(request, _("Period not found."))
    except ProtectedError:
        messages.error(request, _("Related entries exists"))
    return redirect(period_view)


@login_required
def period_change(request):
    """this function is used to detect the period change and return the start and end date of that period"""
    is_ajax = request.headers.get("X-Requested-With") == "XMLHttpRequest"
    if is_ajax:
        if request.method == "POST":
            data = json.load(request)
            period_obj = Period.objects.get(id=data)
            start_date = period_obj.start_date
            end_date = period_obj.end_date
            return JsonResponse({"start_date": start_date, "end_date": end_date})
        return JsonResponse({"failed": "failed"})
    return HttpResponse(status=204)


@login_required
def dashboard_view(request):
    """
    This view is used to view dashboard.
    Returns:
        it will redirect to dashboard.
    """
    user = request.user
    employee = Employee.objects.filter(employee_user_id=user).first()
    is_manager = Employee.objects.filter(
        employee_work_info__reporting_manager_id=employee
    )

    if user.has_perm("pms.view_employeeobjective") and user.has_perm(
        "pms.view_feedback"
    ):
        count_objective = EmployeeObjective.objects.all().count()
        count_key_result = EmployeeKeyResult.objects.all().count()
        count_feedback = Feedback.objects.all().count()
        okr_at_risk = EmployeeObjective.objects.filter(status="At Risk")
    elif is_manager:
        employees_ids = [employee.id for employee in is_manager]
        count_objective = EmployeeObjective.objects.filter(
            employee_id__in=employees_ids
        ).count()
        count_key_result = EmployeeObjective.objects.filter(
            emp_obj_id__employee_id__in=employees_ids
        ).count()
        count_feedback = Feedback.objects.filter(employee_id__in=employees_ids).count()
        okr_at_risk = EmployeeObjective.objects.filter(
            employee_id__in=employees_ids
        ).filter(status="At Risk")
    else:
        count_objective = EmployeeObjective.objects.filter(employee_id=employee).count()
        count_key_result = EmployeeKeyResult.objects.filter(
            employee_id=employee
        ).count()
        count_feedback = Feedback.objects.filter(employee_id=employee).count()
        okr_at_risk = EmployeeObjective.objects.filter(employee_id=employee).filter(
            status="At Risk"
        )
    context = {
        "count_objective": count_objective,
        "count_key_result": count_key_result,
        "count_feedback": count_feedback,
        "okr_at_risk": okr_at_risk,
    }
    return render(request, "dashboard/pms_dashboard.html", context)


@login_required
def dashboard_objective_status(request):
    """objective dashboard data"""
    is_ajax = request.headers.get("X-Requested-With") == "XMLHttpRequest"
    if is_ajax and request.method == "GET":
        objective_status = EmployeeObjective.STATUS_CHOICES
        data = {"message": _("No data Found...")}
        for status in objective_status:
            objectives = EmployeeObjective.objects.filter(status=status[0])
            objectives_count = filtersubordinates(
                request, queryset=objectives, perm="pms.view_employeeobjective"
            ).count()
            # if not objectives_count:

            data.setdefault("objective_label", []).append(status[1])
            data.setdefault("objective_value", []).append(objectives_count)
        return JsonResponse(data)


@login_required
def dashboard_key_result_status(request):
    """key result dashboard data"""
    is_ajax = request.headers.get("X-Requested-With") == "XMLHttpRequest"
    if is_ajax and request.method == "GET":
        key_result_status = EmployeeKeyResult.STATUS_CHOICES
        data = {"message": _("No data Found...")}
        for i in key_result_status:
            key_results = EmployeeKeyResult.objects.filter(status=i[0])
            key_results_count = filtersubordinates(
                request, queryset=key_results, perm="pms.view_employeekeyresult"
            ).count()
            data.setdefault("key_result_label", []).append(i[1])
            data.setdefault("key_result_value", []).append(key_results_count)
        return JsonResponse(data)


@login_required
def dashboard_feedback_status(request):
    """feedback dashboard data"""
    is_ajax = request.headers.get("X-Requested-With") == "XMLHttpRequest"
    if is_ajax and request.method == "GET":
        feedback_status = Feedback.STATUS_CHOICES
        data = {"message": _("No data Found...")}
        for i in feedback_status:
            feedbacks = Feedback.objects.filter(status=i[0])
            feedback_count = filtersubordinates(
                request, queryset=feedbacks, perm="pms.view_feedback"
            ).count()
            data.setdefault("feedback_label", []).append(i[1])
            data.setdefault("feedback_value", []).append(feedback_count)
        return JsonResponse(data)


def filtersubordinates(request, queryset, perm=None):
    """
    This method is used to filter out subordinates queryset element.
    """
    user = request.user
    if user.has_perm(perm):
        return queryset
    manager = Employee.objects.filter(employee_user_id=user).first()
    if manager:
        queryset = queryset.filter(
            employee_id__employee_work_info__reporting_manager_id=manager
        ) | queryset.filter(employee_id=manager)
        return queryset
    else:
        queryset = queryset.filter(employee_id=user.employee_get)
        return queryset


@login_required
def create_period(request):
    """
    This is an ajax method to return json response to create stage related
    to the project in the task-all form fields
    """

    if request.method == "GET":
        form = PeriodForm()
    if request.method == "POST":
        form = PeriodForm(request.POST)
        if form.is_valid():
            instance = form.save()
            return JsonResponse(
                {
                    "id": instance.id,
                    "name": instance.period_name,
                    "start_date": instance.start_date,
                    "end_date": instance.end_date,
                }
            )
        errors = form.errors.as_json()
        return JsonResponse({"errors": errors})
    return render(request, "okr/create_period.html", context={"form": form})


@login_required
def objective_bulk_archive(request):
    """
    This method is used to archive/un-archive bulk objectivs
    """
    ids = request.POST["ids"]
    ids = json.loads(ids)
    is_active = False
    message = _("un-archived")
    if request.GET.get("is_active") == "False":
        is_active = True
        message = _("archived")
    for objective_id in ids:
        objective_obj = EmployeeObjective.objects.get(id=objective_id)
        objective_obj.archive = is_active
        objective_obj.save()
        messages.success(
            request,
            _("{objective} is {message}").format(
                objective=objective_obj, message=message
            ),
        )
    return JsonResponse({"message": "Success"})


@login_required
@manager_can_enter(perm="pms.delete_employeeobjective")
def objective_bulk_delete(request):
    """
    This method is used to bulk delete objective
    """
    ids = request.POST["ids"]
    ids = json.loads(ids)
    for objective_id in ids:
        try:
            objective = EmployeeObjective.objects.get(id=objective_id)
            if objective.status == "Not Started" or objective.status == "Closed":
                objective.delete()
                messages.success(
                    request,
                    _("%(employee)s's %(objective)s deleted")
                    % {
                        "objective": objective.objective,
                        "employee": objective.employee_id,
                    },
                )
            else:
                messages.warning(
                    request,
                    _("You can't delete objective %(objective)s with status %(status)s")
                    % {"objective": objective.objective, "status": objective.status},
                )
        except EmployeeObjective.DoesNotExist:
            messages.error(request, _("Objective not found."))

    return JsonResponse({"message": "Success"})


@login_required
def feedback_bulk_archive(request):
    """
    This method is used to archive/un-archive bulk feedbacks
    """
    ids = request.POST["ids"]
    ids = json.loads(ids)
    is_active = False
    message = _("un-archived")
    if request.GET.get("is_active") == "False":
        is_active = True
        message = _("archived")
    for feedback_id in ids:
        feedback_id = Feedback.objects.get(id=feedback_id)
        feedback_id.archive = is_active
        feedback_id.save()
        messages.success(
            request,
            _("{feedback} is {message}").format(feedback=feedback_id, message=message),
        )
    return JsonResponse({"message": "Success"})


@login_required
@manager_can_enter(perm="pms.delete_feedback")
def feedback_bulk_delete(request):
    """
    This method is used to bulk delete feedbacks
    """
    ids = request.POST["ids"]
    ids = json.loads(ids)
    for feedback_id in ids:
        try:
            feedback = Feedback.objects.get(id=feedback_id)
            if feedback.status == "Closed" or feedback.status == "Not Started":
                feedback.delete()
                messages.success(
                    request,
                    _("Feedback %(review_cycle)s deleted successfully!")
                    % {"review_cycle": feedback.review_cycle},
                )
            else:
                messages.warning(
                    request,
                    _(
                        "You can't delete feedback %(review_cycle)s with status %(status)s"
                    )
                    % {
                        "review_cycle": feedback.review_cycle,
                        "status": feedback.status,
                    },
                )

        except Feedback.DoesNotExist:
            messages.error(request, _("Feedback not found."))
    return JsonResponse({"message": "Success"})


@login_required
def objective_select(request):
    """
    This method is used to return all the id of the employees to select the employee row
    """
    page_number = request.GET.get("page")
    table = request.GET.get("tableName")
    user = request.user.employee_get
    employees = EmployeeObjective.objects.all()
    if page_number == "all":
        if table == "all":
            employees = EmployeeObjective.objects.filter(archive=False)
        else:
            employees = EmployeeObjective.objects.filter(
                employee_id=user, archive=False
            )

    employee_ids = [str(emp.id) for emp in employees]
    total_count = employees.count()

    context = {"employee_ids": employee_ids, "total_count": total_count}

    return JsonResponse(context, safe=False)


@login_required
def objective_select_filter(request):
    """
    This method is used to return all the ids of the filtered employees
    """
    page_number = request.GET.get("page")
    filtered = request.GET.get("filter")
    filters = json.loads(filtered) if filtered else {}
    table = request.GET.get("tableName")
    user = request.user.employee_get

    employee_filter = ObjectiveFilter(filters, queryset=EmployeeObjective.objects.all())
    if page_number == "all":
        if table == "all":
            employee_filter = ObjectiveFilter(
                filters, queryset=EmployeeObjective.objects.all()
            )
        else:
            employee_filter = ObjectiveFilter(
                filters, queryset=EmployeeObjective.objects.filter(employee_id=user)
            )
        # Get the filtered queryset
        filtered_employees = employee_filter.qs

        employee_ids = [str(emp.id) for emp in filtered_employees]
        total_count = filtered_employees.count()

        context = {"employee_ids": employee_ids, "total_count": total_count}

        return JsonResponse(context)
