# ---------- Warnings Enclosure ---------- #

import logging

class _AfcWarningFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        return "Direct use of automatic function calling" not in record.getMessage()


logging.getLogger("google_genai.models").addFilter(_AfcWarningFilter())

# ---------- LLM CONFIGURATION ---------- #

import os
import socket
from pathlib import Path

from dotenv import load_dotenv
from pydantic import SecretStr

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq
from langchain_ollama import ChatOllama
from langchain_openai import ChatOpenAI

load_dotenv(Path(__file__).resolve().parent / ".env")


gemini_key = os.getenv("GEMINI_API_KEY")
groq_key = os.getenv("GROQ_API_KEY")
nvidia_key = os.getenv("NVIDIA_API_KEY")
ollama_model = os.getenv("OLLAMA_MODEL", "qwen2.5:3b")
groq_timeout = max(10.0, float(os.getenv("CRONUS_LLM_TIMEOUT", os.getenv("ATLAS_LLM_TIMEOUT", "10"))))
nvidia_timeout = max(20.0, float(os.getenv("NVIDIA_LLM_TIMEOUT", "20.0")))


def _secret(value: str | None) -> SecretStr | None:
    return SecretStr(value) if value else None


def _build_groq(model: str) -> ChatGroq:
    return ChatGroq(
        model=model,
        temperature=0.7,
        max_tokens=512,
        reasoning_effort="low",
        reasoning_format="hidden",
        timeout=groq_timeout,
        max_retries=0,
        api_key=_secret(groq_key),
    )


def _build_gemini(model: str) -> ChatGoogleGenerativeAI:
    # Uses native SDK RPC transport for instant response without artificial deadline bottlenecks
    return ChatGoogleGenerativeAI(
        model=model,
        temperature=0.7,
        max_tokens=128,
        thinking_level="low",
        google_api_key=_secret(gemini_key),
    )


def _build_nvidia(
    model: str = "nvidia/nemotron-3-ultra-550b-a55b",
    max_tokens: int = 512,
    temperature: float = 0.7,
) -> ChatOpenAI:
    """Builds a high-performance NVIDIA NIM client (e.g. Nemotron 3 Ultra 550B MoE)."""
    return ChatOpenAI(
        model=model,
        base_url="https://integrate.api.nvidia.com/v1",
        api_key=_secret(nvidia_key),
        temperature=temperature,
        max_tokens=max_tokens,
        timeout=nvidia_timeout,
        max_retries=1,
    )


# Tier 1: Groq (ultra-low latency conversational: ~300ms)
t1a = _build_groq("openai/gpt-oss-120b") if groq_key else None
t1b = _build_groq("openai/gpt-oss-20b") if groq_key else None

# Tier 2: NVIDIA NIM (Nemotron 3 Ultra 550B MoE flagship reasoning)
t2_nemotron = _build_nvidia("nvidia/nemotron-3-ultra-550b-a55b", max_tokens=512) if nvidia_key else None
t2_nemotron_reasoning = _build_nvidia("nvidia/nemotron-3-nano-omni-30b-a3b-reasoning", max_tokens=512) if nvidia_key else None

# Tier 3: Google Gemini (high-reliability cloud fallback)
t3a = _build_gemini("gemini-flash-latest") if gemini_key else None
t3b = _build_gemini("gemini-pro-latest") if gemini_key else None

# Tier 4: Ollama (zero-network local offline fallback)
t4_local = ChatOllama(model=ollama_model, temperature=0.7, num_predict=128)

# Aliases for backwards compatibility with existing modules
t2a = t3a
t2b = t3b
t3 = t4_local


def _available_cloud_models():
    """Returns a list of available cloud models based on active API keys."""
    cloud_candidates = [t1a, t1b, t2_nemotron, t3a, t3b]
    return [provider for provider in cloud_candidates if provider is not None]


def _make_waterfall(online: bool):
    """Constructs a waterfall chain of LLMs based on online availability."""
    candidates = _available_cloud_models() + [t4_local] if online else [t4_local]
    primary, *fallbacks = candidates
    return primary.with_fallbacks(fallbacks, exceptions_to_handle=(Exception,))


def _make_reasoning_waterfall(online: bool):
    """Constructs a high-reasoning waterfall chain with Nemotron 3 Ultra as primary."""
    if not online:
        return t4_local
    reasoning_candidates = [
        c for c in (t2_nemotron, t3b, t1a, t3a) if c is not None
    ]
    if not reasoning_candidates:
        return t4_local
    primary, *fallbacks = reasoning_candidates + [t4_local]
    return primary.with_fallbacks(fallbacks, exceptions_to_handle=(Exception,))


def is_online(host: str = "8.8.8.8", port: int = 53, timeout: float = 1.0) -> bool:
    """Checks DNS connectivity to skip cloud timeouts when offline."""
    try:
        with socket.create_connection((host, port), timeout=timeout):
            pass
        return True
    except OSError:
        return False

# -----------------------------------------------------------------------------
# LLM ENTRYPOINTS
# -----------------------------------------------------------------------------
def get_llm():
    """Return a fast cloud-first chain (Groq -> Nemotron 3 Ultra -> Gemini -> Ollama)."""
    return _make_waterfall(is_online())


def get_reasoning_llm():
    """Return an advanced reasoning chain (Nemotron 3 Ultra 550B -> Gemini Pro -> Groq 120B -> Ollama)."""
    return _make_reasoning_waterfall(is_online())


llm_waterfall = _make_waterfall(is_online())
