import datetime
from django.utils.translation import ugettext_lazy as _
from estorecore.admin.sites import custom_site
from estorecore.admin import EntityModelAdmin
from estoreoperation.push.models import Message
from estoreoperation.push.forms import PushMessageAdminForm
from estorecore.models.constants import COMMON_MESSAGE_ACTIONS


class PushMessageAdmin(EntityModelAdmin):
    form = PushMessageAdminForm
    list_editable = ('status', 'published', 'review_status')
    list_display = ('title', 'id', 'display_content', 'action', 'value_readable', 'invalid_before', 'invalid_after', \
            'display_area', 'status', 'published', 'review_status', 'sync_status')
    list_per_page = 50
    list_filter = ('status', 'review_status', 'display_area','published')
    search_fields = ['title', 'content']
    ordering = ('-created_time',)
    fieldsets = (
            (_('Basic'), {
                'fields': ('title', 'content', 'action', 'value', 'display_area', 'icon_url', 'icon_path'),
                }),
            (_('Invalid Date'), {
                'fields': ('invalid_before', 'invalid_after'),
                }),
            (_('Extra infos'), {
                'fields': ('extra_repeat_time', 'extra_act_hour'),
                'classes': ('collapse',)
                }),
            (_('Status'), {
                'fields': ('published', 'review_status'),
                }),
            (_('Targeting'), {
                'fields': (
                        ('tg_msg_group', 'tg_phone'),
                        ('tg_device', 'tg_sys_version', 'tg_screen_size'),
                        ('tg_operator',),
                        ('tg_city',),
                        ('tg_installed_app', 'tg_uninstalled_app'),
                        ('tg_gender', 'tg_marriage_status', 'tg_age', 'tg_keyword'),
                    ),
                'classes': ('targeting',),
                }),
            )
    def queryset(self,request):
        qs = super(PushMessageAdmin,self).queryset(request)
        if not request.user.is_superuser and request.user.has_perm('push.common_push_message'):
            action_list = COMMON_MESSAGE_ACTIONS.to_dict().keys()
            return qs.filter(action__in = action_list)
        return qs

    def render_change_form(self, request, context, *args, **kwargs):
        context['adminform'].form.fields['invalid_before'].initial = datetime.datetime.now()

        if not request.user.is_superuser and request.user.has_perm('push.common_push_message'):
            context['adminform'].form.fields['action'].choices = COMMON_MESSAGE_ACTIONS.to_choices()

        return super(PushMessageAdmin, self).render_change_form(request, context, *args, **kwargs)

custom_site.register(Message, PushMessageAdmin)
