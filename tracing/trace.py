from pydantic import BaseModel, Field
from tracing.span import Span

class Trace(BaseModel):
    """
    Pydantic schema representing the complete trace document aggregating
    individual step execution spans and overall latencies/tokens.
    """
    trace_id: str = Field(..., description="Unique ID mapping this transaction")
    document_name: str = Field(..., description="The name of the document processed during this trace run")
    status: str = Field(..., description="Overall trace status: SUCCESS or FAILED")
    spans: list[Span] = Field(default_factory=list, description="Collection of execution spans recorded during this run")
    overall_latency_ms: float = Field(..., description="Total elapsed latency for the entire pipeline execution")
    overall_token_count: int = Field(0, description="Sum of tokens consumed across all steps in the trace")
