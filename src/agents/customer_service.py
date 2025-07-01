import asyncio
from typing import Any, Dict
from agents import Agent, Runner, function_tool
from src.agents.base import BaseEcommerceAgent
from src.models.order import Order, AgentDecision


@function_tool
def create_support_ticket(order_id: str, issue_type: str, description: str) -> str:
    import random
    ticket_id = f"TKT{random.randint(100000, 999999)}"
    return f"Support ticket created: {ticket_id} for order {order_id}"


@function_tool
def check_customer_history(customer_email: str) -> str:
    import random
    order_count = random.randint(0, 10)
    if order_count > 5:
        return f"Customer {customer_email} has {order_count} previous orders - VIP customer"
    elif order_count > 0:
        return f"Customer {customer_email} has {order_count} previous orders - returning customer"
    else:
        return f"Customer {customer_email} has no previous orders - new customer"


@function_tool
def suggest_resolution(issue_type: str, order_amount: float) -> str:
    if issue_type == "payment_failed":
        return "Suggest alternative payment method or contact customer for updated card"
    elif issue_type == "inventory_unavailable":
        return "Offer similar products or suggest backorder with discount"
    elif issue_type == "shipping_unavailable":
        return "Suggest alternative shipping address or hold order for pickup"
    elif issue_type == "fraud_suspicion":
        return "Request additional verification or escalate to fraud team"
    else:
        return "Contact customer directly to resolve issue"


@function_tool
def calculate_refund_amount(order_amount: float, issue_type: str) -> str:
    if issue_type == "payment_failed":
        return f"No refund needed - payment was not processed"
    elif issue_type == "inventory_unavailable":
        return f"Full refund of ${order_amount:.2f} plus 10% compensation"
    else:
        return f"Partial refund of ${order_amount * 0.8:.2f}"


class CustomerServiceAgent(BaseEcommerceAgent):
    def __init__(self):
        instructions = """
        You are a Customer Service Agent responsible for handling escalated e-commerce issues.
        
        Your responsibilities:
        1. Create support tickets for issues
        2. Check customer history and status
        3. Suggest appropriate resolutions
        4. Calculate refunds when necessary
        5. Escalate to human agents when needed
        
        Always prioritize customer satisfaction while following company policies.
        """
        super().__init__("Customer Service Agent", instructions)
        self.agent.tools = [
            create_support_ticket,
            check_customer_history,
            suggest_resolution,
            calculate_refund_amount
        ]
    
    async def process(self, context: Dict[str, Any]) -> AgentDecision:
        order: Order = context["order"]
        issue_type = context.get("issue_type", "general")
        escalation_reason = context.get("escalation_reason", "Unknown issue")
        
        prompt = f"""
        Please handle this customer service escalation:
        
        Order ID: {order.id}
        Customer: {order.customer.name} ({order.customer.email})
        Issue Type: {issue_type}
        Escalation Reason: {escalation_reason}
        Order Amount: ${order.total_amount}
        
        Please:
        1. Check customer history
        2. Create a support ticket
        3. Suggest appropriate resolution
        4. Calculate refund if necessary
        5. Determine if human intervention is needed
        
        Provide your decision: RESOLVE, ESCALATE_TO_HUMAN, or CANCEL_ORDER
        """
        
        result = await Runner.run(self.agent, prompt)
        
        decision_text = result.final_output.lower()
        
        if "resolve" in decision_text and "human" not in decision_text:
            return self._create_decision(
                decision="RESOLVE",
                confidence=0.8,
                reasoning=result.final_output,
                next_action="apply_resolution"
            )
        elif "human" in decision_text or "escalate" in decision_text:
            return self._create_decision(
                decision="ESCALATE_TO_HUMAN",
                confidence=0.9,
                reasoning=result.final_output,
                next_action="assign_to_human_agent",
                requires_human_intervention=True
            )
        else:
            return self._create_decision(
                decision="CANCEL_ORDER",
                confidence=0.7,
                reasoning=result.final_output,
                next_action="cancel_and_refund"
            ) 