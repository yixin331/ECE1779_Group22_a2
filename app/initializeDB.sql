DROP DATABASE IF EXISTS ECE1779A1;

CREATE DATABASE ECE1779A1;

USE ECE1779A1;

DROP TABLE IF EXISTS image;

CREATE TABLE image (
	ID VARCHAR(100) PRIMARY KEY,
	path VARCHAR(1000),
	last_edited_time TIMESTAMP
);

DROP TABLE IF EXISTS memcache_config;

CREATE TABLE memcache_config (
	updated_time TIMESTAMP PRIMARY KEY DEFAULT CURRENT_TIMESTAMP,
	capacity INT DEFAULT 128,
	policy VARCHAR(10) DEFAULT 'LRU'
);

INSERT INTO memcache_config (updated_time, capacity, policy) VALUES (DEFAULT,  DEFAULT,  DEFAULT);

DROP TABLE IF EXISTS memcache_stat;

CREATE TABLE memcache_stat (
	updated_time TIMESTAMP PRIMARY KEY DEFAULT CURRENT_TIMESTAMP,
	num_item INT,
	total_size INT,
	num_request INT,
	miss_rate FLOAT,
	hit_rate FLOAT
);

