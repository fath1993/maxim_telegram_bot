from django.urls import path

app_name = 'motion-array'

urlpatterns = [
    path('motion-array-check-auth/', motion_array_check_auth_view, name='motion-array-check-auth'),
]
