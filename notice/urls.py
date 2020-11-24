from django.urls import path
from notice.views import NoticeListView, NoticeDetailView, NoticeMainView

urlpatterns = [
    path('/list', NoticeListView.as_view()),
    path('/list/<str:search>', NoticeListView.as_view()),
    path('/detail', NoticeDetailView.as_view()),
    path('/detail/<int:notice_id>', NoticeDetailView.as_view()),
    path('/main', NoticeMainView.as_view())
]