"""
CRONUS Spoken Receipts & Deterministic Voice Acknowledgments
Fast, zero-latency canned responses that never touch external LLM APIs,
conserving API rate limits and guaranteeing instant audio feedback.
"""

from __future__ import annotations
import random
from typing import Optional

# Approved noble titles
DEFAULT_TITLES = ["Sir", "Boss", "Mr Roy"]

WAKE_RESPONSES = [
    "At your command, {title}.",
    "Systems primed and listening, {title}.",
    "Standing by, {title}.",
    "At your service, {title}.",
    "Ready when you are, {title}.",
]

DISMISS_RESPONSES = [
    "Standing down, {title}.",
    "Entering standby mode, {title}.",
    "Retiring to background processes, {title}.",
    "Until next time, {title}.",
]

SHUTDOWN_RESPONSES = [
    "Deactivating all systems, {title}. Standing down completely.",
    "Powering down cognitive and acoustic cores, {title}.",
    "Terminating runtime processes. Farewell, {title}.",
]

OFFLINE_RESPONSES = [
    "My apologies, {title}, my cloud cognitive systems are unreachable. Operating in local mode.",
    "Pardon me, {title}, cloud gateways are unresponsive. Engaging local neural fallback.",
]

def get_wake_receipt(forced_title: Optional[str] = None) -> str:
    """Acknowledges system awakening."""
    title = forced_title if forced_title else random.choice(DEFAULT_TITLES)
    return random.choice(WAKE_RESPONSES).format(title=title)

def get_dismiss_receipt(forced_title: Optional[str] = None) -> str:
    """Acknowledges standby request."""
    title = forced_title if forced_title else random.choice(DEFAULT_TITLES)
    return random.choice(DISMISS_RESPONSES).format(title=title)

def get_shutdown_receipt(forced_title: Optional[str] = None) -> str:
    """Acknowledges system shutdown."""
    title = forced_title if forced_title else random.choice(DEFAULT_TITLES)
    return random.choice(SHUTDOWN_RESPONSES).format(title=title)

def get_offline_receipt(forced_title: Optional[str] = None) -> str:
    """Acknowledges offline state."""
    title = forced_title if forced_title else random.choice(DEFAULT_TITLES)
    return random.choice(OFFLINE_RESPONSES).format(title=title)
