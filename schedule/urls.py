from django.urls import path
from schedule.views import ScheduleListView, ScheduleDetailView

urlpatterns = [
    path('/monthly', ScheduleListView.as_view()),
    path('/detail', ScheduleDetailView.as_view()),
    path('/detail/<int:schedule_id>', ScheduleDetailView.as_view()),
]
