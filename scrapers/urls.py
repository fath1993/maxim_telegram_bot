from django.urls import path
from scrapers.views import envato_check_auth_view, motion_array_check_auth_view

app_name = 'scrapers'

urlpatterns = [
    path('envato-check-auth/', envato_check_auth_view, name='envato-check-auth'),
    path('motion-array-check-auth/', motion_array_check_auth_view, name='motion-array-check-auth'),
]
