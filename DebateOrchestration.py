from typing import Generator, Dict, Any, List, Tuple
from dataclasses import dataclass
from DebateAgent import DebateAgent
from DebateFoundation import DebateFoundation
from DebateFoundation import DebateLogger
from config import DebateConfig
from debate_evaluation import EvaluationCriteria, ArgumentQuality


@dataclass
class DebateState:
    round_number: int
    status: str  # 'initializing', 'in_progress', 'completed', 'error'
    current_turn: str  # 'pro' or 'against'


class DebateModeration(DebateFoundation):
    def __init__(self, config: DebateConfig):
        super().__init__(config)
        self.config = config
        self.state = DebateState(
            round_number=0,
            status='initializing',
            current_turn='pro'
        )
        self.pro_agent = self._initialize_pro_agent()
        self.against_agent = self._initialize_against_agent()
        self.evaluations: List[Tuple[EvaluationCriteria, EvaluationCriteria]] = []

    def _initialize_pro_agent(self) -> DebateAgent:
        """Initialize the pro-position debate agent"""
        # Use self instead of creating a new foundation instance
        # since DebateModeration already has the concrete query_llm implementation

        # Gather context for pro position
        context_prompt = f"""Gather key information and evidence to support the position: {self.config.pro_position}
        Focus on factual data, research, and logical arguments."""
        context = self.query_llm(context_prompt)

        # Create agent config dict
        pro_config = {
            'agent_id': self.config.agent1_id,
            'foundation': self  # Pass self as the foundation
        }

        return DebateAgent(
            config=pro_config,
            memory=context,
            position=self.config.pro_position,
            persona=DebateConfig.get_default_persona()
        )

    def _initialize_against_agent(self) -> DebateAgent:
        """Initialize the against-position debate agent"""
        # Use self instead of creating a new foundation instance

        # Gather context for against position
        context_prompt = f"""Gather key information and evidence to support the position: {self.config.against_position}
        Focus on factual data, research, and logical arguments."""
        context = self.query_llm(context_prompt)

        # Create agent config dict
        against_config = {
            'agent_id': self.config.agent2_id,
            'foundation': self  # Pass self as the foundation
        }

        return DebateAgent(
            config=against_config,
            memory=context,
            position=self.config.against_position,
            persona=DebateConfig.get_default_persona()
        )

    def run_rounds(self) -> Generator[Dict[str, Any], None, None]:
        """Run the debate rounds with proper state management"""
        try:
            self.state.status = 'in_progress'

            # Opening arguments
            pro_opening = self.pro_agent.return_introduction(self.config.topic)
            against_opening = self.against_agent.return_introduction(
                self.config.topic,
                pro_opening
            )

            yield {
                'round': 0,
                'type': 'opening',
                'pro_argument': pro_opening,
                'against_argument': against_opening
            }

            # Rebuttal rounds
            for round_num in range(1, self.config.rounds + 1):
                self.state.round_number = round_num

                # Pro rebuttal
                self.state.current_turn = 'pro'
                pro_rebuttal = self.pro_agent.return_rebuttal(against_opening)

                # Against rebuttal
                self.state.current_turn = 'against'
                against_rebuttal = self.against_agent.return_rebuttal(pro_rebuttal)

                # Update for next round
                against_opening = against_rebuttal

                yield {
                    'round': round_num,
                    'type': 'rebuttal',
                    'pro_argument': pro_rebuttal,
                    'against_argument': against_rebuttal
                }

            self.state.status = 'completed'

        except Exception as error:
            self.state.status = 'error'
            self.logger.log_error(
                prompt="Debate round execution failed",
                error=error,
                metadata={"round": self.state.round_number}
            )
            raise

    def get_debate_state(self) -> DebateState:
        return self.state

    def conclusion(self) -> Dict[str, Any]:
        """Generate concluding arguments from both agents"""
        if self.state.status != 'completed':
            raise ValueError("Cannot generate conclusion before debate completion")

        pro_conclusion = self.pro_agent.return_conclusion()
        against_conclusion = self.against_agent.return_conclusion()

        return {
            'type': 'conclusion',
            'pro_argument': pro_conclusion,
            'against_argument': against_conclusion
        }

    def evaluate_round(self, pro_argument: str, against_argument: str) -> Tuple[EvaluationCriteria, EvaluationCriteria]:
        """Evaluate both arguments from a debate round"""
        evaluation_prompt = f"""
        Evaluate the following debate arguments according to these criteria:
        1. Logical Structure (coherence, evidence quality)
        2. Engagement Quality (relevance, counter-argument strength)
        3. Content Quality (factual accuracy, source credibility)
        4. Rhetorical Effectiveness (persuasiveness, clarity)
        5. Debate Ethics (intellectual honesty, fallacy avoidance)

        Rate each criterion from 1 (Poor) to 5 (Excellent).

        PRO ARGUMENT:
        {pro_argument}

        AGAINST ARGUMENT:
        {against_argument}
        """

        # Use self instead of creating a new foundation instance
        eval_response = self.query_llm(evaluation_prompt)

        pro_eval, against_eval = self._parse_evaluation(eval_response)
        self.evaluations.append((pro_eval, against_eval))

        return pro_eval, against_eval

    def query_llm(self, prompt, context=None):
        """
        Concrete implementation of LLM query method
        Args:
            prompt (str): The prompt to send to the LLM
            context (str, optional): Additional context for the prompt
        Returns:
            str: The LLM response
        """
        # This is a simple example using OpenAI - adjust based on your actual LLM integration
        try:
            from openai import OpenAI
            client = OpenAI()

            full_prompt = prompt
            if context:
                full_prompt = f"{context}\n\n{prompt}"

            response = client.chat.completions.create(
                model="gpt-4",  # or your preferred model
                messages=[
                    {"role": "user", "content": full_prompt}
                ]
            )
            return response.choices[0].message.content
        except Exception as e:
            raise Exception(f"Error querying LLM: {str(e)}")

    def _parse_evaluation(self, eval_response: str) -> Tuple[EvaluationCriteria, EvaluationCriteria]:
        """Parse LLM evaluation response into EvaluationCriteria objects"""
        try:
            # Expected format: ratings for each criterion (1-5) for both pro and against
            lines = eval_response.strip().split('\n')
            pro_ratings = []
            against_ratings = []

            for line in lines:
                if ':' not in line:
                    continue
                criterion, ratings = line.split(':')
                pro, against = map(int, ratings.strip().split())
                pro_ratings.append(ArgumentQuality(pro))
                against_ratings.append(ArgumentQuality(against))

            # Create EvaluationCriteria objects
            pro_eval = EvaluationCriteria(*pro_ratings[:10])  # Take first 10 ratings
            against_eval = EvaluationCriteria(*against_ratings[:10])  # Take first 10 ratings

            return pro_eval, against_eval

        except Exception as error:
            self.logger.log_error(
                prompt="Failed to parse evaluation response",
                error=error,
                metadata={"response": eval_response}
            )
            # Return default evaluations if parsing fails
            default_rating = ArgumentQuality.SATISFACTORY
            default_criteria = [default_rating] * 10
            return (
                EvaluationCriteria(*default_criteria),
                EvaluationCriteria(*default_criteria)
            )








