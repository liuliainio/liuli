from django.utils.translation import ugettext as _
from django.db.models.base import ModelBase

from estorecore.admin.management import create_permission
from estorecore.models.constants import REVIEW_STATUS
from estorecore.models.app import CustomManager
from estoreoperation.utils import string_with_title
from estoreoperation.app.models import Application, Category

CATEGORIES = {}


def get_category(cate_name, only_id=False):
    if cate_name not in CATEGORIES:
        try:
            category = Category.objects.get(name=cate_name, level=1)
            CATEGORIES[cate_name] = category
        except:
            pass
    cate = CATEGORIES.get(cate_name, None)
    return cate.id if cate and only_id else cate


def query_categories(only_id=False):
    categories = Category.objects.filter(parent_category__id=None)
    for cate in categories:
        CATEGORIES[cate.name] = cate
    return [c.id for c in categories] if only_id else categories


def cateapp_factory(class_s, category_name, model=Application):

    def _get_meta(category_name):
        class Meta:
            proxy = True
            app_label = string_with_title("cateapps", _("Category Apps"))
            verbose_name = category_name
            verbose_name_plural = category_name
        return Meta

    class_attrs = {
        'Meta': _get_meta(category_name),
        '__module__': __name__,
        'objects': CustomManager({'category__id': get_category(category_name, only_id=True), 'review_status__gte': REVIEW_STATUS.APPROVED})
    }
    class_name = '%s%s' % (model.__name__, class_s)
    model_class = ModelBase(class_name, (model,), class_attrs)
    create_permission(model_class)
    return model_class
