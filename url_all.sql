/*
 Navicat Premium Data Transfer

 Source Server         : 
 Source Server Type    : MariaDB
 Source Server Version : 100320
 Source Host           : 192.168.102.227:3306
 Source Schema         : url_all

 Target Server Type    : MariaDB
 Target Server Version : 100320
 File Encoding         : 65001

 Date: 03/09/2020 15:17:56
*/

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------
-- Table structure for ip_tables
-- ----------------------------
DROP TABLE IF EXISTS `ip_tables`;
CREATE TABLE `ip_tables`  (
  `id` int(22) NOT NULL AUTO_INCREMENT,
  `ip` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
  `extract` int(22) NOT NULL DEFAULT 0,
  PRIMARY KEY (`id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 51304 CHARACTER SET = utf8 COLLATE = utf8_general_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for url_tables
-- ----------------------------
DROP TABLE IF EXISTS `url_tables`;
CREATE TABLE `url_tables`  (
  `id` int(20) NOT NULL AUTO_INCREMENT,
  `url` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
  `CreateTime` datetime(0) NULL DEFAULT current_timestamp() COMMENT '创建时间',
  `extract` int(4) NULL DEFAULT 0,
  PRIMARY KEY (`id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 3174897 CHARACTER SET = utf8 COLLATE = utf8_general_ci ROW_FORMAT = Dynamic;

SET FOREIGN_KEY_CHECKS = 1;
