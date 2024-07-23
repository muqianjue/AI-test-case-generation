from sqlalchemy import create_engine, Column, String, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()


class DemandInfo(Base):
    __tablename__ = 'atcg_demand_info'

    id = Column(String(64), primary_key=True)
    batch_id = Column(String(64), nullable=False)
    title = Column(String(64))
    parent = Column(String(64))
    start_index = Column(String(64))
    end_index = Column(String(64))
    content = Column(Text)
    number = Column(String(64))
    parent_number = Column(String(64))

    def __repr__(self):
        return (f"<DemandInfo(id='{self.id}', batch_id='{self.batch_id}', title='{self.title}', "
                f"parent='{self.parent}', start_index='{self.start_index}', end_index='{self.end_index}', "
                f"content='{self.content}', number='{self.number}', parent_number='{self.parent_number}')>")

DATABASE_URL = "mysql+pymysql://root:password@localhost:3306/atcg"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class DemandInfoMapper:
    def __init__(self, db):
        self.db = db

    def insert_demand_info(self, demand_info):
        self.db.add(demand_info)
        self.db.commit()

    def update_demand_info(self, demand_info):
        self.db.merge(demand_info)
        self.db.commit()

    def delete_demand_info(self, id):
        demand_info = self.db.query(DemandInfo).filter(DemandInfo.id == id).first()
        if demand_info:
            self.db.delete(demand_info)
            self.db.commit()

    def get_demand_info_by_id(self, id):
        return self.db.query(DemandInfo).filter(DemandInfo.id == id).first()

    def get_demand_info_by_batch_id(self, batch_id):
        return self.db.query(DemandInfo).filter(DemandInfo.batch_id == batch_id).all()

    def get_all(self):
        return self.db.query(DemandInfo).all()
