from pydantic import BaseModel, Field
from openai import OpenAI
from utils.settings import settings
from utils.logger import get_logger
from utils.thresholds import ConfidenceSchema, check_confidence_threshold

logger = get_logger("pipeline.extraction")

class ExtractionInput(BaseModel):
    """
    Input model for the Extraction step.
    """
    document_name: str = Field(..., description="The name of the analyzed document")
    sanitized_text: str = Field(..., description="Sanitized incident text content")

class ExtractedFact(BaseModel):
    """
    Pydantic model representing a single technical fact or log event extracted.
    """
    entity: str = Field(..., description="The system components, services, or users involved")
    error_code: str = Field(..., description="Specific error code or warning ID (e.g. ERR-502, NULL if none)")
    timestamp: str = Field(..., description="The time of the event (ISO 8601 or raw log timestamp)")
    description: str = Field(..., description="A short summary of what occurred in this specific log event")

class ExtractionOutput(BaseModel):
    """
    Output model for the Extraction step.
    """
    document_name: str = Field(..., description="The name of the analyzed document")
    facts: list[ExtractedFact] = Field(..., description="List of technical facts extracted from the logs")
    raw_log_context: str = Field(..., description="The raw context segment relating to these facts")
    confidence_score: int = Field(..., description="Co-generated confidence score (1-5)")
    confidence_justification: str = Field(..., description="Textual justification for the assigned confidence score")

# Internal Pydantic schema helper for structured response formats
class ExtractionResponseSchema(BaseModel):
    facts: list[ExtractedFact]
    raw_log_context: str
    confidence: ConfidenceSchema

from tracing.instrumentation import instrument, record_llm_telemetry

@instrument("Extraction")
def run_step(input_data: ExtractionInput) -> ExtractionOutput:
    """
    Extraction step execution: Submits sanitized text to LLM and extracts
    structured technical facts along with a co-generated confidence score.
    """
    logger.info(f"Running LLM Extraction for: {input_data.document_name}")
    
    client = OpenAI(api_key=settings.OPENAI_API_KEY)
    
    prompt = f"""
    You are an expert failure forensics co-pilot.
    Analyze the following technical incident log or document:
    
    <document_context>
    {input_data.sanitized_text}
    </document_context>
    
    Extract all technical facts, key system components (entities), precise error codes,
    timestamps, and clear descriptions of occurrences. Also isolate the specific raw logs 
    supporting these facts as raw log context.
    
    Additionally, rate your confidence in this extraction on an integer scale from 1 (very low confidence/noisy input) 
    to 5 (absolute certainty/clean input) and provide a short technical justification.
    """
    
    # Utilizing modern OpenAI Structured Outputs for type safety and schema validation
    completion = client.beta.chat.completions.parse(
        model=settings.LLM_MODEL,
        messages=[
            {"role": "system", "content": "You are a professional system operations failure analyst. Co-generate your extraction results and confidence self-score together in a single API completion request."},
            {"role": "user", "content": prompt}
        ],
        response_format=ExtractionResponseSchema
    )
    
    result = completion.choices[0].message.parsed
    if not result:
        raise ValueError("Failed to extract structured facts from OpenAI response.")
    
    # Record LLM telemetry metrics into active context, passing the co-generated confidence score
    record_llm_telemetry(
        prompt=prompt,
        response=completion.choices[0].message.content or "",
        tokens=getattr(completion.usage, "total_tokens", 0),
        confidence=result.confidence.score
    )
    
    # Perform confidence warnings threshold checking
    check_confidence_threshold("Extraction", result.confidence.score, result.confidence.justification)
        
    output = ExtractionOutput(
        document_name=input_data.document_name,
        facts=result.facts,
        raw_log_context=result.raw_log_context,
        confidence_score=result.confidence.score,
        confidence_justification=result.confidence.justification
    )
    
    logger.info(f"Extraction completed for {input_data.document_name} ({len(output.facts)} facts found, Confidence: {output.confidence_score}/5)")
    return output
