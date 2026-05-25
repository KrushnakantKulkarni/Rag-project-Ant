import os
import time
import json
import pytest
from unittest.mock import MagicMock, patch
from utils.settings import settings
from pipeline import intake, extraction, classification, summarization, runner
from tracing.instrumentation import instrument, trace_session, get_active_spans
from tracing.trace import Trace
from tracing.span import Span
from tracing.storage import save_trace

@pytest.fixture(autouse=True)
def setup_temp_db(tmp_path, monkeypatch):
    """
    Autouse fixture that sandboxes the settings DATABASE_PATH and TRACE_ARCHIVE_DIR
    to temporary testing folders and initializes the tables using schema.sql.
    """
    db_path = str(tmp_path / "test_traces.db")
    archive_dir = str(tmp_path / "test_traces_dir")
    
    monkeypatch.setattr(settings, "DATABASE_PATH", db_path)
    monkeypatch.setattr(settings, "TRACE_ARCHIVE_DIR", archive_dir)
    
    # Initialize schema
    import sqlite3
    with sqlite3.connect(db_path) as conn:
        with open("schema.sql") as f:
            conn.executescript(f.read())
    yield

# ==============================================================================
# Step 1: Intake Step Unit Tests
# ==============================================================================
def test_intake_step_success():
    """
    Verifies that the Intake step normalizes input text, extracts the filename,
    and returns a validated model correctly.
    """
    raw_log = "   2026-05-25 [ERROR] Database server crashed   \n"
    input_data = intake.IntakeInput(
        filepath="logs/db_crash.log",
        raw_content=raw_log
    )
    
    output = intake.run_step(input_data)
    
    assert output.document_name == "db_crash.log"
    assert output.sanitized_text == "2026-05-25 [ERROR] Database server crashed"
    assert output.char_count == len("2026-05-25 [ERROR] Database server crashed")


# ==============================================================================
# Step 2: Extraction Step Unit Tests (Offline Mocked)
# ==============================================================================
@patch("pipeline.extraction.OpenAI")
def test_extraction_step_success(mock_openai_class):
    """
    Verifies structured OpenAI log entity extraction runs successfully using mocks.
    """
    # Configure mock client hierarchy
    mock_client = MagicMock()
    mock_openai_class.return_value = mock_client
    
    mock_completion = MagicMock()
    mock_client.beta.chat.completions.parse.return_value = mock_completion
    
    # Formulate mock parsed output model containing confidence metrics
    mock_parsed_facts = extraction.ExtractionResponseSchema(
        facts=[
            extraction.ExtractedFact(
                entity="AuthService",
                error_code="ERR-401",
                timestamp="2026-05-23T12:00:00Z",
                description="Unauthorized access warning received"
            )
        ],
        raw_log_context="2026-05-23T12:00:00Z AuthService ERR-401",
        confidence=extraction.ConfidenceSchema(score=4, justification="clean extraction log")
    )
    
    # Ensure raw prompt message content has a mock string to avoid validation crashes
    mock_completion.choices = [MagicMock()]
    mock_completion.choices[0].message.parsed = mock_parsed_facts
    mock_completion.choices[0].message.content = "mock raw completion response facts context"
    
    input_data = extraction.ExtractionInput(
        document_name="auth_err.log",
        sanitized_text="2026-05-23T12:00:00Z AuthService ERR-401"
    )
    
    output = extraction.run_step(input_data)
    
    assert output.document_name == "auth_err.log"
    assert len(output.facts) == 1
    assert output.facts[0].entity == "AuthService"
    assert output.facts[0].error_code == "ERR-401"
    assert output.raw_log_context == "2026-05-23T12:00:00Z AuthService ERR-401"
    assert output.confidence_score == 4
    assert output.confidence_justification == "clean extraction log"



# ==============================================================================
# Step 3: Classification Step Unit Tests (Offline Mocked)
# ==============================================================================
@patch("pipeline.classification.OpenAI")
def test_classification_step_success(mock_openai_class):
    """
    Verifies that the logical failure taxonomy classification step runs successfully using mocks.
    """
    mock_client = MagicMock()
    mock_openai_class.return_value = mock_client
    
    mock_completion = MagicMock()
    mock_client.beta.chat.completions.parse.return_value = mock_completion
    
    mock_parsed_classification = classification.ClassificationResponseSchema(
        category="Security",
        severity="Critical",
        justification="AuthService ERR-401 errors represent active access control policy rejections.",
        confidence=classification.ConfidenceSchema(score=5, justification="confident classification")
    )
    
    mock_completion.choices = [MagicMock()]
    mock_completion.choices[0].message.parsed = mock_parsed_classification
    mock_completion.choices[0].message.content = "mock classification raw response context"
    
    input_data = classification.ClassificationInput(
        document_name="auth_err.log",
        facts=[
            extraction.ExtractedFact(
                entity="AuthService",
                error_code="ERR-401",
                timestamp="2026-05-23T12:00:00Z",
                description="Unauthorized access warning"
            )
        ]
    )
    
    output = classification.run_step(input_data)
    
    assert output.category == "Security"
    assert output.severity == "Critical"
    assert "access control" in output.justification
    assert output.confidence_score == 5
    assert output.confidence_justification == "confident classification"



# ==============================================================================
# Step 4: Summarization Step Unit Tests (Offline Mocked)
# ==============================================================================
@patch("pipeline.summarization.OpenAI")
def test_summarization_step_success(mock_openai_class):
    """
    Verifies executive incident report and remediation compilation runs successfully using mocks.
    """
    mock_client = MagicMock()
    mock_openai_class.return_value = mock_client
    
    mock_completion = MagicMock()
    mock_client.beta.chat.completions.parse.return_value = mock_completion
    
    mock_parsed_summary = summarization.SummarizationResponseSchema(
        executive_summary="Active authorization token failure at AuthService.",
        remediation_steps="1. Review firewall blocks.\n2. Invalidate expired session tokens.",
        confidence=summarization.ConfidenceSchema(score=4, justification="summarization confident")
    )
    
    mock_completion.choices = [MagicMock()]
    mock_completion.choices[0].message.parsed = mock_parsed_summary
    mock_completion.choices[0].message.content = "mock summarization raw response content"
    
    input_data = summarization.SummarizationInput(
        document_name="auth_err.log",
        category="Security",
        severity="Critical",
        facts=[
            extraction.ExtractedFact(
                entity="AuthService",
                error_code="ERR-401",
                timestamp="2026-05-23T12:00:00Z",
                description="Unauthorized access warning"
            )
        ]
    )
    
    output = summarization.run_step(input_data)
    
    assert "AuthService" in output.executive_summary
    assert "Invalidate expired" in output.remediation_steps
    assert output.confidence_score == 4
    assert output.confidence_justification == "summarization confident"



# ==============================================================================
# E2E Pipeline Orchestrator Tests (Offline Mocked)
# ==============================================================================
@patch("pipeline.extraction.OpenAI")
@patch("pipeline.classification.OpenAI")
@patch("pipeline.summarization.OpenAI")
def test_runner_e2e_mock_success(mock_sum_openai, mock_cls_openai, mock_ext_openai):
    """
    Verifies that the orchestrator chains output variables of upstream steps 
    into input structures of downstream steps cleanly.
    """
    # 1. Mock Extraction completion outputs
    mock_ext_client = MagicMock()
    mock_ext_openai.return_value = mock_ext_client
    mock_ext_comp = MagicMock()
    mock_ext_client.beta.chat.completions.parse.return_value = mock_ext_comp
    mock_ext_comp.choices = [MagicMock()]
    mock_ext_comp.choices[0].message.parsed = extraction.ExtractionResponseSchema(
        facts=[
            extraction.ExtractedFact(
                entity="NetworkGateway",
                error_code="NET-TIMEOUT",
                timestamp="14:02:11",
                description="Failed to ping API server"
            )
        ],
        raw_log_context="NET-TIMEOUT on Gateway",
        confidence=extraction.ConfidenceSchema(score=4, justification="facts parsed")
    )
    mock_ext_comp.choices[0].message.content = "mock raw facts extraction completion text"
    
    # 2. Mock Classification completion outputs
    mock_cls_client = MagicMock()
    mock_cls_openai.return_value = mock_cls_client
    mock_cls_comp = MagicMock()
    mock_cls_client.beta.chat.completions.parse.return_value = mock_cls_comp
    mock_cls_comp.choices = [MagicMock()]
    mock_cls_comp.choices[0].message.parsed = classification.ClassificationResponseSchema(
        category="Network",
        severity="Major",
        justification="Network timeouts represent structural service issues.",
        confidence=classification.ConfidenceSchema(score=5, justification="taxons matched")
    )
    mock_cls_comp.choices[0].message.content = "mock raw classification completion text"
    
    # 3. Mock Summarization completion outputs
    mock_sum_client = MagicMock()
    mock_sum_openai.return_value = mock_sum_client
    mock_sum_comp = MagicMock()
    mock_sum_client.beta.chat.completions.parse.return_value = mock_sum_comp
    mock_sum_comp.choices = [MagicMock()]
    mock_sum_comp.choices[0].message.parsed = summarization.SummarizationResponseSchema(
        executive_summary="Network service loss.",
        remediation_steps="Restart network switch.",
        confidence=summarization.ConfidenceSchema(score=4, justification="remediations compiled")
    )
    mock_sum_comp.choices[0].message.content = "mock raw summarization completion text"
    
    # Run Orchestrator
    result = runner.execute_pipeline(
        filepath="logs/net.log",
        raw_content="   NET-TIMEOUT on Gateway   \n"
    )
    
    # Assert successful chaining across all 4 stages
    assert result.status == "SUCCESS"
    assert result.document_name == "net.log"
    assert result.intake is not None
    assert result.intake.char_count == len("NET-TIMEOUT on Gateway")
    assert result.extraction.facts[0].entity == "NetworkGateway"
    assert result.classification.category == "Network"
    assert result.summarization.executive_summary == "Network service loss."
    
    # Assert confidence co-generation metrics are integrated
    assert result.extraction.confidence_score == 4
    assert result.classification.confidence_score == 5
    assert result.summarization.confidence_score == 4



# ==============================================================================
# Phase 03: Telemetry, Decorator, and Storage Layer Unit Tests
# ==============================================================================
def test_decorator_timing_and_exception_capture():
    """
    Verifies that the @instrument decorator profiles execution speeds, 
    captures input/output schemas, and logs exceptions with full tracebacks.
    """
    @instrument("TimingStep")
    def dummy_step(input_data: intake.IntakeInput):
        time.sleep(0.05)  # Simulate 50ms processing latency
        return intake.IntakeOutput(
            document_name="dummy.log",
            sanitized_text="processed_content",
            char_count=17
        )

    @instrument("FailingStep")
    def dummy_fail_step(input_data: intake.IntakeInput):
        raise ValueError("Simulated step failure")

    # Test timing accuracy
    with trace_session("tr-test-timing") as spans:
        inp = intake.IntakeInput(filepath="dummy.log", raw_content="raw")
        out = dummy_step(inp)
        assert out.char_count == 17
        
        assert len(spans) == 1
        span = spans[0]
        assert span.step_name == "TimingStep"
        assert span.status == "SUCCESS"
        # Monotonic timers should reflect sleep duration (typically 45-80ms under CI/CD load)
        assert 45.0 <= span.latency_ms <= 120.0
        assert "dummy.log" in span.serialized_input
        assert "processed_content" in span.serialized_output

    # Test exception capture and status marking
    with trace_session("tr-test-fail") as spans:
        inp = intake.IntakeInput(filepath="dummy.log", raw_content="raw")
        with pytest.raises(ValueError, match="Simulated step failure"):
            dummy_fail_step(inp)
            
        assert len(spans) == 1
        span = spans[0]
        assert span.step_name == "FailingStep"
        assert span.status == "FAILED"
        assert span.serialized_output is None
        assert "traceback" in span.error.lower() or "line" in span.error.lower()
        assert "Simulated step failure" in span.error


def test_atomic_storage_transaction_success():
    """
    Verifies that save_trace creates JSON logs on disk and commits parent-child
    telemetry records to SQLite in a single transaction block.
    """
    span = Span(
        span_id="sp-test-1",
        trace_id="tr-test-atomic",
        step_name="Intake",
        status="SUCCESS",
        serialized_input='{"filepath": "test.log", "raw_content": "val"}',
        serialized_output='{"document_name": "test.log", "sanitized_text": "val", "char_count": 3}',
        latency_ms=12.5
    )
    
    trace = Trace(
        trace_id="tr-test-atomic",
        document_name="test.log",
        status="SUCCESS",
        spans=[span],
        overall_latency_ms=12.5,
        overall_token_count=0
    )
    
    # Execute atomic save
    save_trace(trace)
    
    # 1. Assert JSON trace file exists in sandboxed folder
    json_path = os.path.join(settings.TRACE_ARCHIVE_DIR, f"{trace.trace_id}.json")
    assert os.path.exists(json_path)
    
    with open(json_path, "r", encoding="utf-8") as f:
        saved_data = json.load(f)
        assert saved_data["trace_id"] == "tr-test-atomic"
        assert len(saved_data["spans"]) == 1
        assert saved_data["spans"][0]["span_id"] == "sp-test-1"
        
    # 2. Assert SQLite entries exist in transactionally committed tables
    import sqlite3
    with sqlite3.connect(settings.DATABASE_PATH) as conn:
        cur = conn.cursor()
        
        # Assert trace parent row
        cur.execute("SELECT document_name, status, overall_latency_ms FROM traces WHERE trace_id = ?", ("tr-test-atomic",))
        trace_row = cur.fetchone()
        assert trace_row is not None
        assert trace_row[0] == "test.log"
        assert trace_row[1] == "SUCCESS"
        assert trace_row[2] == 12.5
        
        # Assert span child row
        cur.execute("SELECT step_name, status, latency_ms FROM spans WHERE span_id = ?", ("sp-test-1",))
        span_row = cur.fetchone()
        assert span_row is not None
        assert span_row[0] == "Intake"
        assert span_row[1] == "SUCCESS"
        assert span_row[2] == 12.5


# ==============================================================================
# Phase 04: Confidence Scoring, Parsing Resilience, and Threshold Unit Tests
# ==============================================================================
def test_confidence_validation_resilience():
    """
    Verifies that invalid confidence formats (e.g. strings like "High", "90%", 
    or integers out of bounds) are gracefully auto-translated to standard default (3).
    """
    from utils.thresholds import ConfidenceSchema
    
    # 1. Test clean valid integers
    c1 = ConfidenceSchema(score=4, justification="clean")
    assert c1.score == 4
    
    # 2. Test string numerical percentage parsing
    c2 = ConfidenceSchema(score="90%", justification="noisy percent")
    assert c2.score == 3  # "90" parsed as 90 which is out of bounds, thus falling back to 3
    
    c3 = ConfidenceSchema(score="4/5", justification="slash format")
    assert c3.score == 4  # "4" extracted and validated successfully
    
    # 3. Test textual inputs falling back to default 3
    c4 = ConfidenceSchema(score="High", justification="qualitative description")
    assert c4.score == 3
    
    # 4. Test integers out of bounds (score <= 0 or score > 5) falling back to default 3
    c5 = ConfidenceSchema(score=6, justification="too high")
    assert c5.score == 3
    
    c6 = ConfidenceSchema(score=0, justification="too low")
    assert c6.score == 3


def test_confidence_threshold_alerts(caplog):
    """
    Verifies that utils/thresholds.py correctly identifies low confidence scores 
    (score <= 2) and logs standard warning flags.
    """
    import logging
    from utils.thresholds import check_confidence_threshold
    
    # Run with log capturing enabled at the WARNING level
    with caplog.at_level(logging.WARNING):
        # 1. Test acceptable score (no warning triggered)
        triggered_1 = check_confidence_threshold("TestStep", 4, "acceptable facts")
        assert triggered_1 is False
        assert len(caplog.records) == 0
        
        # 2. Test low score (warning alert triggered)
        triggered_2 = check_confidence_threshold("TestStep", 2, "highly ambiguous logs")
        assert triggered_2 is True
        assert len(caplog.records) == 1
        assert "LOW CONFIDENCE ALERT" in caplog.text
        assert "TestStep" in caplog.text
        assert "highly ambiguous logs" in caplog.text


