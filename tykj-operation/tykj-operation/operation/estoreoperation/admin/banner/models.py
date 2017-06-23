from django.utils.translation import ugettext as _
from django.db.models.base import ModelBase

from estorecore.admin.management import create_permission
from estorecore.models.constants import BANNER_IMAGE_AREAS, RECOMMEND_TYPES
from estorecore.models.app import CustomManager
from estoreoperation.utils import string_with_title
from estoreoperation.app.models import CategoryFoucsImage
from estoreoperation.admin.cateapps.models import get_category


def banner_factory(area, cate_name=None, recommend_type=None, model=CategoryFoucsImage):

    def _get_meta(area, cate_name=None, recommend_type=None):
        banner_verbose_name = '%s - %s' % (BANNER_IMAGE_AREAS.get_label(area) + '', \
                cate_name if area == BANNER_IMAGE_AREAS.TOP else RECOMMEND_TYPES.get_label(recommend_type))
        class Meta:
            proxy = True
            app_label = string_with_title("banner", _("Banner Recommend"))
            verbose_name = banner_verbose_name
            verbose_name_plural = banner_verbose_name
        return Meta

    manager_cond = {'area__exact': area}
    class_name = '%s%s' % (model.__name__, BANNER_IMAGE_AREAS.get_key(area))
    if area == BANNER_IMAGE_AREAS.TOP:
        cate_id = get_category(cate_name, only_id=True)
        manager_cond.update({'category__id': cate_id})
        class_name += str(cate_id)
    else:
        manager_cond.update({'recommend_type__exact': recommend_type})
        class_name += RECOMMEND_TYPES.get_key(recommend_type)

    class_attrs = {
        'Meta': _get_meta(area, cate_name, recommend_type),
        '__module__': __name__,
        'objects': CustomManager(manager_cond)
    }
    model_class = ModelBase(class_name, (model,), class_attrs)
    create_permission(model_class)
    return model_class
