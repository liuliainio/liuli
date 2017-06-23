CREATE DATABASE IF NOT EXISTS market
  DEFAULT CHARACTER SET utf8
  DEFAULT COLLATE utf8_general_ci;
  
 
USE market;

CREATE TABLE IF NOT EXISTS apk_map (
  id int(11) NOT NULL auto_increment,
  server_ip varchar(32) NOT NULL,
  file_path varchar(255) NOT NULL,
  download_link varchar(255) NOT NULL,
  source varchar(32) NOT NULL,
  PRIMARY KEY (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

ALTER TABLE apk_map ADD UNIQUE link_index(download_link);