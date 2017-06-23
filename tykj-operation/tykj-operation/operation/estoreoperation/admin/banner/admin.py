#! -*- coding:utf-8 -*-
import logging
from django import forms
from estorecore.admin.sites import custom_site
from estoreoperation.app.admin import CategoryFoucsImageAdmin
from estoreoperation.admin.banner.models import BANNER_IMAGE_AREAS, RECOMMEND_TYPES, banner_factory
from estoreoperation.admin.cateapps.models import get_category, query_categories

logger = logging.getLogger('estoreoperation')


class TopAreaBannerAdmin(CategoryFoucsImageAdmin):

    def queryset(self, request):
        return super(CategoryFoucsImageAdmin, self).queryset(request).filter(area__exact=self.area)\
                .filter(category__id=self.category.id)

    def has_sync_to_permission(self, request, obj=None):
        return True

    @property
    def category(self):
        return get_category(self.cate_name)

    def save_model(self, request, obj, form, change):
        obj.area = self.area
        obj.category = self.category
        obj.recommend_type = None
        super(CategoryFoucsImageAdmin, self).save_model(request, obj, form, change)


class RecommendAreaBannerAdmin(CategoryFoucsImageAdmin):

    def set_group(self):
        get_custom_group = lambda: self.recommend_type == RECOMMEND_TYPES.MATCHEST
        self.custom_group = get_custom_group()

    def queryset(self, request):
        default_queryset = super(CategoryFoucsImageAdmin, self).queryset(request).filter(area__exact=self.area)\
                .filter(recommend_type=self.recommend_type)
        self.set_group()
        return self.post_queryset(request, default_queryset)


    def has_sync_to_permission(self, request, obj=None):
        return True

    def save_model(self, request, obj, form, change):
        obj.area = self.area
        obj.category = None
        obj.recommend_type = self.recommend_type
        self.set_group()
        super(CategoryFoucsImageAdmin, self).save_model(request, obj, form, change)


def banneradmin_factory(area, cate_name=None, recommend_type=None, model=TopAreaBannerAdmin):

    class_attrs = {
        'area': area,
        'cate_name': cate_name,
        'recommend_type': recommend_type,
        '__module__': __name__,
    }
    class_name = '%s%s' % (model.__name__, get_category(cate_name, only_id=True) \
            if area == BANNER_IMAGE_AREAS.TOP else recommend_type)
    return forms.MediaDefiningClass(class_name, (model,), class_attrs)


categories = query_categories()
for area in BANNER_IMAGE_AREAS.to_dict().keys():
    if area == BANNER_IMAGE_AREAS.TOP:
        for cate in categories:
            custom_site.register(banner_factory(area, cate_name=cate.name), \
                    banneradmin_factory(area, cate_name=cate.name))
    else:
        for recommend_type in RECOMMEND_TYPES.to_dict().keys():
            custom_site.register(banner_factory(area, recommend_type=recommend_type), \
                    banneradmin_factory(area, recommend_type=recommend_type, model=RecommendAreaBannerAdmin))
