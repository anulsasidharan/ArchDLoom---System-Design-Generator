from __future__ import annotations

from enum import Enum
from typing import Literal

from pydantic import BaseModel, Field


class GenerationJobStatus(str, Enum):
    QUEUED = "queued"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class GenerationOptions(BaseModel):
    include_cost_estimates: bool = True
    focus_ai_ml: bool = False
    compliance_emphasis: bool = False
    aiml_architecture: Literal["auto", "rag", "fine_tuning", "realtime_inference", "agentic"] = (
        "auto"
    )
