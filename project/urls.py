from django.urls import path
from .views import MainListView, ProjectListView, ThreadView

urlpatterns = [
    path('/main', MainListView.as_view()),
    path('/list', ProjectListView.as_view()),
    path('/detail/<int:project_id>', ThreadView.as_view()),
]
