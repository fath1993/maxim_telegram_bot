from django.urls import path

from scrapers.views import envato_check_auth_view, motion_array_check_auth_view

app_name = 'scrapers'

urlpatterns = [
    path('envato-check-auth/', envato_check_auth_view, name='envato-check-auth'),
    # path('envato-sign-in-all/', envato_auth_all_view, name='envato-auth-all-view'),
    # path('envato-sign-in/', envato_auth_view, name='envato-auth-view'),

    path('motion-array-check-auth/', motion_array_check_auth_view, name='motion-array-check-auth'),
]
