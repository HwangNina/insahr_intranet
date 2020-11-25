from django.urls import path
from employee.views import SignUpView, SignInView, EmployeeInfoView

urlpatterns = [
    path('/hr/list', HumanResourceListView.as_view()),
    path('/hr/management',HumanResourceManagementView.as_view())
]
