from pydantic import BaseModel
from typing import Optional, List, Any


class HealthResponse(BaseModel):
    status: str
    database: str
    db_path: str


class DashboardSummary(BaseModel):
    total_orders: int
    completed: int
    cancelled: int
    pending: int
    recorded_revenue: float
    missing_amounts: int
    missing_delivery: int
    total_customers: int
    total_products: int


class StatusCount(BaseModel):
    status: str
    count: int
    percentage: float


class MonthlyTrend(BaseModel):
    month: str
    orders: int


class TopProduct(BaseModel):
    product_name: str
    category: str
    order_count: int
    recorded_revenue: Optional[float]


class CityCount(BaseModel):
    city: str
    customers: int


class CategoryRevenue(BaseModel):
    category: str
    orders: int
    recorded_revenue: float
    avg_order: float


class OrderRecord(BaseModel):
    order_id: str
    customer_id: str
    product_id: str
    product_name: Optional[str]
    quantity: Optional[int]
    order_ts: Optional[str]
    status: str
    discount_pct: Optional[int]
    order_amount: Optional[float]
    delivery_minutes: Optional[float]


class OrdersResponse(BaseModel):
    data: List[OrderRecord]
    total: int
    page: int
    page_size: int
    total_pages: int


class ProductRecord(BaseModel):
    product_id: str
    product_name: str
    category: str
    price_inr: int
    order_count: int
    quantity_sold: int
    recorded_revenue: Optional[float]


class CustomerRecord(BaseModel):
    customer_id: str
    city: str
    age: Optional[int]
    gender: Optional[str]
    signup_date: Optional[str]
    order_count: int
    recorded_spend: Optional[float]


class DataQualitySummary(BaseModel):
    total_orders: int
    missing_amounts: int
    missing_amounts_pct: float
    missing_delivery: int
    missing_delivery_pct: float
    duplicate_order_ids: int
    orphan_customer_refs: int
    orphan_product_refs: int
    completed_missing_amount: int


class AssistantRequest(BaseModel):
    message: str


class AssistantResponse(BaseModel):
    answer: str
    data: Optional[List[Any]] = None
    columns: Optional[List[str]] = None
    supported: bool = True
