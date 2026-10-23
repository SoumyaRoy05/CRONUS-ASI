# Ears Organ (`Organs/ears.py`)

The **Ears** organ provides real-time acoustic hearing, wake detection, and continuous speech-to-text (STT) for CRONUS. It leverages GPU-accelerated **Faster Whisper** running on local NVIDIA Tensor Cores.

---

## 1. Core Engineering Highlights

* **16,000 Hz Mono Streaming**: Audio is recorded at the standard 16 kHz sample rate required by Whisper acoustic models.
* **Thread-Safe Queue Buffering**: Uses a non-blocking background `SoundDevice.InputStream` callback that pushes 0.5s audio blocks into a thread-safe `queue.Queue`.
* **Hardware Acceleration**: Automatically discovers and injects NVIDIA CUDA and cuBLAS DLLs (`nvidia_dir / bin`) into the Windows runtime path.
* **Calibrated Energy Thresholding**: Dynamically computes ambient root-mean-square (RMS) noise levels before listening to prevent background noise false-triggers.
* **Tuned Real-Time Responsiveness**:
  * `PHRASE_PAUSE_SECONDS = 0.3` (300ms silence detection immediately triggers transcription).
  * `MIN_SPEECH_DURATION_SECONDS = 0.2` (rejects brief mic pops or accidental key clatter).
  * `SESSION_TIMEOUT_SECONDS = 4.0` (safety watchdog preventing indefinite listening deadlocks).

---

## 2. Technical Architecture

```text
+--------------------------------------------------------------------------+
|                        EARS PIPELINE ARCHITECTURE                        |
+--------------------------------------------------------------------------+

   Microphone Input
         |
         v
   [ SoundDevice InputStream ]  (16 kHz, Mono, float32)
         |
         |---> audio_callback() pushes 0.5s chunks into queue.Queue
         |
         v
   [ calibrate_threshold() ]
         * Computes ambient RMS noise level over 1.0s
         * Sets dynamic energy floor: threshold = max(0.015, avg_rms * 1.5)
         |
         v
   [ hear() Event Loop ]
         |
         |---> Read chunk from queue
         |---> Calculate chunk RMS energy
         |
         +---> Is Energy > Threshold?
         |        |
         |        +-- YES: Set speech_started = True
         |        |        Append chunk to speech_buffer
         |        |        Reset pause_counter
         |        |
         |        +-- NO:  If speech_started is True:
         |                 Increment pause_counter
         |                 If pause_counter >= 300ms:
         |                     BREAK and transcribe!
         v
   [ Faster Whisper CUDA Inference ]
         * Model: 'small' on device='cuda', compute_type='float16'
         * Segments generator extracts text with beam_size=1 (speed tuned)
         v
   [ Transcribed Text Output ]
```

---

## 3. Configuration & Tuning Parameters

| Parameter | Default Value | Purpose |
| :--- | :--- | :--- |
| `SAMPLE_RATE` | `16000` | Standard Whisper audio frequency |
| `BLOCK_DURATION` | `0.5` | Duration of each individual buffer slice in seconds |
| `PHRASE_PAUSE_SECONDS` | `0.3` | Silence duration required to finalize a phrase (tuned for snappy conversational interaction) |
| `MIN_SPEECH_DURATION_SECONDS` | `0.2` | Minimum speech duration required to qualify as legitimate user voice |
| `SESSION_TIMEOUT_SECONDS` | `4.0` | Fallback timeout if no speech is detected |

---

## 4. Public API

```python
from Organs.ears import hear

# Starts microphone stream, listens for user speech, returns clean transcript
transcribed_text = hear()
print(f"User said: {transcribed_text}")
```
