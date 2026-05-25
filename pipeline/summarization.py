from pydantic import BaseModel, Field
from openai import OpenAI
from utils.settings import settings
from utils.logger import get_logger
from utils.thresholds import ConfidenceSchema, check_confidence_threshold
from pipeline.extraction import ExtractedFact

logger = get_logger("pipeline.summarization")

class SummarizationInput(BaseModel):
    """
    Input model for the Summarization step.
    """
    document_name: str = Field(..., description="The name of the analyzed document")
    category: str = Field(..., description="The classified failure category of the incident")
    severity: str = Field(..., description="The classified severity level of the incident")
    facts: list[ExtractedFact] = Field(..., description="The technical facts extracted in stage two")

class SummarizationOutput(BaseModel):
    """
    Output model for the Summarization step.
    """
    document_name: str = Field(..., description="The name of the analyzed document")
    executive_summary: str = Field(..., description="A concise, high-level summary of the incident for leadership")
    remediation_steps: str = Field(..., description="Actionable step-by-step remediation instructions to resolve the failure")
    confidence_score: int = Field(..., description="Co-generated confidence score (1-5)")
    confidence_justification: str = Field(..., description="Textual justification for the assigned confidence score")

# Internal Pydantic schema for structured response formats
class SummarizationResponseSchema(BaseModel):
    executive_summary: str
    remediation_steps: str
    confidence: ConfidenceSchema

from tracing.instrumentation import instrument, record_llm_telemetry

@instrument("Summarization")
def run_step(input_data: SummarizationInput) -> SummarizationOutput:
    """
    Summarization step execution: Synthesizes categories and facts into executive
    reports and remediation checklists, co-generating a confidence score.
    """
    logger.info(f"Running LLM Summarization for: {input_data.document_name}")
    
    client = OpenAI(api_key=settings.OPENAI_API_KEY)
    
    # Format facts for prompt context ingestion
    facts_str = "\n".join([
        f"- Fact: {f.description} (Entity: {f.entity}, Code: {f.error_code}, Time: {f.timestamp})"
        for f in input_data.facts
    ])
    
    prompt = f"""
    You are an expert failure forensics co-pilot.
    Formulate a concise executive summary and clear remediation steps for this incident:
    
    Incident Details:
    - Document: {input_data.document_name}
    - Category: {input_data.category}
    - Severity: {input_data.severity}
    
    Extracted Facts:
    {facts_str}
    
    Additionally, rate your confidence in this summarization on an integer scale from 1 (very low confidence/noisy input) 
    to 5 (absolute certainty/clean input) and provide a short technical justification.
    """
    
    # Utilizing structured outputs to extract clean markdown responses
    completion = client.beta.chat.completions.parse(
        model=settings.LLM_MODEL,
        messages=[
            {"role": "system", "content": "You are a professional IT service reliability manager compiling executive incident reports. Co-generate your summary and confidence self-score together in a single API completion request."},
            {"role": "user", "content": prompt}
        ],
        response_format=SummarizationResponseSchema
    )
    
    result = completion.choices[0].message.parsed
    if not result:
        raise ValueError("Failed to extract structured summary from OpenAI response.")
    
    # Record LLM telemetry metrics into active context
    record_llm_telemetry(
        prompt=prompt,
        response=completion.choices[0].message.content or "",
        tokens=getattr(completion.usage, "total_tokens", 0),
        confidence=result.confidence.score
    )
    
    # Perform confidence warnings threshold checking
    check_confidence_threshold("Summarization", result.confidence.score, result.confidence.justification)
        
    output = SummarizationOutput(
        document_name=input_data.document_name,
        executive_summary=result.executive_summary,
        remediation_steps=result.remediation_steps,
        confidence_score=result.confidence.score,
        confidence_justification=result.confidence.justification
    )
    
    logger.info(f"Summarization completed for {input_data.document_name} (Confidence: {output.confidence_score}/5)")
    return output
