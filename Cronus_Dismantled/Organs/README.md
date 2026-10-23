# CRONUS Sensory-Vocal Organ Subsystem

The **Organs** subsystem forms the bio-mimetic physical interface of CRONUS. It handles continuous, non-blocking acoustic listening, intelligent cognitive orchestration, and real-time neural vocalization.

---

## 1. Organ Roster & Functional Matrix

| Organ | Implementation | Primary Technology | Primary Function | Typical Latency |
| :--- | :--- | :--- | :--- | :--- |
| **Ears** | [Organs/ears.py](file:///D:/Codes/CRONUS-ASI/Organs/ears.py) | `faster-whisper` (CUDA), `sounddevice`, `numpy` | Auditory sensing, RMS energy calibration, real-time STT | 200ms to 400ms |
| **Brain** | [Organs/brain.py](file:///D:/Codes/CRONUS-ASI/Organs/brain.py) | `LangGraph`, `ChatGroq`, `ChatOpenAI`, `ChatGoogleGenAI` | Cognitive state graph, persona injection, multi-tier LLM waterfall | 300ms (Groq) / 1s (Gemini/NVIDIA) |
| **Mouth** | [Organs/mouth.py](file:///D:/Codes/CRONUS-ASI/Organs/mouth.py) | `Kokoro-82M`, `sounddevice`, `phonemizer` | Neural text-to-speech synthesis, 24kHz stream playback | 150ms to 350ms first-chunk |

---

## 2. Real-Time Operational Loop

```text
+-----------------------------------------------------------------------------------+
|                           THE CONTINUOUS ORGAN LIFECYCLE                          |
+-----------------------------------------------------------------------------------+

   [ Acoustic Sound Wave ]
              |
              v
     +-----------------+
     |   EARS ORGAN    | <--- SoundDevice 16kHz mono stream (0.5s chunks)
     +--------+--------+ <--- Background Daemon Thread & Thread-safe Queue
              |          <--- RMS Energy Calibration for noise threshold
              |          <--- 300ms pause triggers automatic end-of-speech
              v
       [ Spoken Text ]   e.g., "Cronus, what is our current deployment status?"
              |
              v
     +-----------------+
     |   BRAIN ORGAN   |
     +--------+--------+
              |
              |---> Node 1: prepare_input
              |             * Loads persona from Behaviour/persona.py
              |             * Formats system instructions & wake receipts
              |             * Dynamically resolves active LLM via llm.py
              |
              |---> Node 2: thinking
              |             * Invokes active LLM waterfall
              |             * Groq (300ms) -> Nemotron 3 Ultra -> Gemini -> Ollama
              |
              |---> Node 3: send_to_mouth
              |             * Strips markdown bolding, code fences, emojis
              |             * Formats human-friendly prosody for vocalization
              v
       [ Clean Text ]    e.g., "All systems are operational and synchronized."
              |
              v
     +-----------------+
     |   MOUTH ORGAN   |
     +--------+--------+
              |
              |---> Console Echo: Prints '[Mouth] All systems are operational...'
              |---> Kokoro Pipeline: Synthesizes American English audio tensors
              |---> Audio Playback: SoundDevice streams at 24,000 Hz
              |---> Resilient Failover: PyTTSx3 fallback if GPU audio is busy
              v
   [ Acoustic Vocal Wave ]
```

---

## 3. Subfolder Documentation Index

* **[Brain.md](file:///D:/Codes/CRONUS-ASI/Cronus_Dismantled/Organs/Brain.md)**: Deep dive into the LangGraph state machine, persona injection, and the multi-tier cloud waterfall.
* **[Ears.md](file:///D:/Codes/CRONUS-ASI/Cronus_Dismantled/Organs/Ears.md)**: Deep dive into hardware-accelerated Whisper inference, audio queue buffering, and 300ms pause detection.
* **[Mouth.md](file:///D:/Codes/CRONUS-ASI/Cronus_Dismantled/Organs/Mouth.md)**: Deep dive into Kokoro-82M neural synthesis, phoneme generation, and resilient audio fallbacks.
