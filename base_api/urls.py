from django.urls import re_path,path
from . import views

urlpatterns = [

    
    re_path(r'^job-positions/(?P<pk>\d+)?$', views.JobPositionView.as_view(), name="job_position_detail"),
    re_path(r'^job-roles/(?P<pk>\d+)?$', views.JobRoleView.as_view(), name="job_roles_details"),
    re_path(r'^companies/(?P<pk>\d+)?$', views.CompanyView.as_view(), name="companies_detail"),
    re_path(r'^departments/(?P<pk>\d+)?$', views.DepartmentView.as_view(), name="job_position_detail"),
    re_path(r'^work-types/(?P<pk>\d+)?$', views.WorkTypeView.as_view(), name="worktype_detail"),
    re_path(r'^rotating-worktypes/(?P<pk>\d+)?$', views.RotatingWorkTypeView.as_view(), name="rotating-worktypes-details"),
    re_path(r'^rotating-worktype-assigns/(?P<pk>\d+)?$', views.RotatingWorkTypeAssignView.as_view(), name='rotating-worktype-details'),
    re_path(r'^employee-shiftdays/(?P<pk>\d+)?$', views.EmployeeShiftDayView.as_view(), name='employee-shift-days-details'),
    re_path(r'^employee-shift/(?P<pk>\d+)?$', views.EmployeeShiftView.as_view(), name='employee-shift-details'),
    re_path(r'^employee-shift-schedules/(?P<pk>\d+)?$', views.EmployeeShiftScheduleView.as_view(), name='employeeshiftschedule-details'),
    re_path(r'^rotating-shifts/(?P<pk>\d+)?$', views.RotatingShiftView.as_view(), name='rotating-shifts-details'),
    re_path(r'^rotating-shift-assigns/(?P<pk>\d+)?$', views.RotatingShiftAssignView.as_view(), name='rotating-shift-assigns-details'),
    re_path(r'^worktype-requests/(?P<pk>\d+)?$', views.WorkTypeRequestView.as_view(), name='worktype-requests-details'),
    re_path(r'^worktype/(?P<pk>\d+)?$', views.WorkTypeView.as_view(), name='worktype-details'),
    re_path(r'^shift-requests/(?P<pk>\d+)?$', views.ShiftRequestView.as_view(), name='shift-requests-details'),
    path('shift-request-groupby/<str:class_name>', views.ShiftRequestGroupByView.as_view(), name='shift-requests-groupby'),
    path('shift-request-approve/<int:pk>', views.ShiftRequestApproveView.as_view(), name='shift-requests-approve'),
    path('shift-request-bulk-approve', views.ShiftRequestBulkApproveView.as_view(), name='shift-request-bulk-approve'),
    path('shift-request-cancel/<int:pk>', views.ShiftRequestCancelView.as_view(), name='shift-request-cancel'),
    path('shift-request-bulk-cancel', views.ShiftRequestBulkCancelView.as_view(), name='shift-request-bulk-cancel'),
    path('shift-request-delete/<int:pk>', views.ShiftRequestDeleteView.as_view(), name='shift-request-delete'),
    path('shift-request-bulk-delete', views.ShiftRequestDeleteView.as_view(), name='shift-request-bulk-delete'),
    path('shift-request-export', views.ShiftRequestExportView.as_view(), name='shift-request-export'),

]
