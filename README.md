# Malayalam Speech-to-Text and English Translation System

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![License](https://img.shields.io/badge/License-MIT-yellow)
![Frontends](https://img.shields.io/badge/Frontends-5-brightgreen)

An end-to-end project that captures spoken **Malayalam**, transcribes it to text, and translates it to **English** — shipped with **5 different frontends** and **2 translation backends**.

> Published research project — see `Project_report.pdf` and `e- Certificate_of_publication.png` for the accompanying publication.

---

## What's inside

### 🎨 Five Frontends

| Frontend | File / Folder | Type | Best for |
|---|---|---|---|
| **Tkinter (cloud)** | `app.py` | Desktop GUI | Quick local use |
| **Tkinter (offline)** | `app_offline.py` | Desktop GUI | Fully offline NMT (requires model) |
| **Gradio** | `app_gradio.py` | Web UI | HuggingFace Spaces deploy |
| **Streamlit** | `app_streamlit.py` | Web UI | Streamlit Cloud deploy |
| **Flask + HTML/CSS/JS** | `flask_app/` | Custom web app | Full control, deploy anywhere |

### 🧠 Two Translation Backends

| Backend | Used by | Internet | Setup |
|---|---|---|---|
| Google Translate (`deep-translator`) | All web versions + `app.py` | Required | Just pip install |
| IndicTrans2 + ctranslate2 (offline NMT) | `app_offline.py` + original notebook | No | Download model (~800 MB+) |

---

## Project Structure

```
Malayalam-speech-translation/
├── app.py                          # Tkinter desktop (cloud / Google Translate)
├── app_offline.py                  # Tkinter desktop (offline IndicTrans2)
├── app_gradio.py                   # Gradio web UI
├── app_streamlit.py                # Streamlit web UI
├── flask_app/
│   ├── app.py                      # Flask backend
│   ├── templates/index.html        # Custom HTML
│   └── static/
│       ├── style.css               # Custom CSS
│       └── app.js                  # Browser MediaRecorder + fetch
├── project_code_cmpltd.ipynb       # Original research notebook
├── requirements.txt                # Tkinter cloud version deps
├── requirements-offline.txt        # Offline NMT deps
├── requirements-web.txt            # Web frontends (Gradio + Streamlit + Flask)
├── Project_report.pdf
├── e- Certificate_of_publication.png
├── README.md
├── LICENSE
└── .gitignore
```

---

## Quick Start

```bash
git clone https://github.com/ZainRafeeque/Malayalam-speech-translation.git
cd Malayalam-speech-translation

python -m venv venv
# Windows
venv\Scripts\activate
# Linux / macOS
source venv/bin/activate
```

Then install whichever frontend stack you want and run it:

### 1. Tkinter desktop (default)

```bash
pip install -r requirements.txt
python app.py
```

> **Windows:** `pip install pipwin && pipwin install pyaudio` if PyAudio fails.
> **Linux:** `sudo apt-get install portaudio19-dev python3-pyaudio` first.

### 2. Gradio web UI

```bash
pip install -r requirements-web.txt
python app_gradio.py
# Opens http://127.0.0.1:7860
```

### 3. Streamlit web UI

```bash
pip install -r requirements-web.txt
streamlit run app_streamlit.py
# Opens http://localhost:8501
```

### 4. Flask + custom HTML/CSS/JS

```bash
pip install -r requirements-web.txt
# ffmpeg required for browser audio conversion (https://ffmpeg.org/download.html)
python flask_app/app.py
# Opens http://127.0.0.1:5000
```

### 5. Offline IndicTrans2 (Tkinter)

```bash
pip install -r requirements-offline.txt
# Download an IndicTrans2 ml->en ctranslate2 model into ./final_model/
python app_offline.py
```

See the [Offline version](#offline-version-indictrans2--ctranslate2) section below.

---

## How to use any frontend

1. Click **Start Recording** (or upload an audio file in Streamlit / type in any version).
2. Speak in Malayalam (clear voice, quiet room).
3. The Malayalam transcription appears.
4. The English translation appears below it.

> An active **internet connection** is required for both speech recognition (Google Speech API) and translation in all cloud versions.

---

## Deploy

### Gradio → HuggingFace Spaces (free)

1. Create a new Gradio Space at https://huggingface.co/new-space
2. Upload `app_gradio.py` (rename to `app.py` in the Space)
3. Upload `requirements-web.txt` (rename to `requirements.txt`)
4. Done — your Space gets a public URL

### Streamlit → Streamlit Community Cloud (free)

1. Push this repo to GitHub
2. Sign in at https://share.streamlit.io
3. Pick this repo, point to `app_streamlit.py`
4. Set requirements file to `requirements-web.txt`

### Flask → Render / Railway / Fly.io

1. Use a `gunicorn` start command: `gunicorn -w 2 -b 0.0.0.0:$PORT flask_app.app:app`
2. Add ffmpeg to the build (most platforms have it as a buildpack/preinstalled)

---

## Offline Version (IndicTrans2 + ctranslate2)

### 1. Install offline deps

```bash
pip install -r requirements-offline.txt
```

### 2. Obtain an IndicTrans2 ml→en model in ctranslate2 format

You need a folder with:

```
final_model/
├── config.json
├── model.bin
└── vocab/
    ├── model.SRC
    └── model.TGT
```

Convert from the official model:

- HF: https://huggingface.co/ai4bharat/indictrans2-indic-en-1B
- or distilled: https://huggingface.co/ai4bharat/indictrans2-indic-en-dist-200M
- Tool: `ct2-transformers-converter` (from the `ctranslate2` package)
- Guide: https://opennmt.net/CTranslate2/guides/transformers.html

### 3. Run

```bash
python app_offline.py                                # default ./final_model
python app_offline.py --model-dir /path/to/model    # custom path
# Or set MALAYALAM_MODEL_DIR environment variable
```

---

## Tech Stack

| Concern | Library |
|---|---|
| Desktop GUI | Tkinter |
| Web UI options | Gradio · Streamlit · Flask + vanilla JS |
| Speech recognition | SpeechRecognition + Google Speech API |
| Audio capture (desktop) | PyAudio |
| Audio capture (web) | Browser MediaRecorder API / Streamlit `st.audio_input` / Gradio `gr.Audio` |
| Audio format conversion (Flask) | pydub + ffmpeg |
| Cloud translation | deep-translator (Google Translate) |
| Offline translation | ctranslate2 (IndicTrans2 model) |
| Offline preprocessing | indic-nlp-library, SentencePiece |

---

## Roadmap

- [ ] Offline ASR option (Whisper / Vosk) for end-to-end offline pipeline
- [ ] Stop-recording hotkey
- [ ] Multi-target language selector
- [ ] Audio file upload in Tkinter version
- [ ] Save transcription/translation history to file
- [ ] Docker image bundling all 5 frontends

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
