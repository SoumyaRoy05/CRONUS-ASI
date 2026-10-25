"""
Behaviour Package - CRONUS Sovereign Behaviour & Directives
"""

from .persona import (
    get_pure_persona,
    get_system_prompt,
    get_fast_memory_context,
    USER_MD_PATH,
    MEMORY_MD_PATH,
    NOBLE_TITLES,
    ASSISTANT_ALIASES,
)

from .directives import (
    get_acoustic_directives,
    ACOUSTIC_DIRECTIVES,
    FORMATTING_CONSTRAINTS,
)

from .receipts import (
    get_wake_receipt,
    get_dismiss_receipt,
    get_shutdown_receipt,
    get_offline_receipt,
    WAKE_RESPONSES,
    DISMISS_RESPONSES,
    SHUTDOWN_RESPONSES,
    OFFLINE_RESPONSES,
)

from .router_prompt import get_router_prompt

__all__ = [
    # Persona
    "get_pure_persona",
    "get_system_prompt",
    "get_fast_memory_context",
    "USER_MD_PATH",
    "MEMORY_MD_PATH",
    "NOBLE_TITLES",
    "ASSISTANT_ALIASES",
    # Directives
    "get_acoustic_directives",
    "ACOUSTIC_DIRECTIVES",
    "FORMATTING_CONSTRAINTS",
    # Receipts
    "get_wake_receipt",
    "get_dismiss_receipt",
    "get_shutdown_receipt",
    "get_offline_receipt",
    # Router
    "get_router_prompt",
]
