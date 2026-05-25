from pydantic import BaseModel, Field
from utils.logger import get_logger
from pipeline import intake, extraction, classification, summarization
from pipeline.intake import IntakeOutput
from pipeline.extraction import ExtractionOutput
from pipeline.classification import ClassificationOutput
from pipeline.summarization import SummarizationOutput

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
    Captures outputs at every step and catches execution exceptions gracefully.
    """
    logger.info(f"Starting E2E analysis pipeline run for: {filepath}")
    
    # 1. Initialize result trackers
    doc_name = filepath.split("/")[-1].split("\\")[-1]
    result = PipelineRunResult(
        document_name=doc_name,
        status="FAILED"
    )
    
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
        
        # Mark run as completely successful
        result.status = "SUCCESS"
        logger.info(f"E2E analysis pipeline execution completed successfully for: {result.document_name}")
        
    except Exception as e:
        error_msg = str(e)
        logger.error(f"E2E pipeline failed during execution for {doc_name}. Error: {error_msg}")
        result.status = "FAILED"
        result.error_message = error_msg
        
    return result
