from typing import Any, Dict, Optional
from agents import Agent
from src.models.order import AgentDecision


class BaseEcommerceAgent:
    def __init__(self, name: str, instructions: str):
        self.name = name
        self.agent = Agent(name=name, instructions=instructions)
    
    async def process(self, context: Dict[str, Any]) -> AgentDecision:
        raise NotImplementedError("Subclasses must implement process method")
    
    def _create_decision(
        self,
        decision: str,
        confidence: float,
        reasoning: str,
        next_action: str,
        requires_human_intervention: bool = False
    ) -> AgentDecision:
        return AgentDecision(
            agent_name=self.name,
            decision=decision,
            confidence=confidence,
            reasoning=reasoning,
            next_action=next_action,
            requires_human_intervention=requires_human_intervention
        ) 