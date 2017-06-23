estore database:
	create database estore CHARACTER SET UTF8;
	CREATE USER 'estore_admin'@'localhost' IDENTIFIED BY '123456';
	grant all on estore.* to 'estore_admin'@'localhost' identified by '123456';

	cd /var/app/enabled/service/estoreservice
	python manage.py syncdb
