# coding=utf-8
import os
import ftplib
import time
import smtplib
import simplejson


class MySQLdbWrapper:

    conn = None

    def connect(self):
        self.conn = MySQLdb.connect('192.168.130.77', 'dev_market', 'market_dev_pwd', 'market')
        self.conn.set_character_set('utf8')

    def cursor(self):
        try:
            if not self.conn:
                self.connect()
            return self.conn.cursor()
        except MySQLdb.OperationalError:
            self.connect()
            return self.conn.cursor()

_db = MySQLdbWrapper()

api_host = '42.121.118.131:8080'
ftp_host = '42.121.118.131'
ftp_username = 'administrator'
ftp_password = '7cb1ea54'


def check_status():
    i = 0
    while True:
        num = get_num()
        print time.time(), i, num

        if not num:
            i += 1
        else:
            i = 0
        if i > 10:
            message = """From: itunes status
To: To Person <qpwang@bainainfo.com>
MIME-Version: 1.0
Content-type: text/html
Subject: ***itunes monitor report***

<b>itunes download failed!</b>"""
            send_mail(message)
        queue_num = get_queue_num()
        if queue_num < 3:
            upload_conf()
            status = refresh_conf()
            if status in [0, -3, -4]:
                print "upload conf status:%d" % status
            else:
                print "upload conf error!"
        time.sleep(300)


def get_queue_num():
    conn = httplib.HTTPConnection(api_host)
    conn.request("GET", "/service/1/getqueuestatus")
    response = conn.getresponse()
    result = response.read()
    result = simplejson.loads(result)
    queue_num = result['data']['queue_num']
    free_disk = result['data']['free_disk']
    if free_disk > 5 * 1024 * 1024 * 1024:
        return queue_num
    else:
        print "not free disk!!!"
        return 10


def refresh_conf():
    conn = httplib.HTTPConnection(api_host)
    conn.request("GET", "/service/1/getconf")
    response = conn.getresponse()
    result = response.read()
    print result
    result = simplejson.loads(result)
    return result['data']['result']


def upload_conf():
    file_path = 'itunes_apps.plist'
    download_list = get_download_list()
    get_conf_plist(download_list, file_path)
    sftp = ftplib.FTP(ftp_host, ftp_username, ftp_password)
    fp = open(file_path, 'rb')
    sftp.storbinary('STOR %s' % file_path, fp)
    fp.close()
    sftp.quit()


def get_conf_plist(download_list, file_path):
    biplist.writePlist(download_list, file_path, False)


def get_download_list():
    ipas = get_ipas()
    apple_id_dic = {}
    apps_dic = {}
    download_list = []
    for ipa in ipas:
        apple_id_dic[ipa[0]] = 0
        if ipa[0] in apps_dic:
            apps_dic[ipa[0]].append(ipa[1])
        else:
            apps_dic[ipa[0]] = [ipa[1]]
    apple_id_dic = get_account_info(apple_id_dic.keys())
    for key in apps_dic.keys():
        app = {'AppleId': key,
               'Password': apple_id_dic[key],
               'DownloadList': apps_dic[key]}
        download_list.append(app)
    return download_list


def get_account_info(apple_id):
    try:
        apple_id_dic = {}
        cursor = _db.cursor()
        sql = "SELECT username,password from apple_account where username in ('%s')" % "','".join(apple_id)
        cursor.execute(sql)
        results = cursor.fetchall()
        for result in results:
            apple_id_dic[result[0]] = result[1]
        return apple_id_dic
    except MySQLdb.Error as e:
        print e


def get_ipas():
    try:
        cursor = _db.cursor()
        sql = "SELECT apple_id, download_link, id FROM app_itunes WHERE tag is null and price = 0 limit 100"
        cursor.execute(sql)
        results = cursor.fetchall()
        id_set = [str(tup[2]) for tup in results]
        if id_set:
            sql = "UPDATE app_itunes set tag = 2 where id in (%s)" % ",".join(id_set)
            cursor.execute(sql)
            _db.conn.commit()
        return results
    except MySQLdb.Error as e:
        print e
    finally:
        cursor.close()


def get_num():
    sftp = ftplib.FTP(ftp_host, ftp_username, ftp_password)
    sftp.cwd('itunes\Mobile Applications')
    download_list = sftp.nlst()
    return len(download_list)


def send_mail(message):
    fromaddr = 'app.search.crawler@gmail.com'
#    toaddrs = ['qpwang@bainainfo.com']
    toaddrs = ['qpwang@bainainfo.com', 'jhuang@bainainfo.com', 'hlli@bainainfo.com']
    # Credentials
    username = 'app.search.crawler'
    password = 'youpeng!'

    # The actual mail send
    server = smtplib.SMTP('smtp.gmail.com:587')
    server.starttls()
    server.login(username, password)
    server.sendmail(fromaddr, toaddrs, message.encode('utf8'))
    server.quit()

if __name__ == "__main__":
    check_status()
