


start:
	export PYTHONPATH=$$PYTHONPATH:../../core && export PYTHONPATH=$$PYTHONPATH:../../reporting && python manage.py runserver 0.0.0.0:8888


init: 
	mysql -uroot -p  -e "create database if not exists estore character set utf8; grant all on  estore.* to 'estore_admin'@'localhost' identified by '123456'";
	export PYTHONPATH=$$PYTHONPATH:../../core && export PYTHONPATH=$$PYTHONPATH:../../reporting && python manage.py syncdb
