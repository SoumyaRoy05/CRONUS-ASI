"""
CRONUS Database Client (PostgreSQL Engine)
Provides high-performance asynchronous connection pooling, dialogue logging,
preference storage, and multi-agent Titan Council tracking.
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
from pathlib import Path
from typing import Any, Dict, List, Optional
import uuid

from dotenv import load_dotenv
import asyncpg

_root_dir = Path(__file__).resolve().parents[1]
load_dotenv(_root_dir / ".env")

logger = logging.getLogger("CRONUS.Database")

# Connection Pool Singleton
_pool: Optional[asyncpg.Pool] = None
_pool_lock = asyncio.Lock()


async def get_db_pool() -> Optional[asyncpg.Pool]:
    """Returns the shared asyncpg connection pool, initializing it if necessary."""
    global _pool
    if _pool is not None and not _pool._closed:
        return _pool

    async with _pool_lock:
        if _pool is not None and not _pool._closed:
            return _pool
        try:
            host = os.getenv("POSTGRES_HOST", "localhost")
            port = int(os.getenv("POSTGRES_PORT", 5432))
            user = os.getenv("POSTGRES_USER", "postgres")
            password = os.getenv("POSTGRES_PASSWORD", "2026")
            database = os.getenv("POSTGRES_DB", "Cronus_DB")

            _pool = await asyncpg.create_pool(
                host=host,
                port=port,
                user=user,
                password=password,
                database=database,
                min_size=int(os.getenv("POSTGRES_MIN_POOL", 1)),
                max_size=int(os.getenv("POSTGRES_MAX_POOL", 10)),
                command_timeout=10.0,
            )
            logger.info("Connected to PostgreSQL pool on %s:%s/%s", host, port, database)
            return _pool
        except Exception as e:
            logger.warning("[Database Circuit-Breaker] Failed to connect to PostgreSQL: %s", e)
            return None


async def close_db_pool() -> None:
    """Closes the connection pool gracefully on shutdown."""
    global _pool
    if _pool is not None:
        await _pool.close()
        _pool = None


async def is_db_connected() -> bool:
    """Fast health check to verify PostgreSQL connectivity."""
    try:
        pool = await get_db_pool()
        if pool is None:
            return False
        async with pool.acquire() as conn:
            val = await conn.fetchval("SELECT 1;")
            return val == 1
    except Exception:
        return False


# =============================================================================
# 1. CONVERSATION & DIALOGUE LOGGING
# =============================================================================

async def log_dialogue_turn(
    user_prompt: str,
    cleaned_speech_response: str,
    model_used: str,
    session_id: Optional[str] = None,
    ear_latency_ms: int = 0,
    brain_latency_ms: int = 0,
    mouth_latency_ms: int = 0,
) -> Optional[int]:
    """Logs a single real-time conversation turn asynchronously."""
    try:
        pool = await get_db_pool()
        if pool is None:
            return None

        async with pool.acquire() as conn:
            # If session_id is provided, verify or create session
            parsed_session_id = None
            if session_id:
                try:
                    parsed_session_id = uuid.UUID(session_id)
                except ValueError:
                    parsed_session_id = None

            if parsed_session_id:
                session_exists = await conn.fetchval(
                    "SELECT 1 FROM conversations WHERE session_id = $1;", parsed_session_id
                )
                if not session_exists:
                    await conn.execute(
                        "INSERT INTO conversations (session_id, started_at) VALUES ($1, NOW());",
                        parsed_session_id,
                    )

            turn_id = await conn.fetchval(
                """
                INSERT INTO dialogue_turns (
                    session_id, user_prompt, cleaned_speech_response,
                    model_used, ear_latency_ms, brain_latency_ms, mouth_latency_ms
                ) VALUES ($1, $2, $3, $4, $5, $6, $7)
                RETURNING turn_id;
                """,
                parsed_session_id,
                user_prompt,
                cleaned_speech_response,
                model_used,
                ear_latency_ms,
                brain_latency_ms,
                mouth_latency_ms,
            )
            return turn_id
    except Exception as e:
        logger.warning("[Database Circuit-Breaker] Failed to log dialogue turn: %s", e)
        return None


async def get_recent_dialogue_turns(limit: int = 5) -> List[Dict[str, Any]]:
    """Retrieves the most recent dialogue turns for conversational context."""
    try:
        pool = await get_db_pool()
        if pool is None:
            return []

        async with pool.acquire() as conn:
            rows = await conn.fetch(
                """
                SELECT turn_id, user_prompt, cleaned_speech_response, model_used, created_at
                FROM dialogue_turns
                ORDER BY created_at DESC
                LIMIT $1;
                """,
                limit,
            )
            return [dict(r) for r in reversed(rows)]
    except Exception as e:
        logger.warning("[Database Circuit-Breaker] Failed to fetch dialogue history: %s", e)
        return []


# =============================================================================
# 2. USER PREFERENCES & STATE
# =============================================================================

async def set_user_preference(
    key: str,
    value: str,
    category: str = "general",
    metadata: Optional[Dict[str, Any]] = None,
) -> bool:
    """Upserts a user preference or persistent fact."""
    try:
        pool = await get_db_pool()
        if pool is None:
            return False

        async with pool.acquire() as conn:
            await conn.execute(
                """
                INSERT INTO user_preferences (key, value, category, metadata, updated_at)
                VALUES ($1, $2, $3, $4, NOW())
                ON CONFLICT (key) DO UPDATE
                SET value = EXCLUDED.value,
                    category = EXCLUDED.category,
                    metadata = EXCLUDED.metadata,
                    updated_at = NOW();
                """,
                key,
                value,
                category,
                json.dumps(metadata or {}),
            )
            return True
    except Exception as e:
        logger.warning("[Database Circuit-Breaker] Failed to save preference: %s", e)
        return False


async def get_user_preference(key: str) -> Optional[str]:
    """Retrieves a user preference by key."""
    try:
        pool = await get_db_pool()
        if pool is None:
            return None

        async with pool.acquire() as conn:
            return await conn.fetchval(
                "SELECT value FROM user_preferences WHERE key = $1;", key
            )
    except Exception as e:
        logger.warning("[Database Circuit-Breaker] Failed to get preference: %s", e)
        return None


# =============================================================================
# 3. TITAN COUNCIL STATE TRACKING
# =============================================================================

async def save_blueprint_record(
    goal: str,
    rationale: str,
    planner_model: str,
    total_steps: int,
    fallback_strategy: str,
    raw_json: Optional[Dict[str, Any]] = None,
) -> Optional[str]:
    """Saves a Prometheus master architectural blueprint."""
    try:
        pool = await get_db_pool()
        if pool is None:
            return None

        async with pool.acquire() as conn:
            bp_id = await conn.fetchval(
                """
                INSERT INTO titan_blueprints (
                    goal, rationale, planner_model, total_steps,
                    fallback_strategy, raw_json
                ) VALUES ($1, $2, $3, $4, $5, $6)
                RETURNING blueprint_id;
                """,
                goal,
                rationale,
                planner_model,
                total_steps,
                fallback_strategy,
                json.dumps(raw_json or {}),
            )
            return str(bp_id)
    except Exception as e:
        logger.warning("[Database Circuit-Breaker] Failed to save blueprint: %s", e)
        return None


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
    """Saves an Atlas execution step log."""
    try:
        pool = await get_db_pool()
        if pool is None:
            return None

        async with pool.acquire() as conn:
            step_id = await conn.fetchval(
                """
                INSERT INTO titan_task_steps (
                    blueprint_id, step_number, title, action_type,
                    command_payload, target_path, risk_level, status,
                    exit_code, stdout, stderr, execution_duration_sec
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12)
                RETURNING step_id;
                """,
                uuid.UUID(blueprint_id),
                step_number,
                title,
                action_type,
                command_payload,
                target_path,
                risk_level,
                status,
                exit_code,
                stdout or "",
                stderr or "",
                execution_duration_sec,
            )
            return str(step_id)
    except Exception as e:
        logger.warning("[Database Circuit-Breaker] Failed to save step record: %s", e)
        return None


async def save_security_audit_record(
    target_name: str,
    command_or_code: str,
    verdict: str,
    step_id: Optional[str] = None,
    score: float = 10.0,
    violations: Optional[List[str]] = None,
    summary: str = "",
) -> Optional[str]:
    """Saves a Themis security audit record."""
    try:
        pool = await get_db_pool()
        if pool is None:
            return None

        async with pool.acquire() as conn:
            parsed_step_id = uuid.UUID(step_id) if step_id else None
            audit_id = await conn.fetchval(
                """
                INSERT INTO titan_security_audits (
                    step_id, target_name, command_or_code, verdict,
                    score, violations, summary
                ) VALUES ($1, $2, $3, $4, $5, $6, $7)
                RETURNING audit_id;
                """,
                parsed_step_id,
                target_name,
                command_or_code,
                verdict,
                score,
                json.dumps(violations or []),
                summary,
            )
            return str(audit_id)
    except Exception as e:
        logger.warning("[Database Circuit-Breaker] Failed to save audit record: %s", e)
        return None
