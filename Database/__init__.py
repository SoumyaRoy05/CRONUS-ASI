"""
CRONUS Database Engine
Asynchronous PostgreSQL client with zero-crash circuit-breaker resilience.
"""

from .client import (
    get_db_pool,
    close_db_pool,
    is_db_connected,
    log_dialogue_turn,
    get_recent_dialogue_turns,
    set_user_preference,
    get_user_preference,
    save_blueprint_record,
    save_task_step_record,
    save_security_audit_record,
)

__all__ = [
    "get_db_pool",
    "close_db_pool",
    "is_db_connected",
    "log_dialogue_turn",
    "get_recent_dialogue_turns",
    "set_user_preference",
    "get_user_preference",
    "save_blueprint_record",
    "save_task_step_record",
    "save_security_audit_record",
]
