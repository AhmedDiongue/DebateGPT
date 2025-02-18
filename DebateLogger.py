import traceback
import datetime
import json
import logging
from typing import Any, Dict
from pathlib import Path
from debate_evaluation import EvaluationCriteria


# Logger for Debate
class DebateLogger:
    def __init__(self, log_file="debate_logs.ndjson", max_file_size_mb=10):
        self.log_file = Path(log_file)
        self.max_file_size = max_file_size_mb * 1024 * 1024
        self.setup_logging()

    def setup_logging(self):
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger('DebateSystem')

    def rotate_log_if_needed(self):
        if self.log_file.exists() and self.log_file.stat().st_size > self.max_file_size:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            new_name = self.log_file.with_name(f"{self.log_file.stem}_{timestamp}{self.log_file.suffix}")
            self.log_file.rename(new_name)

    def write_entry(self, entry: Dict[str, Any]):
        self.rotate_log_if_needed()
        with open(self.log_file, "a") as f:
            f.write(json.dumps(entry) + "\n")
        self.logger.info(f"Logged entry of type: {entry.get('type', 'unknown')}")

    def log_query(self, prompt: str, response: str, metadata: Dict[str, Any] = None):
        entry = {
            "timestamp": datetime.datetime.now().isoformat(),
            "type": "query",
            "success": True,
            "prompt": prompt,
            "response": response,
            "metadata": metadata or {}
        }
        self.write_entry(entry)

    def log_error(self, prompt: str, error: Exception, metadata: Dict[str, Any] = None):
        entry = {
            "timestamp": datetime.datetime.now().isoformat(),
            "type": "error",
            "success": False,
            "prompt": prompt,
            "error_type": type(error).__name__,
            "error_message": str(error),
            "traceback": traceback.format_exc(),
            "metadata": metadata or {}
        }
        self.write_entry(entry)
        self.logger.error(f"Error occurred: {str(error)}")

    def log_evaluation(self, round_num: int, pro_eval: EvaluationCriteria, against_eval: EvaluationCriteria):
        """Log debate round evaluations"""
        entry = {
            "time": datetime.datetime.now().isoformat(),
            "type": "evaluation",
            "round": round_num,
            "pro_score": pro_eval.calculate_score(),
            "against_score": against_eval.calculate_score(),
            "pro_criteria": {
                "argument_coherence": pro_eval.argument_coherence.value,
                "evidence_quality": pro_eval.evidence_quality.value,
                # ... other criteria
            },
            "against_criteria": {
                "argument_coherence": against_eval.argument_coherence.value,
                "evidence_quality": against_eval.evidence_quality.value,
                # ... other criteria
            }
        }
        self.write_entry(entry)
