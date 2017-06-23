CREATE TABLE IF NOT EXISTS `category` 
(
  cate_id INT(11) NOT NULL AUTO_INCREMENT, 
  store_id INT(11) DEFAULT NULL,
  cate_name VARCHAR(255) NOT NULL,
  parent_id INT(11) NOT NULL,
  sort_order INT(11),
  is_show INT(11),
  imagepath VARCHAR(255),
  description VARCHAR(255) NULL,
  PRIMARY KEY (`cate_id`),
  UNIQUE KEY `cate_full_name` (`parent_id`,`cate_name`)
)

insert into category (CATE_ID, STORE_ID, CATE_NAME, PARENT_ID, SORT_ORDER, IS_SHOW, IMAGEPATH, DESCRIPTION)
values (14334, -1, '软件', 0, 1, 1, 'data/app_files/a0976c6bb2fb850fc5d869291c273c97.jpg', null);

insert into category (CATE_ID, STORE_ID, CATE_NAME, PARENT_ID, SORT_ORDER, IS_SHOW, IMAGEPATH, DESCRIPTION)
values (14335, -1, '影音阅读', 14334, 1, 1, 'data/app_files/55a54caefc35d294bff2e3d2058070e7.jpg', null);

insert into category (CATE_ID, STORE_ID, CATE_NAME, PARENT_ID, SORT_ORDER, IS_SHOW, IMAGEPATH, DESCRIPTION)
values (14336, -1, '生活娱乐', 14334, 2, 1, 'data/app_files/bcd817c3cc2cfebae250f0a1ceb5f67d.jpg', null);

insert into category (CATE_ID, STORE_ID, CATE_NAME, PARENT_ID, SORT_ORDER, IS_SHOW, IMAGEPATH, DESCRIPTION)
values (14337, -1, '聊天社区', 14334, 3, 1, 'data/app_files/5d1c12bc7414bfd26a80283e0096791d.jpg', null);

insert into category (CATE_ID, STORE_ID, CATE_NAME, PARENT_ID, SORT_ORDER, IS_SHOW, IMAGEPATH, DESCRIPTION)
values (14338, -1, '通话通信', 14334, 4, 1, 'data/app_files/60c33902526c8a3c021808737a2dc485.jpg', null);

insert into category (CATE_ID, STORE_ID, CATE_NAME, PARENT_ID, SORT_ORDER, IS_SHOW, IMAGEPATH, DESCRIPTION)
values (14339, -1, '金融理财', 14334, 5, 1, 'data/app_files/9fc691ed65fd466fb9dbaae687be3e0f.jpg', null);

insert into category (CATE_ID, STORE_ID, CATE_NAME, PARENT_ID, SORT_ORDER, IS_SHOW, IMAGEPATH, DESCRIPTION)
values (14340, -1, '体育竞技', 14334, 6, 1, 'data/app_files/5ab9300cc57f71ffd30833905d930e87.jpg', null);

insert into category (CATE_ID, STORE_ID, CATE_NAME, PARENT_ID, SORT_ORDER, IS_SHOW, IMAGEPATH, DESCRIPTION)
values (14341, -1, '电子办公', 14334, 7, 1, 'data/app_files/2cdaa0ee5e4e7298ae402121834bf640.jpg', null);

insert into category (CATE_ID, STORE_ID, CATE_NAME, PARENT_ID, SORT_ORDER, IS_SHOW, IMAGEPATH, DESCRIPTION)
values (14342, -1, '资讯新闻', 14334, 8, 1, 'data/app_files/641583dbd00060495a2bc777a003e939.jpg', null);

insert into category (CATE_ID, STORE_ID, CATE_NAME, PARENT_ID, SORT_ORDER, IS_SHOW, IMAGEPATH, DESCRIPTION)
values (14343, -1, '交通导航', 14334, 9, 1, 'data/app_files/1cc6a61904c147ed45af33e2fe3dfa90.jpg', null);

insert into category (CATE_ID, STORE_ID, CATE_NAME, PARENT_ID, SORT_ORDER, IS_SHOW, IMAGEPATH, DESCRIPTION)
values (14344, -1, '拍照摄影', 14334, 10, 1, 'data/app_files/df804b6f89c47a96895577aacb1e796c.jpg', null);

insert into category (CATE_ID, STORE_ID, CATE_NAME, PARENT_ID, SORT_ORDER, IS_SHOW, IMAGEPATH, DESCRIPTION)
values (14345, -1, '系统工具', 14334, 11, 1, 'data/app_files/ecbb123493c08db55726707896a2b9e0.jpg', null);

insert into category (CATE_ID, STORE_ID, CATE_NAME, PARENT_ID, SORT_ORDER, IS_SHOW, IMAGEPATH, DESCRIPTION)
values (14346, -1, '窗口小部件', 14334, 12, 1, 'data/app_files/303a233e5e46853c641e673b81dcced2.jpg', null);

insert into category (CATE_ID, STORE_ID, CATE_NAME, PARENT_ID, SORT_ORDER, IS_SHOW, IMAGEPATH, DESCRIPTION)
values (14347, -1, '实用工具', 14334, 13, 1, 'data/app_files/1ff14ff9c8a1c9fb0ba5e8404acdaf3d.jpg', null);

insert into category (CATE_ID, STORE_ID, CATE_NAME, PARENT_ID, SORT_ORDER, IS_SHOW, IMAGEPATH, DESCRIPTION)
values (14348, -1, '事务管理', 14334, 14, 1, 'data/app_files/d3ce42423c7ec700a35f11e1d88c4cbe.jpg', null);

insert into category (CATE_ID, STORE_ID, CATE_NAME, PARENT_ID, SORT_ORDER, IS_SHOW, IMAGEPATH, DESCRIPTION)
values (14349, -1, '教育阅读', 14334, 15, 1, 'data/app_files/d1605f323349c102833f84df9d767525.jpg', null);

insert into category (CATE_ID, STORE_ID, CATE_NAME, PARENT_ID, SORT_ORDER, IS_SHOW, IMAGEPATH, DESCRIPTION)
values (14350, -1, '主题桌面', 14334, 16, 1, 'data/app_files/cd785fc92b58feb41855fff47cad12cd.jpg', null);

insert into category (CATE_ID, STORE_ID, CATE_NAME, PARENT_ID, SORT_ORDER, IS_SHOW, IMAGEPATH, DESCRIPTION)
values (14351, -1, '健康医疗', 14334, 17, 1, 'data/app_files/ce2e8e3291647f08d7808f1c94cc609e.jpg', null);

insert into category (CATE_ID, STORE_ID, CATE_NAME, PARENT_ID, SORT_ORDER, IS_SHOW, IMAGEPATH, DESCRIPTION)
values (14352, -1, '词典翻译', 14334, 18, 1, 'data/app_files/079c3b81581bbef0a3656fa2e40e0585.jpg', null);

insert into category (CATE_ID, STORE_ID, CATE_NAME, PARENT_ID, SORT_ORDER, IS_SHOW, IMAGEPATH, DESCRIPTION)
values (14353, -1, '浏览器', 14334, 19, 1, 'data/app_files/3609ea07e8a89d9ec398fa5c056040e0.jpg', null);

insert into category (CATE_ID, STORE_ID, CATE_NAME, PARENT_ID, SORT_ORDER, IS_SHOW, IMAGEPATH, DESCRIPTION)
values (14354, -1, '安全防护', 14334, 20, 1, 'data/app_files/24df5834b86e8d8ab213e869dde36ccf.jpg', null);

insert into category (CATE_ID, STORE_ID, CATE_NAME, PARENT_ID, SORT_ORDER, IS_SHOW, IMAGEPATH, DESCRIPTION)
values (14355, -1, '输入法', 14334, 21, 1, 'data/app_files/837775bca7743ac3d9ea3abf586e798e.jpg', null);

insert into category (CATE_ID, STORE_ID, CATE_NAME, PARENT_ID, SORT_ORDER, IS_SHOW, IMAGEPATH, DESCRIPTION)
values (14356, -1, '网络购物', 14334, 22, 1, 'data/app_files/24561684085801631377dc23220dfac4.jpg', null);

insert into category (CATE_ID, STORE_ID, CATE_NAME, PARENT_ID, SORT_ORDER, IS_SHOW, IMAGEPATH, DESCRIPTION)
values (14357, -1, '游戏', 0, 2, 1, 'data/app_files/1a07f82016c14744fbb19b49a4438017.jpg', null);

insert into category (CATE_ID, STORE_ID, CATE_NAME, PARENT_ID, SORT_ORDER, IS_SHOW, IMAGEPATH, DESCRIPTION)
values (14358, -1, '休闲', 14357, 1, 1, 'data/app_files/8fcfe4e9e6343673da6108f7e389645e.jpg', null);

insert into category (CATE_ID, STORE_ID, CATE_NAME, PARENT_ID, SORT_ORDER, IS_SHOW, IMAGEPATH, DESCRIPTION)
values (14359, -1, '益智', 14357, 2, 1, 'data/app_files/e5c4c600eb7ca2cc4497e7e3093b8b14.jpg', null);

insert into category (CATE_ID, STORE_ID, CATE_NAME, PARENT_ID, SORT_ORDER, IS_SHOW, IMAGEPATH, DESCRIPTION)
values (14360, -1, '角色扮演', 14357, 3, 1, 'data/app_files/fe4caa83626141070cfae7ec7ac5cd17.jpg', null);

insert into category (CATE_ID, STORE_ID, CATE_NAME, PARENT_ID, SORT_ORDER, IS_SHOW, IMAGEPATH, DESCRIPTION)
values (14361, -1, '战略', 14357, 4, 1, 'data/app_files/8aab97167718a86a8b989400b9be4d45.jpg', null);

insert into category (CATE_ID, STORE_ID, CATE_NAME, PARENT_ID, SORT_ORDER, IS_SHOW, IMAGEPATH, DESCRIPTION)
values (14362, -1, '动作', 14357, 5, 1, 'data/app_files/7d16ef1326b7c826c2c855d8dc3dcb13.jpg', null);

insert into category (CATE_ID, STORE_ID, CATE_NAME, PARENT_ID, SORT_ORDER, IS_SHOW, IMAGEPATH, DESCRIPTION)
values (14363, -1, '射击', 14357, 6, 1, 'data/app_files/dcfdd11b2b698bdf8ed0f9d7529dd428.jpg', null);

insert into category (CATE_ID, STORE_ID, CATE_NAME, PARENT_ID, SORT_ORDER, IS_SHOW, IMAGEPATH, DESCRIPTION)
values (14364, -1, '经营', 14357, 7, 1, 'data/app_files/26c0b20f6261cb7bc50f3e05966bf7b4.jpg', null);

insert into category (CATE_ID, STORE_ID, CATE_NAME, PARENT_ID, SORT_ORDER, IS_SHOW, IMAGEPATH, DESCRIPTION)
values (14365, -1, '养成', 14357, 8, 1, 'data/app_files/40b39488d2c5d451f5c963ebdf195d7e.jpg', null);

insert into category (CATE_ID, STORE_ID, CATE_NAME, PARENT_ID, SORT_ORDER, IS_SHOW, IMAGEPATH, DESCRIPTION)
values (14366, -1, '冒险', 14357, 9, 1, 'data/app_files/6c5cf9c72db6f153186abd639daa5255.jpg', null);

insert into category (CATE_ID, STORE_ID, CATE_NAME, PARENT_ID, SORT_ORDER, IS_SHOW, IMAGEPATH, DESCRIPTION)
values (14367, -1, '网游', 14357, 10, 1, 'data/app_files/88b74bb02bfb4d241aef154db5ca192f.jpg', null);

insert into category (CATE_ID, STORE_ID, CATE_NAME, PARENT_ID, SORT_ORDER, IS_SHOW, IMAGEPATH, DESCRIPTION)
values (14368, -1, '棋牌', 14357, 11, 1, 'data/app_files/5258fd843698830e787807c80a20a770.jpg', null);

insert into category (CATE_ID, STORE_ID, CATE_NAME, PARENT_ID, SORT_ORDER, IS_SHOW, IMAGEPATH, DESCRIPTION)
values (14369, -1, '模拟器', 14357, 12, 1, 'data/app_files/be7071be2b21a3d53dd64a761fa97abb.jpg', null);

insert into category (CATE_ID, STORE_ID, CATE_NAME, PARENT_ID, SORT_ORDER, IS_SHOW, IMAGEPATH, DESCRIPTION)
values (14370, -1, '体育', 14357, 13, 1, 'data/app_files/3c069210cf34c2066cea88953cc5d5c4.jpg', null);

insert into category (CATE_ID, STORE_ID, CATE_NAME, PARENT_ID, SORT_ORDER, IS_SHOW, IMAGEPATH, DESCRIPTION)
values (14371, -1, '电子书', 0, 3, 1, 'data/app_files/91ab4dc31fc009e88c6215d6acf0bfbf.jpg', null);

insert into category (CATE_ID, STORE_ID, CATE_NAME, PARENT_ID, SORT_ORDER, IS_SHOW, IMAGEPATH, DESCRIPTION)
values (14372, -1, '书籍', 14371, 1, 1, 'data/app_files/2a92379631e6210f82f67458afce48d4.jpg', null);

insert into category (CATE_ID, STORE_ID, CATE_NAME, PARENT_ID, SORT_ORDER, IS_SHOW, IMAGEPATH, DESCRIPTION)
values (14373, -1, '漫画', 14371, 2, 1, 'data/app_files/5eb01e49ebdb5aa4f7c22527437e59e0.jpg', null);

insert into category (CATE_ID, STORE_ID, CATE_NAME, PARENT_ID, SORT_ORDER, IS_SHOW, IMAGEPATH, DESCRIPTION)
values (14374, -1, '有声阅读', 14371, 3, 1, 'data/app_files/cb3a97a10c6d585a6adaf41e68bc8d75.jpg', null);

insert into category (CATE_ID, STORE_ID, CATE_NAME, PARENT_ID, SORT_ORDER, IS_SHOW, IMAGEPATH, DESCRIPTION)
values (14375, -1, '笑话', 14371, 4, 1, 'data/app_files/f86a94fcce3e7a5ad06e3a261087f121.jpg', null);

insert into category (CATE_ID, STORE_ID, CATE_NAME, PARENT_ID, SORT_ORDER, IS_SHOW, IMAGEPATH, DESCRIPTION)
values (14376, -1, '资料', 14371, 5, 1, 'data/app_files/3090a342aaed5643448b30be35aa3b24.jpg', null);

insert into category (CATE_ID, STORE_ID, CATE_NAME, PARENT_ID, SORT_ORDER, IS_SHOW, IMAGEPATH, DESCRIPTION)
values (14377, -1, '影音', 0, 4, 1, 'data/app_files/6f7ed8e1fced3ae72a21bf57aae79659.jpg', null);

insert into category (CATE_ID, STORE_ID, CATE_NAME, PARENT_ID, SORT_ORDER, IS_SHOW, IMAGEPATH, DESCRIPTION)
values (14378, -1, '音乐', 14377, 1, 1, 'data/app_files/816a1d179f902aef694fa219529a7088.jpg', null);

insert into category (CATE_ID, STORE_ID, CATE_NAME, PARENT_ID, SORT_ORDER, IS_SHOW, IMAGEPATH, DESCRIPTION)
values (14379, -1, '视频', 14377, 2, 1, 'data/app_files/f0e1cb13eed3a9817732d3498db2fa9d.jpg', null);



CREATE TABLE IF NOT EXISTS `categoryappmap` 
(
  app_id INT(11) NOT NULL,
  firstcate_id INT(11)  NOT NULL,
  secondcate_id INT(11) NOT NULL,
  cate_id INT(11) NOT NULL,
  last_modify_date datetime,
  UNIQUE KEY `app_id` (`app_id`)
)
%s/\(\d\+-\d\+\)\(-\)\(\d\+\)/\3\2\1/
%s/dd-mm-yyyy hh24:mi:ss/%Y-%m-%d %H:%m:%s/
%s/to_date/date_format
%s/t_androidappcatemap/categoryappmap/
