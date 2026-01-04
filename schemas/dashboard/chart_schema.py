from pydantic import BaseModel
from typing import List

class DailySales(BaseModel):
    date: str
    amount: int

class ChartData(BaseModel):
    sales_history: List[DailySales]