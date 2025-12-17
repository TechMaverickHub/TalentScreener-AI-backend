from django.urls import path

from app.jobrole.views import StoreJDOrResumeApiView
from app.user.views import SuperAdminSetupView, UserLogin, UserLogout, AdminSetupView, AdminListFilter, UserDetailAPI, \
    UserSetupView

urlpatterns = [

    path('store-jd-or-resume/', StoreJDOrResumeApiView.as_view(), name='store-jd-or-resume'),



]
