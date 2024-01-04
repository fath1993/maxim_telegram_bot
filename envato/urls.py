from django.urls import path
from envato.views import envato_check_auth_view

app_name = 'envato'

urlpatterns = [
    path('envato-check-auth/', envato_check_auth_view, name='envato-check-auth'),
    # path('envato-sign-in-all/', envato_auth_all_view, name='envato-auth-all-view'),
    # path('envato-sign-in/', envato_auth_view, name='envato-auth-view'),
]
