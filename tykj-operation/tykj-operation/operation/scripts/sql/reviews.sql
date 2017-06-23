CREATE TABLE IF NOT EXISTS `appreview`( 
 comment_id INT(11) NOT NULL AUTO_INCREMENT,
 app_id INT(11) NOT NULL,
 grade DECIMAL(25,5) NOT NULL,
 add_date DATETIME NULL,
 is_show INT(11) DEFAULT NULL,
 user_id INT(11) NOT NULL,
 agree_user_count INT(11) DEFAULT NULL,
 reject_user_count INT(11) DEFAULT NULL,
 ip VARCHAR(255) DEFAULT NULL,
 content VARCHAR(255) NOT NULL,
 source VARCHAR(255) DEFAULT NULL, 
 PRIMARY KEY (`comment_id`)
)

%s/\(\d\+-\d\+\)\(-\)\(\d\+\)/\3\2\1/
%s/dd-mm-yyyy hh24:mi:ss/%Y-%m-%d %H:%m:%s/
%s/to_date/date_format
%s/t_appcomment/appreview/
