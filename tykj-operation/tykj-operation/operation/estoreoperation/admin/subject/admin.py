import datetime
from django.utils.translation import ugettext_lazy as _

from estorecore.admin.sites import custom_site
from estoreoperation.promotion.admin import ActivityAdmin
from estoreoperation.app.admin import CategorySubjectAdmin
from estoreoperation.app.models import SubjectItem
from estoreoperation.admin.subject.models import AppSubject, Activity


class AppSubjectAdmin(CategorySubjectAdmin):
    list_display = ('order', 'name', 'id', 'sub_title', 'subject_items', 'clicks_count', 'modified_time', \
            'modifier', 'published', 'sync_status')
    list_display_links = ('name',)
    ordering = ('-order',)

    def subject_items(self, obj):
        return """<a href="/admin/utilities/subjectapplication/?subject__exact=%(subject)s">
                    <strong>%(items)s</strong>
                </a>""" % {"subject": obj.id, "id": obj.id, "items": SubjectItem.objects.filter(subject__pk__exact=obj.id).count()}
    subject_items.allow_tags = True
    subject_items.short_description = _("subject items")

    def render_change_form(self, request, context, *args, **kwargs):
        context['adminform'].form.fields['pub_date'].initial = datetime.datetime.now()
        return super(AppSubjectAdmin, self).render_change_form(request, context, *args, **kwargs)


class ActivityAdmin(ActivityAdmin):
    list_display = ('order', 'title', 'id', 'tag', 'type', 'attr', 'start_date', 'end_date', \
            'status', 'modified_time', 'published', 'sync_status')
    list_display_links = ('title',)
    ordering = ('order',)


custom_site.register(AppSubject, AppSubjectAdmin)
custom_site.register(Activity, ActivityAdmin)
