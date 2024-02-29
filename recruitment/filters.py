"""
filters.py

This page is used to register filter for recruitment models

"""
import uuid
import django_filters
from django import forms
from recruitment.models import Candidate, Recruitment, Stage, RecruitmentSurvey
from base.filters import FilterSet

# from django.forms.widgets import Boo




class CandidateFilter(FilterSet):
    """
    Filter set class for Candidate model

    Args:
        FilterSet (class): custom filter set class to apply styling
    """

    name = django_filters.CharFilter(field_name="name", lookup_expr="icontains")
    start_date = django_filters.DateFilter(
        field_name="recruitment_id__start_date",
        widget=forms.DateInput(attrs={"type": "date"}),
    )
    end_date = django_filters.DateFilter(
        field_name="recruitment_id__end_date",
        widget=forms.DateInput(attrs={"type": "date"}),
    )
    scheduled_from = django_filters.DateFilter(
        field_name="joining_date",
        lookup_expr="gte",
        widget=forms.DateInput(attrs={"type": "date"}),
    )
    scheduled_till = django_filters.DateFilter(
        field_name="joining_date",
        lookup_expr="lte",
        widget=forms.DateInput(attrs={"type": "date"}),
    )
    recruitment = django_filters.CharFilter(
        field_name="recruitment_id__title", lookup_expr="icontains"
    )

    class Meta:
        """
        Meta class to add the additional info
        """

        model = Candidate
        fields = [
            "recruitment",
            "recruitment_id",
            "stage_id",
            "schedule_date",
            "email",
            "mobile",
            "country",
            "state",
            "city",
            "zip",
            "gender",
            "start_onboard",
            "hired",
            "canceled",
            "is_active",
            "recruitment_id__company_id",
            "job_position_id",
            "recruitment_id__closed",
            "recruitment_id__is_active",
            "job_position_id__department_id",
            "recruitment_id__recruitment_managers",
            "stage_id__stage_managers",
            "stage_id__stage_type",
            "joining_date",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.form.fields["is_active"].initial = True
        for field in self.form.fields.keys():
            self.form.fields[field].widget.attrs["id"] = f"{uuid.uuid4()}"


BOOLEAN_CHOICES = (
    ("", ""),
    ("false", "False"),
    ("true", "True"),
)


class RecruitmentFilter(FilterSet):
    """
    Filter set class for Recruitment model

    Args:
        FilterSet (class): custom filter set class to apply styling
    """

    description = django_filters.CharFilter(lookup_expr="icontains")
    start_date = django_filters.DateFilter(
        field_name="start_date", widget=forms.DateInput(attrs={"type": "date"})
    )
    end_date = django_filters.DateFilter(
        field_name="end_date", widget=forms.DateInput(attrs={"type": "date"})
    )
    start_from = django_filters.DateFilter(
        field_name="start_date",
        lookup_expr="gte",
        widget=forms.DateInput(attrs={"type": "date"}),
    )
    end_till = django_filters.DateFilter(
        field_name="end_date",
        lookup_expr="lte",
        widget=forms.DateInput(attrs={"type": "date"}),
    )
    search = django_filters.CharFilter(method="filter_by_name")

    class Meta:
        """
        Meta class to add the additional info
        """

        model = Recruitment
        fields = [
            "recruitment_managers",
            "company_id",
            "title",
            "is_event_based",
            "start_date",
            "end_date",
            "closed",
            "is_active",
            "job_position_id",
        ]

    def filter_by_name(self, queryset, _, value):
        """
        Filter queryset by first name or last name.
        """
        # Split the search value into first name and last name
        parts = value.split()
        first_name = parts[0]
        last_name = " ".join(parts[1:]) if len(parts) > 1 else ""

        job_queryset = queryset.filter(
            open_positions__job_position__icontains=value
        ) | queryset.filter(title__icontains=value)
        if first_name and last_name:
            queryset = queryset.filter(
                recruitment_managers__employee_first_name__icontains=first_name,
                recruitment_managers__employee_last_name__icontains=last_name,
            )
        elif first_name:
            queryset = queryset.filter(
                recruitment_managers__employee_first_name__icontains=first_name
            )
        elif last_name:
            queryset = queryset.filter(
                recruitment_managers__employee_last_name__icontains=last_name
            )

        queryset = queryset | job_queryset
        return queryset.distinct()


class StageFilter(FilterSet):
    """
    Filter set class for Stage model

    Args:
        FilterSet (class): custom filter set class to apply styling
    """

    search = django_filters.CharFilter(method="filter_by_name")

    class Meta:
        """
        Meta class to add the additional info
        """

        model = Stage
        fields = [
            "recruitment_id",
            "recruitment_id__job_position_id",
            "recruitment_id__job_position_id__department_id",
            "recruitment_id__company_id",
            "recruitment_id__recruitment_managers",
            "stage_managers",
            "stage_type",
        ]

    def filter_by_name(self, queryset, _, value):
        """
        Filter queryset by first name or last name.
        """
        # Split the search value into first name and last name
        parts = value.split()
        first_name = parts[0]
        last_name = " ".join(parts[1:]) if len(parts) > 1 else ""

        # Filter the queryset by first name and last name
        stage_queryset = queryset.filter(stage__icontains=value)
        if first_name and last_name:
            queryset = queryset.filter(
                stage_managers__employee_first_name__icontains=first_name,
                stage_managers__employee_last_name__icontains=last_name,
            )
        elif first_name:
            queryset = queryset.filter(
                stage_managers__employee_first_name__icontains=first_name
            )
        elif last_name:
            queryset = queryset.filter(
                stage_managers__employee_last_name__icontains=last_name
            )

        return queryset | stage_queryset


class SurveyFilter(FilterSet):
    """
    SurveyFIlter
    """

    options = django_filters.CharFilter(
        lookup_expr="icontains",
        label="Options",
        field_name="options",
    )

    question = django_filters.CharFilter(
        lookup_expr="icontains",
        label="Question",
        field_name="question",
    )

    class Meta:
        """
        class Meta for additional options
        """

        model = RecruitmentSurvey
        fields = "__all__"
        exclude = [
            "sequence",
        ]

class CandidateReGroup:
    """
    Class to keep the field name for group by option
    """
    fields = [
        ("","select"),
        ("recruitment_id","Recruitment"),
        ("job_position_id","Job Position"),
        ("hired", "Status"),
    ]