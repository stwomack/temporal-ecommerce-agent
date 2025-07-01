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
async def process_order_intake(order_data: Dict[str, Any]) -> Dict[str, Any]:
    logger.info(f"Processing order intake for order {order_data['id']}")
    
    agent = OrderIntakeAgent()
    context = {"order": Order(**order_data)}
    
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
async def process_payment(order_data: Dict[str, Any], retry_count: int = 0) -> Dict[str, Any]:
    logger.info(f"Processing payment for order {order_data['id']} (retry {retry_count})")
    
    agent = PaymentAgent()
    context = {"order": Order(**order_data), "retry_count": retry_count}
    
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
async def process_fulfillment(order_data: Dict[str, Any]) -> Dict[str, Any]:
    logger.info(f"Processing fulfillment for order {order_data['id']}")
    
    agent = FulfillmentAgent()
    context = {"order": Order(**order_data)}
    
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
    order_data: Dict[str, Any],
    issue_type: str,
    escalation_reason: str
) -> Dict[str, Any]:
    logger.info(f"Handling customer service for order {order_data['id']}")
    
    agent = CustomerServiceAgent()
    context = {
        "order": Order(**order_data),
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
async def update_order_status(order_data: Dict[str, Any], status: OrderStatus) -> Dict[str, Any]:
    logger.info(f"Updating order {order_data['id']} status to {status}")
    
    order_data['status'] = status
    order_data['updated_at'] = datetime.now().isoformat()
    
    return order_data


@activity.defn
async def update_payment_status(order_data: Dict[str, Any], status: PaymentStatus) -> Dict[str, Any]:
    logger.info(f"Updating order {order_data['id']} payment status to {status}")
    
    order_data['payment_status'] = status
    order_data['updated_at'] = datetime.now().isoformat()
    
    return order_data


@activity.defn
async def update_shipping_status(order_data: Dict[str, Any], status: ShippingStatus) -> Dict[str, Any]:
    logger.info(f"Updating order {order_data['id']} shipping status to {status}")
    
    order_data['shipping_status'] = status
    order_data['updated_at'] = datetime.now().isoformat()
    
    return order_data


@activity.defn
async def send_notification(order_data: Dict[str, Any], message: str) -> None:
    logger.info(f"Sending notification for order {order_data['id']}: {message}")
    
    await asyncio.sleep(0.1)
    logger.info(f"Notification sent to {order_data['customer']['email']}: {message}")


@activity.defn
async def log_order_event(order_data: Dict[str, Any], event: str, details: str) -> None:
    logger.info(f"Order {order_data['id']} - {event}: {details}")
    
    await asyncio.sleep(0.1)
    logger.info(f"Event logged: {event} for order {order_data['id']}") 