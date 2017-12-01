-- Create database. --

create database tukutter character set utf8 collate utf8_general_ci;

-- Create "user" table. --

CREATE TABLE `tukutter`.`user` (
  `id` INT NOT NULL AUTO_INCREMENT COMMENT 'use id',
  `login_id` VARCHAR(255) NOT NULL COMMENT 'defined by user at sign up',
  `password` VARCHAR(255) NOT NULL COMMENT 'defined by user when sign up',
  `username` VARCHAR(255) NOT NULL COMMENT 'defined by user when sign up',
  `profile` VARCHAR(255) NULL COMMENT 'user profile',
  `active_flg` BIT(1) NOT NULL DEFAULT 1 COMMENT 'will be changed 0 when user closes the account',
  PRIMARY KEY (`id`),
  UNIQUE INDEX `id_UNIQUE` (`id` ASC),
  UNIQUE INDEX `login_id_UNIQUE` (`login_id` ASC),
  UNIQUE INDEX `username_UNIQUE` (`username` ASC));

ALTER TABLE `tukutter`.`user` 
ADD COLUMN `prof_pict` VARCHAR(255) NULL COMMENT 'link to profile picture' AFTER `profile`;

-- Create "tweet" table. --

CREATE TABLE `tukutter`.`tweet` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `content` VARCHAR(600) NOT NULL COMMENT 'content of tweet',
  `user_id` INT NOT NULL,
  `time` TIMESTAMP NOT NULL,
  `active_flg` BIT(1) NOT NULL DEFAULT 1,
  PRIMARY KEY (`id`),
  UNIQUE INDEX `id_UNIQUE` (`id` ASC));

-- Create "favorite" table. --

CREATE TABLE `tukutter`.`favorite` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `user_id` INT NOT NULL,
  `tweet_id` INT NOT NULL,
  `active_flg` BIT(1) NOT NULL DEFAULT 1,
  PRIMARY KEY (`id`),
  UNIQUE INDEX `id_UNIQUE` (`id` ASC));

-- Create "follow" table. --

CREATE TABLE `tukutter`.`follow` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `follower_id` INT NOT NULL COMMENT 'user id who follows',
  `user_id` INT NOT NULL COMMENT 'user id who is followed',
  `active_flg` BIT(1) NOT NULL DEFAULT 1,
  PRIMARY KEY (`id`),
  UNIQUE INDEX `id_UNIQUE` (`id` ASC));
