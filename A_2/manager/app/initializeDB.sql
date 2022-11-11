DROP DATABASE IF EXISTS ECE1779A2;

CREATE DATABASE ECE1779A2;

USE ECE1779A2;

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

DROP TABLE IF EXISTS memcache_mode;

CREATE TABLE memcache_mode (
	updated_time TIMESTAMP PRIMARY KEY DEFAULT CURRENT_TIMESTAMP,
	num_node INT DEFAULT 1,
	mode VARCHAR(10) DEFAULT 'Manual',
	max_thr FLOAT DEFAULT 1,
	min_thr FLOAT DEFAULT 0,
	expand_ratio FLOAT DEFAULT 1,
	shrink_ratio FLOAT DEFAULT 1
);

INSERT INTO memcache_mode (updated_time, num_node, mode, max_thr, min_thr, expand_ratio, shrink_ratio) VALUES (DEFAULT,  DEFAULT,  DEFAULT, DEFAULT, DEFAULT, DEFAULT, DEFAULT);

