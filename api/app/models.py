from pydantic import BaseModel, Field


class OrderItemIn(BaseModel):
    sku: str = Field(..., examples=["AUD-0024"])
    quantity: int = Field(..., gt=0, le=100, examples=[1])


class OrderIn(BaseModel):
    customer_email: str = Field(..., examples=["alice@example.com"])
    items: list[OrderItemIn] = Field(..., min_length=1)
