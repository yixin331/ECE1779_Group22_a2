IF EXISTS (SELECT * FROM sys.databases WHERE name = 'ECE1779A1')
BEGIN
    DROP DATABASE ECE1779A1;
END;

CREATE DATABASE ECE1779A1;
GO

USE ECE1779A1;
GO

IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='image' and xtype='U')
BEGIN
    CREATE TABLE image (
        ID VARCHAR(100) PRIMARY KEY,
        path VARCHAR(1000),
        last_edited_time TIMESTAMP
    )
END

IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='memcache_config' and xtype='U')
BEGIN
    CREATE TABLE image (
        updated_time TIMESTAMP PRIMARY KEY DEFAULT CURRENT_TIMESTAMP,
        capacity INT DEFAULT 128,
        policy VARCHAR(10) DEFAULT 'LRU'
    )
END

IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='memcache_stat' and xtype='U')
BEGIN
    CREATE TABLE image (
        updated_time TIMESTAMP PRIMARY KEY DEFAULT CURRENT_TIMESTAMP,
        num_item INT,
        total_size INT,
        num_request INT,
        miss_rate DOUBLE(2),
        hit_rate DOUBLE(2)
    )
END

