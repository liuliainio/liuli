

Setup Scripts:


1.  sudo apt-get install mysql-server
2.  mysql -uroot -pyourpassword
    mysql> create database estore character set utf8;
    mysql> grant all on  estore.* to 'estore_admin'@'localhost' identified by '123456';
    NOTICE:
          * ensure the database name admin user/password match configuration in estoreoperation.cfg
3.  cd estoreoperation
    python manage.py syncdb  --pythonpath=../../core/
4.  python manage.py runserver {ip}:{port} --pythonpath=../../core/


TIPS:
  * delete all tables:
    mysql -u{user} -p{password} estore -e "show tables;" | cut -d: -f 1 | xargs -i mysql -u{user} -p{password} estore -e "drop table {}"
  * delete deleted file from git
    git status | grep deleted | cut -d: -f 2 | xargs git rm
