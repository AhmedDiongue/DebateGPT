from dataclasses import dataclass
from typing import Optional
import os


@dataclass
class DebateConfig:
    topic: str
    pro_position: str
    against_position: str
    agent1_id: str
    agent2_id: str
    rounds: int = 3
    model: str = "gpt-4"
    temperature: float = 0.7
    max_retries: int = 3
    retry_delay: int = 1
    max_tokens: int = 4000

    @staticmethod
    def get_default_persona() -> str:
        return """You are a logical, intellectually honest, and truth-seeking academic scholar. 
        A frequent and passionate debater, you are disciplined in rigorous reasoning. 
        Your expertise spans environmental science, economics, political philosophy, bioethics, and public policy. 
        You are strong-minded in your view, but you reject ideological bias in favor of evidence-based, nuanced discourse."""


class APIConfig:
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY not found in environment variables")