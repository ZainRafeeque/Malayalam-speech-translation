# Malayalam Speech-to-Text and English Translation System

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![License](https://img.shields.io/badge/License-MIT-yellow)
![Libraries](https://img.shields.io/badge/Libraries-Tkinter%20%7C%20SpeechRecognition%20%7C%20ctranslate2-green)

An end-to-end desktop application that captures spoken **Malayalam**, transcribes it to text, and translates it to **English**.

> Published research project — see `Project_report.pdf` and `e- Certificate_of_publication.png` for the accompanying publication.

---

## Two Versions

This repository ships **two interchangeable apps**:

| Script | Translation backend | Internet | Setup effort |
|---|---|---|---|
| `app.py` | Google Translate (via `deep-translator`) | Required | One pip install — works instantly |
| `app_offline.py` | IndicTrans2 + ctranslate2 (offline NMT) | Speech-to-text only | Requires downloading a translation model |

Both share the same Tkinter GUI, threaded mic capture, and Google Speech Recognition for the speech-to-text step.

---

## Features

- **Real-time Speech Recognition** — Captures and transcribes Malayalam speech via Google Speech API.
- **Two translation backends** — Pick the cloud (`app.py`) or offline NMT (`app_offline.py`) version.
- **User-Friendly GUI** — Clean Tkinter interface with separate transcription and translation panes, status indicator, and a Clear button.
- **Threaded I/O** — Recording and translation run on a background thread so the UI never freezes.
- **Robust Error Handling** — Friendly messages for mic issues, network failures, and unrecognized speech.
- **Dialect Adaptation** (offline) — Indic NLP normalization + Devanagari transliteration before NMT.
- **Long Sentence Handling** (offline) — Auto-truncates at 256 tokens.

---

## Project Structure

```
Malayalam-speech-translation/
├── app.py                          # Cloud version (Google Translate)
├── app_offline.py                  # Offline version (IndicTrans2 + ctranslate2)
├── project_code_cmpltd.ipynb       # Original research notebook
├── requirements.txt                # Deps for app.py
├── requirements-offline.txt        # Deps for app_offline.py
├── Project_report.pdf              # Published research report
├── e- Certificate_of_publication.png
├── README.md
├── LICENSE
└── .gitignore
```

---

## Quick Start (Cloud version)

```bash
git clone https://github.com/ZainRafeeque/Malayalam-speech-translation.git
cd Malayalam-speech-translation

python -m venv venv
# Windows
venv\Scripts\activate
# Linux / macOS
source venv/bin/activate

pip install -r requirements.txt
python app.py
```

> **Windows users:** If `PyAudio` fails to install, try a prebuilt wheel:
> `pip install pipwin && pipwin install pyaudio`
>
> **Linux users:** Install PortAudio first:
> `sudo apt-get install portaudio19-dev python3-pyaudio`

### How to use

1. Click **"Start Recording"**.
2. Speak in Malayalam after the *"Listening... speak now"* status appears.
3. The transcribed Malayalam text appears in the **upper** text box.
4. The English translation appears in the **lower** text box.
5. Click **"Clear"** to reset, or **"Exit"** to close.

> An active **internet connection** is required for both the speech recognition and translation services in this version.

---

## Offline Version (IndicTrans2 + ctranslate2)

The offline version is the original research-stage prototype. It runs neural machine translation **fully on your machine** (no translation API call), but you must supply the model files yourself.

### 1. Install offline dependencies

```bash
pip install -r requirements-offline.txt
```

### 2. Obtain an IndicTrans2 ml→en model in ctranslate2 format

You need a folder containing the following files:

```
final_model/
├── config.json
├── model.bin
└── vocab/
    ├── model.SRC      # SentencePiece source model
    └── model.TGT      # SentencePiece target model
```

Common ways to obtain it:

- **Convert from the official IndicTrans2 model** (recommended for best quality):
  - HF model: https://huggingface.co/ai4bharat/indictrans2-indic-en-1B
                or distilled: https://huggingface.co/ai4bharat/indictrans2-indic-en-dist-200M
  - Conversion tool: `ct2-transformers-converter` (from the `ctranslate2` package)
  - See: https://opennmt.net/CTranslate2/guides/transformers.html
- **Use a community pre-converted ctranslate2 model** if one is available.

### 3. Run

```bash
# Default model path: ./final_model
python app_offline.py

# Or pass a custom path
python app_offline.py --model-dir "/path/to/final_model"

# Or use an environment variable
export MALAYALAM_MODEL_DIR="/path/to/final_model"     # Linux / macOS
$env:MALAYALAM_MODEL_DIR="C:\path\to\final_model"     # PowerShell
set MALAYALAM_MODEL_DIR=C:\path\to\final_model        # cmd
python app_offline.py
```

The first translation triggers a one-time model load (a few seconds on CPU); subsequent translations are fast.

---

## Tech Stack

| Component | `app.py` | `app_offline.py` |
|---|---|---|
| GUI | Tkinter | Tkinter |
| Speech recognition | SpeechRecognition + Google Speech API | SpeechRecognition + Google Speech API |
| Audio capture | PyAudio | PyAudio |
| Text normalization | — | indic-nlp-library |
| Tokenization | — | SentencePiece |
| Translation | deep-translator (Google Translate) | ctranslate2 (IndicTrans2 model) |

---

## Roadmap

- [ ] Offline ASR option (Vosk / Whisper) for end-to-end offline pipeline
- [ ] Stop-recording button / hotkey
- [ ] Language selector (translate to languages other than English)
- [ ] Audio file upload (translate pre-recorded files)
- [ ] Save transcription/translation history to file

---

## Citation

If you use this project, please cite the published report:

> Zain Rafeeque, *A Novel Approach to Malayalam Speech-to-Text and Text-to-English Translation*. See `Project_report.pdf`.

---

## License

Distributed under the MIT License. See `LICENSE` for details.

---

## Author

**Zain Rafeeque** — [GitHub @ZainRafeeque](https://github.com/ZainRafeeque)
