CREATE DATABASE IF NOT EXISTS atcg;

USE atcg;

CREATE TABLE IF NOT EXISTS atcg_demand_info (
    id VARCHAR(64) PRIMARY KEY COMMENT '全局唯一标识符',
    batch_id VARCHAR(64) NOT NULL COMMENT '批次ID，表示数据所属的批次',
    title VARCHAR(64) COMMENT '标题',
    parent VARCHAR(64) COMMENT '父级标题',
    start_index VARCHAR(64) COMMENT '正文内容的起始段落索引',
    end_index VARCHAR(64) COMMENT '正文内容的结束段落索引',
    content TEXT COMMENT '正文内容',
    number VARCHAR(64) COMMENT '标题序号',
    parent_number VARCHAR(64) COMMENT '父级标题序号'
) COMMENT '需求信息表';

CREATE TABLE IF NOT EXISTS actg_history_record (
    id VARCHAR(64) PRIMARY KEY COMMENT '全局唯一标识符',
    file_name VARCHAR(256) COMMENT '需求文件名',
    file_hash_code VARCHAR(256) COMMENT '需求文件哈希码',
    upload_time TIMESTAMP COMMENT '开始上传时间',
    last_analyze_time TIMESTAMP COMMENT '最近一次分析时间',
    status VARCHAR(64) COMMENT '状态（0是已上传，1是已分析，2是已删除）'
) COMMENT '历史记录表';
