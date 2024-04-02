from django.urls import path

from website.views import start_service_view, stop_service_view

app_name = 'website'

urlpatterns = [
    path('start/', start_service_view, name='start'),
    path('stop/', stop_service_view, name='stop'),
]
