from django.urls import path

from . import views

urlpatterns = [
    path("", views.MediaListView.as_view(), name="media-list"),
    path("upload/", views.UploadView.as_view(), name="media-upload"),
    path("history/", views.UploadHistoryView.as_view(), name="upload-history"),
    path("<int:pk>/", views.MediaDetailView.as_view(), name="media-detail"),
    path("<int:pk>/serve/", views.ServeMediaView.as_view(), name="media-serve"),
    path("<int:pk>/thumbnail/", views.ServeThumbnailView.as_view(), name="media-thumbnail"),
]
