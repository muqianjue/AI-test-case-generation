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
            demandInfoList = mapper.get_demand_info_by_batch_id(batch_id)
            # for item in demand_info:
            #     print(item)
            # 初始化过滤到后的需求信息
            newDemandInfoList = []
            # 得到父标题集合
            parentNumbers = {demand.parent_number for demand in demandInfoList}
            # 遍历需求功能点
            for demand in demandInfoList:
                # 如果是前三章直接跳过
                if demand.number.startswith('1') or demand.number.startswith('2') or demand.number.startswith('3'):
                    continue
                # 如果是别的需求标题的父标题也跳过
                if demand.number in parentNumbers:
                    continue
                # 保留的需求功能点就压入
                newDemandInfoList.append(demand)
            return newDemandInfoList


demandInfoService = DemandInfoService()
