#! -*- coding:utf-8 -*-
import logging
from django import forms
from django.db.models import F
from django.utils.translation import ugettext as _
from estorecore.models.app import Category
from estorecore.admin.sites import custom_site
from estorecore.admin.filters import SubCategoryFilterSpec, DecimalFieldFilterSpec
from estoreoperation.utils import json_response
from estoreoperation.app.admin import ApplicationAdmin
from estoreoperation.admin.cateapps.models import Application, get_category, \
        query_categories, cateapp_factory

logger = logging.getLogger('estoreoperation')


class CategoryAppAdmin(ApplicationAdmin):
    list_editable = ('rate', 'order', 'clicks_count', 'downloads_count', 'reviews_count', 'published')
    list_display =  ('order', 'id', 't_id', 't_paytype', 'name', 'current_version_name', 'versions_count', 't_chargemode', 'price', 'clicks_count', 'downloads_count', 'reviews_count', 'source_name', 'rate', 'reviewed_desc_preview_status', 'published', 'has_icon', 'sync_status')
    list_display_links = ('name',)
    ordering = ('-order',)
    list_filter = ('sub_category', 'sync_status', 'price', 'reviewed_desc_preview_status', 'published', 't_paytype')
    search_fields = ['id', 't_id', 'name', 'package_name']

    def insert(self, obj):
        return """<a href="/admin/utilities/searchapp/" inserted_order="%(order)s" id="insert_%(id)s" onclick="return showRelatedObjectLookupPopup(this);">
                    <strong>%(insert)s</strong>
                </a>""" % {"order": obj.order, "id": obj.id, "insert": _("insert").encode("utf-8")}
    insert.allow_tags = True
    insert.short_description = _("insert")

    def render_change_form(self, request, context, *args, **kwargs):
        # context['adminform'].form.fields['category'].queryset = Category.objects.filter(name__exact=self.cate_name)
        context['adminform'].form.fields['category'].initial = self.category
        context['adminform'].form.fields['sub_category'].queryset = \
                Category.objects.filter(parent_category__isnull=False).filter(parent_category__id=self.category.id)
        return super(CategoryAppAdmin, self).render_change_form(request, context, *args, **kwargs)

    def queryset(self, request):
        return super(CategoryAppAdmin, self).queryset(request).filter(category__id=self.category.id)

    def has_add_permission(self, request):
        return False

    def has_sync_to_permission(self, request, obj=None):
        return True

    @json_response
    def insert_app_view(self, request):
        try:
            app_id = int(request.REQUEST.get('id'))
            order = int(request.POST.get('order'))
            inserted_app = Application.objects.get(pk__exact=app_id)
            # change the app category
            if inserted_app.category.name != self.category.name:
                inserted_app.category = self.category
                inserted_app.sub_category = None
            # adjust order
            Application.objects.filter(order__gte=order).update(order=F('order') + 1)
            inserted_app.order = order
            inserted_app.sync_status = 0
            inserted_app.save()
            return 'success'
        except Exception, e:
            logger.exception('Insert app failed, error: %s' % e)
        return 'failed'

    def get_urls(self):
        urlpatterns = super(CategoryAppAdmin, self).get_urls()
        from django.conf.urls.defaults import url
        urlpatterns += (
                url(r'^insert$', self.insert_app_view, name='insert_app'),
            )
        return urlpatterns

    @property
    def category(self):
        return get_category(self.cate_name)

    class Media:
        js = ("cateapps/js/cateapps.js",)


def cateappadmin_factory(class_s, category_name, model=CategoryAppAdmin):

    class_attrs = {
        'cate_name': category_name,
        '__module__': __name__,
    }
    class_name = '%s%s' % (model.__name__, class_s)
    return forms.MediaDefiningClass(class_name, (model,), class_attrs)


categories = query_categories()
for cate in categories:
    custom_site.register(cateapp_factory(cate.id, cate.name), cateappadmin_factory(cate.id, cate.name))
