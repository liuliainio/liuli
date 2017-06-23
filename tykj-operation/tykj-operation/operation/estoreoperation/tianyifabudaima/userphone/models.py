#coding:utf8
from django.db import models
from django.utils.translation import ugettext_lazy as _
from estoreoperation.admin.usermanagement.models import User


__author__ = 'root'


class UserPhones(models.Model):
    phone = models.BigIntegerField(verbose_name=_('phone'))
    user = models.OneToOneField(User,related_name='user_phone',verbose_name=_('user'))
    # def __unicode__(self):
    #     return self.phone


    class Meta:
        app_label = 'userphone'
        db_table ='userphone'
        verbose_name = _('User Profile')
        verbose_name_plural = _('User Profiles')