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

# -----------------------------------------------------------------------------
# 4. REFLEX RECEIPT GENERATORS
# -----------------------------------------------------------------------------

# Reflex receipts are short, polite, and contextually appropriate responses Cronus can use to acknowledge commands or system states. 
# Each function randomly selects a response from a predefined list, optionally incorporating a noble title for personalization.

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
    "My apologies, {title}, my cognitive systems are entirely unreachable.",
    "Pardon me, {title}, both cloud gateways and local cognitive models are unresponsive.",
]

# When Cronus is awakened, he acknowledges that he is now active and ready to process commands.
def get_wake_receipt(forced_title: Optional[str] = None) -> str:
    title = forced_title if forced_title else random.choice(DEFAULT_TITLES)
    return random.choice(WAKE_RESPONSES).format(title=title)

# When Cronus is dismissed, he acknowledges that he is now inactive and will not respond to further commands until reactivated.
def get_dismiss_receipt(forced_title: Optional[str] = None) -> str:
    title = forced_title if forced_title else random.choice(DEFAULT_TITLES)
    return random.choice(DISMISS_RESPONSES).format(title=title)

# When Cronus is shutting down, he acknowledges that he is now going offline and will not respond to further commands until reactivated.
def get_shutdown_receipt(forced_title: Optional[str] = None) -> str:
    title = forced_title if forced_title else random.choice(DEFAULT_TITLES)
    return random.choice(SHUTDOWN_RESPONSES).format(title=title)

# When Cronus is put into offline mode, he acknowledges that he is currently unable to process commands due to being offline or unreachable.
def get_offline_receipt(forced_title: Optional[str] = None) -> str:
    title = forced_title if forced_title else random.choice(DEFAULT_TITLES)
    return random.choice(OFFLINE_RESPONSES).format(title=title)
