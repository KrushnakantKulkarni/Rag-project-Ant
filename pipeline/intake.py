import os
from pydantic import BaseModel, Field
from utils.logger import get_logger

logger = get_logger("pipeline.intake")

class IntakeInput(BaseModel):
    """
    Input model for the Intake step.
    """
    filepath: str = Field(..., description="The physical or logical path of the input file")
    raw_content: str = Field(..., description="The raw uncleaned content of the log or incident document")

class IntakeOutput(BaseModel):
    """
    Output model for the Intake step.
    """
    document_name: str = Field(..., description="The base filename derived from the input path")
    sanitized_text: str = Field(..., description="The stripped, normalized text ready for downstream analysis")
    char_count: int = Field(..., description="The exact character length of the sanitized text")

def run_step(input_data: IntakeInput) -> IntakeOutput:
    """
    Intake step execution: Normalizes whitespace, extracts filename,
    and returns validated model parameters.
    """
    logger.info(f"Processing intake file: {input_data.filepath}")
    
    # Strip unnecessary leading/trailing whitespace
    sanitized = input_data.raw_content.strip()
    char_count = len(sanitized)
    
    # Extract base filename as document name
    doc_name = os.path.basename(input_data.filepath)
    
    output = IntakeOutput(
        document_name=doc_name,
        sanitized_text=sanitized,
        char_count=char_count
    )
    
    logger.info(f"Intake completed for {doc_name} (Length: {char_count} chars)")
    return output
