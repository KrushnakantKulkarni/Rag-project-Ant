import time
import uuid
import traceback
import contextvars
import contextlib
from typing import Optional, Callable, Any
from pydantic import BaseModel
from utils.logger import get_logger
from tracing.span import Span

logger = get_logger("tracing.instrumentation")

# Thread-safe context variables for tracing lifecycle
_active_trace_id: contextvars.ContextVar[str] = contextvars.ContextVar("active_trace_id", default="")
_active_spans: contextvars.ContextVar[list[Span]] = contextvars.ContextVar("active_spans")

# Context variables to hold LLM-specific telemetry captured during a step function execution
_last_llm_prompt: contextvars.ContextVar[Optional[str]] = contextvars.ContextVar("last_llm_prompt", default=None)
_last_llm_response: contextvars.ContextVar[Optional[str]] = contextvars.ContextVar("last_llm_response", default=None)
_last_llm_tokens: contextvars.ContextVar[int] = contextvars.ContextVar("last_llm_tokens", default=0)
_last_confidence_score: contextvars.ContextVar[Optional[int]] = contextvars.ContextVar("last_confidence_score", default=None)


def record_llm_telemetry(prompt: str, response: str, tokens: int, confidence: Optional[int] = None) -> None:
    """
    Exposed helper for step functions to record LLM-specific observability data.
    The active decorator will intercept these values upon function return.
    """
    _last_llm_prompt.set(prompt)
    _last_llm_response.set(response)
    _last_llm_tokens.set(tokens)
    if confidence is not None:
        _last_confidence_score.set(confidence)


@contextlib.contextmanager
def trace_session(trace_id: str):
    """
    Context manager to initialize and scope a thread-safe tracing execution session.
    """
    token_trace = _active_trace_id.set(trace_id)
    token_spans = _active_spans.set([])
    try:
        yield _active_spans.get()
    finally:
        _active_trace_id.reset(token_trace)
        _active_spans.reset(token_spans)


def get_active_spans() -> list[Span]:
    """
    Returns the list of recorded spans in the active tracing session.
    """
    try:
        return _active_spans.get()
    except LookupError:
        return []


def instrument(step_name: str) -> Callable:
    """
    Decorator to profile pipeline step execution, capture input/output schemas,
    intercept latencies/tokens, and automatically log traceback exceptions.
    """
    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            trace_id = _active_trace_id.get()
            if not trace_id:
                # If executed outside an active trace context, run standard function
                return func(*args, **kwargs)

            # Generate step identifiers and serialize inputs
            span_id = f"sp-{uuid.uuid4().hex[:8]}"
            
            # Serialize the primary Pydantic input model
            serialized_input = "{}"
            if args and isinstance(args[0], BaseModel):
                serialized_input = args[0].model_dump_json()
            elif kwargs:
                # Fallback to key-value serialization if passed as keyword args
                import json
                serialized_input = json.dumps({k: v.model_dump() if isinstance(v, BaseModel) else str(v) for k, v in kwargs.items()})

            # Reset LLM step context variables before running
            _last_llm_prompt.set(None)
            _last_llm_response.set(None)
            _last_llm_tokens.set(0)
            _last_confidence_score.set(None)

            # Start monotonic high-resolution timing clock
            start_time_ns = time.perf_counter_ns()
            
            try:
                # Run the stateless step
                output = func(*args, **kwargs)
                
                # Compute latency in milliseconds
                end_time_ns = time.perf_counter_ns()
                latency_ms = (end_time_ns - start_time_ns) / 1_000_000.0
                
                # Serialize outputs
                serialized_output = None
                if isinstance(output, BaseModel):
                    serialized_output = output.model_dump_json()

                # Fetch confidence and tokens dynamically from context or Pydantic attributes
                confidence = _last_confidence_score.get()
                if confidence is None and hasattr(output, "confidence_score"):
                    confidence = getattr(output, "confidence_score")
                
                tokens = _last_llm_tokens.get()
                if tokens == 0 and hasattr(output, "token_count"):
                    tokens = getattr(output, "token_count", 0)

                # Enforce strict Python types on captured parameters to avoid Pydantic validation crashes with loose mock objects
                raw_prompt = _last_llm_prompt.get()
                if raw_prompt is not None and not isinstance(raw_prompt, str):
                    raw_prompt = str(raw_prompt)
                    
                raw_response = _last_llm_response.get()
                if raw_response is not None and not isinstance(raw_response, str):
                    raw_response = str(raw_response)
                    
                if tokens is not None and not isinstance(tokens, int):
                    try:
                        tokens = int(tokens)
                    except Exception:
                        tokens = 0
                        
                if confidence is not None and not isinstance(confidence, int):
                    try:
                        confidence = int(confidence)
                    except Exception:
                        confidence = None

                # Formulate Span
                span = Span(
                    span_id=span_id,
                    trace_id=trace_id,
                    step_name=step_name,
                    status="SUCCESS",
                    serialized_input=serialized_input,
                    serialized_output=serialized_output,
                    raw_llm_prompt=raw_prompt,
                    raw_llm_response=raw_response,
                    token_count=tokens,
                    latency_ms=latency_ms,
                    confidence_score=confidence,
                    error=None
                )
                
                # Append to current session span list
                _active_spans.get().append(span)
                logger.info(f"Span {step_name} logged successfully. Status: SUCCESS, Latency: {latency_ms:.2f}ms")
                return output
                
            except Exception as e:
                # Compute elapsed latency even on failure
                end_time_ns = time.perf_counter_ns()
                latency_ms = (end_time_ns - start_time_ns) / 1_000_000.0
                
                tb_str = traceback.format_exc()
                
                # Enforce strict type conversions even on failure
                raw_prompt = _last_llm_prompt.get()
                if raw_prompt is not None and not isinstance(raw_prompt, str):
                    raw_prompt = str(raw_prompt)
                    
                raw_response = _last_llm_response.get()
                if raw_response is not None and not isinstance(raw_response, str):
                    raw_response = str(raw_response)
                    
                fail_tokens = _last_llm_tokens.get()
                if fail_tokens is not None and not isinstance(fail_tokens, int):
                    try:
                        fail_tokens = int(fail_tokens)
                    except Exception:
                        fail_tokens = 0
                        
                fail_conf = _last_confidence_score.get()
                if fail_conf is not None and not isinstance(fail_conf, int):
                    try:
                        fail_conf = int(fail_conf)
                    except Exception:
                        fail_conf = None
                
                # Formulate Failed Span
                span = Span(
                    span_id=span_id,
                    trace_id=trace_id,
                    step_name=step_name,
                    status="FAILED",
                    serialized_input=serialized_input,
                    serialized_output=None,
                    raw_llm_prompt=raw_prompt,
                    raw_llm_response=raw_response,
                    token_count=fail_tokens,
                    latency_ms=latency_ms,
                    confidence_score=fail_conf,
                    error=tb_str
                )
                
                _active_spans.get().append(span)
                logger.error(f"Span {step_name} failed. Latency: {latency_ms:.2f}ms, Error: {str(e)}")
                
                # Re-raise exception to abort pipeline execution safely
                raise e
                
        return wrapper
    return decorator
