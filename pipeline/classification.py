from typing import Literal
from pydantic import BaseModel, Field
from openai import OpenAI
from utils.settings import settings
from utils.logger import get_logger
from utils.thresholds import ConfidenceSchema, check_confidence_threshold
from pipeline.extraction import ExtractedFact

logger = get_logger("pipeline.classification")

class ClassificationInput(BaseModel):
    """
    Input model for the Classification step.
    """
    document_name: str = Field(..., description="The name of the analyzed document")
    facts: list[ExtractedFact] = Field(..., description="The technical facts extracted in the prior stage")

class ClassificationOutput(BaseModel):
    """
    Output model for the Classification step.
    """
    document_name: str = Field(..., description="The name of the analyzed document")
    category: str = Field(..., description="Assigned failure category: Legal, Security, Network, Database, Application")
    severity: str = Field(..., description="Assigned incident severity: Critical, Major, Minor")
    justification: str = Field(..., description="Clear textual logic detailing why this category/severity was assigned")
    confidence_score: int = Field(..., description="Co-generated confidence score (1-5)")
    confidence_justification: str = Field(..., description="Textual justification for the assigned confidence score")

# Internal Pydantic schema enforcing literals for structured outputs
class ClassificationResponseSchema(BaseModel):
    category: Literal["Legal", "Security", "Network", "Database", "Application"]
    severity: Literal["Critical", "Major", "Minor"]
    justification: str
    confidence: ConfidenceSchema

from tracing.instrumentation import instrument, record_llm_telemetry

@instrument("Classification")
def run_step(input_data: ClassificationInput) -> ClassificationOutput:
    """
    Classification step execution: Performs incident classification on categories 
    and severities based on extracted facts, co-generating a confidence score.
    """
    logger.info(f"Running LLM Classification for: {input_data.document_name}")
    
    client = OpenAI(api_key=settings.OPENAI_API_KEY)
    
    # Format facts for prompt ingestion
    facts_str = "\n".join([
        f"- Fact: {f.description} (Entity: {f.entity}, Code: {f.error_code}, Time: {f.timestamp})"
        for f in input_data.facts
    ])
    
    prompt = f"""
    You are an expert failure forensics co-pilot.
    Analyze the following extracted technical facts and assign:
    1. A failure category (Legal, Security, Network, Database, Application)
    2. A severity level (Critical, Major, Minor)
    3. A clear, technical justification of your choices.
    
    Additionally, rate your confidence in this classification on an integer scale from 1 (very low confidence/noisy input) 
    to 5 (absolute certainty/clean input) and provide a short technical justification.
    
    <extracted_facts>
    {facts_str}
    </extracted_facts>
    """
    
    # Utilizing constrained schemas in modern OpenAI Structured Outputs
    completion = client.beta.chat.completions.parse(
        model=settings.LLM_MODEL,
        messages=[
            {"role": "system", "content": "You are a professional system operations reliability engineer. Co-generate your classification results and confidence self-score together in a single API completion request."},
            {"role": "user", "content": prompt}
        ],
        response_format=ClassificationResponseSchema
    )
    
    result = completion.choices[0].message.parsed
    if not result:
        raise ValueError("Failed to extract structured classification from OpenAI response.")
    
    # Record LLM telemetry metrics into active context
    record_llm_telemetry(
        prompt=prompt,
        response=completion.choices[0].message.content or "",
        tokens=getattr(completion.usage, "total_tokens", 0),
        confidence=result.confidence.score
    )
    
    # Perform confidence warnings threshold checking
    check_confidence_threshold("Classification", result.confidence.score, result.confidence.justification)
        
    output = ClassificationOutput(
        document_name=input_data.document_name,
        category=result.category,
        severity=result.severity,
        justification=result.justification,
        confidence_score=result.confidence.score,
        confidence_justification=result.confidence.justification
    )
    
    logger.info(f"Classification completed for {input_data.document_name} (Category: {output.category}, Severity: {output.severity}, Confidence: {output.confidence_score}/5)")
    return output
