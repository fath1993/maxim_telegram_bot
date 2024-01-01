from django.urls import path, include

from cpanel.views import DashboardView, ajax_get_resource_usage, get_network_transfer_rate, UserView, UserRemoveView, \
    RedeemCodeView, RemoveRedeemCodeView

app_name = 'cpanel'

urlpatterns = [
    path('', DashboardView.as_view(), name='dashboard'),
    path('resource/ajax-get-network-usage/', ajax_get_resource_usage, name='ajax-get-network-usage'),
    path('resource/ajax-get-network-transfer-rate/', get_network_transfer_rate, name='ajax-get-network-transfer-rate'),

    path('users/', UserView.as_view(), name='users'),
    path('user-remove&user-id=<int:user_id>/', UserRemoveView.as_view(), name='user-remove-with-user-id'),

    path('redeem-codes/', RedeemCodeView.as_view(), name='redeem-codes'),
    path('redeem-code-remove&id=<int:redeem_code_id>/', RemoveRedeemCodeView.as_view(), name='redeem-code-remove-with-id'),
]
