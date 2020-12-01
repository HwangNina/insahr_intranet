from django.urls import path
from hr_mgmt.views import HumanResourceListView, HumanResourceManagementView

urlpatterns = [
    path('/list', HumanResourceListView.as_view()),
    path('/management/<int:employee_id>',HumanResourceManagementView.as_view())
]
