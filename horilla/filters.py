"""
filters.py
"""
import uuid
import django_filters
from django import forms
from base.methods import reload_queryset

def filter_by_name(queryset, name, value):
    """
    Filter queryset by first name or last name.
    """
    # Split the search value into first name and last name
    parts = value.split()
    first_name = parts[0]
    last_name = ' '.join(parts[1:]) if len(parts) > 1 else ''

    # Filter the queryset by first name and last name
    if first_name and last_name:
        queryset = queryset.filter(employee_id__employee_first_name__icontains=first_name, employee_id__employee_last_name__icontains=last_name)
    elif first_name:
        queryset = queryset.filter(employee_id__employee_first_name__icontains=first_name)
    elif last_name:
        queryset = queryset.filter(employee_id__employee_last_name__icontains=last_name)

    return queryset

class FilterSet(django_filters.FilterSet):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        reload_queryset(self.form.fields)
        for field_name, field in self.form.fields.items():
            filter_widget = self.filters[field_name]
            widget = filter_widget.field.widget
            if isinstance(widget, (forms.NumberInput, forms.EmailInput,forms.TextInput)):
                field.widget.attrs.update({'class': 'oh-input w-100'})
            elif isinstance(widget,(forms.Select,)):
                field.widget.attrs.update({'class': 'oh-select oh-select-2 select2-hidden-accessible','id':uuid.uuid4()})
            elif isinstance(widget,(forms.Textarea)):
                field.widget.attrs.update({'class': 'oh-input w-100'})
            elif isinstance(widget, (forms.CheckboxInput,forms.CheckboxSelectMultiple,)):
                field.widget.attrs.update({'class': 'oh-switch__checkbox'})
            elif isinstance(widget,(forms.ModelChoiceField)):
                field.widget.attrs.update({'class': 'oh-select oh-select-2 select2-hidden-accessible',})