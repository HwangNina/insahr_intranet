from django.urls import path
from .views import WorkTimeView

urlpatterns = [
    path('/time', WorkTimeView.as_view()),
]
