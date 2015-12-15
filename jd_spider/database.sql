DROP TABLE IF EXISTS `jd_sku`;
CREATE TABLE `jd_sku` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `sku_id` bigint(20) NOT NULL DEFAULT 0 COMMENT '商品id',
  `sku_url` varchar(200) DEFAULT NULL DEFAULT '' COMMENT '商品url',
  `sku_title` varchar(200) DEFAULT NULL DEFAULT '' COMMENT '商品标题',
  `sku_pic` varchar(255) DEFAULT NULL DEFAULT '' COMMENT '商品图片',
  `sku_price` varchar(100) DEFAULT NULL  COMMENT '商品价钱',
  `creation_date` datetime DEFAULT NULL  COMMENT '创建日期',
  PRIMARY KEY (`id`),
  KEY `sku_id_index` (`sku_id`) USING BTREE,
  UNIQUE KEY `sku_id` (`sku_id`)
) ENGINE=InnoDB  DEFAULT CHARSET=utf8 COMMENT '京东商品表';