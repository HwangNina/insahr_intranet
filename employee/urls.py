from django.urls import path
from employee.views import SignUpView

urlpatterns = [
    path('/signup', SignUpView.as_view()),
    path('/profile', EmployeeInfoView.as_view())
]
