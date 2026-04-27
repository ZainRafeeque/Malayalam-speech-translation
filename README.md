# Malayalam Speech-to-Text and English Translation System

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![License](https://img.shields.io/badge/License-MIT-yellow)
![Libraries](https://img.shields.io/badge/Libraries-Tkinter%20%7C%20SpeechRecognition%20%7C%20ctranslate2-green)

An end-to-end desktop application that captures spoken **Malayalam**, transcribes it to text, and translates it to **English** using neural machine translation (IndicTrans2 + ctranslate2).

> Published research project — see `Project_report.pdf` and `e- Certificate_of_publication.png` for the accompanying publication.

---

## Features

- **Real-time Speech Recognition** — Captures and transcribes Malayalam speech via Google Speech API.
- **Neural Machine Translation** — Translates Malayalam text to English using `ctranslate2`-optimized IndicTrans2 models.
- **User-Friendly GUI** — Clean Tkinter interface with separate transcription and translation panes.
- **Dialect Adaptation** — Handles diverse Malayalam dialects via Indic NLP normalization.
- **Long Sentence Handling** — Automatically splits/truncates long sentences for optimal translation quality.

---

## Project Structure

```
Malayalam-speech-translation/
├── app.py                          # Standalone runnable application
├── project_code_cmpltd.ipynb       # Original Jupyter notebook
├── requirements.txt                # Python dependencies
├── Project_report.pdf              # Published research report
├── e- Certificate_of_publication.png
├── README.md
├── LICENSE
└── .gitignore
```

---

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/ZainRafeeque/Malayalam-speech-translation.git
cd Malayalam-speech-translation
```

### 2. Create a virtual environment (recommended)

```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux / macOS
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

> **Windows users:** If `PyAudio` fails to install, use a prebuilt wheel:
> `pip install pipwin && pipwin install pyaudio`

> **Linux users:** Install PortAudio first:
> `sudo apt-get install portaudio19-dev python3-pyaudio`

### 4. Download the translation model

This project uses an **IndicTrans2 Malayalam → English** model converted to the `ctranslate2` format.

1. Download or convert an IndicTrans2 ml→en model. Reference:
   - IndicTrans2: https://github.com/AI4Bharat/IndicTrans2
   - ctranslate2 conversion docs: https://opennmt.net/CTranslate2/guides/transformers.html
2. Place the converted model under a folder, e.g. `./final_model/`. The folder must contain:
   - `model.bin` (or shards)
   - `config.json`
   - `vocab/model.SRC` (SentencePiece source model)
   - `vocab/model.TGT` (SentencePiece target model)

---

## Usage

### Run the GUI app

```bash
# Use default model location: ./final_model
python app.py

# Or pass a custom model path
python app.py --model-dir "/path/to/your/final_model"

# Or set via environment variable
export MALAYALAM_MODEL_DIR="/path/to/your/final_model"   # Linux/macOS
set MALAYALAM_MODEL_DIR=C:\path\to\final_model           # Windows cmd
$env:MALAYALAM_MODEL_DIR="C:\path\to\final_model"        # Windows PowerShell
python app.py
```

### How to use the app

1. Click **"Start Recording"**.
2. Speak in Malayalam after the "Listening..." prompt appears.
3. The transcribed Malayalam text appears in the upper text box.
4. The English translation appears in the lower text box.
5. Click **"Exit"** to close.

---

## Tech Stack

| Component | Library |
|-----------|---------|
| GUI | Tkinter |
| Speech Recognition | SpeechRecognition + Google Speech API |
| Audio Capture | PyAudio |
| Text Normalization | indic-nlp-library |
| Tokenization | SentencePiece |
| Translation Engine | ctranslate2 (IndicTrans2 model) |

---

## Roadmap

- [ ] Stop-recording button / hotkey
- [ ] Language selector (translate to languages other than English)
- [ ] Offline speech recognition (Vosk / Whisper)
- [ ] Audio file upload (translate pre-recorded files)
- [ ] Progress bar during translation
- [ ] Bundled lightweight translation model

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
