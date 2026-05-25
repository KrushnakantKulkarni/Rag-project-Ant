import os
import sqlite3
import json
from utils.settings import settings
from utils.logger import get_logger
from tracing.trace import Trace

logger = get_logger("tracing.storage")

def save_trace(trace: Trace) -> None:
    """
    Saves trace telemetry atomically:
    1. Writes trace details as structured JSON to a disk archive file.
    2. Inserts trace metadata and individual step spans into the SQLite database
       in a single context-managed database transaction.
    """
    logger.info(f"Saving telemetry trace file on disk: {trace.trace_id}")
    
    # 1. Write JSON telemetry file to disk
    os.makedirs(settings.TRACE_ARCHIVE_DIR, exist_ok=True)
    json_path = os.path.join(settings.TRACE_ARCHIVE_DIR, f"{trace.trace_id}.json")
    
    try:
        with open(json_path, "w", encoding="utf-8") as f:
            f.write(trace.model_dump_json(indent=2))
        logger.info(f"Successfully archived JSON trace logs to {json_path}")
    except Exception as e:
        logger.error(f"Failed to save JSON trace file on disk: {str(e)}")
        raise e

    # 2. Write to SQLite in a single transaction block
    logger.info(f"Transactional indexing database commit started: {trace.trace_id}")
    
    # Extract overall error message if present in spans
    error_msg = None
    for span in trace.spans:
        if span.status == "FAILED" and span.error:
            error_msg = span.error
            break
            
    try:
        # Standard context-managed transaction handles rollback on exception automatically
        with sqlite3.connect(settings.DATABASE_PATH) as conn:
            # 2a. Insert parent trace
            conn.execute(
                """
                INSERT OR REPLACE INTO traces (
                    trace_id, document_name, status, error_message, overall_latency_ms, overall_token_count
                ) VALUES (?, ?, ?, ?, ?, ?);
                """,
                (
                    trace.trace_id,
                    trace.document_name,
                    trace.status,
                    error_msg,
                    trace.overall_latency_ms,
                    trace.overall_token_count
                )
            )
            
            # 2b. Insert child spans
            for span in trace.spans:
                conn.execute(
                    """
                    INSERT OR REPLACE INTO spans (
                        span_id, trace_id, step_name, status, confidence_score, latency_ms, token_count, error
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?);
                    """,
                    (
                        span.span_id,
                        span.trace_id,
                        span.step_name,
                        span.status,
                        span.confidence_score,
                        span.latency_ms,
                        span.token_count,
                        span.error
                    )
                )
        
        logger.info(f"Transactional index commit succeeded for trace {trace.trace_id}")
        
    except Exception as e:
        logger.error(f"SQLite transaction commit failed. Trace: {trace.trace_id}. Error: {str(e)}")
        # Delete generated JSON file on database fail to preserve atomic sync
        if os.path.exists(json_path):
            try:
                os.remove(json_path)
            except Exception:
                pass
        raise e
