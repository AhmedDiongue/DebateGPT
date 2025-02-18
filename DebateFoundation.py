from openai import OpenAI
from tenacity import retry, stop_after_attempt, wait_exponential
from typing import Optional, Dict, Any
import time
from config import APIConfig, DebateConfig
from DebateLogger import DebateLogger
import json
import os
from dotenv import load_dotenv

# Load the .env file
load_dotenv()


class DebateFoundation:
    def __init__(self, config: DebateConfig):
        # Initialize OpenAI API and logger
        self.api = OpenAI(api_key=APIConfig().api_key)
        self.logger = DebateLogger()
        self.config = config

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    def query_llm(self, prompt: str, context: Optional[str] = None) -> Optional[str]:
        """
        Query the LLM with retry logic and proper error handling
        """
        try:
            messages = []
            if context:
                messages.append({"role": "system", "content": context})
            messages.append({"role": "user", "content": prompt})

            llm_response = self.api.chat.completions.create(
                model=self.config.model,
                messages=messages,
                temperature=self.config.temperature,
                max_tokens=self.config.max_tokens,
                stream=False
            )

            content = llm_response.choices[0].message.content
            self.logger.log_query(
                prompt=prompt,
                response=content,
                metadata={
                    "model": self.config.model,
                    "temperature": self.config.temperature,
                    "max_tokens": self.config.max_tokens
                }
            )
            return content

        except Exception as e:
            self.logger.log_error(
                prompt=prompt,
                error=e,
                metadata={"context": context if context else "No context provided"}
            )
            raise

    def fact_check(self, argument: str) -> Dict[str, Any]:
        """Verify factual claims in an argument"""
        fact_check_prompt = f"""
        Analyze the following argument for factual claims:
        {argument}

        For each claim:
        1. Identify the specific claim
        2. Rate confidence (1-5) in its accuracy
        3. Provide supporting or contradicting evidence
        4. Note any context or nuance needed

        Format response as JSON with fields:
        - claims: list of identified claims
        - confidence_scores: corresponding confidence ratings
        - evidence: supporting/contradicting evidence
        - context_notes: additional context or nuance
        """

        llm_result = self.query_llm(fact_check_prompt)
        try:
            return json.loads(llm_result)
        except json.JSONDecodeError as e:
            self.logger.log_error(
                prompt="Failed to parse fact check response",
                error=e,
                metadata={"failed_response": llm_result}
            )
            return {"error": "Failed to parse fact check response"}


if __name__ == "__main__":
    config = DebateConfig(
        topic="Test topic",
        pro_position="Test pro",
        against_position="Test against",
        agent1_id="Test1",
        agent2_id="Test2"
    )
    test = DebateFoundation(config)
    prompt = "Tell me the ten hottest peppers on the planet and what regions they are native to."
    response = test.query_llm(prompt)
    print(response) 
