from django.urls import path, include

from accounts.views import login_view, logout_view, ProfileView, ProfileEditView, ProfileDownloadHistoryView, \
    ProfileRedeemHistoryView

app_name = 'accounts'

urlpatterns = [
    # authenticate
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),

    path('profile&user-id=<int:user_id>/', ProfileView.as_view(), name='profile-with-user-id'),
    path('profile-edit&user-id=<int:user_id>/', ProfileEditView.as_view(), name='profile-edit-with-user-id'),
    path('profile-download-history&user-id=<int:user_id>/', ProfileDownloadHistoryView.as_view(), name='profile-download-history-with-user-id'),
    path('profile-redeem-history&user-id=<int:user_id>/', ProfileRedeemHistoryView.as_view(), name='profile-redeem-history-with-user-id'),
]

