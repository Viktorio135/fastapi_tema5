from sqlalchemy import Column, Integer, String, Date, DateTime, func, BigInteger
from sqlalchemy.ext.hybrid import hybrid_method


from .database import Base


class SpimexTradingResults(Base):
    __tablename__ = 'spimex_trading_results'
    id = Column(Integer, primary_key=True, index=True)
    exchange_product_id = Column(String)
    exchange_product_name = Column(String)
    delivery_basis_name = Column(String)
    volume = Column(Integer)
    total = Column(BigInteger)
    count = Column(Integer)
    date = Column(Date)
    created_on = Column(DateTime, server_default=func.now())
    updated_on = Column(DateTime, onupdate=func.now())

    @hybrid_method
    def oil_id(self):
        return self.exchange_product_id[:4]

    @oil_id.expression
    @classmethod
    def oil_id(cls):
        return func.substring(cls.exchange_product_id, 1, 4)

    @hybrid_method
    def delivery_basis_id(self):
        return self.exchange_product_id[4:7]

    @delivery_basis_id.expression
    @classmethod
    def delivery_basis_id(cls):
        return func.substring(cls.exchange_product_id, 5, 3)

    @hybrid_method
    def delivery_type_id(self):
        return self.exchange_product_id[-1]

    @delivery_type_id.expression
    @classmethod
    def delivery_type_id(cls):
        return func.right(cls.exchange_product_id, 1)
