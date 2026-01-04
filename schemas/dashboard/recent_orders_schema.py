from pydantic import BaseModel
from datetime import datetime

class RecentOrder(BaseModel):
    order_no: int
    product_name: str
    created_at: datetime