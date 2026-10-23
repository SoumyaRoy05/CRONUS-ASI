# Mouth Organ (`Organs/mouth.py`)

The **Mouth** organ provides neural speech synthesis and acoustic vocalization for CRONUS. It utilizes the state-of-the-art **Kokoro-82M** neural TTS model running locally to produce expressive, ultra-realistic human vocal audio.

---

## 1. Core Engineering Highlights

* **Neural TTS (Kokoro-82M)**: Uses `kokoro` weights cached locally in the user's Hugging Face model directory (`HF_HOME`), eliminating external network requests during vocalization.
* **American English Phonemization**: Converts input text into phoneme tokens using `phonemizer` with the `a` (American English) language code and the `af_heart` voice profile.
* **NumPy Audio Concatenation**: Combines streaming audio tensors generated chunk-by-chunk into a seamless 24,000 Hz float32 array.
* **Low-Latency Streaming Playback**: Employs `sounddevice.play(audio, 24000)` with `sounddevice.wait()` for clear, jitter-free playback.
* **Dual Fallback System**: If CUDA VRAM is saturated or SoundDevice encounters an audio hardware lock, the system gracefully falls back to `pyttsx3` (Windows SAPI5) and outputs text to the console so no information is lost.
* **Warning Suppression Filters**: Suppresses redundant PyTorch recurrent layer dropout and weight-norm deprecation warnings to maintain pristine terminal logs.

---

## 2. Technical Architecture

```text
+--------------------------------------------------------------------------+
|                        MOUTH PIPELINE ARCHITECTURE                       |
+--------------------------------------------------------------------------+

   Clean Input Text from Brain
         |
         v
   [ Console Echo ]
         * Immediately flushes '[Mouth] {text}' to stdout for zero-delay visual receipt
         |
         v
   [ Kokoro Neural TTS Pipeline ]
         * Language: 'a' (American English)
         * Voice: 'af_heart' (warm, articulate, authoritative tone)
         |
         |---> text_to_phonemes()
         |---> neural_acoustic_synthesis()
         |---> Yields (graphemes, phonemes, audio_tensor)
         |
         v
   [ Audio Concatenation & Normalization ]
         * np.concatenate(audio_pieces, axis=0)
         * Sample Rate: 24,000 Hz
         |
         v
   [ SoundDevice Audio Output ]
         * sd.play(full_audio, 24000)
         * sd.wait() blocks until vocalization completes cleanly
         |
    (If Error)
         v
   [ SAPI5 / PyTTSx3 Fallback ]
         * Fallback to local Windows speech synthesizer
```

---

## 3. Configuration & Optimization

* **Voice Profile**: Configured to `af_heart` (female voice) or customizable via the `KOKORO_VOICE` environment variable.
* **Sample Rate**: 24,000 Hz (Kokoro native output resolution).
* **Console Transparency**: Always outputs `[Mouth] {text}` to stdout before synthesis starts, ensuring immediate feedback even while neural tensors are computing.

---

## 4. Public API

```python
from Organs.mouth import speak

# Vocalizes text through Kokoro 82M and prints console receipt
speak("Initialization complete. All systems are synchronized.")
```
