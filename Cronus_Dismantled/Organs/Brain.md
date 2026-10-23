# Brain Organ (`Organs/brain.py`)

The **Brain** is the central reasoning and cognitive coordinator of CRONUS. Built on **LangGraph**, it transforms raw transcribed text from the Ears into a structured, persona-aligned response and prepares it for speech synthesis by the Mouth.

---

## 1. Structural Overview & Responsibilities

The Brain organ enforces a deterministic state machine through LangGraph's `StateGraph`. Every cycle executes three sequential nodes:
1. **`prepare_input`**: Formats the conversational prompt, applies the active persona, and selects the optimal LLM.
2. **`thinking`**: Transmits the structured message payload to the selected LLM and handles live failovers.
3. **`send_to_mouth`**: Sanitizes the raw model response into natural, speakable text and forwards it to the Mouth.

---

## 2. The `BrainState` Schema

The shared state passed through each node in the LangGraph graph is typed via `BrainState`:

```python
class BrainState(TypedDict, total=False):
    user_prompt: str         # Transcribed text input from Ears
    system_prompt: str       # Persona system instructions
    messages: list           # SystemMessage and HumanMessage payload
    selected_llm: Any        # Active BaseChatModel instance from llm.py
    raw_response: str        # Raw string output from LLM invocation
    final_response: str      # Cleaned, speakable string ready for Mouth
```

---

## 3. Node-by-Node Breakdown

### Node 1: `prepare_input(state: BrainState) -> BrainState`
* **Persona Loading**: Queries [Behaviour/persona.py](file:///D:/Codes/CRONUS-ASI/Behaviour/persona.py) to load CRONUS's core persona (`CRONUS_PERSONA`), identity guidelines, and wake-word receipts.
* **Message Packaging**: Constructs LangChain message structures:
  * `SystemMessage(content=system_prompt)`
  * `HumanMessage(content=user_prompt)`
* **Model Dynamic Resolution**: Calls `llm.get_llm()` to obtain the active conversational waterfall.

### Node 2: `thinking(state: BrainState) -> BrainState`
* Invokes the resolved LLM chain synchronously:
  ```python
  response = selected_llm.invoke(messages)
  state["raw_response"] = response.content
  ```
* Seamlessly catches transient network timeouts and triggers downstream model fallbacks automatically.

### Node 3: `send_to_mouth(state: BrainState) -> BrainState`
* Language models frequently output asterisks (`**bold**`), code blocks (` ``` `), bullet points, and emojis.
* The Brain strips visual markdown artifacts and formats numbers and abbreviations so Kokoro TTS synthesizes smooth, natural-sounding audio.

---

## 4. Multi-Tier LLM Waterfall Integration

The Brain relies on the multi-tier waterfall defined in [llm.py](file:///D:/Codes/CRONUS-ASI/llm.py):

| Tier | Provider & Model | Latency | Role |
| :--- | :--- | :--- | :--- |
| **Tier 1** | **Groq** (`openai/gpt-oss-120b`, `openai/gpt-oss-20b`) | ~300ms | Ultra-fast real-time voice response |
| **Tier 2** | **NVIDIA NIM** (`nvidia/nemotron-3-ultra-550b-a55b`) | ~1s | Deep reasoning, 550B MoE intelligence |
| **Tier 3** | **Google Gemini** (`gemini-flash-latest`, `gemini-pro-latest`) | ~800ms | Resilient cloud secondary failover |
| **Tier 4** | **Ollama** (`qwen2.5:3b`) | Local | Zero-network offline fallback |

---

## 5. Public API

```python
from Organs.brain import Brain

brain = Brain()
final_response = brain.think(prompt="What is your status?")
```
* **Execution Flow**: `think(prompt)` executes the compiled LangGraph workflow end-to-end and immediately calls `Mouth.speak(final_response)`.
