# from contextlib import contextmanager
# import sys
# import os
#
# # 添加项目根目录到sys.path
# sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# from src.mapper.DemandInfoMapper import SessionLocal, DemandInfoMapper, DemandInfo
# from src.util.SnowflakeUtil import snowflake
#
#
# @contextmanager
# def get_db_session():
#     db1 = SessionLocal()
#     try:
#         yield db1
#     finally:
#         db1.close()
#
#
# def insert():
#     # 创建一个新记录并插入数据库
#     with get_db_session() as db:
#         mapper = DemandInfoMapper(db)
#         new_demand_info = DemandInfo(
#             id=str(snowflake.get_id()),
#             batch_id="example_batch_id",
#             title="Example Title",
#             parent="Example Parent",
#             start_index="0",
#             end_index="10",
#             content="Example Content",
#             number="1",
#             parent_number="0"
#         )
#         mapper.insert_demand_info(new_demand_info)
#
#
# def select():
#     # 从数据库中获取记录
#     with get_db_session() as db:
#         mapper = DemandInfoMapper(db)
#         demand_info = mapper.get_all()
#         for item in demand_info:
#             print(item)
#
# # insert()
# select()
