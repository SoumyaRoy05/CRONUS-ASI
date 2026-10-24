"""
CRONUS Database Client (PostgreSQL 18 Engine)
Thread-safe, multi-loop resilient database engine with dedicated background worker.

Guarantees:
  - 100% immune to 'Event loop is closed'
  - 100% immune to 'cannot perform operation: another operation is in progress'
  - Transparent support for both sync (fire-and-forget) and async (awaitable) calls
  - Full-text search with tsvector GIN index over vault.memories
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
import threading
import time
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional

from dotenv import load_dotenv
import asyncpg

_root_dir = Path(__file__).resolve().parents[1]
load_dotenv(_root_dir / ".env")

logger = logging.getLogger("CRONUS.Database")

# Dedicated Persistent Background Event Loop for PostgreSQL Operations
_db_init_lock = threading.Lock()
_db_loop: Optional[asyncio.AbstractEventLoop] = None
_db_thread: Optional[threading.Thread] = None
_db_pool: Optional[asyncpg.Pool] = None


def _get_db_loop() -> asyncio.AbstractEventLoop:
    """Returns the dedicated, permanently open database event loop."""
    global _db_loop, _db_thread
    with _db_init_lock:
        if _db_loop is None or _db_loop.is_closed():
            loop = asyncio.new_event_loop()
            ready = threading.Event()

            def _loop_runner():
                asyncio.set_event_loop(loop)
                ready.set()
                loop.run_forever()

            _db_thread = threading.Thread(target=_loop_runner, daemon=True, name="CronusDBWorker")
            _db_thread.start()
            ready.wait()
            _db_loop = loop
        return _db_loop


async def _get_pool_internal() -> Optional[asyncpg.Pool]:
    """Initializes or retrieves the asyncpg pool on the dedicated DB event loop."""
    global _db_pool
    if _db_pool is not None and not _db_pool._closed:
        return _db_pool

    host = os.getenv("POSTGRES_HOST", "localhost")
    port = int(os.getenv("POSTGRES_PORT", "5432"))
    user = os.getenv("POSTGRES_USER", "postgres")
    password = os.getenv("POSTGRES_PASSWORD", "2026")
    database = os.getenv("POSTGRES_DB", "cronus_master")

    try:
        _db_pool = await asyncpg.create_pool(
            host=host,
            port=port,
            user=user,
            password=password,
            database=database,
            min_size=2,
            max_size=10,
            timeout=5.0,
        )
        logger.info("[Database] Connected successfully to PostgreSQL database '%s' at %s:%d", database, host, port)
        return _db_pool
    except Exception as e:
        logger.warning("[Database Circuit-Breaker] PostgreSQL connection failed: %s. Operating in resilient offline mode.", e)
        return None


def run_on_db_loop(coro, timeout: float = 8.0) -> Any:
    """Dispatches a coroutine to the dedicated DB event loop and returns the result safely."""
    loop = _get_db_loop()
    try:
        # Check if caller is already running inside _db_loop
        try:
            current_loop = asyncio.get_running_loop()
            if current_loop is loop:
                return coro
        except RuntimeError:
            pass

        fut = asyncio.run_coroutine_threadsafe(coro, loop)
        return fut.result(timeout=timeout)
    except Exception as e:
        logger.warning("[Database Circuit-Breaker] Query execution error: %s", e)
        return None


def schedule_on_db_loop(coro) -> None:
    """Fire-and-forget dispatch of a coroutine to the dedicated DB event loop (0ms caller overhead)."""
    try:
        loop = _get_db_loop()
        asyncio.run_coroutine_threadsafe(coro, loop)
    except Exception as e:
        logger.warning("[Database Circuit-Breaker] Failed to schedule background DB task: %s", e)


async def get_db_pool() -> Optional[asyncpg.Pool]:
    """Compatibility getter for the pool."""
    loop = _get_db_loop()
    fut = asyncio.run_coroutine_threadsafe(_get_pool_internal(), loop)
    return fut.result(timeout=5.0)


async def close_db_pool() -> None:
    """Gracefully closes the database connection pool."""
    global _db_pool
    if _db_pool is not None:
        loop = _get_db_loop()
        async def _close():
            global _db_pool
            if _db_pool is not None:
                await _db_pool.close()
                _db_pool = None
        fut = asyncio.run_coroutine_threadsafe(_close(), loop)
        fut.result(timeout=5.0)


async def is_db_connected() -> bool:
    """Liveness check for PostgreSQL responsiveness."""
    return check_database_health_sync()


def check_database_health_sync() -> bool:
    """Synchronous health check that dispatches to the DB worker loop."""
    async def _health():
        pool = await _get_pool_internal()
        if pool is None:
            return False
        async with pool.acquire() as conn:
            return await conn.fetchval("SELECT 1;") == 1
    res = run_on_db_loop(_health(), timeout=3.0)
    return bool(res)


# =============================================================================
# 1. CORE SCHEMA: DIALOGUE & CONVERSATIONS
# =============================================================================

async def _log_dialogue_turn_impl(
    user_prompt: str,
    cleaned_speech_response: str,
    model_used: Optional[str] = "groq",
    ear_latency_ms: int = 0,
    brain_latency_ms: int = 0,
    mouth_latency_ms: int = 0,
    session_id: Optional[str] = None,
    intent: str = "REFLEX",
) -> Optional[int]:
    pool = await _get_pool_internal()
    if pool is None:
        return None

    async with pool.acquire() as conn:
        parsed_session_id = None
        if session_id:
            try:
                parsed_session_id = uuid.UUID(session_id)
            except ValueError:
                parsed_session_id = None

        if parsed_session_id:
            exists = await conn.fetchval("SELECT 1 FROM core.conversations WHERE session_id = $1;", parsed_session_id)
            if not exists:
                await conn.execute("INSERT INTO core.conversations (session_id, started_at) VALUES ($1, NOW());", parsed_session_id)

        turn_id = await conn.fetchval(
            """
            INSERT INTO core.dialogue_turns (
                session_id, user_prompt, cleaned_speech_response,
                model_used, ear_latency_ms, brain_latency_ms, mouth_latency_ms, intent
            ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
            RETURNING turn_id;
            """,
            parsed_session_id,
            user_prompt,
            cleaned_speech_response,
            model_used,
            ear_latency_ms,
            brain_latency_ms,
            mouth_latency_ms,
            intent,
        )
        return turn_id


async def log_dialogue_turn(
    user_prompt: str,
    cleaned_speech_response: str,
    model_used: Optional[str] = "groq",
    ear_latency_ms: int = 0,
    brain_latency_ms: int = 0,
    mouth_latency_ms: int = 0,
    session_id: Optional[str] = None,
    intent: str = "REFLEX",
) -> Optional[int]:
    """Async wrapper that dispatches to the dedicated DB event loop."""
    coro = _log_dialogue_turn_impl(
        user_prompt, cleaned_speech_response, model_used,
        ear_latency_ms, brain_latency_ms, mouth_latency_ms, session_id, intent
    )
    return run_on_db_loop(coro)


def log_dialogue_turn_background(
    user_prompt: str,
    cleaned_speech_response: str,
    model_used: Optional[str] = "groq",
    ear_latency_ms: int = 0,
    brain_latency_ms: int = 0,
    mouth_latency_ms: int = 0,
    session_id: Optional[str] = None,
    intent: str = "REFLEX",
) -> None:
    """Non-blocking fire-and-forget dialogue logger (0ms latency impact)."""
    coro = _log_dialogue_turn_impl(
        user_prompt, cleaned_speech_response, model_used,
        ear_latency_ms, brain_latency_ms, mouth_latency_ms, session_id, intent
    )
    schedule_on_db_loop(coro)


async def get_recent_dialogue_turns(limit: int = 5) -> List[Dict[str, Any]]:
    """Retrieves recent dialogue turns."""
    async def _impl():
        pool = await _get_pool_internal()
        if pool is None:
            return []
        async with pool.acquire() as conn:
            rows = await conn.fetch(
                """
                SELECT turn_id, user_prompt, cleaned_speech_response, model_used, intent, created_at
                FROM core.dialogue_turns
                ORDER BY created_at DESC
                LIMIT $1;
                """,
                limit,
            )
            return [dict(r) for r in reversed(rows)]
    res = run_on_db_loop(_impl())
    return res or []


# =============================================================================
# 2. CORE SCHEMA: USER PREFERENCES
# =============================================================================

async def set_user_preference(
    key: str,
    value: str,
    category: str = "general",
    metadata: Optional[Dict[str, Any]] = None,
) -> bool:
    """Upserts a preference."""
    async def _impl():
        pool = await _get_pool_internal()
        if pool is None:
            return False
        async with pool.acquire() as conn:
            await conn.execute(
                """
                INSERT INTO core.user_preferences (key, value, category, metadata, updated_at)
                VALUES ($1, $2, $3, $4, NOW())
                ON CONFLICT (key) DO UPDATE
                SET value = EXCLUDED.value, category = EXCLUDED.category,
                    metadata = EXCLUDED.metadata, updated_at = NOW();
                """,
                key, value, category, json.dumps(metadata or {}),
            )
            return True
    res = run_on_db_loop(_impl())
    return bool(res)


async def get_user_preference(key: str) -> Optional[str]:
    """Retrieves a preference by key."""
    async def _impl():
        pool = await _get_pool_internal()
        if pool is None:
            return None
        async with pool.acquire() as conn:
            return await conn.fetchval("SELECT value FROM core.user_preferences WHERE key = $1;", key)
    return run_on_db_loop(_impl())


# =============================================================================
# 3. COUNCIL SCHEMA: BLUEPRINTS & AUDITS
# =============================================================================

async def save_blueprint_record(
    goal: str,
    rationale: str,
    planner_model: str,
    total_steps: int,
    fallback_strategy: str,
    raw_json: Optional[Dict[str, Any]] = None,
) -> Optional[str]:
    """Saves Prometheus blueprint to council.blueprints."""
    async def _impl():
        pool = await _get_pool_internal()
        if pool is None:
            return None
        async with pool.acquire() as conn:
            bp_id = await conn.fetchval(
                """
                INSERT INTO council.blueprints (
                    goal, rationale, planner_model, total_steps, fallback_strategy, raw_json
                ) VALUES ($1, $2, $3, $4, $5, $6)
                RETURNING blueprint_id;
                """,
                goal, rationale, planner_model, total_steps, fallback_strategy,
                json.dumps(raw_json or {}),
            )
            return str(bp_id)
    return run_on_db_loop(_impl())


async def save_task_step_record(
    blueprint_id: str,
    step_number: int,
    title: str,
    action_type: str,
    command_payload: str,
    target_path: Optional[str] = None,
    risk_level: str = "LOW",
    status: str = "COMPLETED",
    exit_code: Optional[int] = 0,
    stdout: Optional[str] = None,
    stderr: Optional[str] = None,
    execution_duration_sec: float = 0.0,
) -> Optional[str]:
    """Saves an Atlas step log."""
    async def _impl():
        pool = await _get_pool_internal()
        if pool is None:
            return None
        async with pool.acquire() as conn:
            step_id = await conn.fetchval(
                """
                INSERT INTO council.task_steps (
                    blueprint_id, step_number, title, action_type,
                    command_payload, target_path, risk_level, status,
                    exit_code, stdout, stderr, execution_duration_sec
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12)
                RETURNING step_id;
                """,
                uuid.UUID(blueprint_id), step_number, title, action_type,
                command_payload, target_path, risk_level, status, exit_code,
                stdout or "", stderr or "", execution_duration_sec,
            )
            return str(step_id)
    return run_on_db_loop(_impl())


async def save_security_audit_record(
    target_name: str,
    command_or_code: str,
    verdict: str,
    step_id: Optional[str] = None,
    score: float = 10.0,
    violations: Optional[List[str]] = None,
    summary: str = "",
) -> Optional[str]:
    """Saves Themis audit record."""
    async def _impl():
        pool = await _get_pool_internal()
        if pool is None:
            return None
        async with pool.acquire() as conn:
            parsed_step = uuid.UUID(step_id) if step_id else None
            audit_id = await conn.fetchval(
                """
                INSERT INTO council.security_audits (
                    step_id, target_name, command_or_code, verdict, score, violations, summary
                ) VALUES ($1, $2, $3, $4, $5, $6, $7)
                RETURNING audit_id;
                """,
                parsed_step, target_name, command_or_code, verdict, score,
                json.dumps(violations or []), summary,
            )
            return str(audit_id)
    return run_on_db_loop(_impl())


# =============================================================================
# 4. VAULT SCHEMA: FULL-TEXT SEARCH
# =============================================================================

async def remember_vault_memory(
    key: str,
    content: str,
    record_type: str = "declarative",
    metadata: Optional[Dict[str, Any]] = None,
) -> Optional[str]:
    """Stores record into vault.memories with tsvector index."""
    async def _impl():
        pool = await _get_pool_internal()
        if pool is None:
            return None
        async with pool.acquire() as conn:
            rec_id = await conn.fetchval(
                """
                INSERT INTO vault.memories (key, content, record_type, metadata, created_at)
                VALUES ($1, $2, $3, $4, NOW())
                RETURNING record_id;
                """,
                key, content, record_type, json.dumps(metadata or {}),
            )
            return str(rec_id)
    return run_on_db_loop(_impl())


async def search_vault_memories(query: str, limit: int = 5) -> List[Dict[str, Any]]:
    """Performs full-text tsvector search over vault.memories."""
    async def _impl():
        pool = await _get_pool_internal()
        if pool is None:
            return []
        async with pool.acquire() as conn:
            rows = await conn.fetch(
                """
                SELECT record_id, key, content, record_type, metadata,
                       ts_rank_cd(tsv, plainto_tsquery('english', $1)) AS rank
                FROM vault.memories
                WHERE tsv @@ plainto_tsquery('english', $1)
                ORDER BY rank DESC
                LIMIT $2;
                """,
                query, limit,
            )
            return [dict(r) for r in rows]
    res = run_on_db_loop(_impl())
    return res or []


# =============================================================================
# 5. TELEMETRY SCHEMA: METRICS
# =============================================================================

async def log_telemetry_metrics(cpu_pct: float, ram_pct: float, gpu_mem_used_mb: float = 0.0) -> bool:
    """Logs system metrics."""
    async def _impl():
        pool = await _get_pool_internal()
        if pool is None:
            return False
        async with pool.acquire() as conn:
            await conn.execute(
                """
                INSERT INTO telemetry.system_metrics (cpu_pct, ram_pct, gpu_mem_used_mb, created_at)
                VALUES ($1, $2, $3, NOW());
                """,
                cpu_pct, ram_pct, gpu_mem_used_mb,
            )
            return True
    res = run_on_db_loop(_impl())
    return bool(res)
