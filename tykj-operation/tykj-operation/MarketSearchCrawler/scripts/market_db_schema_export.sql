-- MySQL dump 10.13  Distrib 5.1.61, for debian-linux-gnu (x86_64)
--
-- Host: 192.168.130.77    Database: market
-- ------------------------------------------------------
-- Server version	5.1.61-0ubuntu0.10.10.1-log

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `app`
--

DROP TABLE IF EXISTS `app`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `app` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(128) NOT NULL,
  `icon_link` text,
  `icon_path` text,
  `source` varchar(64) NOT NULL,
  `source_link` varchar(255) NOT NULL,
  `rating` varchar(16) DEFAULT NULL,
  `version` varchar(32) DEFAULT NULL,
  `developer` varchar(64) DEFAULT NULL,
  `sdk_support` varchar(128) DEFAULT NULL,
  `category` varchar(64) DEFAULT NULL,
  `screen_support` varchar(256) DEFAULT NULL,
  `apk_size` varchar(32) DEFAULT NULL,
  `language` varchar(64) DEFAULT NULL,
  `publish_date` int(11) DEFAULT NULL,
  `downloads` varchar(64) DEFAULT NULL,
  `description` text,
  `images` text,
  `images_path` text,
  `qr_link` text,
  `download_link` varchar(255) DEFAULT NULL,
  `last_crawl` int(11) NOT NULL,
  `tag` bigint(20) DEFAULT NULL,
  `update_note` text,
  PRIMARY KEY (`id`),
  UNIQUE KEY `link_index` (`source_link`),
  KEY `idx_dl` (`download_link`),
  KEY `idx_source` (`source`),
  KEY `app_tag` (`tag`),
  KEY `idx_last_crawl` (`last_crawl`)
) ENGINE=InnoDB AUTO_INCREMENT=8581067 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `app_comment`
--

DROP TABLE IF EXISTS `app_comment`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `app_comment` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `app_id` varchar(100) NOT NULL,
  `comment` varchar(500) DEFAULT NULL,
  `created_at` datetime NOT NULL,
  `username` varchar(45) NOT NULL,
  `rate` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `app_ios`
--

DROP TABLE IF EXISTS `app_ios`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `app_ios` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(128) NOT NULL,
  `icon_link` text,
  `icon_path` text,
  `source` varchar(64) NOT NULL,
  `source_link` varchar(255) NOT NULL,
  `rating` varchar(16) DEFAULT NULL,
  `version` varchar(32) DEFAULT NULL,
  `developer` varchar(64) DEFAULT NULL,
  `sdk_support` varchar(128) DEFAULT NULL,
  `category` varchar(64) DEFAULT NULL,
  `screen_support` varchar(256) DEFAULT NULL,
  `apk_size` varchar(32) DEFAULT NULL,
  `language` varchar(64) DEFAULT NULL,
  `publish_date` int(11) DEFAULT NULL,
  `downloads` varchar(64) DEFAULT NULL,
  `description` text,
  `images` text,
  `images_path` text,
  `qr_link` text,
  `download_link` text,
  `last_crawl` int(11) NOT NULL,
  `tag` text,
  PRIMARY KEY (`id`),
  UNIQUE KEY `link_index` (`source_link`)
) ENGINE=InnoDB AUTO_INCREMENT=443292 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `app_ios_2`
--

DROP TABLE IF EXISTS `app_ios_2`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `app_ios_2` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(128) NOT NULL,
  `icon_link` text,
  `icon_path` text,
  `source` varchar(64) NOT NULL,
  `source_link` varchar(255) NOT NULL,
  `rating` varchar(16) DEFAULT NULL,
  `version` varchar(32) DEFAULT NULL,
  `developer` varchar(64) DEFAULT NULL,
  `sdk_support` varchar(128) DEFAULT NULL,
  `category` varchar(64) DEFAULT NULL,
  `screen_support` varchar(256) DEFAULT NULL,
  `apk_size` varchar(32) DEFAULT NULL,
  `language` varchar(64) DEFAULT NULL,
  `publish_date` int(11) DEFAULT NULL,
  `downloads` varchar(64) DEFAULT NULL,
  `description` text,
  `images` text,
  `images_path` text,
  `qr_link` text,
  `download_link` text,
  `last_crawl` int(11) NOT NULL,
  `tag` text,
  PRIMARY KEY (`id`),
  UNIQUE KEY `link_index` (`source_link`)
) ENGINE=InnoDB AUTO_INCREMENT=152125 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `app_ipad`
--

DROP TABLE IF EXISTS `app_ipad`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `app_ipad` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(128) NOT NULL,
  `icon_link` text,
  `icon_path` text,
  `source` varchar(64) NOT NULL,
  `source_link` varchar(255) NOT NULL,
  `rating` varchar(16) DEFAULT NULL,
  `version` varchar(32) DEFAULT NULL,
  `developer` varchar(64) DEFAULT NULL,
  `sdk_support` varchar(128) DEFAULT NULL,
  `category` varchar(64) DEFAULT NULL,
  `screen_support` varchar(256) DEFAULT NULL,
  `apk_size` varchar(32) DEFAULT NULL,
  `language` varchar(64) DEFAULT NULL,
  `publish_date` int(11) DEFAULT NULL,
  `downloads` varchar(64) DEFAULT NULL,
  `description` text,
  `images` text,
  `images_path` text,
  `qr_link` text,
  `download_link` text,
  `last_crawl` int(11) NOT NULL,
  `tag` text,
  PRIMARY KEY (`id`),
  UNIQUE KEY `link_index` (`source_link`)
) ENGINE=InnoDB AUTO_INCREMENT=107646 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `app_iphone`
--

DROP TABLE IF EXISTS `app_iphone`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `app_iphone` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(128) NOT NULL,
  `icon_link` text,
  `icon_path` text,
  `source` varchar(64) NOT NULL,
  `source_link` varchar(255) NOT NULL,
  `rating` varchar(16) DEFAULT NULL,
  `version` varchar(32) DEFAULT NULL,
  `developer` varchar(64) DEFAULT NULL,
  `sdk_support` varchar(128) DEFAULT NULL,
  `category` varchar(64) DEFAULT NULL,
  `screen_support` varchar(256) DEFAULT NULL,
  `apk_size` varchar(32) DEFAULT NULL,
  `language` varchar(64) DEFAULT NULL,
  `publish_date` int(11) DEFAULT NULL,
  `downloads` varchar(64) DEFAULT NULL,
  `description` text,
  `images` text,
  `images_path` text,
  `qr_link` text,
  `download_link` text,
  `last_crawl` int(11) NOT NULL,
  `tag` text,
  PRIMARY KEY (`id`),
  UNIQUE KEY `link_index` (`source_link`)
) ENGINE=InnoDB AUTO_INCREMENT=143385 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `app_itunes`
--

DROP TABLE IF EXISTS `app_itunes`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `app_itunes` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(128) NOT NULL,
  `icon_link` text,
  `icon_path` text,
  `source` varchar(64) NOT NULL,
  `source_link` varchar(255) NOT NULL,
  `rating` varchar(16) DEFAULT NULL,
  `version` varchar(32) DEFAULT NULL,
  `developer` varchar(64) DEFAULT NULL,
  `sdk_support` varchar(128) DEFAULT NULL,
  `category` varchar(64) DEFAULT NULL,
  `screen_support` varchar(256) DEFAULT NULL,
  `apk_size` varchar(32) DEFAULT NULL,
  `language` varchar(64) DEFAULT NULL,
  `publish_date` int(11) DEFAULT NULL,
  `downloads` varchar(64) DEFAULT NULL,
  `description` text,
  `images` text,
  `images_path` text,
  `qr_link` text,
  `download_link` text,
  `last_crawl` int(11) NOT NULL,
  `tag` text,
  `price` float DEFAULT '0',
  `app_id` varchar(255) DEFAULT NULL,
  `apple_id` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `link_index` (`source_link`)
) ENGINE=InnoDB AUTO_INCREMENT=571642 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `apple_account`
--

DROP TABLE IF EXISTS `apple_account`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `apple_account` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `username` varchar(255) NOT NULL,
  `password` varchar(255) NOT NULL,
  `app_num` int(11) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=32 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `apt`
--

DROP TABLE IF EXISTS `apt`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `apt` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(128) NOT NULL,
  `icon_link` text,
  `icon_path` text,
  `source` varchar(64) NOT NULL,
  `source_link` varchar(255) NOT NULL,
  `rating` varchar(16) DEFAULT NULL,
  `version` varchar(32) DEFAULT NULL,
  `developer` varchar(64) DEFAULT NULL,
  `sdk_support` varchar(128) DEFAULT NULL,
  `category` varchar(64) DEFAULT NULL,
  `screen_support` varchar(256) DEFAULT NULL,
  `apk_size` varchar(32) DEFAULT NULL,
  `language` varchar(64) DEFAULT NULL,
  `publish_date` int(11) DEFAULT NULL,
  `downloads` varchar(64) DEFAULT NULL,
  `description` text,
  `images` text,
  `images_path` text,
  `qr_link` text,
  `download_link` text,
  `last_crawl` int(11) NOT NULL,
  `tag` text,
  PRIMARY KEY (`id`),
  UNIQUE KEY `link_index` (`source_link`)
) ENGINE=InnoDB AUTO_INCREMENT=11105 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `config`
--

DROP TABLE IF EXISTS `config`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `config` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `key` varchar(100) NOT NULL,
  `value` varchar(1024) NOT NULL,
  `desc` varchar(200) DEFAULT NULL,
  `created_at` datetime NOT NULL,
  `updated_at` datetime NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `key_UNIQUE` (`key`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `duplicate_apk`
--

DROP TABLE IF EXISTS `duplicate_apk`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `duplicate_apk` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `package_name` varchar(255) NOT NULL,
  `version_code` bigint(20) DEFAULT NULL,
  `download_link` varchar(255) NOT NULL,
  `source_link` varchar(255) NOT NULL,
  `source` varchar(32) NOT NULL,
  `vol_id` varchar(32) NOT NULL,
  `tag` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `index_download_link` (`download_link`),
  KEY `duplicate_apk_package_name_version_code_source` (`package_name`,`version_code`,`source`)
) ENGINE=InnoDB AUTO_INCREMENT=2409933 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `entry`
--

DROP TABLE IF EXISTS `entry`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `entry` (
  `download_link` varchar(255) NOT NULL,
  `source_link` varchar(255) NOT NULL,
  `source` varchar(32) NOT NULL,
  `file_name` varchar(256) DEFAULT NULL,
  `vol_id` varchar(32) NOT NULL,
  `tag` int(11) DEFAULT NULL,
  PRIMARY KEY (`download_link`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `final_app`
--

DROP TABLE IF EXISTS `final_app`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `final_app` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(128) NOT NULL,
  `icon_link` text,
  `icon_path` text,
  `source` varchar(64) NOT NULL,
  `source_link` varchar(255) DEFAULT NULL,
  `rating` varchar(16) DEFAULT NULL,
  `version` varchar(255) DEFAULT NULL,
  `developer` varchar(64) DEFAULT NULL,
  `sdk_support` varchar(128) DEFAULT NULL,
  `category` varchar(64) DEFAULT NULL,
  `screen_support` varchar(256) DEFAULT NULL,
  `apk_size` varchar(32) DEFAULT NULL,
  `language` varchar(64) DEFAULT NULL,
  `publish_date` int(11) DEFAULT NULL,
  `downloads` varchar(64) DEFAULT NULL,
  `description` text,
  `images` text,
  `images_path` text,
  `qr_link` text,
  `download_link` text,
  `last_crawl` int(11) NOT NULL,
  `tag` text,
  `security_status` varchar(32) DEFAULT NULL,
  `package_name` varchar(255) DEFAULT NULL,
  `version_code` bigint(20) unsigned DEFAULT NULL,
  `file_path` varchar(255) DEFAULT NULL,
  `vol_id` int(11) DEFAULT NULL,
  `sig` varchar(64) DEFAULT NULL,
  `is_refresh` int(11) DEFAULT NULL,
  `price` float DEFAULT '0',
  `file_type` varchar(32) DEFAULT NULL,
  `min_sdk_version` int(32) DEFAULT NULL,
  `is_break` int(32) DEFAULT NULL,
  `platform` int(11) DEFAULT NULL,
  `package_hash` varchar(64) DEFAULT NULL,
  `update_note` text,
  `avail_download_links` varchar(2048) DEFAULT NULL,
  `status` int(11) DEFAULT '0',
  `updated_at` datetime DEFAULT NULL,
  `error` varchar(1024) DEFAULT NULL,
  `labels` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `source_link` (`source_link`),
  UNIQUE KEY `index_p_v_f_s` (`package_name`,`version_code`,`file_type`,`is_break`),
  KEY `idx_pv` (`package_name`,`version_code`),
  KEY `pk_h_index` (`package_hash`),
  KEY `finalapp_last_crawl` (`last_crawl`),
  KEY `idx_u_s` (`updated_at`,`status`)
) ENGINE=InnoDB AUTO_INCREMENT=2433764 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `final_app_version`
--

DROP TABLE IF EXISTS `final_app_version`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `final_app_version` (
  `id` int(11) NOT NULL DEFAULT '0',
  `package_name` varchar(255) DEFAULT NULL,
  `version_code` bigint(20) DEFAULT NULL,
  `is_move` int(11) DEFAULT NULL,
  `img_status` int(11) DEFAULT NULL,
  `security_status` varchar(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `idx_pk` (`package_name`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `img`
--

DROP TABLE IF EXISTS `img`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `img` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(128) NOT NULL,
  `icon_link` text,
  `icon_path` text,
  `source` varchar(64) NOT NULL,
  `source_link` varchar(255) NOT NULL,
  `rating` varchar(16) DEFAULT NULL,
  `version` varchar(32) DEFAULT NULL,
  `developer` varchar(64) DEFAULT NULL,
  `sdk_support` varchar(128) DEFAULT NULL,
  `category` varchar(64) DEFAULT NULL,
  `screen_support` varchar(256) DEFAULT NULL,
  `apk_size` varchar(32) DEFAULT NULL,
  `language` varchar(64) DEFAULT NULL,
  `publish_date` int(11) DEFAULT NULL,
  `downloads` varchar(64) DEFAULT NULL,
  `description` text,
  `images` text,
  `images_path` text,
  `qr_link` text,
  `download_link` varchar(255) DEFAULT NULL,
  `last_crawl` int(11) NOT NULL,
  `tag` text,
  PRIMARY KEY (`id`),
  UNIQUE KEY `link_index` (`source_link`),
  KEY `idx_dl` (`download_link`)
) ENGINE=InnoDB AUTO_INCREMENT=81627 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `itunes_game_cate`
--

DROP TABLE IF EXISTS `itunes_game_cate`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `itunes_game_cate` (
  `app_id` varchar(255) NOT NULL,
  `app_name` varchar(255) NOT NULL,
  `cate_id` varchar(255) NOT NULL,
  `cate_name` varchar(255) NOT NULL,
  PRIMARY KEY (`app_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `link_monitor`
--

DROP TABLE IF EXISTS `link_monitor`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `link_monitor` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `source` varchar(64) NOT NULL,
  `category` varchar(64) NOT NULL,
  `link` varchar(255) NOT NULL,
  `description` text,
  `create_time` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`source`,`category`,`create_time`)
) ENGINE=InnoDB AUTO_INCREMENT=5022568 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `move_apk`
--

DROP TABLE IF EXISTS `move_apk`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `move_apk` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `vol_id` int(11) DEFAULT NULL,
  `file_path` varchar(255) DEFAULT NULL,
  `status` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `file_path` (`file_path`)
) ENGINE=MyISAM AUTO_INCREMENT=43 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `new_link`
--

DROP TABLE IF EXISTS `new_link`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `new_link` (
  `id` char(32) NOT NULL DEFAULT '',
  `source` varchar(64) NOT NULL,
  `link` varchar(256) NOT NULL,
  `last_crawl` int(11) NOT NULL,
  `priority` float NOT NULL,
  `pages` int(11) NOT NULL DEFAULT '0',
  PRIMARY KEY (`id`),
  KEY `index2` (`link`(255)),
  KEY `idx_multi` (`source`,`priority`,`last_crawl`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `nineone_comment`
--

DROP TABLE IF EXISTS `nineone_comment`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `nineone_comment` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `app_id` varchar(100) NOT NULL,
  `comment` varchar(500) DEFAULT NULL,
  `created_at` datetime NOT NULL,
  `username` varchar(45) NOT NULL,
  `rate` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=153484 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `qihu_comment`
--

DROP TABLE IF EXISTS `qihu_comment`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `qihu_comment` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `app_id` varchar(100) NOT NULL,
  `comment` varchar(500) DEFAULT NULL,
  `created_at` datetime NOT NULL,
  `username` varchar(45) NOT NULL,
  `rate` varchar(45) DEFAULT NULL,
  `rate_dst` tinyint(4) DEFAULT '0',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1289874 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `simple_crawler_91_comment`
--

DROP TABLE IF EXISTS `simple_crawler_91_comment`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `simple_crawler_91_comment` (
  `link` varchar(255) NOT NULL,
  `status` tinyint(3) unsigned NOT NULL DEFAULT '0' COMMENT '0: not started 1: processing 2: success 3: failed',
  `extra` varchar(1000) DEFAULT NULL,
  `reason` varchar(1000) DEFAULT NULL,
  `source` varchar(300) DEFAULT NULL,
  `add_time` datetime DEFAULT NULL,
  `update_time` datetime DEFAULT NULL,
  `priority` int(11) DEFAULT '0',
  PRIMARY KEY (`link`),
  KEY `s_p` (`status`,`priority`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `simple_crawler_qihu_comment`
--

DROP TABLE IF EXISTS `simple_crawler_qihu_comment`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `simple_crawler_qihu_comment` (
  `link` varchar(255) NOT NULL,
  `status` tinyint(3) unsigned NOT NULL DEFAULT '0' COMMENT '0: not started 1: processing 2: success 3: failed',
  `extra` varchar(1000) DEFAULT NULL,
  `reason` varchar(1000) DEFAULT NULL,
  `source` varchar(300) DEFAULT NULL,
  `add_time` datetime DEFAULT NULL,
  `update_time` datetime DEFAULT NULL,
  `priority` int(11) DEFAULT '0',
  PRIMARY KEY (`link`),
  KEY `s_p` (`status`,`priority`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `smart_app_back`
--

DROP TABLE IF EXISTS `smart_app_back`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `smart_app_back` (
  `id` int(11) NOT NULL,
  `description` text,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `smart_link`
--

DROP TABLE IF EXISTS `smart_link`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `smart_link` (
  `id` char(32) NOT NULL DEFAULT '',
  `source` varchar(64) NOT NULL,
  `link` varchar(256) NOT NULL,
  `last_crawl` int(11) NOT NULL,
  `priority` float NOT NULL,
  `pages` int(11) NOT NULL DEFAULT '0',
  `package_name` varchar(255) DEFAULT NULL,
  `version_code` bigint(20) unsigned DEFAULT NULL,
  `add_time` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`source`,`last_crawl`,`priority`),
  KEY `index2` (`link`(255))
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `sph_counter`
--

DROP TABLE IF EXISTS `sph_counter`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `sph_counter` (
  `counter_id` int(11) NOT NULL,
  `max_doc_id` int(11) NOT NULL,
  PRIMARY KEY (`counter_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `t_appinfo`
--

DROP TABLE IF EXISTS `t_appinfo`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `t_appinfo` (
  `APP_ID` int(11) NOT NULL,
  `STORE_ID` int(11) DEFAULT NULL,
  `AP_ID` int(11) DEFAULT NULL,
  `APP_TYPE` int(11) DEFAULT NULL,
  `APP_NAME` varchar(255) DEFAULT NULL,
  `APP_SPELL` varchar(255) DEFAULT NULL,
  `CATE_ID` int(11) DEFAULT NULL,
  `FIRSTCATE_ID` int(11) DEFAULT NULL,
  `SECONDCATE_ID` int(11) DEFAULT NULL,
  `STORE_CATE_ID` int(11) DEFAULT NULL,
  `CLICK_COUNT` int(11) DEFAULT NULL,
  `RECOMMEND_COUNT` int(11) DEFAULT NULL,
  `COMMENT_COUNT` int(11) DEFAULT NULL,
  `COLLECT_COUNT` int(11) DEFAULT NULL,
  `SALE_COUNT` int(11) DEFAULT NULL,
  `DOWNLOAD_COUNT` int(11) DEFAULT NULL,
  `KEYWORD` varchar(255) DEFAULT NULL,
  `APP_BRIEF` text,
  `ADD_DATE` datetime DEFAULT NULL,
  `LAST_EDIT_DATE` datetime DEFAULT NULL,
  `LAST_ONSALE_DATE` datetime DEFAULT NULL,
  `IS_APRECOMMEND` int(11) DEFAULT NULL,
  `IS_MALLRECOMMEND` int(11) DEFAULT NULL,
  `IS_NEWRECOMMEND` int(11) DEFAULT NULL,
  `AUTHOR` varchar(32) DEFAULT NULL,
  `AVG_GRADE` float DEFAULT NULL,
  `LANG` varchar(32) DEFAULT NULL,
  `VERSION` varchar(32) DEFAULT NULL,
  `CHARGE_TYPE` int(11) DEFAULT NULL,
  `PRICE` float DEFAULT NULL,
  `PRICE_ID` int(11) DEFAULT NULL,
  `SALE_STATUS` int(11) DEFAULT NULL,
  `DOWN_MAXTIMES` int(11) DEFAULT NULL,
  `COPY_NO` varchar(255) DEFAULT NULL,
  `STATUS` int(11) DEFAULT NULL,
  `REFER_ID` int(11) DEFAULT NULL,
  `CALLBACK_URL` varchar(255) DEFAULT NULL,
  `SKILL_REMARK` varchar(255) DEFAULT NULL,
  `HANDLE_REMARK` varchar(255) DEFAULT NULL,
  `TEST_REMARK` varchar(255) DEFAULT NULL,
  `APP_DESC` varchar(255) DEFAULT NULL,
  `ISCOMMEND` varchar(32) DEFAULT NULL,
  `APPKEY` varchar(32) DEFAULT NULL,
  `IDENTIFY_IP` varchar(32) DEFAULT NULL,
  `LIST_TYPE` int(11) DEFAULT NULL,
  `TWOCODEBIGPIC` varchar(255) DEFAULT NULL,
  `TWOCODESMALLPIC` varchar(255) DEFAULT NULL,
  `TWOCODEID` varchar(32) DEFAULT NULL,
  `DOWNLOAD_BASE` int(11) DEFAULT NULL,
  `DOWNLOAD_MANUAL` int(11) DEFAULT NULL,
  `RULE_GRADE` float DEFAULT NULL,
  `REALAVG_GRADE` float DEFAULT NULL,
  `INTER_GRADE` float DEFAULT NULL,
  `FIRST_ONSALE_DATE` datetime DEFAULT NULL,
  `DOWN_COUNT_WEEK` int(11) DEFAULT NULL,
  `DOWN_COUNT_MONTH` int(11) DEFAULT NULL,
  `PACKAGE_TYPE` int(11) DEFAULT NULL,
  `ANDROID_FLOW` int(11) DEFAULT NULL,
  `IS_TRYPLAY` int(11) DEFAULT NULL,
  `GRADE_COUNT` int(11) DEFAULT NULL,
  `TRYPLAY_TIME` int(11) DEFAULT NULL,
  `SHORTADDRPIC` varchar(255) DEFAULT NULL,
  `tag` int(11) DEFAULT NULL,
  PRIMARY KEY (`APP_ID`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `tmp_360`
--

DROP TABLE IF EXISTS `tmp_360`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `tmp_360` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `source_link` varchar(255) NOT NULL,
  `images` text,
  `images_path` text,
  `is_refresh` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `link_index` (`source_link`)
) ENGINE=MyISAM AUTO_INCREMENT=102459 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `tmp_for_icon`
--

DROP TABLE IF EXISTS `tmp_for_icon`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `tmp_for_icon` (
  `id` int(11) NOT NULL DEFAULT '0',
  `package_name` varchar(255) CHARACTER SET utf8 DEFAULT NULL,
  `version_code` bigint(20) unsigned DEFAULT NULL
) ENGINE=MyISAM DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `unique_apk`
--

DROP TABLE IF EXISTS `unique_apk`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `unique_apk` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `package_name` varchar(255) NOT NULL,
  `version_code` bigint(20) unsigned DEFAULT NULL,
  `download_link` varchar(255) NOT NULL,
  `source_link` varchar(255) NOT NULL,
  `source` varchar(32) NOT NULL,
  `vol_id` varchar(32) NOT NULL,
  `sig` varchar(64) DEFAULT NULL,
  `tag` int(11) DEFAULT NULL,
  `tag2` int(2) DEFAULT NULL,
  `is_refresh` int(11) DEFAULT NULL,
  `img_status` int(11) DEFAULT NULL,
  `watermark_status` int(11) DEFAULT NULL,
  `version` varchar(64) DEFAULT NULL,
  `apk_size` varchar(32) DEFAULT NULL,
  `file_type` varchar(32) DEFAULT NULL,
  `min_sdk_version` int(32) DEFAULT NULL,
  `screen_support` varchar(32) DEFAULT NULL,
  `is_break` int(32) DEFAULT NULL,
  `platform` int(11) DEFAULT NULL,
  `package_hash` varchar(64) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `idx_u_s` (`source_link`),
  UNIQUE KEY `index_p_v_f_s` (`package_name`,`version_code`,`file_type`,`is_break`),
  KEY `idx_sourcelink` (`source_link`,`source`)
) ENGINE=InnoDB AUTO_INCREMENT=1972251 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `unique_apk_temp`
--

DROP TABLE IF EXISTS `unique_apk_temp`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `unique_apk_temp` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `package_name` varchar(255) NOT NULL,
  `version_code` bigint(20) unsigned DEFAULT NULL,
  `download_link` varchar(255) NOT NULL,
  `source_link` varchar(255) NOT NULL,
  `source` varchar(32) NOT NULL,
  `vol_id` varchar(32) NOT NULL,
  `sig` varchar(64) DEFAULT NULL,
  `tag` int(11) DEFAULT NULL,
  `tag2` int(2) DEFAULT NULL,
  `is_refresh` int(11) DEFAULT NULL,
  `img_status` int(11) DEFAULT NULL,
  `watermark_status` int(11) DEFAULT NULL,
  `version` varchar(64) DEFAULT NULL,
  `apk_size` varchar(32) DEFAULT NULL,
  `file_type` varchar(32) DEFAULT NULL,
  `min_sdk_version` int(32) DEFAULT NULL,
  `screen_support` varchar(32) DEFAULT NULL,
  `is_break` int(32) DEFAULT NULL,
  `platform` int(11) DEFAULT NULL,
  `package_hash` varchar(64) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `index_p_v_f_s` (`package_name`,`version_code`,`file_type`,`is_break`),
  KEY `idx_sourcelink` (`source_link`,`source`)
) ENGINE=InnoDB AUTO_INCREMENT=1959931 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `unique_apk_temp1`
--

DROP TABLE IF EXISTS `unique_apk_temp1`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `unique_apk_temp1` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `package_name` varchar(255) NOT NULL,
  `version_code` bigint(20) unsigned DEFAULT NULL,
  `download_link` varchar(255) NOT NULL,
  `source_link` varchar(255) NOT NULL,
  `source` varchar(32) NOT NULL,
  `vol_id` varchar(32) NOT NULL,
  `sig` varchar(64) DEFAULT NULL,
  `tag` int(11) DEFAULT NULL,
  `tag2` int(2) DEFAULT NULL,
  `is_refresh` int(11) DEFAULT NULL,
  `img_status` int(11) DEFAULT NULL,
  `watermark_status` int(11) DEFAULT NULL,
  `version` varchar(64) DEFAULT NULL,
  `apk_size` varchar(32) DEFAULT NULL,
  `file_type` varchar(32) DEFAULT NULL,
  `min_sdk_version` int(32) DEFAULT NULL,
  `screen_support` varchar(32) DEFAULT NULL,
  `is_break` int(32) DEFAULT NULL,
  `platform` int(11) DEFAULT NULL,
  `package_hash` varchar(64) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `index_p_v_f_s` (`package_name`,`version_code`,`file_type`,`is_break`),
  KEY `idx_sourcelink` (`source_link`,`source`)
) ENGINE=InnoDB AUTO_INCREMENT=1965396 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `update_link`
--

DROP TABLE IF EXISTS `update_link`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `update_link` (
  `id` char(32) NOT NULL DEFAULT '',
  `source` varchar(64) NOT NULL,
  `link` varchar(256) NOT NULL,
  `last_crawl` int(11) NOT NULL,
  `priority` float NOT NULL,
  `pages` int(11) NOT NULL DEFAULT '0',
  PRIMARY KEY (`id`),
  KEY `index1` (`source`,`last_crawl`,`priority`),
  KEY `index2` (`link`(255))
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `vol`
--

DROP TABLE IF EXISTS `vol`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `vol` (
  `id` varchar(32) NOT NULL,
  `total_kbytes` int(16) NOT NULL,
  `used_kbytes` int(16) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2013-09-05 18:52:34
