from django.urls import path
from django.views.decorators.csrf import csrf_exempt

from core.views import RequestFile, merge_and_download

app_name = 'core'

urlpatterns = [
    path('request-file/', csrf_exempt(RequestFile.as_view()), name='request-file'),
    path('merge-and-download&id=<int:text_id>/', merge_and_download, name='merge-and-download-with-text-id'),
]
