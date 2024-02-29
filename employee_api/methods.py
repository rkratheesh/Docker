from employee.models import Employee
from django.db.models import Count
from rest_framework.pagination import PageNumberPagination

def get_next_badge_id():
    """
    This method is used to generate badge id
    """
    try:
        highest_badge_id = Employee.objects.filter(badge_id__isnull=False).order_by('-badge_id').first().badge_id
    except AttributeError:
        highest_badge_id = None
    
    # Increment the badge_id if it exists, otherwise start from '1'
    if highest_badge_id:
        if '#' in highest_badge_id:
            prefix, number = highest_badge_id.split('#')  # Split prefix and number
            new_number = str(int(number) + 1).zfill(len(number))  # Increment the number
            new_badge_id = f"{prefix}#{new_number}"
        else:
            new_badge_id = f"{highest_badge_id}#001"  # Add number to existing prefix
    else:
        new_badge_id = "EMP#001"  # Default start badge ID if no employees exist
    return new_badge_id


def groupby_queryset(model, field_name,request):
    """
    Get counts of related objects grouped by the specified field.
    Args:
        model_name (str): The name of the model.
        field_name (str): The name of the field to group by.
    Returns:
        list: A list of dictionaries containing the grouped counts.
    """

    counts = model.objects.values(field_name)
    counts = model.objects.values(field_name).annotate(count=Count(field_name))
    related_model = model._meta.get_field(field_name).related_model
    data = []
    
    for item in counts:
        if item[field_name] is None:
            continue 
        if isinstance(item[field_name],int):
            grouby_name = related_model.objects.filter(id=item[field_name]).first()
        else:
            grouby_name = item[field_name]
        count = item['count']
        data.append({field_name:item[field_name],"field_name": str(grouby_name), 'count': count})
    pagination = PageNumberPagination()
    page = pagination.paginate_queryset(data,request)
    return pagination.get_paginated_response(page)
    