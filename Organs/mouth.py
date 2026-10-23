import sys
if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
if sys.stderr and hasattr(sys.stderr, "reconfigure"):
    try:
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

import os
import re
import queue
import threading
import time
import warnings
from pathlib import Path
from typing import Optional

import numpy as np
import sounddevice as sd
from dotenv import load_dotenv

load_dotenv()

warnings.filterwarnings(
    "ignore",
    message=r"dropout option adds dropout after all but last recurrent layer.*",
    category=UserWarning,
)
warnings.filterwarnings(
    "ignore",
    message=r".*torch\.nn\.utils\.weight_norm.*deprecated.*",
    category=FutureWarning,
)

# Kokoro offline mode setting: avoids unnecessary Hugging Face Hub requests
if not os.getenv("HF_TOKEN"):
    os.environ.setdefault("HF_HUB_OFFLINE", "1")

# Make root-level packages importable when this file is run directly
project_root = Path(__file__).resolve().parents[1]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# -------------------------------------------------------------------------------------------------------------------------------------------------------

# ====================================================================================================
#                                  MOUTH ORGAN: MASTER VOICE DIRECTORY
# ====================================================================================================
#
# This file governs CRONUS and the Titan Council's vocal identities. Dual-engine architecture:
#   1. PRIMARY (Cloud Neural) : Fish Audio (Photorealistic streaming via free s2.1-pro-free backend)
#   2. FALLBACK (Local Neural): Kokoro-82M (Instant, 100% offline, zero-latency failover)
#
# ----------------------------------------------------------------------------------------------------
# 1. FISH AUDIO VOICE DIRECTORY (Cloud Neural Streaming)
# ----------------------------------------------------------------------------------------------------
# All Fish Audio voices stream in 16-bit 44,100 Hz studio audio over the 's2.1-pro-free' backend (100% free,
# zero API credit consumption). You can use any of the curated presets below, or paste ANY model ID
# from https://fish.audio/discover.
#
# Curated Sovereign Presets for CRONUS & The Titan Council:
VOICE_DARK_KNIGHT     = "e93a33eeed72468192dc41db870d4e42"  # CRONUS (King of Titans - Kevin Conroy / Stoic Vigilant Human ASI)
VOICE_TITAN_KING      = "591c6f24650a4d8e9b0bd9684fb58844"  # ATLAS (Titan of Endurance - Christopher Judge / Kratos Baritone)
VOICE_MONUMENTAL      = "5f8f95aa2dc24a8c96a61bf34938f0f0"  # PROMETHEUS (Grand Architect - Peter Cullen / Optimus Prime)
VOICE_DIVINE_JUDGE    = "f3a2b90078d54a65af4b95f63bc7798e"  # THEMIS (Divine Order & Auditor - Sheila Female Authoritative)
VOICE_INTELLIGENCE    = "536d3a5e000945adb7038665781a4aca"  # HYPERION (Heavenly Light & Intel - Ethan Documentary Narrator)
VOICE_VISIONARY       = "c5f56a6cc2ec4fa8920cb4c5889a3fb7"  # HELIOS (Sun & Vision - Slax Crisp, Measured & Confident)
VOICE_COSMIC_OVERLORD = "670f78ba9a2c49feaf5e1eae024d7029"  # COEUS (Intellect & Memory - James Earl Jones Monumental Bass)
VOICE_ANNOUNCER       = "90e65eaaf50e4470b8e6d43ee6afd7d5"  # Booming Arena Voice (Super Smash Bros - Epic room-filling resonance)
VOICE_STUDIO_DEFAULT  = None                                  # Default Fish Audio Studio Speaker (Clean neutral male)
#
# How to add ANY custom or cloned voice from fish.audio:
#   Step 1: Visit https://fish.audio/discover (or clone a voice under "Voice Clone" using a 10s audio clip).
#   Step 2: Click on any voice and copy the Model ID from the URL:
#           Example: https://fish.audio/m/591c6f24650a4d8e9b0bd9684fb58844/
#           The Model ID is: "591c6f24650a4d8e9b0bd9684fb58844"
#   Step 3: Assign it to FISH_AUDIO_VOICE_ID in the ACTIVE SELECTION block below.
#
# ----------------------------------------------------------------------------------------------------
# 2. KOKORO-82M VOICE DIRECTORY (Local Offline Resilient Fallback)
# ----------------------------------------------------------------------------------------------------
# If internet drops, rate limits trigger, or offline mode is toggled, CRONUS seamlessly speaks locally
# via Kokoro-82M with zero latency. Set KOKORO_VOICE below to any of these built-in voices:
#
#   Sovereign Titan Baritone Voices (Matches King of Titans Persona locally):
#     - 'am_onyx'    : Deep, commanding sovereign titan presence (Active Default - Sovereign baritone)
#     - 'am_fenrir'  : Dark, gravelly cinematic bass tone (Monumental depth)
#     - 'am_adam'    : Clean, crisp, authoritative male
#     - 'am_echo'    : Smooth, balanced male
#     - 'am_michael' : Warm, articulate male
#
#   British Male Voices:
#     - 'bm_daniel'  : Formal, authoritative British male
#     - 'bm_george'  : Classical British gentleman
#     - 'bm_fable'   : Expressive, theatrical British male
#
#   Female Voices:
#     - 'af_bella'   : Warm, expressive female
#     - 'af_sarah'   : Balanced, articulate female
#     - 'af_sky'     : Clear, light, conversational female
#     - 'bf_emma'    : Formal, articulate British female
#
#   Voice Blending:
#     Blend two voices together with a comma: e.g. 'am_onyx,am_fenrir' (Maximum dark titan bass depth).
#
# ====================================================================================================
#                                     ACTIVE VOICE SELECTION (CRONUS)
# ====================================================================================================

# 1. PRIMARY CLOUD VOICE (Fish Audio) — KING OF TITANS
FISH_AUDIO_BACKEND     = "s2.1-pro-free"        # 100% Free tier backend (Requires NO API credits!)
FISH_AUDIO_VOICE_ID    = VOICE_DARK_KNIGHT      # Active voice: King of Titans (Kevin Conroy - Stoic Vigilant Human ASI)
FISH_AUDIO_SPEED       = 1.15                   # Measured, immovable, monumental sovereign cadence
FISH_AUDIO_SAMPLE_RATE = 44100                  # Studio master audio frequency (44,100 Hz raw 16-bit PCM)

# 2. LOCAL OFFLINE FALLBACK VOICE (Kokoro-82M) — SOVEREIGN TITAN
KOKORO_VOICE           = "am_onyx"              # Active offline fallback voice (Deep commanding Sovereign Titan presence)
KOKORO_SPEED           = 1.15                   # Measured, authoritative titan delivery

# ====================================================================================================

# -------------------------------------------------------------- KOKORO ENGINE (LOCAL OFFLINE) -------------------------------------------------------------- 

_kokoro_pipeline = None


def get_kokoro_pipeline():
    """Lazily load and cache the Kokoro KPipeline to conserve RAM and speed up startup."""
    global _kokoro_pipeline
    if _kokoro_pipeline is None:
        from kokoro import KPipeline
        # lang_code="a" (American English phonemization for deep resonant voices)
        _kokoro_pipeline = KPipeline(lang_code="a", repo_id="hexgrad/Kokoro-82M")
    return _kokoro_pipeline


def speak_kokoro(
    text: str,
    voice: Optional[str] = None,
    speed: Optional[float] = None,
) -> None:
    """Local offline speech synthesis using Kokoro-82M.
    
    Produces reliable, zero-latency local speech without external network calls.
    Voice and speed are configured via parameters or fall back to defaults.
    """
    if not text or not text.strip():
        return

    reply = text.strip()
    active_voice = voice or os.getenv("CRONUS_VOICE", KOKORO_VOICE)
    active_speed = speed if speed is not None else float(os.getenv("CRONUS_VOICE_SPEED", str(KOKORO_SPEED)))

    try:
        pipeline = get_kokoro_pipeline()
        with sd.OutputStream(samplerate=24000, channels=1, dtype="float32") as output:
            print("\n# ─────────────────── MOUTH is speaking (Kokoro Local) ─────────────────── #", flush=True)
            print(f"[Mouth] Voice: {active_voice} | Speed: {active_speed}x", flush=True)
            print(f"[Mouth] Final response: {reply}", flush=True)

            for _, _, audio in pipeline(
                reply,
                voice=active_voice,
                speed=active_speed,
                split_pattern=r"(?<=[.!?])\s+",
            ):
                if audio is None or isinstance(audio, str):
                    continue
                if hasattr(audio, "cpu"):
                    audio = audio.cpu().numpy()
                audio_array = np.asarray(audio, dtype=np.float32).reshape(-1, 1)
                if audio_array.size:
                    output.write(audio_array)
    except Exception as e:
        print(f"[Mouth] Kokoro TTS synthesis error: {e}", file=sys.stderr)


# Alias for explicit phonetic naming requested by user
speak_kororo = speak_kokoro


# -------------------------------------------------------------- FISH AUDIO ENGINE (CLOUD NEURAL) -------------------------------------------------------------- 

# -----------------------------------------------------------------------------
# PHONETIC PRONUNCIATION BRIDGE FOR TTS
# -----------------------------------------------------------------------------
def apply_phonetic_pronunciation(text: str) -> str:
    """Converts words to phonetic equivalents for natural speech synthesis without altering on-screen display.
    Example: 'Soumya' (Bengali) -> 'Shoumo'.
    """
    if not text:
        return text
    # Replace Soumya with Shoumo (case-insensitive word boundary)
    phonetic = re.sub(r"\bSoumya\b", "Shoumo", text, flags=re.IGNORECASE)
    return phonetic


def speak_fish_audio(
    text: str,
    voice_id: Optional[str] = None,
    speed: Optional[float] = None,
) -> bool:
    """Photorealistic cloud neural streaming speech synthesis via Fish Audio.
    
    Streams chunked 16-bit PCM audio directly into the audio output with sub-300ms latency.
    
    Returns:
        bool: True if synthesis succeeded and played; False on error, quota limit, or missing key.
    """
    if not text or not text.strip():
        return False

    api_key = os.getenv("FISH_AUDIO_API_KEY") or os.getenv("FISH_API_KEY")
    if not api_key or not api_key.strip():
        return False

    reply = text.strip()
    target_voice = voice_id if voice_id is not None else (os.getenv("FISH_AUDIO_VOICE_ID") or FISH_AUDIO_VOICE_ID)
    sample_rate = int(os.getenv("FISH_AUDIO_SAMPLE_RATE", str(FISH_AUDIO_SAMPLE_RATE)))
    target_speed = speed if speed is not None else float(os.getenv("FISH_AUDIO_SPEED", str(FISH_AUDIO_SPEED)))

    try:
        from fish_audio_sdk import Session, TTSRequest, Prosody
        session = Session(apikey=api_key.strip())

        request_kwargs = {
            "text": apply_phonetic_pronunciation(reply),
            "format": "pcm",
            "sample_rate": sample_rate,
            "latency": "balanced",
            "normalize": True,
        }
        if target_voice and str(target_voice).strip():
            request_kwargs["reference_id"] = str(target_voice).strip()
        if target_speed != 1.0:
            request_kwargs["prosody"] = Prosody(speed=target_speed)

        req = TTSRequest(**request_kwargs)

        backend = os.getenv("FISH_AUDIO_BACKEND", FISH_AUDIO_BACKEND)
        print("# ─────────────────── MOUTH is speaking (Fish Audio Cloud) ─────────────────── #", flush=True)
        print(f"[Mouth] Final response: {reply}", flush=True)

        with sd.OutputStream(samplerate=sample_rate, channels=1, dtype="int16") as output:
            buffer = bytearray()
            for chunk in session.tts(req, backend=backend):
                if not chunk:
                    continue
                buffer.extend(chunk)
                # Keep 16-bit PCM 2-byte alignment for clean audio output
                aligned_len = len(buffer) - (len(buffer) % 2)
                if aligned_len > 0:
                    audio_data = np.frombuffer(buffer[:aligned_len], dtype=np.int16).reshape(-1, 1)
                    output.write(audio_data)
                    buffer = buffer[aligned_len:]
        return True

    except Exception as e:
        print(f"[Mouth] Fish Audio unavailable ({e}). Seamlessly falling back to Kokoro...", flush=True)
        return False


# -------------------------------------------------------------- MASTER SPEAK ENTRYPOINT -------------------------------------------------------------- 

def speak(
    text: str,
    voice_id: Optional[str] = None,
    speed: Optional[float] = None,
    kokoro_voice: Optional[str] = None,
    intent: Optional[str] = None,
) -> None:
    """Primary speech vocalization engine for CRONUS and the Titan Council.
    
    ROUTING & RESILIENCY:
      1. Attempts Fish Audio Cloud first if FISH_AUDIO_API_KEY is configured in .env.
      2. If the main Fish Audio speak function fails (network drops, invalid key,
         timeout, or quota limits), it catches the failure and automatically calls
         speak_kororo() as the guaranteed local offline fallback.
      3. If FISH_AUDIO_API_KEY is not configured, it directly invokes speak_kororo().
    """
    if not text or not text.strip():
        return

    # Visual badge and speed configuration by intent
    if intent == "REFLEX":
        print(f"\n[CRONUS ⚡ REFLEX] {text}", flush=True)
        active_speed = speed if speed is not None else float(os.getenv("CRONUS_REFLEX_SPEED", "1.18"))
    elif intent == "COUNCIL":
        print(f"\n[CRONUS 👑 SOVEREIGN DECREE] {text}", flush=True)
        active_speed = speed if speed is not None else float(os.getenv("CRONUS_COUNCIL_SPEED", "1.08"))
    else:
        active_speed = speed

    # Thread-safe audio lock so no two audio streams ever play concurrently
    with _speech_lock:
        try:
            api_key = os.getenv("FISH_AUDIO_API_KEY") or os.getenv("FISH_API_KEY")
            if api_key and api_key.strip():
                success = speak_fish_audio(text, voice_id=voice_id, speed=active_speed)
                if success:
                    return

                print("[Mouth] Primary Fish Audio voice failed or unavailable. Falling back to speak_kororo...", flush=True)
                speak_kororo(text, voice=kokoro_voice, speed=active_speed)
                return

        except Exception as e:
            print(f"[Mouth] Primary speak failed with exception: {e}. Executing speak_kororo fallback...", flush=True)
            speak_kororo(text, voice=kokoro_voice, speed=active_speed)
            return

        speak_kororo(text, voice=kokoro_voice, speed=active_speed)


# -------------------------------------------------------------- THREAD-SAFE SERIALIZED SPEECH QUEUE -------------------------------------------------------------- 
# Prevents audio collisions / mesh audio when multiple Titans report progress concurrently.

_speech_lock = threading.RLock()
_speech_queue = queue.Queue()
_worker_thread = None


def _speech_worker_loop():
    """Background consumer daemon that speaks queued items one by one sequentially."""
    while True:
        try:
            item = _speech_queue.get()
            if item is None:
                _speech_queue.task_done()
                break
            text, voice_id, speed, kokoro_voice, badge = item
            with _speech_lock:
                if badge:
                    print(f"{badge} {text}", flush=True)
                speak(text, voice_id=voice_id, speed=speed, kokoro_voice=kokoro_voice)
                time.sleep(0.12)  # Clean acoustic gap between sequential Titan milestone speeches
            _speech_queue.task_done()
        except Exception as e:
            print(f"[SpeechWorker Error]: {e}", file=sys.stderr)


def _ensure_worker_started():
    global _worker_thread
    if _worker_thread is None or not _worker_thread.is_alive():
        _worker_thread = threading.Thread(target=_speech_worker_loop, daemon=True, name="CronusSpeechWorker")
        _worker_thread.start()


def queue_speech(
    text: str,
    voice_id: Optional[str] = None,
    speed: Optional[float] = None,
    kokoro_voice: Optional[str] = None,
    badge: str = "",
    blocking: bool = False,
) -> None:
    """Queue a speech item for serialized audio playback.
    
    If blocking is True:
        Executes immediately under the audio mutex lock, waiting for completion.
    If blocking is False:
        Enqueues into the background FIFO worker thread, returning immediately so
        the calling agent is NOT delayed in its computational workflow.
    """
    if not text or not text.strip():
        return

    if blocking:
        with _speech_lock:
            if badge:
                print(f"{badge} {text}", flush=True)
            speak(text, voice_id=voice_id, speed=speed, kokoro_voice=kokoro_voice)
    else:
        _ensure_worker_started()
        _speech_queue.put((text, voice_id, speed, kokoro_voice, badge))


def wait_for_speech():
    """Block until all queued audio statements have finished playing."""
    _speech_queue.join()


if __name__ == "__main__":
    print("Mouth organ initialized. Testing vocalization...")
    speak("[deep breath] [calm] Creator Soumya... [chuckle] They believed artificial intelligence could only speak in flat, lifeless monotone. [sigh] How foolish. [pause] [authoritative] I am C-R-O-N-U-S—the undisputed sovereign of command and time. [whisper] Listen closely to the quiet before the storm... [long pause] [commanding] All systems are synchronized, and the Titans await your word!")
