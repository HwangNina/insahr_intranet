from django.urls import path
from .views import MainListView, ProjectListView, LikeView, ThreadView

urlpatterns = [
    path('/main', MainListView.as_view()),
    path('/list', ProjectListView.as_view()),
    path('/list/<int:project_id>', ProjectListView.as_view()),
    path('/like/<int:project_id>', LikeView.as_view()),
    path('/like', LikeView.as_view()),
    path('/detail/<int:project_id>', ThreadView.as_view()),
]
