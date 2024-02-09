from django.http import JsonResponse


def motion_array_check_auth_view(request):
    if request.user.is_authenticated and request.user.is_superuser:
        if request.method == 'GET':
            motion_array_check_auth()
            return JsonResponse({'message': 'motion_array_auth: motion array check auth function has been started'})
        else:
            return JsonResponse({'message': 'not allowed'})
    else:
        return JsonResponse({'message': 'not allowed'})