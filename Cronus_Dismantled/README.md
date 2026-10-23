# CRONUS ASI: Dismantled Architecture & Engineering Blueprint

CRONUS is engineered as a bi-cameral autonomous artificial superintelligence (ASI) architecture consisting of two complementary operational layers:
1. **The Sensory-Vocal Organ Layer (`Organs/`)**: Low-latency, real-time auditory acquisition, neural speech-to-text, LangGraph cognitive state orchestration, and high-fidelity neural voice synthesis.
2. **The Titan Council Cognitive Layer (`Titan_Council/`)**: High-concurrency, asynchronous multi-agent deliberation framework governed by 6 specialized Titan agents under the consensus orchestration of the Council Chamber.

---

## Architectural Topology

```text
=============================================================================
                          CRONUS BI-CAMERAL TOPOLOGY
=============================================================================

                      +-----------------------------+
                      |         USER INPUT          |
                      |  (Acoustic Audio / Speech)  |
                      +--------------+--------------+
                                     |
                                     v
                        [ ORGAN: Ears (Auditio) ]
                        - 16 kHz Mono Sampling
                        - SoundDevice Stream Queue
                        - Ambient Energy Calibration
                        - Faster Whisper (CUDA float16)
                        - 300ms Dynamic Phrase Pause
                                     |
                                     v
                       [ ORGAN: Brain (Cerebrum) ]
                        - LangGraph State Machine
                        - Persona & Receipt Injection
                        - Multi-Tier LLM Waterfall:
                            * Tier 1: Groq (300ms Conversational)
                            * Tier 2: NVIDIA Nemotron 3 Ultra (550B MoE)
                            * Tier 3: Google Gemini (Flash / Pro)
                            * Tier 4: Ollama (Qwen2.5 Local Fallback)
                        - Text Sanitizer & Speech Cleaner
                                     |
                                     v
                        [ ORGAN: Mouth (Vox/Sonus) ]
                        - Kokoro 82M Neural TTS
                        - American English Phonemizer
                        - NumPy Audio Stitching
                        - 24 kHz SoundDevice Output
                        - Resilient PyTTSx3 Fallback
                                     |
                                     v
                      +-----------------------------+
                      |       USER PERCEPTION       |
                      |    (Spoken Vocal Response)  |
                      +-----------------------------+

                                     *
                                  *     *  (Complex Cognitive Tasks)
                               *           *
                             v               v
=============================================================================
                      THE TITAN COUNCIL (COGNITIVE CHAMBER)
=============================================================================
  
        +---------------------------------------------------------+
        |                 CouncilChamber Engine                   |
        |             High-Concurrency Async Gather               |
        +----------------------------+----------------------------+
                                     |
      +------------------------------+------------------------------+
      |                              |                              |
      v                              v                              v
[ PROMETHEUS ]                 [  THEMIS  ]                   [  HYPERION  ]
Architectural Planner          AST Safety Auditor             Context & Research
- Multi-step Blueprints        - Static AST Parser            - Web & Doc Scraping
- Dependency Resolution        - Forbidden Module Guard       - API Reference Scraper
- Dynamic Replanning           - Execution Whitelist          - Knowledge Synthesizer
      |                              |                              |
      +------------------------------+------------------------------+
                                     |
      +------------------------------+------------------------------+
      |                              |                              |
      v                              v                              v
[   ATLAS   ]                  [  HELIOS  ]                   [   COEUS    ]
System Execution               Vision & Screen                Memory & Knowledge
- Sandboxed Shell Runner       - Desktop Capture              - SQLite State Store
- Safe File I/O Manager        - Coordinate Mapping           - Session Journal
- Process Lifecycle Guard      - PyAutoGUI / pywin32 GUI      - Long-Term Vector Vault
=============================================================================
```

---

## Directory Navigation

* **[Organs Subfolder](file:///D:/Codes/CRONUS-ASI/Cronus_Dismantled/Organs/README.md)**:
  * [Brain.md](file:///D:/Codes/CRONUS-ASI/Cronus_Dismantled/Organs/Brain.md): LangGraph cognitive state flow, persona synthesis, and multi-tier model waterfalls.
  * [Ears.md](file:///D:/Codes/CRONUS-ASI/Cronus_Dismantled/Organs/Ears.md): Real-time microphone listening, CUDA Whisper acceleration, and 300ms pause tuning.
  * [Mouth.md](file:///D:/Codes/CRONUS-ASI/Cronus_Dismantled/Organs/Mouth.md): Kokoro 82M neural TTS, phoneme generation, 24kHz audio streaming, and fallback.

* **[Titans Subfolder](file:///D:/Codes/CRONUS-ASI/Cronus_Dismantled/Titans/README.md)**:
  * [Chamber.md](file:///D:/Codes/CRONUS-ASI/Cronus_Dismantled/Titans/Chamber.md): High-concurrency async orchestrator and multi-agent consensus engine.
  * [Prometheus.md](file:///D:/Codes/CRONUS-ASI/Cronus_Dismantled/Titans/Prometheus.md): Forethought, architecture decomposition, and strategic replanning.
  * [Atlas.md](file:///D:/Codes/CRONUS-ASI/Cronus_Dismantled/Titans/Atlas.md): System execution, sandboxed shell automation, and contained file I/O.
  * [Themis.md](file:///D:/Codes/CRONUS-ASI/Cronus_Dismantled/Titans/Themis.md): AST syntax security, forbidden module detection, and command auditing.
  * [Hyperion.md](file:///D:/Codes/CRONUS-ASI/Cronus_Dismantled/Titans/Hyperion.md): Real-time web retrieval, documentation scraping, and context synthesis.
  * [Helios.md](file:///D:/Codes/CRONUS-ASI/Cronus_Dismantled/Titans/Helios.md): Desktop visual perception, coordinate mapping, and UI automation.
  * [Coeus.md](file:///D:/Codes/CRONUS-ASI/Cronus_Dismantled/Titans/Coeus.md): Persistent SQLite vault, cross-session continuity, and memory recall.
