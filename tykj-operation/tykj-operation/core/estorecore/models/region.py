# -*- coding: utf-8 -*-
from django.db import models
from estorecore.models.constants import SYNC_STATUS

class PhoneRegion(models.Model):
    city = models.CharField(max_length=100)
    city_pinyin = models.CharField(max_length=100)
    province = models.CharField(max_length=100)
    province_pinyin = models.CharField(max_length=100)
    phone = models.IntegerField()
    sync_status = models.IntegerField(default=0, choices=SYNC_STATUS.to_choices())
    published = models.BooleanField(default=False)

    def __unicode__(self):
        return self.city

    class Meta:
        app_label = 'region'
        verbose_name = 'Phone Region'
        verbose_name_plural = 'Phone Region'
