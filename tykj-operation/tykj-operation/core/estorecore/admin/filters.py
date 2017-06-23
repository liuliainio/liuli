from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.utils.encoding import smart_unicode
from django.contrib.admin.filterspecs import FilterSpec, RelatedFilterSpec

from estorecore.models.app import Category


class SubCategoryFilterSpec(RelatedFilterSpec):

    def choices(self, cl):
        yield {'selected': self.lookup_val is None
                           and not self.lookup_val_isnull,
               'query_string': cl.get_query_string({}, [self.lookup_kwarg, self.lookup_kwarg_isnull]),
               'display': _('All')}
        # get sub categories with parent category name
        cate_name = getattr(cl.model_admin, 'cate_name', None)
        if cate_name:
            categories = Category.objects.filter(parent_category__isnull=False).filter(parent_category__name__exact=cate_name)
        else:
            categories = Category.objects.filter(parent_category__isnull=False).filter(level__exact=2)
        for cate in categories:
            yield {'selected': self.lookup_val == smart_unicode(cate.pk),
                   'query_string': cl.get_query_string({self.lookup_kwarg: cate.pk}, [self.lookup_kwarg_isnull]),
                   'display': cate.name}

FilterSpec.filter_specs.insert(0, (lambda f: getattr(f, 'sub_category_filter', False), SubCategoryFilterSpec))


class DecimalFieldFilterSpec(FilterSpec):
    def __init__(self, f, request, params, model, model_admin, field_path=None):
        super(DecimalFieldFilterSpec, self).__init__(f, request, params, model, model_admin, field_path=field_path)

        self.field_generic = '%s__' % self.field_path
        self.filter_params = dict([(k, v) for k, v in params.items()
                                 if k.startswith(self.field_generic)])

        self.links = (
            (_('All'), {}),
            (_('Equal to zero'), {'%s__exact' % self.field_path: '0'}),
            (_('Greater than zero'), {'%s__gt' % self.field_path: '0'}),
        )

    def title(self):
        return self.field.verbose_name

    def choices(self, cl):
        for title, param_dict in self.links:
            yield {'selected': self.filter_params == param_dict,
                   'query_string': cl.get_query_string(param_dict, [self.field_generic]),
                   'display': title}

FilterSpec.filter_specs.insert(0, (lambda f: isinstance(f, models.DecimalField), DecimalFieldFilterSpec))


class ActionFlagFilterSpec(FilterSpec):
    def __init__(self, f, request, params, model, model_admin, field_path=None):
        super(ActionFlagFilterSpec, self).__init__(f, request, params, model, model_admin, field_path=field_path)

        self.field_generic = '%s__' % self.field_path
        self.filter_params = dict([(k, v) for k, v in params.items()
                                 if k.startswith(self.field_generic)])

        self.links = (
            (_('All'), {}),
            (_('addition action'), {'%s__exact' % self.field_path: '1'}),
            (_('change action'), {'%s__exact' % self.field_path: '2'}),
            (_('deletion action'), {'%s__gt' % self.field_path: '3'}),
        )

    def title(self):
        return self.field.verbose_name

    def choices(self, cl):
        for title, param_dict in self.links:
            yield {'selected': self.filter_params == param_dict,
                   'query_string': cl.get_query_string(param_dict, [self.field_generic]),
                   'display': title}

FilterSpec.filter_specs.insert(0, (lambda f: getattr(f, 'name', False) == 'action_flag', ActionFlagFilterSpec))
