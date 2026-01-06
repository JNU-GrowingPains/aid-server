from pydantic import BaseModel

class DashboardStats(BaseModel):
    total_orders: int
    total_sales: int
    new_customers: int