from django.utils.translation import ugettext_lazy as _
from estorecore.admin.sites import custom_site
from estorecore.admin import EntityModelAdmin, TabularInline
from estoreoperation.update.models import UpdateButton, UpdateApp
from estoreoperation.update.forms import UpdateAppAdminForm
from estorecore.models.constants import REVIEW_STATUS
from estoreoperation.patch.service import queue_single_patch_job

class UpdateButtonInline(TabularInline):
    model = UpdateButton
    fields = ('action', 'btn', 'order')

    def queryset(self, request):
        qs = super(UpdateButtonInline, self).queryset(request)
        return qs.filter(hided__exact=False)


class UpdateAppAdmin(EntityModelAdmin):
    form = UpdateAppAdminForm
    list_editable = ('published', 'review_status')
    list_display = ('package_name', 'version_name', 'source', 'version_code', 'title', 'download_url', 'download_path', \
            'is_force', 'is_auto', 'channel_promote', 'content_title', 'change_log', 'published', 'review_status')
    list_per_page = 50
    list_filter = ('package_name', 'is_force', 'is_auto', 'review_status','published')
    search_fields = ['package_name', 'title']
    ordering = ('-created_time',)
    fieldsets = (
            (_('Basic'), {
                'fields': ('package_name', 'version_name', 'source', 'version_code', 'title', 'package_hash', 'package_size', 'download_url', 'download_path'),
                }),
            (_('Update Info'), {
                'fields': ('is_force', 'is_auto', 'is_patch', 'channel_promote', 'device', 'content_title', 'change_log'),
                }),
            (_('Status'), {
                'fields': ('published', 'review_status'),
                }),
            )
    inlines = (
            UpdateButtonInline,
        )

    def save_model(self, request, obj, form, change):
        super(UpdateAppAdmin, self).save_model(request, obj, form, change)
        if "_saveandsync" in request.POST:
            if obj.review_status == REVIEW_STATUS.APPROVED and obj.is_patch == 1:
                queue_single_patch_job(obj.package_name,obj.version_code, obj.package_hash)

custom_site.register(UpdateApp, UpdateAppAdmin)
