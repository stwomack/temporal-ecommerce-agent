import pytest
import asyncio
from src.agents.order_intake import OrderIntakeAgent
from src.agents.payment import PaymentAgent
from src.agents.fulfillment import FulfillmentAgent
from src.agents.customer_service import CustomerServiceAgent
from src.models.order import Order, Customer, Address, Product, PaymentMethod


@pytest.fixture
def sample_order():
    customer = Customer(
        id="CUST-001",
        name="Test Customer",
        email="test@example.com",
        address=Address(
            street="123 Test St",
            city="Test City",
            state="TS",
            zip_code="12345",
            country="USA"
        )
    )
    
    products = [
        Product(
            id="PROD-001",
            name="Test Product",
            price=50.00,
            quantity=1,
            sku="TEST-001"
        )
    ]
    
    payment_method = PaymentMethod(
        type="credit_card",
        last4="1234",
        expiry_month=12,
        expiry_year=2025
    )
    
    return Order(
        id="ORD-001",
        customer=customer,
        products=products,
        total_amount=50.00,
        payment_method=payment_method
    )


@pytest.mark.asyncio
async def test_order_intake_agent(sample_order):
    agent = OrderIntakeAgent()
    context = {"order": sample_order}
    
    decision = await agent.process(context)
    
    assert decision.agent_name == "Order Intake Agent"
    assert decision.decision in ["APPROVE", "REJECT", "ESCALATE"]
    assert 0 <= decision.confidence <= 1
    assert decision.reasoning is not None


@pytest.mark.asyncio
async def test_payment_agent(sample_order):
    agent = PaymentAgent()
    context = {"order": sample_order, "retry_count": 0}
    
    decision = await agent.process(context)
    
    assert decision.agent_name == "Payment Agent"
    assert decision.decision in ["APPROVE", "RETRY", "ESCALATE"]
    assert 0 <= decision.confidence <= 1
    assert decision.reasoning is not None


@pytest.mark.asyncio
async def test_fulfillment_agent(sample_order):
    agent = FulfillmentAgent()
    context = {"order": sample_order}
    
    decision = await agent.process(context)
    
    assert decision.agent_name == "Fulfillment Agent"
    assert decision.decision in ["SHIP", "HOLD", "ESCALATE"]
    assert 0 <= decision.confidence <= 1
    assert decision.reasoning is not None


@pytest.mark.asyncio
async def test_customer_service_agent(sample_order):
    agent = CustomerServiceAgent()
    context = {
        "order": sample_order,
        "issue_type": "payment_failed",
        "escalation_reason": "Payment declined"
    }
    
    decision = await agent.process(context)
    
    assert decision.agent_name == "Customer Service Agent"
    assert decision.decision in ["RESOLVE", "ESCALATE_TO_HUMAN", "CANCEL_ORDER"]
    assert 0 <= decision.confidence <= 1
    assert decision.reasoning is not None 