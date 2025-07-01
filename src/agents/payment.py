import asyncio
from typing import Any, Dict
from agents import Agent, Runner, function_tool
from src.agents.base import BaseEcommerceAgent
from src.models.order import Order, PaymentResult, AgentDecision


@function_tool
def process_payment(amount: float, payment_method: str, card_last4: str) -> str:
    import random
    success_rate = 0.85
    if random.random() < success_rate:
        transaction_id = f"TXN{random.randint(100000, 999999)}"
        return f"Payment successful. Transaction ID: {transaction_id}"
    else:
        return "Payment failed: Insufficient funds or card declined"


@function_tool
def validate_payment_method(card_last4: str, expiry_month: int, expiry_year: int) -> str:
    import random
    if expiry_year > 2024 and 1 <= expiry_month <= 12:
        return f"Payment method {card_last4} is valid"
    else:
        return f"Payment method {card_last4} is expired or invalid"


@function_tool
def check_fraud_risk(amount: float, customer_email: str, shipping_address: str) -> str:
    import random
    risk_factors = []
    
    if amount > 1000:
        risk_factors.append("High value transaction")
    if "test" in customer_email.lower():
        risk_factors.append("Suspicious email pattern")
    if len(shipping_address) < 20:
        risk_factors.append("Incomplete address")
    
    if risk_factors:
        return f"Fraud risk detected: {', '.join(risk_factors)}"
    else:
        return "Low fraud risk"


class PaymentAgent(BaseEcommerceAgent):
    def __init__(self):
        instructions = """
        You are a Payment Processing Agent responsible for handling e-commerce payments.
        
        Your responsibilities:
        1. Validate payment methods
        2. Process payments with retry logic
        3. Assess fraud risk
        4. Handle payment failures gracefully
        
        Always prioritize security and customer experience. If payment fails multiple times, escalate to customer service.
        """
        super().__init__("Payment Agent", instructions)
        self.agent.tools = [process_payment, validate_payment_method, check_fraud_risk]
    
    async def process(self, context: Dict[str, Any]) -> AgentDecision:
        order: Order = context["order"]
        retry_count = context.get("retry_count", 0)
        
        if not order.payment_method:
            return self._create_decision(
                decision="FAILED",
                confidence=1.0,
                reasoning="No payment method provided",
                next_action="escalate_to_customer_service",
                requires_human_intervention=True
            )
        
        prompt = f"""
        Please process this payment:
        
        Order ID: {order.id}
        Amount: ${order.total_amount}
        Payment Method: {order.payment_method.type} ending in {order.payment_method.last4}
        Retry Count: {retry_count}
        
        Please:
        1. Validate the payment method
        2. Check for fraud risk
        3. Process the payment
        4. If this is a retry (retry_count > 0), be more cautious
        
        Provide your decision: APPROVE, RETRY, or ESCALATE
        """
        
        result = await Runner.run(self.agent, prompt)
        
        decision_text = result.final_output.lower()
        
        if "successful" in decision_text and "approve" in decision_text:
            return self._create_decision(
                decision="APPROVE",
                confidence=0.95,
                reasoning=result.final_output,
                next_action="proceed_to_fulfillment"
            )
        elif "retry" in decision_text and retry_count < 3:
            return self._create_decision(
                decision="RETRY",
                confidence=0.7,
                reasoning=result.final_output,
                next_action="retry_payment"
            )
        else:
            return self._create_decision(
                decision="ESCALATE",
                confidence=0.8,
                reasoning=result.final_output,
                next_action="escalate_to_customer_service",
                requires_human_intervention=True
            ) 