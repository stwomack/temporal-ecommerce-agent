import asyncio
from typing import Any, Dict
from agents import Agent, Runner, function_tool
from src.agents.base import BaseEcommerceAgent
from src.models.order import Order, FulfillmentResult, AgentDecision


@function_tool
def calculate_shipping_cost(weight: float, destination: str, shipping_method: str) -> str:
    import random
    base_cost = 10.0
    if weight > 5:
        base_cost += 5.0
    if "express" in shipping_method.lower():
        base_cost *= 2.5
    return f"Shipping cost: ${base_cost:.2f}"


@function_tool
def generate_tracking_number() -> str:
    import random
    import string
    prefix = "TRK"
    numbers = ''.join(random.choices(string.digits, k=10))
    return f"{prefix}{numbers}"


@function_tool
def check_shipping_availability(destination: str, shipping_method: str) -> str:
    import random
    unavailable_destinations = ["remote_island", "war_zone"]
    
    if any(zone in destination.lower() for zone in unavailable_destinations):
        return f"Shipping to {destination} not available with {shipping_method}"
    else:
        return f"Shipping to {destination} available with {shipping_method}"


@function_tool
def estimate_delivery_time(destination: str, shipping_method: str) -> str:
    import random
    if "express" in shipping_method.lower():
        days = random.randint(1, 3)
    else:
        days = random.randint(3, 7)
    return f"Estimated delivery: {days} business days"


class FulfillmentAgent(BaseEcommerceAgent):
    def __init__(self):
        instructions = """
        You are a Fulfillment Agent responsible for coordinating shipping and tracking.
        
        Your responsibilities:
        1. Calculate shipping costs
        2. Generate tracking numbers
        3. Check shipping availability
        4. Estimate delivery times
        5. Handle shipping exceptions
        
        Always provide accurate shipping information and handle edge cases gracefully.
        """
        super().__init__("Fulfillment Agent", instructions)
        self.agent.tools = [
            calculate_shipping_cost,
            generate_tracking_number,
            check_shipping_availability,
            estimate_delivery_time
        ]
    
    async def process(self, context: Dict[str, Any]) -> AgentDecision:
        order: Order = context["order"]
        
        shipping_address = f"{order.customer.address.street}, {order.customer.address.city}, {order.customer.address.state}"
        total_weight = sum(p.quantity * 0.5 for p in order.products)
        
        prompt = f"""
        Please process fulfillment for this order:
        
        Order ID: {order.id}
        Shipping Address: {shipping_address}
        Products: {[f"{p.name} x{p.quantity}" for p in order.products]}
        Total Weight: {total_weight:.1f} lbs
        
        Please:
        1. Check shipping availability to the destination
        2. Calculate shipping costs
        3. Generate a tracking number
        4. Estimate delivery time
        5. Determine the best shipping method
        
        Provide your decision: SHIP, HOLD, or ESCALATE
        """
        
        result = await Runner.run(self.agent, prompt)
        
        decision_text = result.final_output.lower()
        
        if "available" in decision_text and "ship" in decision_text:
            return self._create_decision(
                decision="SHIP",
                confidence=0.9,
                reasoning=result.final_output,
                next_action="create_shipment"
            )
        elif "not available" in decision_text or "unavailable" in decision_text:
            return self._create_decision(
                decision="ESCALATE",
                confidence=0.8,
                reasoning=result.final_output,
                next_action="escalate_to_customer_service",
                requires_human_intervention=True
            )
        else:
            return self._create_decision(
                decision="HOLD",
                confidence=0.7,
                reasoning=result.final_output,
                next_action="hold_for_review"
            ) 