# coding=utf-8

import sys
reload(sys)
sys.setdefaultencoding( "utf-8" )

import urllib2
sendcodemsg = u"【天翼空间】登陆短信验证码:%s"

# 0成功，1是发送验证码失败，2是超过发送次数，3其它
import random
def genaral_code(phone=''):
    # mysql jilu
    # phone code time use_status
    import string
    CODE_LEN = 6
    code = ''.join([random.choice(string.digits) for ch in range(CODE_LEN)])
    return code


def send_telecode(strtele , strcode):
    url = "http://www.wp114.cn/sms.aspx?action=send&userid=217&account=tykj&password=tykj123&mobile=" + \
                strtele + "&content=" + sendcodemsg % strcode
    try:
        req = urllib2.Request(url)
        print 'req',req
        res_data = urllib2.urlopen(req)
        print res_data
        res = res_data.read()
        print res
        if str(res).find("<returnstatus>Faild</returnstatus>") > -1:
            return 1
    except Exception, e:
        print e
        return 1
    else:
        return 0

send_telecode('18380488050', u'屌丝你好')




