from sqlalchemy import Column, Integer, String, DateTime, Float
import datetime
from base import Base

class SellOrder(Base):
    __tablename__ = 'sell_order'

    id_db = Column(Integer, primary_key=True)
    seller_id = Column(String(50), nullable=False)
    broker_id = Column(String(50), nullable=False)
    share_price = Column(Float, nullable=False)
    amount = Column(Integer, nullable=False)
    sale_date = Column(String(100), nullable=False)
    trace_id = Column(String(250), nullable=False)

    def __init__(self, seller_id, broker_id, share_price, amount, trace_id):
        self.seller_id = seller_id
        self.broker_id = broker_id
        self.share_price = share_price
        self.amount = amount
        self.sale_date = datetime.datetime.now()
        self.trace_id = trace_id
        pass

    def to_dict(self):
        sell_order_dict = {
            'seller_id': self.seller_id,
            'broker_id': self.broker_id,
            'share_price': self.share_price,
            'amount': self.amount,
            'sale_date': self.sale_date,
            'trace_id': self.trace_id

        }
        return sell_order_dict