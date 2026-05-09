from __future__ import annotations

from enum import Enum

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
