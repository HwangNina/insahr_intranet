from django.urls import path
from project.views import 뷰이름

urlpatterns = [
    path('/', SignUpView.as_view()),
]
