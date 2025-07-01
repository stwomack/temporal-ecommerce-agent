import asyncio
import logging
from datetime import datetime
from typing import Dict, Any
from temporalio import activity
from src.agents.order_intake import OrderIntakeAgent
from src.agents.payment import PaymentAgent
from src.agents.fulfillment import FulfillmentAgent
from src.agents.customer_service import CustomerServiceAgent
from src.models.order import Order, OrderStatus, PaymentStatus, ShippingStatus

logger = logging.getLogger(__name__)


@activity.defn
async def process_order_intake(order: Order) -> Dict[str, Any]:
    logger.info(f"Processing order intake for order {order.id}")
    
    agent = OrderIntakeAgent()
    context = {"order": order}
    
    decision = await agent.process(context)
    
    logger.info(f"Order intake decision: {decision.decision} - {decision.reasoning}")
    
    return {
        "decision": decision.decision,
        "confidence": decision.confidence,
        "reasoning": decision.reasoning,
        "next_action": decision.next_action,
        "requires_human_intervention": decision.requires_human_intervention
    }


@activity.defn
async def process_payment(order: Order, retry_count: int = 0) -> Dict[str, Any]:
    logger.info(f"Processing payment for order {order.id} (retry {retry_count})")
    
    agent = PaymentAgent()
    context = {"order": order, "retry_count": retry_count}
    
    decision = await agent.process(context)
    
    logger.info(f"Payment decision: {decision.decision} - {decision.reasoning}")
    
    return {
        "decision": decision.decision,
        "confidence": decision.confidence,
        "reasoning": decision.reasoning,
        "next_action": decision.next_action,
        "requires_human_intervention": decision.requires_human_intervention,
        "retry_count": retry_count
    }


@activity.defn
async def process_fulfillment(order: Order) -> Dict[str, Any]:
    logger.info(f"Processing fulfillment for order {order.id}")
    
    agent = FulfillmentAgent()
    context = {"order": order}
    
    decision = await agent.process(context)
    
    logger.info(f"Fulfillment decision: {decision.decision} - {decision.reasoning}")
    
    return {
        "decision": decision.decision,
        "confidence": decision.confidence,
        "reasoning": decision.reasoning,
        "next_action": decision.next_action,
        "requires_human_intervention": decision.requires_human_intervention
    }


@activity.defn
async def handle_customer_service(
    order: Order,
    issue_type: str,
    escalation_reason: str
) -> Dict[str, Any]:
    logger.info(f"Handling customer service for order {order.id}")
    
    agent = CustomerServiceAgent()
    context = {
        "order": order,
        "issue_type": issue_type,
        "escalation_reason": escalation_reason
    }
    
    decision = await agent.process(context)
    
    logger.info(f"Customer service decision: {decision.decision} - {decision.reasoning}")
    
    return {
        "decision": decision.decision,
        "confidence": decision.confidence,
        "reasoning": decision.reasoning,
        "next_action": decision.next_action,
        "requires_human_intervention": decision.requires_human_intervention
    }


@activity.defn
async def update_order_status(order: Order, status: OrderStatus) -> Order:
    logger.info(f"Updating order {order.id} status to {status}")
    
    order.status = status
    order.updated_at = datetime.now()
    
    return order


@activity.defn
async def update_payment_status(order: Order, status: PaymentStatus) -> Order:
    logger.info(f"Updating order {order.id} payment status to {status}")
    
    order.payment_status = status
    order.updated_at = datetime.now()
    
    return order


@activity.defn
async def update_shipping_status(order: Order, status: ShippingStatus) -> Order:
    logger.info(f"Updating order {order.id} shipping status to {status}")
    
    order.shipping_status = status
    order.updated_at = datetime.now()
    
    return order


@activity.defn
async def send_notification(order: Order, message: str) -> None:
    logger.info(f"Sending notification for order {order.id}: {message}")
    
    await asyncio.sleep(0.1)
    logger.info(f"Notification sent to {order.customer.email}: {message}")


@activity.defn
async def log_order_event(order: Order, event: str, details: str) -> None:
    logger.info(f"Order {order.id} - {event}: {details}")
    
    await asyncio.sleep(0.1)
    logger.info(f"Event logged: {event} for order {order.id}") 