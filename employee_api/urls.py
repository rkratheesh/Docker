from django.urls import path, re_path
from . import views


urlpatterns = [
    re_path(r'^employees/(?P<pk>\d+)?$',
            views.EmployeeAPIView.as_view(), name='employee-detail'),
    re_path(r'^employee-bank-details/(?P<pk>\d+)?$',
            views.EmployeeBankDetailsAPIView.as_view(), name='employee-bank-details-detail'),
    re_path(r'^employee-work-information/(?P<pk>\d+)?$',
            views.EmployeeWorkInformationAPIView.as_view(), name='employee-work-information-detail'),
    path('employees-groupby/<str:class_name>',
         views.EmployeeGroupByView.as_view(), name='employee-groupby'),
    path('employee-work-info-export',
         views.EmployeeWorkInfoExportView.as_view(), name='employee-work-info-export'),
    path('employee-work-info-import',
         views.EmployeeWorkInfoImportView.as_view(), name='employee-work-info-import'),
    path('employee-bulk-update',views.EmployeeBulkUpdateView.as_view(),name='Employee-Bulk-Update')
    
]
