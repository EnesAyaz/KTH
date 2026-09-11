from dataclasses import dataclass
from typing import Optional


@dataclass
class ModelEvidence:
    """
    Metadata describing the source and confidence
    of a model or engineering parameter.
    """

    source_type: str

    source_name: str

    confidence: str

    notes: Optional[str] = None

    reference_id: Optional[str] = None

    valid_min: Optional[float] = None

    valid_max: Optional[float] = None

    valid_unit: Optional[str] = None


def confidence_score(
    confidence: str,
) -> int:
    """
    Convert text confidence to numerical score.
    """

    scores = {

        "high": 3,

        "medium": 2,

        "low": 1,

        "unknown": 0,
    }

    return scores.get(
        str(confidence).lower(),
        0,
    )


def lowest_confidence(
    *confidences,
) -> str:
    """
    Return the lowest confidence level.
    """

    if not confidences:

        return "unknown"

    return min(
        confidences,
        key=confidence_score,
    )


def evidence_to_dict(
    prefix: str,
    evidence: ModelEvidence,
):
    """
    Flatten evidence into fields suitable
    for pandas / Excel output.
    """

    return {

        f"{prefix}_source_type":
            evidence.source_type,

        f"{prefix}_source_name":
            evidence.source_name,

        f"{prefix}_confidence":
            evidence.confidence,

        f"{prefix}_notes":
            evidence.notes,

        f"{prefix}_reference_id":
            evidence.reference_id,

        f"{prefix}_valid_min":
            evidence.valid_min,

        f"{prefix}_valid_max":
            evidence.valid_max,

        f"{prefix}_valid_unit":
            evidence.valid_unit,
    }