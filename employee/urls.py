from django.urls import path
from employee.views import SignUpView, SignInView, EmployeeInfoView, ProfileImageView

urlpatterns = [
    path('/signup', SignUpView.as_view()),
    path('/signin', SignInView.as_view()),
    path('/profile', EmployeeInfoView.as_view()),
    path('/profile/image', ProfileImageView.as_view())
]
