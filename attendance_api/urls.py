from django.urls import path
from .views import *
from .views import AttendanceView

urlpatterns = [
    path('clock-in/', ClockInAPIView.as_view(), name='check-in'),
    path('clock-out/', ClockOutAPIView.as_view(), name='check-out'),
    path('attendance/<int:pk>/', AttendanceView.as_view(), name='attendance-detail'),
    path('attendance/<str:type>', AttendanceView.as_view(), name='attendance-list'),
    path('attendance/', AttendanceView.as_view(), name='attendance-list'),
    path('attendance-overtime-view/<int:pk>/', AttendanceOverTimeView.as_view(), name=''),
    path('attendance-overtime-view/', AttendanceOverTimeView.as_view(), name=''),
    path('late-come-early-out-view/', LateComeEarlyOutView.as_view(), name=''),
    path('attendance-activity/', AttendanceActivityView.as_view(), name=''),
]