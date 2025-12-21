from django.urls import path

from app.jobrole.views import HybridSearchApiView, CandidateSearchFromResumeTextApiView, \
    StoreJobRoleApiView, UploadJobDescriptionAPIView, UploadResumeAPIView, MatchResumeToJobsAPIView

urlpatterns = [

    path('store-jd', StoreJobRoleApiView.as_view(), name='store-jd-or-resume'),
    path("hybrid-search/", HybridSearchApiView.as_view(), name="hybrid_search"),
    path("search-jobs-by-resume/", CandidateSearchFromResumeTextApiView.as_view(), name="search_jobs_by_resume"),

    path("store-jd-1", UploadJobDescriptionAPIView.as_view(), name="store-jd-1"),
    path("resume-upload-1/", UploadResumeAPIView.as_view(), name="resume-upload"),
    path("search-job-by-resume-1/", MatchResumeToJobsAPIView.as_view(), name="match-resume"),

]
