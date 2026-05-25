from typing import Optional
from pydantic import BaseModel, Field

class Span(BaseModel):
    """
    Pydantic schema representing the complete execution telemetry of a single pipeline step.
    """
    span_id: str = Field(..., description="Unique UUID or hash representing this span")
    trace_id: str = Field(..., description="The parent trace ID mapping this execution")
    step_name: str = Field(..., description="The name of the pipeline step (e.g. Intake, Extraction)")
    status: str = Field(..., description="Execution status: SUCCESS or FAILED")
    serialized_input: str = Field(..., description="JSON formatted representation of the step's input model")
    serialized_output: Optional[str] = Field(None, description="JSON formatted representation of the step's output model, None on error")
    raw_llm_prompt: Optional[str] = Field(None, description="The raw system and user prompt sent to the LLM (if applicable)")
    raw_llm_response: Optional[str] = Field(None, description="The raw response returned by the LLM (if applicable)")
    token_count: int = Field(0, description="The number of tokens consumed during the LLM execution")
    latency_ms: float = Field(..., description="Elapsed execution time in milliseconds")
    confidence_score: Optional[int] = Field(None, ge=1, le=5, description="LLM-reported confidence score (integer 1-5)")
    error: Optional[str] = Field(None, description="Detailed traceback error string on step failures")
