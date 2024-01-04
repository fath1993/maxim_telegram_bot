from django.http import JsonResponse
from envato.enva_defs import envato_check_auth


def envato_check_auth_view(request):
    if request.user.is_authenticated and request.user.is_superuser:
        if request.method == 'GET':
            envato_check_auth()
            return JsonResponse({'message': 'envato_auth: envato check auth function has been started'})
        else:
            return JsonResponse({'message': 'not allowed'})
    else:
        return JsonResponse({'message': 'not allowed'})


# def envato_auth_all_view(request):
#     if request.user.is_authenticated and request.user.is_superuser:
#         if request.method == 'GET':
#             envato_auth_all()
#             return JsonResponse({'message': 'envato_auth: sign-in function has been started'})
#         else:
#             return JsonResponse({'message': 'not allowed'})
#     else:
#         return JsonResponse({'message': 'not allowed'})
#
#
# def envato_auth_view(request):
#     if request.user.is_authenticated and request.user.is_superuser:
#         if request.method == 'GET':
#             envato_auth()
#             return JsonResponse({'message': 'envato_auth: sign-in function has been started'})
#         else:
#             return JsonResponse({'message': 'not allowed'})
#     else:
#         return JsonResponse({'message': 'not allowed'})

