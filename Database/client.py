"""
CRONUS Database Client (PostgreSQL 18 Engine)
High-performance asynchronous connection pooling, dialogue logging,
preference storage, Titan Council blueprint tracking, and Vault full-text memory.

Schemas:
  - core: conversations, dialogue_turns, user_preferences
  - council: blueprints, task_steps, security_audits, deliberations
  - vault: memories (tsvector GIN hybrid search), checkpoints, semantic_embeddings
  - telemetry: system_metrics, simulations
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

        host = os.getenv("POSTGRES_HOST", "localhost")
        port = int(os.getenv("POSTGRES_PORT", "5432"))
        user = os.getenv("POSTGRES_USER", "postgres")
        password = os.getenv("POSTGRES_PASSWORD", "2026")
        database = os.getenv("POSTGRES_DB", "cronus_master")

        try:
            _pool = await asyncpg.create_pool(
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
            return _pool
        except Exception as e:
            logger.warning("[Database Circuit-Breaker] PostgreSQL connection failed: %s. Operating in resilient offline mode.", e)
            return None


async def close_db_pool() -> None:
    """Gracefully closes the database connection pool."""
    global _pool
    if _pool is not None:
        await _pool.close()
        _pool = None
        logger.info("[Database] Connection pool closed.")


async def is_db_connected() -> bool:
    """Alias for check_database_health."""
    return await check_database_health()


async def check_database_health() -> bool:
    """Fast liveness check verifying PostgreSQL responsiveness."""
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
# 1. CORE SCHEMA: DIALOGUE & CONVERSATIONS
# =============================================================================

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
    """Logs a completed dialogue turn into core.dialogue_turns."""
    try:
        pool = await get_db_pool()
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
                session_exists = await conn.fetchval(
                    "SELECT 1 FROM core.conversations WHERE session_id = $1;", parsed_session_id
                )
                if not session_exists:
                    await conn.execute(
                        "INSERT INTO core.conversations (session_id, started_at) VALUES ($1, NOW());",
                        parsed_session_id,
                    )

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
                SELECT turn_id, user_prompt, cleaned_speech_response, model_used, intent, created_at
                FROM core.dialogue_turns
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
# 2. CORE SCHEMA: USER PREFERENCES & STATE
# =============================================================================

async def set_user_preference(
    key: str,
    value: str,
    category: str = "general",
    metadata: Optional[Dict[str, Any]] = None,
) -> bool:
    """Upserts a user preference into core.user_preferences."""
    try:
        pool = await get_db_pool()
        if pool is None:
            return False

        async with pool.acquire() as conn:
            await conn.execute(
                """
                INSERT INTO core.user_preferences (key, value, category, metadata, updated_at)
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
    """Retrieves a user preference from core.user_preferences."""
    try:
        pool = await get_db_pool()
        if pool is None:
            return None

        async with pool.acquire() as conn:
            return await conn.fetchval(
                "SELECT value FROM core.user_preferences WHERE key = $1;", key
            )
    except Exception as e:
        logger.warning("[Database Circuit-Breaker] Failed to get preference: %s", e)
        return None


# =============================================================================
# 3. COUNCIL SCHEMA: TITAN BLUEPRINTS & AUDITS
# =============================================================================

async def save_blueprint_record(
    goal: str,
    rationale: str,
    planner_model: str,
    total_steps: int,
    fallback_strategy: str,
    raw_json: Optional[Dict[str, Any]] = None,
) -> Optional[str]:
    """Saves a Prometheus master blueprint into council.blueprints."""
    try:
        pool = await get_db_pool()
        if pool is None:
            return None

        async with pool.acquire() as conn:
            bp_id = await conn.fetchval(
                """
                INSERT INTO council.blueprints (
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
    """Saves an Atlas execution step log into council.task_steps."""
    try:
        pool = await get_db_pool()
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
    """Saves a Themis security audit record into council.security_audits."""
    try:
        pool = await get_db_pool()
        if pool is None:
            return None

        async with pool.acquire() as conn:
            parsed_step_id = uuid.UUID(step_id) if step_id else None
            audit_id = await conn.fetchval(
                """
                INSERT INTO council.security_audits (
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


# =============================================================================
# 4. VAULT SCHEMA: FULL-TEXT SEARCH & MEMORY
# =============================================================================

async def remember_vault_memory(
    key: str,
    content: str,
    record_type: str = "declarative",
    metadata: Optional[Dict[str, Any]] = None,
) -> Optional[str]:
    """Stores a knowledge record into vault.memories with automatic tsvector indexing."""
    try:
        pool = await get_db_pool()
        if pool is None:
            return None

        async with pool.acquire() as conn:
            rec_id = await conn.fetchval(
                """
                INSERT INTO vault.memories (key, content, record_type, metadata, created_at)
                VALUES ($1, $2, $3, $4, NOW())
                RETURNING record_id;
                """,
                key,
                content,
                record_type,
                json.dumps(metadata or {}),
            )
            return str(rec_id)
    except Exception as e:
        logger.warning("[Database Circuit-Breaker] Failed to store vault memory: %s", e)
        return None


async def search_vault_memories(query: str, limit: int = 5) -> List[Dict[str, Any]]:
    """Performs full-text search across vault.memories using tsvector and GIN index."""
    try:
        pool = await get_db_pool()
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
                query,
                limit,
            )
            return [dict(r) for r in rows]
    except Exception as e:
        logger.warning("[Database Circuit-Breaker] Failed to search vault memories: %s", e)
        return []


# =============================================================================
# 5. TELEMETRY SCHEMA: METRICS
# =============================================================================

async def log_telemetry_metrics(cpu_pct: float, ram_pct: float, gpu_mem_used_mb: float = 0.0) -> bool:
    """Logs system metrics into telemetry.system_metrics."""
    try:
        pool = await get_db_pool()
        if pool is None:
            return False

        async with pool.acquire() as conn:
            await conn.execute(
                """
                INSERT INTO telemetry.system_metrics (cpu_pct, ram_pct, gpu_mem_used_mb, created_at)
                VALUES ($1, $2, $3, NOW());
                """,
                cpu_pct,
                ram_pct,
                gpu_mem_used_mb,
            )
            return True
    except Exception as e:
        logger.warning("[Database Circuit-Breaker] Failed to log telemetry: %s", e)
        return False
