CREATE TABLE entry (
  download_link varchar(255) NOT NULL,
  source_link varchar(255) NOT NULL,
  source varchar(32) NOT NULL,
  file_name varchar(256) DEFAULT NULL,
  vol_id varchar(32) NOT NULL,
  tag int(11) DEFAULT NULL,
  PRIMARY KEY (download_link)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE IF NOT EXISTS vol (
  id varchar(32) NOT NULL,
  total_kbytes int(16) NOT NULL,
  used_kbytes int(16) NOT NULL,
  PRIMARY KEY(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE unique_apk (
  id int(11) NOT NULL auto_increment,
  package_name varchar(255) NOT NULL,
  version_code int(32) NOT NULL,
  download_link varchar(255) NOT NULL,
  source_link varchar(255) NOT NULL,
  source varchar(32) NOT NULL,
  vol_id varchar(32) NOT NULL,
  sig varchar(64) DEFAULT NULL,
  tag int(11) DEFAULT NULL,
  tag2 int(2) DEFAULT NULL,
  is_refresh int(11) DEFAULT NULL,
  img_status int(11) DEFAULT NULL,
  watermark_status int(11) DEFAULT NULL,
  version varchar(64) DEFAULT NULL,
  apk_size varchar(32) DEFAULT NULL,
  file_type varchar(32) DEFAULT NULL,
  min_sdk_version int(32) DEFAULT NULL,
  screen_support varchar(32) DEFAULT NULL,
  is_break int(32) DEFAULT NULL,
  platform int(11) DEFAULT NULL,
  PRIMARY KEY (id),
  UNIQUE KEY index_package_vsersion (package_name,version_code)
  UNIQUE KEY index_p_v_f_s (package_name,version_code,file_type,is_break)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;


CREATE TABLE IF NOT EXISTS duplicate_apk (
  id int(11) NOT NULL auto_increment,
  package_name varchar(255) NOT NULL,
  version_code int(32) NOT NULL,
  download_link varchar(255) NOT NULL,
  source_link varchar(255) NOT NULL,
  source varchar(32) NOT NULL,
  vol_id varchar(32) NOT NULL,
  tag int(11),
  PRIMARY KEY (id),
  UNIQUE KEY index_download_link(download_link)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;


CREATE TABLE final_app (
  id int(11) NOT NULL AUTO_INCREMENT,
  name varchar(128) NOT NULL,
  icon_link text,
  icon_path text,
  source varchar(64) NOT NULL,
  source_link varchar(255) DEFAULT NULL,
  rating varchar(16) DEFAULT NULL,
  version varchar(255) DEFAULT NULL,
  developer varchar(64) DEFAULT NULL,
  sdk_support varchar(128) DEFAULT NULL,
  category varchar(64) DEFAULT NULL,
  screen_support varchar(256) DEFAULT NULL,
  apk_size varchar(32) DEFAULT NULL,
  language varchar(64) DEFAULT NULL,
  publish_date int(11) DEFAULT NULL,
  downloads varchar(64) DEFAULT NULL,
  description text,
  images text,
  images_path text,
  qr_link text,
  download_link text,
  last_crawl int(11) NOT NULL,
  tag text,
  security_status varchar(32) DEFAULT NULL,
  package_name varchar(255) DEFAULT NULL,
  version_code bigint(20) DEFAULT NULL,
  file_path varchar(255) DEFAULT NULL,
  vol_id int(11) DEFAULT NULL,
  sig varchar(64) DEFAULT NULL,
  is_refresh int(11) DEFAULT NULL,
  price float DEFAULT '0',
  file_type varchar(32) DEFAULT NULL,
  min_sdk_version int(32) DEFAULT NULL,
  is_break int(32) DEFAULT NULL,
  platform int(11) DEFAULT NULL,
  PRIMARY KEY (id),
  UNIQUE KEY index1 (package_name,version_code),
  UNIQUE KEY source_link (source_link),
  UNIQUE KEY index_p_v_f_s (package_name,version_code,file_type,is_break),
  KEY idx_pv (package_name,version_code)
) ENGINE=InnoDB DEFAULT CHARSET=utf8

CREATE TABLE apple_account (
  id int(11) NOT NULL AUTO_INCREMENT,
  username varchar(255) NOT NULL,
  password varchar(255) NOT NULL,
  status int(11),
  app_num int(11) NOT NULL,
  PRIMARY KEY (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8

CREATE TABLE itunes_game_cate (
  app_id varchar(255) NOT NULL,
  app_name varchar(255) NOT NULL,
  cate_id varchar(255) NOT NULL,
  cate_name varchar(255) NOT NULL,
  PRIMARY KEY (app_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8
