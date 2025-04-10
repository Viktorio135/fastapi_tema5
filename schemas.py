from pydantic import BaseModel, computed_field, Field
from datetime import date, datetime
from typing import Optional


class SpimexTradingBase(BaseModel):
    exchange_product_id: str
    exchange_product_name: str
    delivery_basis_name: str
    volume: int
    total: int
    count: int
    date: date


class SpimexTradingResponse(SpimexTradingBase):
    id: int
    created_on: datetime
    updated_on: Optional[datetime]

    @computed_field
    def oil_id(self) -> str:
        return self.exchange_product_id[:4]

    @computed_field
    def delivery_basis_id(self) -> str:
        return self.exchange_product_id[4:7]

    @computed_field
    def delivery_type_id(self) -> str:
        return self.exchange_product_id[-1]

    class Config:
        from_attributes = True


# class TradingDateResponse(BaseModel):
#     date: date

#     class Config:
#         from_attributes = True


class GetDynamicsFilters(BaseModel):
    oil_id: Optional[str] = Field(None, max_length=4)
    delivery_type_id: Optional[str] = Field(None, max_length=1)
    delivery_basis_id: Optional[str] = Field(None, max_digits=3)
    start_date: date
    end_date: date


class GetTradingResults(BaseModel):
    oil_id: Optional[str] = Field(None, max_length=4)
    delivery_type_id: Optional[str] = Field(None, max_length=1)
    delivery_basis_id: Optional[str] = Field(None, max_digits=3)
