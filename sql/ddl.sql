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
    id VARCHAR(64) PRIMARY KEY COMMENT '全局唯一标识符,对应atcg_demand_info表中的batch_id',
    file_name VARCHAR(256) COMMENT '需求文件名',
    file_hash_code VARCHAR(256) COMMENT '需求文件哈希码',
    upload_time TIMESTAMP COMMENT '开始上传时间',
    last_analyze_time TIMESTAMP COMMENT '最近一次分析时间',
    status VARCHAR(64) COMMENT '状态（0是已上传，1是已分析，2是已删除）'
) COMMENT '历史记录表';

CREATE TABLE IF NOT EXISTS actg_test_case (
    id VARCHAR(64) PRIMARY KEY COMMENT '全局唯一标识符',
    batch_id VARCHAR(64) NOT NULL COMMENT '批次ID，表示数据所属的批次',
    module VARCHAR(64) COMMENT '所属模块',
    version VARCHAR(64) COMMENT '所属版本',
    requirement VARCHAR(256) COMMENT '相关需求',
    title VARCHAR(256) COMMENT '用例标题',
    precondition TEXT COMMENT '前置条件',
    steps TEXT COMMENT '步骤',
    expected_result TEXT COMMENT '预期',
    keywords VARCHAR(256) COMMENT '关键词',
    priority VARCHAR(64) COMMENT '优先级',
    case_type VARCHAR(64) COMMENT '用例类型',
    applicable_phase VARCHAR(64) COMMENT '适用阶段',
    status VARCHAR(64) COMMENT '用例状态'
) COMMENT '测试用例表格';



