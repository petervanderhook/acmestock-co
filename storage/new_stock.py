from sqlalchemy import Column, Integer, String, DateTime, Float
import datetime
from base import Base

class Stock(Base):
    __tablename__ = 'stock'

    id_db = Column(Integer, primary_key=True)
    company = Column(String(50), nullable=False)
    listing_id = Column(String(250), nullable=False)
    share_price = Column(Float, nullable=False)
    total_shares_available = Column(Integer, nullable=False)
    listing_date = Column(String(100), nullable=False)
    trace_id = Column(String(250), nullable=False)

    def __init__(self, company, listing_id, share_price, total_shares_available, trace_id):
        self.company = company
        self.listing_id = listing_id
        self.share_price = share_price
        self.total_shares_available = total_shares_available
        self.listing_date = datetime.datetime.now()
        self.trace_id = trace_id
        pass

    def to_dict(self):
        new_stock_dict = {
            'company': self.company,
            'listing_id': self.listing_id,
            'share_price': self.share_price,
            'total_shares_available': self.total_shares_available,
            'listing_date': self.listing_date,
            'trace_id': self.trace_id
        }
        return new_stock_dict