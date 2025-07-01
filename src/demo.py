import asyncio
import logging
import os
import uuid
from datetime import datetime
from dotenv import load_dotenv
from temporalio.client import Client
from src.models.order import (
    Order, Customer, Address, Product, PaymentMethod,
    OrderStatus, PaymentStatus, ShippingStatus
)
from src.workflows.order_processing import OrderProcessingWorkflow
from src.utils.json_encoder import serialize_for_temporal

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_sample_order(order_id: str = None) -> Order:
    if not order_id:
        order_id = f"ORD-{uuid.uuid4().hex[:8].upper()}"
    
    customer = Customer(
        id=f"CUST-{uuid.uuid4().hex[:6].upper()}",
        name="John Doe",
        email="john.doe@example.com",
        phone="+1-555-0123",
        address=Address(
            street="123 Main Street",
            city="New York",
            state="NY",
            zip_code="10001",
            country="USA"
        )
    )
    
    products = [
        Product(
            id="PROD-001",
            name="Wireless Headphones",
            price=99.99,
            quantity=2,
            sku="WH-001"
        ),
        Product(
            id="PROD-002",
            name="Smartphone Case",
            price=19.99,
            quantity=1,
            sku="SC-002"
        )
    ]
    
    payment_method = PaymentMethod(
        type="credit_card",
        last4="1234",
        expiry_month=12,
        expiry_year=2025
    )
    
    total_amount = sum(p.price * p.quantity for p in products)
    
    return Order(
        id=order_id,
        customer=customer,
        products=products,
        total_amount=total_amount,
        payment_method=payment_method
    )


def create_suspicious_order() -> Order:
    order = create_sample_order("ORD-SUSPICIOUS")
    order.customer.email = "test@test.com"
    order.total_amount = 5000.00
    order.products[0].quantity = 100
    return order


def create_inventory_issue_order() -> Order:
    order = create_sample_order("ORD-INVENTORY")
    order.products[0].sku = "OUT-OF-STOCK"
    return order


def create_payment_issue_order() -> Order:
    order = create_sample_order("ORD-PAYMENT")
    order.payment_method.expiry_year = 2020
    return order


async def run_demo():
    client = await Client.connect(
        os.getenv("TEMPORAL_HOST", "localhost:7233"),
        namespace=os.getenv("TEMPORAL_NAMESPACE", "default")
    )
    
    logger.info("Starting Multi-Agent E-commerce Order Processing Demo")
    logger.info("=" * 60)
    
    demo_orders = [
        ("Normal Order", create_sample_order()),
        ("Suspicious Order", create_suspicious_order()),
        ("Inventory Issue Order", create_inventory_issue_order()),
        ("Payment Issue Order", create_payment_issue_order())
    ]
    
    for order_name, order in demo_orders:
        logger.info(f"\nProcessing {order_name}")
        logger.info(f"   Order ID: {order.id}")
        logger.info(f"   Customer: {order.customer.name}")
        logger.info(f"   Amount: ${order.total_amount:.2f}")
        logger.info(f"   Products: {[f'{p.name} x{p.quantity}' for p in order.products]}")
        
        try:
            result = await client.execute_workflow(
                OrderProcessingWorkflow.run,
                order.to_dict(),
                id=f"order-processing-{order.id}",
                task_queue=os.getenv("TEMPORAL_TASK_QUEUE", "ecommerce-order-processing")
            )
            
            logger.info(f"{order_name} Result: {result['status']}")
            if result.get('reason'):
                logger.info(f"   Reason: {result['reason']}")
            if result.get('tracking_number'):
                logger.info(f"   Tracking: {result['tracking_number']}")
                
        except Exception as e:
            logger.error(f"❌ {order_name} failed: {str(e)}")
        
        await asyncio.sleep(2)
    
    logger.info("\n" + "=" * 60)
    logger.info("Demo completed! Check Temporal UI for detailed workflow execution.")
    logger.info("Run 'temporal web' to view the Temporal UI")


if __name__ == "__main__":
    asyncio.run(run_demo()) 