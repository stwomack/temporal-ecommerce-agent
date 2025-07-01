import asyncio
from typing import Any, Dict
from agents import Agent, Runner, function_tool
from src.agents.base import BaseEcommerceAgent
from src.models.order import Order, OrderValidationResult, AgentDecision


@function_tool
def check_inventory(product_sku: str, quantity: int) -> str:
    import random
    available = random.randint(0, 10)
    if available >= quantity:
        return f"Inventory available: {available} units of {product_sku}"
    else:
        return f"Insufficient inventory: {available} available, {quantity} requested for {product_sku}"


@function_tool
def validate_customer_email(email: str) -> str:
    if "@" in email and "." in email.split("@")[1]:
        return f"Email {email} is valid"
    else:
        return f"Email {email} is invalid"


@function_tool
def validate_address(address: str) -> str:
    if len(address) > 10:
        return f"Address {address} appears valid"
    else:
        return f"Address {address} appears incomplete"


class OrderIntakeAgent(BaseEcommerceAgent):
    def __init__(self):
        instructions = """
        You are an Order Intake Agent responsible for validating e-commerce orders.
        
        Your responsibilities:
        1. Validate customer information (email, address)
        2. Check product inventory availability
        3. Verify order completeness and pricing
        4. Identify potential issues or fraud indicators
        
        Always be thorough and cautious. If you detect any issues, escalate to customer service.
        """
        super().__init__("Order Intake Agent", instructions)
        self.agent.tools = [check_inventory, validate_customer_email, validate_address]
    
    async def process(self, context: Dict[str, Any]) -> AgentDecision:
        order: Order = context["order"]
        
        prompt = f"""
        Please validate this order:
        
        Order ID: {order.id}
        Customer: {order.customer.name} ({order.customer.email})
        Address: {order.customer.address.street}, {order.customer.address.city}
        Products: {[f"{p.name} x{p.quantity}" for p in order.products]}
        Total Amount: ${order.total_amount}
        
        Please check:
        1. Customer email validity
        2. Address completeness
        3. Inventory availability for each product
        4. Any suspicious patterns (high value, unusual quantities, etc.)
        
        Provide your decision: APPROVE, REJECT, or ESCALATE
        """
        
        result = await Runner.run(self.agent, prompt)
        
        decision_text = result.final_output.lower()
        
        if "approve" in decision_text:
            return self._create_decision(
                decision="APPROVE",
                confidence=0.9,
                reasoning=result.final_output,
                next_action="proceed_to_payment"
            )
        elif "escalate" in decision_text or "suspicious" in decision_text:
            return self._create_decision(
                decision="ESCALATE",
                confidence=0.8,
                reasoning=result.final_output,
                next_action="escalate_to_customer_service",
                requires_human_intervention=True
            )
        else:
            return self._create_decision(
                decision="REJECT",
                confidence=0.7,
                reasoning=result.final_output,
                next_action="reject_order"
            ) 