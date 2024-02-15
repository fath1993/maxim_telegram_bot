from django.contrib import admin
from django.contrib.admin.helpers import ACTION_CHECKBOX_NAME

from custom_logs.models import CustomLog, custom_log


@admin.register(CustomLog)
class CustomLogAdmin(admin.ModelAdmin):
    using = 'log_db'

    list_display = (
        'created_at_display',
        'description_display',
        'log_level',
    )

    readonly_fields = (
        'created_at',
    )
    list_filter = (
        'log_level',
    )

    search_fields = (
        'description',
    )

    fields = (
        'description',
        'log_level',
        'created_at',
    )

    @admin.display(description="تاریخ ایجاد", empty_value='???')
    def created_at_display(self, obj):
        data_time = str(obj.created_at.strftime('%y-%m-%d - %H:%M:%S %Z'))
        return data_time

    @admin.display(description="خلاصه", empty_value='???')
    def description_display(self, obj):
        description_summary = str(obj.description[:150])
        return description_summary

    def changelist_view(self, request, extra_context=None):
        if 'action' in request.POST and request.POST['action'] == 'delete_all_logs':
            if not request.POST.getlist(ACTION_CHECKBOX_NAME):
                post = request.POST.copy()
                for u in CustomLog.objects.all():
                    post.update({ACTION_CHECKBOX_NAME: str(u.id)})
                request._set_post(post)
        return super(CustomLogAdmin, self).changelist_view(request, extra_context)


    @admin.action(description='حذف تمامی لاگ ها')
    def delete_all_logs(self, request, queryset):
        try:
            CustomLog.objects.all().delete()
        except Exception as e:
            custom_log(str(e))


    actions = (
        'delete_all_logs',
    )