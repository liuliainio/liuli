--DROP DATABASE IF EXISTS market;
CREATE DATABASE market
  DEFAULT CHARACTER SET utf8
  DEFAULT COLLATE utf8_general_ci;

USE market;

CREATE TABLE IF NOT EXISTS app (
  id int(11) NOT NULL auto_increment,
  name varchar(128) NOT NULL,
  icon_link TEXT,
  icon_path TEXT,
  source varchar(64) NOT NULL,
  source_link varchar(255) NOT NULL,
  rating varchar(16),
  version varchar(32),
  developer varchar(64),
  sdk_support varchar(128),
  category varchar(64),
  screen_support varchar(256),
  apk_size varchar(32),
  language varchar(64),
  publish_date int(11),
  downloads varchar(64),
  description TEXT,
  images TEXT,
  images_path TEXT,
  qr_link TEXT,
  download_link TEXT,
  last_crawl int(11) NOT NULL,
  tag TEXT,
  PRIMARY KEY (id),
  UNIQUE KEY link_index (source_link),
  KEY idx_dl (download_link)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;


CREATE TABLE IF NOT EXISTS apt (
  id int(11) NOT NULL auto_increment,
  name varchar(128) NOT NULL,
  icon_link TEXT,
  icon_path TEXT,
  source varchar(64) NOT NULL,
  source_link varchar(255) NOT NULL,
  rating varchar(16),
  version varchar(32),
  developer varchar(64),
  sdk_support varchar(128),
  category varchar(64),
  screen_support varchar(256),
  apk_size varchar(32),
  language varchar(64),
  publish_date int(11),
  downloads varchar(64),
  description TEXT,
  images TEXT,
  images_path TEXT,
  qr_link TEXT,
  download_link TEXT,
  last_crawl int(11) NOT NULL,
  tag TEXT,
  PRIMARY KEY (id),
  UNIQUE KEY link_index (source_link),
  KEY idx_dl (download_link)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

ALTER TABLE apt ADD UNIQUE link_index(source_link);


CREATE TABLE IF NOT EXISTS new_link (
  id char(32),
  source varchar(64) NOT NULL,
  link varchar(256) NOT NULL,
  last_crawl int(11) NOT NULL,
  priority float(11) NOT NULL,
  pages int(11) NOT NULL DEFAULT 0,
  PRIMARY KEY (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

ALTER TABLE new_link ADD INDEX index1(source, last_crawl, priority);
ALTER TABLE new_link ADD INDEX index2(link);

CREATE TABLE IF NOT EXISTS update_link (
  id char(32),
  source varchar(64) NOT NULL,
  link varchar(256) NOT NULL,
  last_crawl int(11) NOT NULL,
  priority float(11) NOT NULL,
  pages int(11) NOT NULL DEFAULT 0,
  PRIMARY KEY (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

ALTER TABLE update_link ADD INDEX index1(source, last_crawl, priority);
ALTER TABLE update_link ADD INDEX index2(link);

CREATE TABLE IF NOT EXISTS sph_counter
(
    counter_id int(11) NOT NULL,
    max_doc_id int(11) NOT NULL,
    PRIMARY KEY (counter_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE IF NOT EXISTS link_monitor (
  id int(11) NOT NULL auto_increment,
  source varchar(64) NOT NULL,
  category varchar(64) NOT NULL,
  link varchar(255) NOT NULL,
  description TEXT,
  create_time int(11) NOT NULL,
  PRIMARY KEY (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

ALTER TABLE link_monitor ADD INDEX index1(source, category, create_time);



CREATE TABLE IF NOT EXISTS youtube (
  id int(11) NOT NULL auto_increment,
  name varchar(128) NOT NULL,
  source varchar(64) NOT NULL,
  source_link varchar(255) NOT NULL,
  likes int(11),
  dislikes int(11),
  duration varchar(32),
  view_count int(11),
  author varchar(64),
  category varchar(64),
  publish_date int(11),
  comments int(11),
  description TEXT,
  last_crawl int(11) NOT NULL,
  PRIMARY KEY (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

ALTER TABLE youtube ADD UNIQUE link_index(source_link);

CREATE TABLE IF NOT EXISTS bestbuy (
  id int(11) NOT NULL auto_increment,
  name varchar(255) NOT NULL,
  image_link TEXT,
  source varchar(64) NOT NULL,
  source_link varchar(255) NOT NULL,
  customerReviewAverage varchar(16),
  customerReviewCount int(11),
  sku varchar(32) NOT NULL,
  productId varchar(32) NOT NULL,
  quantityLimit int(11),
  salePrice float(11),
  itemUpdateDate int(11),
  manufacturer varchar(64),
  itemCondition varchar(16),
  onSale varchar(16),
  PRIMARY KEY (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
ALTER TABLE bestbuy ADD UNIQUE link_index(source_link);

CREATE TABLE IF NOT EXISTS walmart (
  id int(11) NOT NULL auto_increment,
  name varchar(255) NOT NULL,
  image_link TEXT,
  source varchar(64) NOT NULL,
  source_link varchar(255) NOT NULL,
  salePrice float(11),
  updated int(11),
  PRIMARY KEY (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
ALTER TABLE walmart ADD UNIQUE link_index(source_link);


CREATE TABLE IF NOT EXISTS apple (
  id int(11) NOT NULL auto_increment,
  name varchar(128) NOT NULL,
  icon_link TEXT,
  icon_path TEXT,
  source varchar(64) NOT NULL,
  source_link varchar(255) NOT NULL,
  rating varchar(16),
  current_rating varchar(16),
  rating_num int(11),
  current_rating_num int(11),
  version varchar(32),
  developer varchar(64),
  sdk_support varchar(256),
  category varchar(64),
  screen_support varchar(256),
  apk_size varchar(32),
  language TEXT,
  publish_date int(11),
  downloads int(11),
  description TEXT,
  images TEXT,
  images_path TEXT,
  qr_link TEXT,
  download_link TEXT,
  last_crawl int(11) NOT NULL,
  association varchar(32) NOT NULL,
  PRIMARY KEY (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

ALTER TABLE apple ADD UNIQUE link_index(source_link);


CREATE TABLE IF NOT EXISTS tripadvisor (
  id int(11) NOT NULL auto_increment,
  name varchar(128) NOT NULL,
  source varchar(64) NOT NULL,
  source_link varchar(255) NOT NULL,
  rating varchar(64),
  category varchar(64),
  reviews int(11),
  price varchar(32),
  city varchar(128) NOT NULL,
  address varchar(512),
  phone varchar(32),
  hotel_class varchar(32),
  rank_of_city varchar(64),
  owner_website varchar(128),
  longitude_latitude varchar(64),
  last_crawl int(11) NOT NULL,
  PRIMARY KEY (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

ALTER TABLE tripadvisor ADD UNIQUE link_index(source_link);

-------------------------------------sync update to console-------------------
ALTER TABLE `market`.`final_app` 
    ADD COLUMN `status` INT NULL DEFAULT 0  AFTER `avail_download_links` , 
    ADD COLUMN `updated_at` DATETIME NULL DEFAULT NULL  AFTER `status` , 
    ADD COLUMN `error` VARCHAR(1024) NULL DEFAULT NULL  AFTER `updated_at` ;
ALTER TABLE `market`.`final_app` 
    ADD INDEX `idx_u_s` (`updated_at` ASC, `status` ASC) ;

CREATE  TABLE `market`.`config` (
  `id` INT NOT NULL AUTO_INCREMENT ,
  `key` VARCHAR(100) NOT NULL ,
  `value` VARCHAR(1024) NOT NULL ,
  `desc` VARCHAR(200) NULL ,
  `created_at` DATETIME NOT NULL ,
  `updated_at` DATETIME NOT NULL ,
  PRIMARY KEY (`id`) ,
  UNIQUE INDEX `key_UNIQUE` (`key` ASC) 
)ENGINE=InnoDB DEFAULT CHARSET=utf8;

ALTER TABLE `market`.`final_app` ADD COLUMN `labels` VARCHAR(100) NULL  AFTER `error` ;
ALTER TABLE `market`.`unique_apk` ADD UNIQUE INDEX `idx_u_s` (`source_link` ASC) ;
ALTER TABLE `market`.`app` ADD COLUMN `labels` VARCHAR(100) NULL  AFTER `update_note` ;

CREATE  TABLE `market`.`url_hash` (
  `id` INT NOT NULL AUTO_INCREMENT ,
  `url` VARCHAR(250) NOT NULL ,
  `error_times` SMALLINT NOT NULL DEFAULT 0 ,
  `last_download_time` INT NOT NULL DEFAULT -1 ,
  `hash` VARCHAR(100) NULL ,
  `updated_at` DATETIME NOT NULL ,
  PRIMARY KEY (`id`) ,
  UNIQUE INDEX `url_UNIQUE` (`url` ASC) ,
  INDEX `hash_idx` (`hash` ASC) );

CREATE TABLE `apk_links` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `link` varchar(250) NOT NULL,
  `updated_at` datetime NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `link_UNIQUE` (`link`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;



