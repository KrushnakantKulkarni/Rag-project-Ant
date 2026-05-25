from typing import Any
from pydantic import BaseModel, Field, field_validator
from utils.logger import get_logger

logger = get_logger("utils.thresholds")

# Standard acceptable low confidence threshold
WARNING_THRESHOLD = 2

class ConfidenceSchema(BaseModel):
    """
    Pydantic schema representing step self-confidence scores.
    Features pre-validation type resilience to fall back gracefully on invalid formats.
    """
    score: int = Field(..., description="Self-assigned confidence integer between 1 and 5")
    justification: str = Field(..., description="Short justification explaining the assigned score")

    @field_validator("score", mode="before")
    @classmethod
    def validate_score(cls, v: Any) -> int:
        """
        Validates confidence score, ensuring it is a strict integer between 1 and 5.
        Translates strings (like "High", "90%") and invalid ranges to default 3.
        """
        if isinstance(v, int):
            if 1 <= v <= 5:
                return v
            logger.info(f"Confidence score {v} out of bounds (1-5). Falling back to default (3).")
            return 3
        if isinstance(v, str):
            try:
                import re
                match = re.search(r'\d+', v)
                if match:
                    val = int(match.group())
                    if 1 <= val <= 5:
                        return val
            except Exception:
                pass
            logger.info(f"Invalid string confidence score '{v}'. Falling back to default (3).")
        else:
            logger.info(f"Invalid type for confidence score '{type(v)}'. Falling back to default (3).")
        return 3

def check_confidence_threshold(step_name: str, score: int, justification: str) -> bool:
    """
    Checks if a step's confidence self-score falls below the warnings threshold.
    Logs a warning log entry if confidence is low, and returns True.
    Otherwise returns False.
    """
    if score <= WARNING_THRESHOLD:
        logger.warning(
            f"[LOW CONFIDENCE ALERT] Step '{step_name}' logged low self-confidence (Score: {score}/5). "
            f"Justification: {justification}"
        )
        return True
    return False
