from django.conf import settings
from django.utils.html import escape
from django.utils.text import truncate_words
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _
from django.contrib.admin.widgets import ForeignKeyRawIdWidget


class CustomForeignKeyRawIdWidget(ForeignKeyRawIdWidget):

    def render(self, name, value, attrs=None):
        if attrs is None:
            attrs = {}
        related_url = '../../../%s/%s/' % (self.rel.to._meta.app_label, self.rel.to._meta.object_name.lower())
        params = self.url_parameters()
        if params:
            url = u'?' + u'&amp;'.join([u'%s=%s' % (k, v) for k, v in params.items()])
        else:
            url = u''
        if "class" not in attrs:
            attrs['class'] = 'vForeignKeyRawIdAdminField customForeignKey'   # The JavaScript looks for this hook.
        output = [super(ForeignKeyRawIdWidget, self).render(name, value, attrs)]
        # TODO: "id_" is hard-coded here. This should instead use the correct
        # API to determine the ID dynamically.
        output.append(u'<a href="%s%s" class="related-lookup" id="lookup_id_%s" onclick="return showRelatedObjectLookupPopup(this);"> ' % \
            (related_url, url, name))
        output.append(u'<img src="%simg/admin/selector-search.gif" width="16" height="16" alt="%s" /></a>' % (settings.ADMIN_MEDIA_PREFIX, _('Lookup')))
        output.append(self.label_for_value(value))
        return mark_safe(u''.join(output))

    def label_for_value(self, value):
        key = self.rel.get_related_field().name
        obj_name = self.rel.to._meta.object_name
        related_url = '../../../%s/%s' % (self.rel.to._meta.app_label, self.rel.to._meta.object_name.lower())
        if value:
            try:
                obj = self.rel.to._default_manager.using(self.db).get(**{key: value})
                return '&nbsp;<a href="%s/%s/" cls_name="%s" target="_blank"><strong>%s</strong></a>' \
                        % (related_url, value, obj_name, escape(truncate_words(obj, 14)))
            except (ValueError, self.rel.to.DoesNotExist):
                return '&nbsp;<a href="" cls_name="" target="_blank"><strong></strong></a>'
        else:
            return '&nbsp;<a href="%s/obj_id_placeholder/" cls_name="%s" target="_blank"><strong></strong></a>' \
                    % (related_url, obj_name)
