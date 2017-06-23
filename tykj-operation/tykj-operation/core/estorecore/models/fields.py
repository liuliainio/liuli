from django import forms
from django.db import models
from estorecore.models.widgets import BtnUrlWidget


class BtnURLField(models.URLField):

    def formfield(self, **kwargs):
        # As with CharField, this will cause URL validation to be performed twice
        defaults = {
            'form_class': forms.URLField,
            'widget': BtnUrlWidget,
        }
        kwargs.update(defaults)
        return super(BtnURLField, self).formfield(**kwargs)
