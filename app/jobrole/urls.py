from django.urls import path

from app.jobrole.views import UploadJobDescriptionAPIView, UploadResumeAPIView, MatchResumeToJobsAPIView, \
    JobRoleListFilterAPIView

urlpatterns = [

    #Admin views
    path("upload", UploadJobDescriptionAPIView.as_view(), name="store-jd-1"),
    path("list-filter", JobRoleListFilterAPIView.as_view(), name="list-filter"),

    #User views
    path("resume-upload/", UploadResumeAPIView.as_view(), name="resume-upload"),
    path("resume-match-jobs/", MatchResumeToJobsAPIView.as_view(), name="match-resume"),



]
