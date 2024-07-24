import os
import sys
from contextlib import contextmanager

from core.mapper.DemandInfoMapper import SessionLocal, DemandInfoMapper


@contextmanager
def get_db_session():
    db1 = SessionLocal()
    try:
        yield db1
    finally:
        db1.close()


class DemandInfoService:
    def insert(self, demandInfo):
        # 创建一个新记录并插入数据库
        with get_db_session() as db:
            mapper = DemandInfoMapper(db)
            mapper.insert_demand_info(demandInfo)

    def select_all(self):
        # 从数据库中获取记录
        with get_db_session() as db:
            mapper = DemandInfoMapper(db)
            demand_info = mapper.get_all()
            for item in demand_info:
                print(item)
            return demand_info

    def select_by_batch_id(self, batch_id):
        # 从数据库中获取记录
        with get_db_session() as db:
            mapper = DemandInfoMapper(db)
            demand_info = mapper.get_demand_info_by_batch_id(batch_id)
            # for item in demand_info:
            #     print(item)
            return demand_info


demandInfoService = DemandInfoService()
