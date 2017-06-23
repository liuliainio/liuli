#coding:utf8
from django.contrib.auth.models import User
from userphone.models import UserPhones
from views import search_code

__author__ = 'root'


import MySQLdb
from django.conf import settings
ty_db = settings.DATABASES['default']
ty_db = MySQLdb.connect(ty_db['HOST'], ty_db['USER'], ty_db['PASSWORD'], ty_db['NAME'], charset = 'utf8')
ty_cursor = ty_db.cursor()
ty_cursor.execute('SET foreign_key_checks = 0')

class Codes(object):
    def __init__(self,request):
        self.django_request = request
        self.session_key = 'django-verify-code'


    def get_code(self):
        pass

    def check_code(self,code):
        username = ''
        code = 0
        if request.method == 'POST':
            if 'code' in request.POST.keys():
                code = request.POST['code']
                print code
            if 'username' in request.POST.keys():
                username = request.POST['username']
            user_id = User.objects.get(username=username).pk
            up = UserPhones.objects.filter(user=user_id)

            for pe in up:
                phone = str(pe.phone)
                if phone:
                    scd = search_code(phone=phone,code=code)
                    if scd:
                        sql_update = """UPDATE codephone SET use_status=1 where code ='%s' and phone='%s' """%(code, phone)
                        ty_cursor.execute(sql_update)
                        ty_db.commit()
                        ty_db.close()
                        ajax_status = 200
                        ajax_msg  = 'sucess'
                    else:
                        ajax_status = 400
                        ajax_msg  = 'failed'
                        # messages.error(request,'请重新输入正确的验证码')
                    msg = {'status': ajax_status, 'message': ajax_msg}
                    return msg





if __name__ == '__main__':
    import mock
    request = mock.Mock()
    c = Codes(request)
