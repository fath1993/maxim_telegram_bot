from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.cache import never_cache
from custom_logs.models import CustomLog


@never_cache
def logs_view(request, log_level):
    if log_level == 'debug':
        context = {'page_title': "لاگ عملکرد ربات در سطح برنامه", 'log_level': 'debug'}
    elif log_level == 'info':
        context = {'page_title': "لاگ عملکرد ربات در سطح اطلاعات", 'log_level': 'info'}
    elif log_level == 'all':
        context = {'page_title': "لاگ کامل عملکرد ربات", 'log_level': 'all'}
    elif log_level == 'scrapers':
        context = {'page_title': "لاگ عملکرد ربات در سطح خزنده ها", 'log_level': 'scrapers'}
    else:
        return JsonResponse({'message': 'Invalid URL'})
    if request.user.is_authenticated and request.user.is_superuser:
        return render(request, 'logs.html', context)
    else:
        return JsonResponse({'message': 'you are not authorized to view the content'})


def ajax_logs_data(request):
    log_level = request.POST['log_level']
    log_list = []
    if log_level == 'debug':
        logs = CustomLog.objects.filter(log_level='debug').order_by('-id')[:40]
    elif log_level == 'info':
        logs = CustomLog.objects.filter(log_level='info').order_by('-id')[:40]
    elif log_level == 'all':
        logs = CustomLog.objects.filter().order_by('-id')[:40]
    elif log_level == 'scrapers':
        logs = CustomLog.objects.filter(log_level='scrapers').order_by('-id')[:40]
    else:
        return JsonResponse({'result': 'none'})
    for log in logs:
        log_list.append([log.created_at.strftime('%Y-%m-%d %H:%M'), log.description])
    print(log_list)
    return JsonResponse({'result': log_list})


