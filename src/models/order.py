from datetime import datetime
from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, ConfigDict


class OrderStatus(str, Enum):
    PENDING = "pending"
    VALIDATED = "validated"
    PAYMENT_PROCESSING = "payment_processing"
    PAYMENT_COMPLETED = "payment_completed"
    PAYMENT_FAILED = "payment_failed"
    FULFILLMENT_PROCESSING = "fulfillment_processing"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"
    ESCALATED = "escalated"


class PaymentStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"


class ShippingStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    SHIPPED = "shipped"
    IN_TRANSIT = "in_transit"
    DELIVERED = "delivered"
    FAILED = "failed"


class Product(BaseModel):
    id: str
    name: str
    price: float
    quantity: int
    sku: str


class Address(BaseModel):
    street: str
    city: str
    state: str
    zip_code: str
    country: str


class Customer(BaseModel):
    id: str
    name: str
    email: str
    phone: Optional[str] = None
    address: Address


class PaymentMethod(BaseModel):
    type: str
    last4: str
    expiry_month: int
    expiry_year: int


class Order(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    id: str
    customer: Customer
    products: List[Product]
    total_amount: float
    status: OrderStatus = OrderStatus.PENDING
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    payment_status: PaymentStatus = PaymentStatus.PENDING
    shipping_status: ShippingStatus = ShippingStatus.PENDING
    payment_method: Optional[PaymentMethod] = None
    tracking_number: Optional[str] = None
    notes: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary without datetime fields."""
        data = self.model_dump()
        data.pop('created_at', None)
        data.pop('updated_at', None)
        return data


class OrderValidationResult(BaseModel):
    is_valid: bool
    errors: List[str] = []
    warnings: List[str] = []
    inventory_available: bool = True
    suggested_alternatives: List[Product] = []


class PaymentResult(BaseModel):
    success: bool
    transaction_id: Optional[str] = None
    error_message: Optional[str] = None
    retry_count: int = 0


class FulfillmentResult(BaseModel):
    success: bool
    tracking_number: Optional[str] = None
    shipping_cost: float = 0.0
    estimated_delivery: Optional[datetime] = None
    error_message: Optional[str] = None


class AgentDecision(BaseModel):
    agent_name: str
    decision: str
    confidence: float
    reasoning: str
    next_action: str
    requires_human_intervention: bool = False 