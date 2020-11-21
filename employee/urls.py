from django.urls import path
from employee.views import SignUpView, SignInView, EmployeeInfoView, EmployeeManagementView

urlpatterns = [
    path('/signup', SignUpView.as_view()),
    path('/signin', SignInView.as_view()),
    path('/profile', EmployeeInfoView.as_view()),
    path('/employeemgmt/<int:employee_id>', EmployeeManagementView.as_view())
]
