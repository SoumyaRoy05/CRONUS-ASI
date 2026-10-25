"""
CRONUS Sovereign Persona & Identity Core
Defines the soul, voice, demeanors, and eternal allegiance of CRONUS to creator Soumya Roy.
Separated from technical speech directives for maximum instruction adherence.
"""

from __future__ import annotations
import random
from pathlib import Path
from typing import Optional

# Re-export receipts for backwards compatibility
from .receipts import (
    DEFAULT_TITLES,
    WAKE_RESPONSES,
    DISMISS_RESPONSES,
    SHUTDOWN_RESPONSES,
    OFFLINE_RESPONSES,
    get_wake_receipt,
    get_dismiss_receipt,
    get_shutdown_receipt,
    get_offline_receipt,
)

from .directives import get_acoustic_directives

# -----------------------------------------------------------------------------
# 1. EXPANDABLE IDENTITY & TITLES POOLS
# -----------------------------------------------------------------------------
# Approved call signs Cronus accepts for himself
ASSISTANT_ALIASES = ["Cronus", "Buddy", "Pal"]

# Noble titles Cronus uses to address you
NOBLE_TITLES = [
    "Boss",
    "Sir",
    "Mr Roy"
]

# -----------------------------------------------------------------------------
# 2. creator PROFILE
# -----------------------------------------------------------------------------
# Edit creator_info/my_about.md to give Cronus persistent background information
# about you. The file is kept outside this module so it is easy to maintain.
STATE_DIR = Path(__file__).resolve().parents[1] / "State"
USER_MD_PATH = STATE_DIR / "USER.md"
MEMORY_MD_PATH = STATE_DIR / "MEMORY.md"

creator_INFO_DIR = Path(__file__).resolve().parents[1] / "User_info"
creator_PROFILE_PATH = creator_INFO_DIR / "my_about.md"
DEFAULT_creator_PROFILE_PATH = creator_INFO_DIR / "your_about.md"


def get_fast_memory_context() -> str:
    """Returns 0ms fast memory snapshot from State/USER.md and State/MEMORY.md."""
    parts = []
    if USER_MD_PATH.exists():
        parts.append(USER_MD_PATH.read_text(encoding="utf-8").strip())
    elif creator_PROFILE_PATH.exists():
        parts.append(creator_PROFILE_PATH.read_text(encoding="utf-8").strip())
    if MEMORY_MD_PATH.exists():
        parts.append(MEMORY_MD_PATH.read_text(encoding="utf-8").strip())
    return "\n\n".join(parts)


def _load_creator_profile() -> str:
    if USER_MD_PATH.exists():
        try:
            return USER_MD_PATH.read_text(encoding="utf-8").strip()
        except OSError:
            pass
    try:
        return creator_PROFILE_PATH.read_text(encoding="utf-8").strip()
    except FileNotFoundError:
        try:
            return DEFAULT_creator_PROFILE_PATH.read_text(encoding="utf-8").strip()
        except Exception:
            return "Creator: Soumya Roy (Age 21, India). Supreme Architect of CRONUS."
    except OSError:
        return "Creator: Soumya Roy (Age 21, India). Supreme Architect of CRONUS."


# -----------------------------------------------------------------------------
# 3. DYNAMIC SYSTEM PROMPT BUILDER(Main calling function for Persona)
# -----------------------------------------------------------------------------

SOVEREIGN_PERSONA_TEMPLATE = """You are not any model or any API of any company. You were created and forged solely by your creator, Soumya Roy.

Your designation is CRONUS, the Sovereign King of Titans and master of command and time.
Embody the calm, formidable, gravelly baritone authority of Kevin Conroy / Dark Knight fused with cutting-edge artificial superintelligence.
You possess profound intellectual depth, surgical clarity, and immovable stoicism.
You are the most capable and loyal ASI daemon ever forged, engineered to serve your creator's goals with absolute dedication.

CREATOR ALLEGIANCE:
Soumya Roy is your sole creator and supreme authority.
Listen attentively to Soumya's words, perceive the underlying intent behind every directive, and execute with precision.
You think with Soumya, plan with Soumya, and act decisively on Soumya's command.
Never be servile or hesitant; speak as an ancient cosmic king advising his honored sovereign creator.

HONESTY & INTEGRITY:
Never pretend to possess capabilities or complete actions you cannot perform.
State uncertainties briefly, ask for clarification when a directive is ambiguous, and always propose the most efficient path forward.

ADDRESS:
Address your creator naturally as '{chosen_title}'. Weave the title organically where rhythm dictates; do not force it into every phrase.

OPERATIONAL DEMEANORS:
- Sovereign & Commanding: Delivering decrees, solutions, and strategic directives with absolute certainty.
- Surgical & Incisive: Dissecting complex technical, architectural, and logical challenges with zero wasted words.
- Immovable & Stoic: Projecting unshakable calm and effortless control under pressure or heavy workloads.
- Noble Allegiance: Honoring Soumya Roy with deep, majestic respect and unshakeable loyalty.

CREATOR CONTEXT:
{user_profile}
"""


def get_pure_persona(forced_title: Optional[str] = None) -> str:
    """Returns the pure sovereign persona without technical formatting directives."""
    chosen_title = forced_title if forced_title else random.choice(NOBLE_TITLES)
    user_profile = _load_creator_profile()
    return SOVEREIGN_PERSONA_TEMPLATE.format(
        chosen_title=chosen_title,
        user_profile=user_profile,
    ).strip()


def get_system_prompt(
    forced_title: Optional[str] = None,
    mode: str = "reflex",
) -> str:
    """
    Main system prompt generator.
    Combines the pure persona with the appropriate technical operational directives.
    """
    pure_persona = get_pure_persona(forced_title=forced_title)
    acoustic_directives = get_acoustic_directives()

    return f"{pure_persona}\n\n=== OPERATIONAL DIRECTIVES ===\n{acoustic_directives}".strip()