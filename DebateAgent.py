from dataclasses import dataclass
from typing import List, Dict, Optional, Any
from DebateFoundation import DebateFoundation
from debate_evaluation import EvaluationCriteria, ArgumentQuality
import json


@dataclass
class Argument:
    content: str
    round_number: int
    argument_type: str  # 'introduction', 'rebuttal', 'conclusion'


@dataclass
class ArgumentAnalysis:
    content: str
    key_points: List[str]
    evidence_used: List[str]
    response_to: Optional[List[str]]  # Points being responded to
    fact_check_results: Dict[str, Any]
    evaluation: Optional[EvaluationCriteria]


class DebateAgent:
    def __init__(self, config: Dict, memory: str, position: str, persona: str):
        self.config = config
        self.agentid = config['agent_id']
        self.context = memory
        self.position = position
        self.persona = persona
        self.foundation = config['foundation']  # This is the DebateModeration instance
        self.argument_history: List[Argument] = []
        self.opponent_arguments: List[Argument] = []
        self.argument_analysis: List[ArgumentAnalysis] = []

    def _create_system_prompt(self) -> str:
        return f"""You are a debate agent with the following characteristics:
        - Position: {self.position}
        - Persona: {self.persona}

        Guidelines:
        1. Stay focused on the topic
        2. Use evidence-based reasoning
        3. Address opponent's arguments directly
        4. Maintain logical consistency
        5. Avoid logical fallacies
        6. Be respectful while being assertive
        """

    def _manage_context(self):
        """Maintain relevant context while preventing token overflow"""
        context_summary_prompt = f"""
        Summarize the key points and evidence from the following debate history,
        maintaining crucial information for the ongoing discussion:

        Previous Arguments: {self.argument_history}
        Opponent Arguments: {self.opponent_arguments}
        """

        return self.foundation.query_llm(context_summary_prompt)

    def _format_argument_prompt(self, task: str, opponent_argument: Optional[str] = None):
        # Update context periodically
        if len(self.argument_history) % 2 == 0:
            self.context = self._manage_context()

        prompt_parts = [
            "=== DEBATE FRAMEWORK ===",
            self._create_system_prompt(),
            f"\n=== CONTEXT ===\n{self.context}",
        ]

        if opponent_argument:
            prompt_parts.append(f"\n=== OPPONENT'S ARGUMENT ===\n{opponent_argument}")

        if self.argument_history:
            prompt_parts.append("\n=== PREVIOUS ARGUMENTS ===")
            for arg in self.argument_history[-2:]:  # Only include last 2 arguments
                prompt_parts.append(f"Round {arg.round_number}: {arg.content}")

        prompt_parts.append(f"\n=== TASK ===\n{task}")

        return "\n".join(prompt_parts)

    def return_introduction(self, topic: str, opponent_argument: Optional[str] = None) -> str:
        task = f"Create a compelling opening argument for the topic: {topic}"
        prompt = self._format_argument_prompt(task, opponent_argument)

        response = self.foundation.query_llm(prompt)
        if response:
            argument = Argument(
                content=response,
                round_number=0,
                argument_type='introduction'
            )
            self.argument_history.append(argument)
            return response
        return "Failed to generate introduction"

    def return_rebuttal(self, opponent_argument: str) -> str:
        """Generate a rebuttal to the opponent's argument"""
        current_round = len(self.argument_history)

        # Store opponent's argument
        opponent_arg = Argument(
            content=opponent_argument,
            round_number=current_round,
            argument_type='opponent_argument'
        )
        self.opponent_arguments.append(opponent_arg)

        task = f"""Create a compelling rebuttal to your opponent's argument. Your rebuttal should:
        1. Address the key points of their argument
        2. Identify any logical flaws or unsupported claims
        3. Present counter-evidence where appropriate
        4. Strengthen your position on {self.position}

        Keep your response focused and limited to two paragraphs."""

        prompt = self._format_argument_prompt(task, opponent_argument)
        response = self.foundation.query_llm(prompt)

        if response:
            argument = Argument(
                content=response,
                round_number=current_round,
                argument_type='rebuttal'
            )
            self.argument_history.append(argument)

            # Evaluate the argument
            evaluation = self._evaluate_argument(response, self.context)

            # If quality is below threshold, regenerate
            if evaluation.calculate_score() < 3.5:
                improved_prompt = self._generate_improved_prompt(evaluation)
                response = self.foundation.query_llm(improved_prompt)

            return response
        return "Failed to generate rebuttal"

    def return_conclusion(self) -> str:
        """Generate a concluding argument"""
        task = f"""Create a powerful concluding argument for your position: {self.position}

        Your conclusion should:
        1. Summarize your key arguments
        2. Address how you've countered opponent's main points
        3. Provide a compelling final perspective
        4. Demonstrate why your position is the most reasonable

        Limit your response to three paragraphs."""

        prompt = self._format_argument_prompt(task)
        response = self.foundation.query_llm(prompt)

        if response:
            argument = Argument(
                content=response,
                round_number=len(self.argument_history),
                argument_type='conclusion'
            )
            self.argument_history.append(argument)
            return response
        return "Failed to generate conclusion"

    def _evaluate_argument(self, argument: str, context: str = None) -> EvaluationCriteria:
        """
        Evaluate the quality of an argument
        Args:
            argument (str): The argument to evaluate
            context (str, optional): Additional context for evaluation
        Returns:
            EvaluationCriteria: Quality assessment of the argument
        """
        evaluation_prompt = f"""
        Evaluate this debate argument and rate each criterion from 1 (POOR) to 5 (EXCELLENT):

        1. Argument coherence
        2. Evidence quality
        3. Rebuttal relevance
        4. Counter-argument strength
        5. Factual accuracy
        6. Persuasiveness
        7. Clarity
        8. Intellectual honesty
        9. Fallacy avoidance

        Provide ratings in JSON format like:
        {{
            "argument_coherence": 5,
            "evidence_quality": 4,
            "rebuttal_relevance": 4,
            "counter_argument_strength": 3,
            "factual_accuracy": 5,
            "persuasiveness": 4,
            "clarity": 5,
            "intellectual_honesty": 4,
            "fallacy_avoidance": 4
        }}

        Argument to evaluate:
        {argument}

        Context:
        {context if context else 'No additional context provided'}
        """

        # Use the foundation (DebateModeration) instance directly
        eval_response = self.foundation.query_llm(evaluation_prompt)

        try:
            ratings = json.loads(eval_response)
            return EvaluationCriteria(
                argument_coherence=ArgumentQuality(ratings['argument_coherence']),
                evidence_quality=ArgumentQuality(ratings['evidence_quality']),
                rebuttal_relevance=ArgumentQuality(ratings['rebuttal_relevance']),
                counter_argument_strength=ArgumentQuality(ratings['counter_argument_strength']),
                factual_accuracy=ArgumentQuality(ratings['factual_accuracy']),
                persuasiveness=ArgumentQuality(ratings['persuasiveness']),
                clarity=ArgumentQuality(ratings['clarity']),
                intellectual_honesty=ArgumentQuality(ratings['intellectual_honesty']),
                fallacy_avoidance=ArgumentQuality(ratings['fallacy_avoidance']),
                source_credibility=ArgumentQuality(ratings['source_credibility'])
            )
        except (json.JSONDecodeError, KeyError) as e:
            self.foundation.logger.log_error(f"Failed to parse evaluation response: {str(e)}")
            # Return default evaluation with all criteria set to SATISFACTORY
            return EvaluationCriteria(
                *[ArgumentQuality.SATISFACTORY] * 9  # Creates 9 SATISFACTORY ratings
            )

    def _generate_improved_prompt(self, evaluation: EvaluationCriteria) -> str:
        # Implementation of _generate_improved_prompt method
        # This method should return a prompt to regenerate the rebuttal
        pass

    def analyze_argument(self, argument: str, responding_to: Optional[str] = None) -> ArgumentAnalysis:
        """Analyze an argument for key points and evidence"""
        analysis_prompt = f"""
        Analyze this argument:
        {argument}

        Extract:
        1. Key points made
        2. Evidence/sources cited
        3. Main claims that need verification
        """

        analysis = self.foundation.query_llm(analysis_prompt)
        fact_check = self.foundation.fact_check(argument)

        # Parse response and create ArgumentAnalysis
        key_points = self._extract_key_points(analysis)
        evidence = self._extract_evidence(analysis)
        response_points = self._extract_response_points(analysis, responding_to) if responding_to else None

        return ArgumentAnalysis(
            content=argument,
            key_points=key_points,
            evidence_used=evidence,
            response_to=response_points,
            fact_check_results=fact_check,
            evaluation=None  # Will be set by moderator
        )

    def _extract_key_points(self, analysis: str) -> List[str]:
        """Extract key points from analysis text"""
        try:
            # Look for key points section in the analysis
            points_start = analysis.find("Key points made:")
            if points_start == -1:
                return []

            # Find the next section or end of text
            next_section = analysis.find("\n\n", points_start)
            if next_section == -1:
                points_text = analysis[points_start:]
            else:
                points_text = analysis[points_start:next_section]

            # Split into individual points and clean up
            points = [
                point.strip().lstrip("*-•").strip()
                for point in points_text.split("\n")[1:]  # Skip the header line
                if point.strip()
            ]
            return points
        except Exception as e:
            self.foundation.logger.log_error(f"Failed to extract key points: {str(e)}")
            return []

    def _extract_evidence(self, analysis: str) -> List[str]:
        """Extract evidence/sources from analysis text"""
        try:
            # Look for evidence section in the analysis
            evidence_start = analysis.find("Evidence/sources cited:")
            if evidence_start == -1:
                return []

            # Find the next section or end of text
            next_section = analysis.find("\n\n", evidence_start)
            if next_section == -1:
                evidence_text = analysis[evidence_start:]
            else:
                evidence_text = analysis[evidence_start:next_section]

            # Split into individual pieces of evidence and clean up
            evidence = [
                ev.strip().lstrip("*-•").strip()
                for ev in evidence_text.split("\n")[1:]  # Skip the header line
                if ev.strip()
            ]
            return evidence
        except Exception as e:
            self.foundation.logger.log_error(f"Failed to extract evidence: {str(e)}")
            return []

    def _extract_response_points(self, analysis: str, responding_to: Optional[str]) -> Optional[List[str]]:
        """Extract points that respond to opponent's arguments"""
        if not responding_to:
            return None

        try:
            # Look for response points in the analysis
            response_start = analysis.find("Response to opponent:")
            if response_start == -1:
                return None

            # Find the next section or end of text
            next_section = analysis.find("\n\n", response_start)
            if next_section == -1:
                response_text = analysis[response_start:]
            else:
                response_text = analysis[response_start:next_section]

            # Split into individual response points and clean up
            responses = [
                resp.strip().lstrip("*-•").strip()
                for resp in response_text.split("\n")[1:]  # Skip the header line
                if resp.strip()
            ]
            return responses
        except Exception as e:
            self.foundation.logger.log_error(f"Failed to extract response points: {str(e)}")
            return None
