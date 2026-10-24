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
import sys
from pathlib import Path
from dotenv import load_dotenv

# -----------------------------------------------------------------------------
# 1. Hardware Acceleration & Dynamic Environment Setup
# -----------------------------------------------------------------------------
# Inject NVIDIA CUDA and cuBLAS DLL binaries into the Windows runtime path
nvidia_dir = Path(sys.prefix) / "Lib" / "site-packages" / "nvidia"
if nvidia_dir.exists():
    for bin_folder in nvidia_dir.rglob("bin"):
        if bin_folder.is_dir():
            os.add_dll_directory(str(bin_folder))
            os.environ["PATH"] = str(bin_folder) + os.pathsep + os.environ.get("PATH", "")

from faster_whisper import WhisperModel

# Locate and load environment variables from the project root .env
root_dir = Path(__file__).resolve().parent
load_dotenv(dotenv_path=root_dir / ".env")

# Route Hugging Face models to a creator-specific cache unless explicitly configured.
if not os.getenv("HF_HOME"):
    local_app_data = os.getenv("LOCALAPPDATA")
    cache_root = Path(local_app_data) if local_app_data else Path.home() / ".cache"
    os.environ["HF_HOME"] = str(cache_root / "Cronus" / "huggingface")


# -----------------------------------------------------------------------------
# 2. Sensory Organ Import
# -----------------------------------------------------------------------------
from Organs.ears import hear  # Auditory sensory organ: wake word detection + speech-to-text
from Organs.mouth import speak, wait_until_mouth_silent  # Vocal organ + acoustic drainage
from Organs.brain import Brain  # Cognitive engine: multi-graph orchestration
from Behaviour.persona import get_wake_receipt  # Persona & canned receipts


# -----------------------------------------------------------------------------
# 3. Central Nervous System Lifecycle Supervisor
# -----------------------------------------------------------------------------
def _enforce_single_instance():
    """Guarantees only one instance of CRONUS runs at any time, preventing duplicate voice processes."""
    try:
        import ctypes
        ERROR_ALREADY_EXISTS = 183
        kernel32 = ctypes.windll.kernel32
        mutex = kernel32.CreateMutexW(None, False, "CRONUS_SINGLE_INSTANCE_MUTEX")
        if kernel32.GetLastError() == ERROR_ALREADY_EXISTS:
            print("\n[CRONUS 👑] [ALERT] Another instance of CRONUS is already active on this system.", flush=True)
            print("[CRONUS 👑] [ALERT] Terminating duplicate process to prevent overlapping voice output.\n", flush=True)
            sys.exit(0)
        return mutex
    except Exception:
        return None


def main() -> None:
    """Master ignition routine for Cronus.

    Initializes hardware contexts, boots the acoustic sensory organ,
    and supervises the event loop until clean termination.
    """
    _mutex = _enforce_single_instance()

    print("\n", flush=True)
    print("=" * 60, flush=True)
    print("              CRONUS DIGITAL STEWARD ONLINE                 ", flush=True)
    print("=" * 60, flush=True)
    print("\n", flush=True)

    try:
        print("# ─────────────────── Central Nervous System [CNS] Engaged ─────────────────── #", flush=True)
        print("[CNS] Initializing acoustic and cognitive subsystems...", flush=True)
        print("[CNS] Loading the faster-whisper model on your CUDA (float16)...", flush=True)

        whisper_model = WhisperModel(
            "base.en",
            device="cuda",
            compute_type="float16",
            local_files_only=True,
        )
        print("[CNS] Faster-whisper neural model loaded successfully.", flush=True)

        # the brain instance stores the mouth function for later use in the conversation loop
        brain = Brain(mouth=speak)
        wake_receipt = get_wake_receipt()
        brain.remember_assistant_message(wake_receipt) # Remember the wake receipt in the brain's history
        print("[CNS] Ignition sequence complete. Acoustic sensory organ active.", flush=True)
        speak(wake_receipt)

        # Reuse one Brain and one Whisper model for the complete session.
        while True:
            # Guarantee physical audio output and room echoes are 100% drained before mic opens
            wait_until_mouth_silent()
            transcript = hear(whisper_model)
            if transcript:
                brain.think(transcript)

    # Handle manual keyboard interrupts (e.g., Ctrl+C) for graceful shutdown
    except KeyboardInterrupt:
        print("\n[CNS] Manual keyboard interrupt received. Commencing safe teardown...")

    # Handle system exit signals (e.g., from a shutdown command)
    except SystemExit:
        print("\n[CNS] System power-down command confirmed. Standing down...")

    # Handle any other unexpected exceptions to prevent the program from crashing silently
    except Exception as e:
        print(f"\n[CNS - Critical Fault]: Unhandled pipeline exception: {e}")

    finally:
        print("[CNS] Audio hardware unhooked. GPU contexts released. System offline.")



if __name__ == "__main__":
    main()
