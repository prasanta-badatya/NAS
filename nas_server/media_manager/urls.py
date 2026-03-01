from django.urls import path

from . import views

urlpatterns = [
    path("",                        views.MediaListView.as_view(),       name="media-list"),
    path("upload/",                 views.UploadView.as_view(),          name="media-upload"),
    path("trash/",                  views.TrashListView.as_view(),       name="media-trash"),
    path("batch-download/",         views.BatchDownloadView.as_view(),   name="media-batch-download"),
    path("history/",                views.UploadHistoryView.as_view(),   name="upload-history"),
    path("<int:pk>/",               views.MediaDetailView.as_view(),     name="media-detail"),
    path("<int:pk>/serve/",         views.ServeMediaView.as_view(),      name="media-serve"),
    path("<int:pk>/thumbnail/",     views.ServeThumbnailView.as_view(),  name="media-thumbnail"),
    path("<int:pk>/restore/",       views.RestoreView.as_view(),         name="media-restore"),
    path("<int:pk>/permanent/",     views.PermanentDeleteView.as_view(), name="media-permanent-delete"),
]