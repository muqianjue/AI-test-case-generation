CREATE DATABASE IF NOT EXISTS atcg;

USE atcg;

CREATE TABLE IF NOT EXISTS atcg_demand_info (
    id VARCHAR(64) PRIMARY KEY,
    batch_id VARCHAR(64) NOT NULL,
    title VARCHAR(64),
    parent VARCHAR(64),
    start_index VARCHAR(64),
    end_index VARCHAR(64),
    content TEXT,
    number VARCHAR(64),
    parent_number VARCHAR(64)
);
