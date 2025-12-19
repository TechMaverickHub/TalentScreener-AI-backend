from django.urls import path

from app.jobrole.views import HybridSearchApiView, CandidateSearchFromResumeTextApiView, \
    StoreJobRoleApiView

urlpatterns = [

    path('store-jd', StoreJobRoleApiView.as_view(), name='store-jd-or-resume'),
    path("hybrid-search/", HybridSearchApiView.as_view(), name="hybrid_search"),
    path("search-jobs-by-resume/", CandidateSearchFromResumeTextApiView.as_view(), name="search_jobs_by_resume"),

]
