import asyncio
import logging
from datetime import timedelta
from typing import Dict, Any
from temporalio import workflow
from temporalio.common import RetryPolicy
from src.activities.order_activities import (
    process_order_intake,
    process_payment,
    process_fulfillment,
    handle_customer_service,
    update_order_status,
    update_payment_status,
    update_shipping_status,
    send_notification,
    log_order_event
)
from src.models.order import Order, OrderStatus, PaymentStatus, ShippingStatus

logger = logging.getLogger(__name__)

with workflow.unsafe.imports_passed_through():
    from src.models.order import Order, OrderStatus, PaymentStatus, ShippingStatus


@workflow.defn
class OrderProcessingWorkflow:
    @workflow.run
    async def run(self, order: Order) -> Dict[str, Any]:
        logger.info(f"Starting order processing workflow for order {order.id}")
        
        await workflow.log_info(f"Processing order {order.id} for {order.customer.name}")
        
        try:
            await log_order_event(order, "workflow_started", "Order processing workflow initiated")
            
            order = await update_order_status(order, OrderStatus.PENDING)
            
            intake_result = await workflow.execute_activity(
                process_order_intake,
                order,
                start_to_close_timeout=timedelta(minutes=5)
            )
            
            if intake_result["decision"] == "REJECT":
                order = await update_order_status(order, OrderStatus.CANCELLED)
                await send_notification(order, "Order rejected: " + intake_result["reasoning"])
                await log_order_event(order, "order_rejected", intake_result["reasoning"])
                return {"status": "rejected", "reason": intake_result["reasoning"]}
            
            elif intake_result["decision"] == "ESCALATE":
                order = await update_order_status(order, OrderStatus.ESCALATED)
                await self._handle_escalation(order, "order_intake", intake_result["reasoning"])
                return {"status": "escalated", "reason": intake_result["reasoning"]}
            
            order = await update_order_status(order, OrderStatus.VALIDATED)
            await send_notification(order, "Order validated successfully")
            
            payment_result = await self._process_payment_with_retry(order)
            
            if payment_result["decision"] == "ESCALATE":
                order = await update_order_status(order, OrderStatus.ESCALATED)
                await self._handle_escalation(order, "payment", payment_result["reasoning"])
                return {"status": "escalated", "reason": payment_result["reasoning"]}
            
            order = await update_payment_status(order, PaymentStatus.COMPLETED)
            await send_notification(order, "Payment processed successfully")
            
            fulfillment_result = await workflow.execute_activity(
                process_fulfillment,
                order,
                start_to_close_timeout=timedelta(minutes=5)
            )
            
            if fulfillment_result["decision"] == "ESCALATE":
                order = await update_order_status(order, OrderStatus.ESCALATED)
                await self._handle_escalation(order, "fulfillment", fulfillment_result["reasoning"])
                return {"status": "escalated", "reason": fulfillment_result["reasoning"]}
            
            order = await update_shipping_status(order, ShippingStatus.SHIPPED)
            await send_notification(order, "Order shipped successfully")
            
            await log_order_event(order, "order_completed", "Order processing completed successfully")
            
            return {
                "status": "completed",
                "order_id": order.id,
                "tracking_number": order.tracking_number
            }
            
        except Exception as e:
            logger.error(f"Error processing order {order.id}: {str(e)}")
            await log_order_event(order, "workflow_error", str(e))
            await self._handle_escalation(order, "workflow_error", str(e))
            raise
    
    async def _process_payment_with_retry(self, order: Order) -> Dict[str, Any]:
        max_retries = 3
        retry_policy = RetryPolicy(
            initial_interval=timedelta(seconds=1),
            maximum_interval=timedelta(seconds=10),
            maximum_attempts=max_retries,
            non_retryable_error_types=["ValueError"]
        )
        
        for attempt in range(max_retries):
            try:
                payment_result = await workflow.execute_activity(
                    process_payment,
                    order,
                    attempt,
                    start_to_close_timeout=timedelta(minutes=5),
                    retry_policy=retry_policy
                )
                
                if payment_result["decision"] == "APPROVE":
                    return payment_result
                elif payment_result["decision"] == "RETRY" and attempt < max_retries - 1:
                    await workflow.log_info(f"Payment retry {attempt + 1} for order {order.id}")
                    await asyncio.sleep(2 ** attempt)
                    continue
                else:
                    return payment_result
                    
            except Exception as e:
                if attempt == max_retries - 1:
                    raise
                await workflow.log_warn(f"Payment attempt {attempt + 1} failed: {str(e)}")
        
        return {
            "decision": "ESCALATE",
            "reasoning": f"Payment failed after {max_retries} attempts",
            "requires_human_intervention": True
        }
    
    async def _handle_escalation(self, order: Order, issue_type: str, reason: str) -> None:
        await workflow.log_info(f"Escalating order {order.id} due to {issue_type}: {reason}")
        
        escalation_result = await workflow.execute_activity(
            handle_customer_service,
            order,
            issue_type,
            reason,
            start_to_close_timeout=timedelta(minutes=10)
        )
        
        await log_order_event(order, "escalation_handled", escalation_result["reasoning"])
        
        if escalation_result["decision"] == "CANCEL_ORDER":
            order = await update_order_status(order, OrderStatus.CANCELLED)
            await send_notification(order, "Order cancelled: " + escalation_result["reasoning"])
        elif escalation_result["requires_human_intervention"]:
            await send_notification(order, "Order requires human review: " + escalation_result["reasoning"]) 