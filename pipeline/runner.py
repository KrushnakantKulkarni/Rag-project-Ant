from pydantic import BaseModel, Field
from utils.logger import get_logger
from pipeline import intake, extraction, classification, summarization
from pipeline.intake import IntakeOutput
from pipeline.extraction import ExtractionOutput
from pipeline.classification import ClassificationOutput
from pipeline.summarization import SummarizationOutput
import uuid
import time
from tracing.instrumentation import trace_session
from tracing.trace import Trace
from tracing.storage import save_trace

logger = get_logger("pipeline.runner")

class PipelineRunResult(BaseModel):
    """
    Combined output model containing the complete sequential outputs 
    and telemetry details for an entire execution trace.
    """
    document_name: str = Field(..., description="The name of the processed document")
    status: str = Field(..., description="Overall execution status: SUCCESS or FAILED")
    error_message: str | None = Field(None, description="The traceback or error details if execution failed")
    intake: IntakeOutput | None = Field(None, description="Output from the Intake Step")
    extraction: ExtractionOutput | None = Field(None, description="Output from the Extraction Step")
    classification: ClassificationOutput | None = Field(None, description="Output from the Classification Step")
    summarization: SummarizationOutput | None = Field(None, description="Output from the Summarization Step")

def execute_pipeline(filepath: str, raw_content: str) -> PipelineRunResult:
    """
    Orchestrates the sequential execution of the 4-stage pipeline stateless steps.
    Runs inside a context-scoped thread-safe tracing session, collecting Spans,
    and committing overall trace records atomically to JSON and SQLite.
    """
    doc_name = filepath.split("/")[-1].split("\\")[-1]
    trace_id = f"tr-{uuid.uuid4().hex[:8]}"
    logger.info(f"Starting E2E analysis pipeline run: {trace_id} for: {filepath}")
    
    # 1. Initialize result trackers
    result = PipelineRunResult(
        document_name=doc_name,
        status="FAILED"
    )
    
    start_time_ns = time.perf_counter_ns()
    
    # 2. Enter isolated trace session
    with trace_session(trace_id) as session_spans:
        try:
            # Step 1: Intake
            intake_in = intake.IntakeInput(filepath=filepath, raw_content=raw_content)
            intake_out = intake.run_step(intake_in)
            result.intake = intake_out
            result.document_name = intake_out.document_name
            
            # Step 2: Extraction
            extraction_in = extraction.ExtractionInput(
                document_name=intake_out.document_name,
                sanitized_text=intake_out.sanitized_text
            )
            extraction_out = extraction.run_step(extraction_in)
            result.extraction = extraction_out
            
            # Step 3: Classification
            classification_in = classification.ClassificationInput(
                document_name=extraction_out.document_name,
                facts=extraction_out.facts
            )
            classification_out = classification.run_step(classification_in)
            result.classification = classification_out
            
            # Step 4: Summarization
            summarization_in = summarization.SummarizationInput(
                document_name=classification_out.document_name,
                category=classification_out.category,
                severity=classification_out.severity,
                facts=extraction_out.facts
            )
            summarization_out = summarization.run_step(summarization_in)
            result.summarization = summarization_out
            
            # Mark run status
            result.status = "SUCCESS"
            logger.info(f"E2E steps executed successfully for: {result.document_name}")
            
        except Exception as e:
            error_msg = str(e)
            logger.error(f"E2E steps execution failed for {doc_name}. Error: {error_msg}")
            result.status = "FAILED"
            result.error_message = error_msg
            
        # Compute overall E2E nanosecond clock latency in milliseconds
        end_time_ns = time.perf_counter_ns()
        overall_latency_ms = (end_time_ns - start_time_ns) / 1_000_000.0
        
        # Aggregate token counts across collected spans
        overall_token_count = sum(span.token_count for span in session_spans)
        
        # Build consolidated Trace telemetry model
        trace = Trace(
            trace_id=trace_id,
            document_name=result.document_name,
            status=result.status,
            spans=session_spans,
            overall_latency_ms=overall_latency_ms,
            overall_token_count=overall_token_count
        )
        
        # Save trace JSON archive and SQLite index atomically
        try:
            save_trace(trace)
        except Exception as se:
            logger.error(f"Failed to transactionally commit trace telemetry: {str(se)}")
            if result.status == "SUCCESS":
                result.status = "FAILED"
                result.error_message = f"Observability storage indexing failed: {str(se)}"
                
    return result
