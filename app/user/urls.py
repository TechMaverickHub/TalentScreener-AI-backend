from django.urls import path

from app.user.views import SuperAdminSetupView, UserLogin, UserLogout, AdminSetupView, AdminListFilter, UserDetailAPI, \
    UserSetupView

urlpatterns = [
    # Authentication
    path('login/', UserLogin.as_view(), name='user-login'),
    path('logout/', UserLogout.as_view(), name='user-logout'),

    # Setup
    path('super-admin-setup/', SuperAdminSetupView.as_view(), name='super-admin-setup'),
    path('admin-setup/', AdminSetupView.as_view(), name='admin-setup'),
    path('user-sign-up/', UserSetupView.as_view(), name='user-setup'),



    # Superadmin views
    path('admin-list-filter/', AdminListFilter.as_view(), name='admin-list-filter'),
    path('<str:pk>', UserDetailAPI.as_view(), name='user-detail')



]
