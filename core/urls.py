from django.urls import path
from django.views.decorators.csrf import csrf_exempt

from core.tasks import merge_and_download
from core.views import RequestFile, scrapers_start_view

app_name = 'core'

urlpatterns = [
    path('start-scrapers/', scrapers_start_view, name='start-scrapers'),
    path('request-file/', csrf_exempt(RequestFile.as_view()), name='request-file'),
    path('merge-and-download&id=<int:text_id>/', merge_and_download, name='merge-and-download-with-text-id'),
]
