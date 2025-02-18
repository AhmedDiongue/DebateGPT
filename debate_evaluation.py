from dataclasses import dataclass
from typing import List, Dict
from enum import Enum


class ArgumentQuality(Enum):
    EXCELLENT = 5
    GOOD = 4
    SATISFACTORY = 3
    NEEDS_IMPROVEMENT = 2
    POOR = 1


@dataclass
class EvaluationCriteria:
    # Logical Structure
    argument_coherence: ArgumentQuality  # How well-structured and logical is the argument
    evidence_quality: ArgumentQuality  # Quality and relevance of evidence used

    # Engagement Quality
    rebuttal_relevance: ArgumentQuality  # How well it addresses opponent's points
    counter_argument_strength: ArgumentQuality  # Effectiveness of counter-arguments

    # Content Quality
    factual_accuracy: ArgumentQuality  # Accuracy of presented facts
    source_credibility: ArgumentQuality  # Credibility of cited sources/evidence

    # Rhetorical Effectiveness
    persuasiveness: ArgumentQuality  # Overall persuasive impact
    clarity: ArgumentQuality  # Clarity of expression

    # Debate Ethics
    intellectual_honesty: ArgumentQuality  # Fairness in representing opposing views
    fallacy_avoidance: ArgumentQuality  # Avoidance of logical fallacies

    def calculate_score(self) -> float:
        total = sum(criteria.value for criteria in [
            self.argument_coherence,
            self.evidence_quality,
            self.rebuttal_relevance,
            self.counter_argument_strength,
            self.factual_accuracy,
            self.source_credibility,
            self.persuasiveness,
            self.clarity,
            self.intellectual_honesty,
            self.fallacy_avoidance
        ])
        return total / 10  # Average score out of 5