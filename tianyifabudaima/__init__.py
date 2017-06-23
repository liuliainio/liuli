# -*- coding: utf-8 -*-
import os
from math import ceil
import Image, ImageDraw, ImageFont, random, StringIO
from django.http import HttpResponse

import MySQLdb
from django.conf import settings
from estoreoperation.admin.usermanagement.models import User
from estoreoperation.userphone.models import UserPhones


ty_db = settings.DATABASES['default']
ty_db = MySQLdb.connect(ty_db['HOST'], ty_db['USER'], ty_db['PASSWORD'], ty_db['NAME'], charset = 'utf8')
ty_cursor = ty_db.cursor()
ty_cursor.execute('SET foreign_key_checks = 0')

current_path = os.path.normpath(os.path.dirname(__file__))


class Code(object):

    def __init__(self,request):
        """
        初始化,设置各种属性
        """
        self.django_request = request
        self.session_key = 'django-verify-code'

    def get_code(self):
        pass

    def check(self, code):
        """
        检查用户输入的验证码是否正确
        """
        username = ''
        if self.django_request.method == 'POST':
            if 'code' in self.django_request.POST.keys():
                code = self.django_request.POST['code']
                print code
            if 'username' in self.django_request.POST.keys():
                username = self.django_request.POST['username']
            user_id = User.objects.get(username=username).pk
            up = UserPhones.objects.filter(user=user_id)

            for pe in up:
                phone = str(pe.phone)
                if phone:
                    from views import search_code
                    scd = search_code(phone=phone,code=code)
                    if scd:
                        print scd
                        sql_update = """UPDATE codephone SET use_status=1 where code ='%s' and phone='%s' """%(code, phone)
                        ty_cursor.execute(sql_update)
                        ty_db.commit()
                        ty_db.close()

                        return True
                    # _code = self.django_request.session.get(self.session_key) or ''
                    # print _code
                    # if not _code:
                    #     return False
                    return False

if __name__ == '__main__':
    import mock
    request = mock.Mock()
    c = Code(request)
